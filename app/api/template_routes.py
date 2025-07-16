from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from sqlalchemy import desc, or_
from app.models import db, EmailTemplate, EmailResponse
import json

template_bp = Blueprint('template_api', __name__)

@template_bp.route('/', methods=['GET'])
def get_templates():
    """Get email templates with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        search = request.args.get('search')
        
        # Build query
        query = EmailTemplate.query
        
        # Apply filters
        if category:
            query = query.filter(EmailTemplate.category == category)
        
        if active_only:
            query = query.filter(EmailTemplate.is_active == True)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    EmailTemplate.name.ilike(search_term),
                    EmailTemplate.description.ilike(search_term),
                    EmailTemplate.subject_template.ilike(search_term),
                    EmailTemplate.body_template.ilike(search_term)
                )
            )
        
        # Order by most recent
        query = query.order_by(desc(EmailTemplate.updated_at))
        
        # Paginate
        templates = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format response
        template_list = []
        for template in templates.items:
            # Count usage
            usage_count = EmailResponse.query.filter(
                EmailResponse.template_used == template.name
            ).count()
            
            template_data = {
                'id': template.id,
                'name': template.name,
                'description': getattr(template, 'description', ''),
                'category': template.category,
                'subject_template': template.subject_template,
                'body_preview': template.body_template[:200] + '...' if len(template.body_template or '') > 200 else (template.body_template or ''),
                'variables': template.variables if template.variables else [],
                'is_active': template.is_active,
                'usage_count': usage_count,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat() if template.updated_at else None
            }
            template_list.append(template_data)
        
        return jsonify({
            'templates': template_list,
            'pagination': {
                'page': templates.page,
                'pages': templates.pages,
                'per_page': templates.per_page,
                'total': templates.total,
                'has_next': templates.has_next,
                'has_prev': templates.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': 'Failed to get templates'}), 500

@template_bp.route('/<int:template_id>', methods=['GET'])
def get_template_detail(template_id):
    """Get detailed template information"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        # Count usage
        usage_count = EmailResponse.query.filter(
            EmailResponse.template_used == template.name
        ).count()
        
        # Get recent usage examples
        recent_usage = EmailResponse.query.filter(
            EmailResponse.template_used == template.name
        ).order_by(desc(EmailResponse.created_at)).limit(5).all()
        
        usage_examples = []
        for response in recent_usage:
            usage_examples.append({
                'id': response.id,
                'email_id': response.email_id,
                'subject': response.subject,
                'status': response.status,
                'confidence': response.generation_confidence,
                'created_at': response.created_at.isoformat()
            })
        
        template_data = {
            'id': template.id,
            'name': template.name,
            'description': getattr(template, 'description', ''),
            'category': template.category,
            'subject_template': template.subject_template,
            'body_template': template.body_template,
            'variables': template.variables if template.variables else [],
            'is_active': template.is_active,
            'usage_count': usage_count,
            'recent_usage': usage_examples,
            'created_at': template.created_at.isoformat(),
            'updated_at': template.updated_at.isoformat() if template.updated_at else None
        }
        
        return jsonify(template_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting template detail: {str(e)}")
        return jsonify({'error': 'Failed to get template details'}), 500

@template_bp.route('/', methods=['POST'])
def create_template():
    """Create a new email template"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'subject_template', 'body_template']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if template name already exists
        existing = EmailTemplate.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Template name already exists'}), 400
        
        # Create template
        template = EmailTemplate(
            name=data['name'],
            category=data.get('category', 'general'),
            subject_template=data['subject_template'],
            body_template=data['body_template'],
            variables=data.get('variables', []),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'id': template.id,
            'name': template.name,
            'category': template.category,
            'subject_template': template.subject_template,
            'body_template': template.body_template,
            'variables': template.variables,
            'is_active': template.is_active,
            'created_at': template.created_at.isoformat()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating template: {str(e)}")
        return jsonify({'error': 'Failed to create template'}), 500

@template_bp.route('/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        # Check if name is being changed and if it conflicts
        if 'name' in data and data['name'] != template.name:
            existing = EmailTemplate.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'error': 'Template name already exists'}), 400
        
        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'category' in data:
            template.category = data['category']
        if 'subject_template' in data:
            template.subject_template = data['subject_template']
        if 'body_template' in data:
            template.body_template = data['body_template']
        if 'variables' in data:
            template.variables = data['variables']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': template.id,
            'name': template.name,
            'category': template.category,
            'subject_template': template.subject_template,
            'body_template': template.body_template,
            'variables': template.variables,
            'is_active': template.is_active,
            'updated_at': template.updated_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating template: {str(e)}")
        return jsonify({'error': 'Failed to update template'}), 500

@template_bp.route('/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        # Check if template is being used
        usage_count = EmailResponse.query.filter(
            EmailResponse.template_used == template.name
        ).count()
        
        if usage_count > 0:
            return jsonify({
                'error': f'Cannot delete template. It has been used {usage_count} times.'
            }), 400
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'message': 'Template deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting template: {str(e)}")
        return jsonify({'error': 'Failed to delete template'}), 500

@template_bp.route('/<int:template_id>/toggle', methods=['POST'])
def toggle_template_status(template_id):
    """Toggle template active status"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        template.is_active = not template.is_active
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': template.id,
            'name': template.name,
            'is_active': template.is_active,
            'updated_at': template.updated_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error toggling template status: {str(e)}")
        return jsonify({'error': 'Failed to toggle template status'}), 500

@template_bp.route('/categories', methods=['GET'])
def get_template_categories():
    """Get all template categories"""
    try:
        categories = db.session.query(EmailTemplate.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        # Add default categories if not present
        default_categories = ['general', 'vendas', 'suporte', 'agendamento', 'informacao']
        for cat in default_categories:
            if cat not in category_list:
                category_list.append(cat)
        
        return jsonify({
            'categories': sorted(category_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting template categories: {str(e)}")
        return jsonify({'error': 'Failed to get template categories'}), 500

@template_bp.route('/stats', methods=['GET'])
def get_template_stats():
    """Get template usage statistics"""
    try:
        # Total templates
        total_templates = EmailTemplate.query.count()
        active_templates = EmailTemplate.query.filter_by(is_active=True).count()
        
        # Most used templates
        most_used = db.session.query(
            EmailResponse.template_used,
            db.func.count(EmailResponse.id).label('usage_count')
        ).filter(
            EmailResponse.template_used.isnot(None)
        ).group_by(
            EmailResponse.template_used
        ).order_by(
            desc('usage_count')
        ).limit(5).all()
        
        most_used_list = []
        for template_name, count in most_used:
            template = EmailTemplate.query.filter_by(name=template_name).first()
            most_used_list.append({
                'name': template_name,
                'usage_count': count,
                'category': template.category if template else 'unknown'
            })
        
        # Templates by category
        by_category = db.session.query(
            EmailTemplate.category,
            db.func.count(EmailTemplate.id).label('count')
        ).group_by(
            EmailTemplate.category
        ).all()
        
        category_stats = {}
        for category, count in by_category:
            category_stats[category or 'uncategorized'] = count
        
        return jsonify({
            'total_templates': total_templates,
            'active_templates': active_templates,
            'inactive_templates': total_templates - active_templates,
            'most_used': most_used_list,
            'by_category': category_stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting template stats: {str(e)}")
        return jsonify({'error': 'Failed to get template statistics'}), 500

@template_bp.route('/<int:template_id>/preview', methods=['POST'])
def preview_template(template_id):
    """Preview template with sample data"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        data = request.get_json() or {}
        
        # Get sample variables or use provided ones
        variables = data.get('variables', {})
        
        # Default sample data
        default_vars = {
            'sender_name': 'João Silva',
            'sender_email': 'joao@exemplo.com',
            'business_name': 'Prof. Diogo Moreira',
            'product_name': 'Coaching Individual',
            'product_price': 'R$ 2.997',
            'current_date': datetime.now().strftime('%d/%m/%Y'),
            'current_time': datetime.now().strftime('%H:%M')
        }
        
        # Merge with provided variables
        preview_vars = {**default_vars, **variables}
        
        # Simple template rendering (replace {{variable}} with values)
        subject_preview = template.subject_template
        body_preview = template.body_template
        
        for var_name, var_value in preview_vars.items():
            placeholder = f"{{{{{var_name}}}}}"
            subject_preview = subject_preview.replace(placeholder, str(var_value))
            body_preview = body_preview.replace(placeholder, str(var_value))
        
        return jsonify({
            'template_id': template.id,
            'template_name': template.name,
            'subject_preview': subject_preview,
            'body_preview': body_preview,
            'variables_used': preview_vars
        })
        
    except Exception as e:
        current_app.logger.error(f"Error previewing template: {str(e)}")
        return jsonify({'error': 'Failed to preview template'}), 500
