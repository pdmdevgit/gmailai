from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.models import db, EmailTemplate, SystemSettings, ProcessingLog
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService

admin_bp = Blueprint('admin_api', __name__)

@admin_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get all email templates"""
    try:
        templates = EmailTemplate.query.order_by(EmailTemplate.name).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'product': template.product,
                'subject_template': template.subject_template,
                'body_template': template.body_template,
                'variables': template.variables,
                'usage_count': template.usage_count,
                'success_rate': template.success_rate,
                'is_active': template.is_active,
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat()
            })
        
        return jsonify({
            'templates': template_list,
            'total': len(template_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': 'Failed to get templates'}), 500

@admin_bp.route('/templates', methods=['POST'])
def create_template():
    """Create a new email template"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'subject_template', 'body_template']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if template name already exists
        existing = EmailTemplate.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Template name already exists'}), 400
        
        template = EmailTemplate(
            name=data['name'],
            category=data['category'],
            product=data.get('product'),
            subject_template=data['subject_template'],
            body_template=data['body_template'],
            variables=data.get('variables', {}),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'id': template.id,
            'name': template.name,
            'message': 'Template created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating template: {str(e)}")
        return jsonify({'error': 'Failed to create template'}), 500

@admin_bp.route('/templates/<int:template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an email template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            # Check if new name conflicts with existing template
            existing = EmailTemplate.query.filter(
                EmailTemplate.name == data['name'],
                EmailTemplate.id != template_id
            ).first()
            if existing:
                return jsonify({'error': 'Template name already exists'}), 400
            template.name = data['name']
        
        if 'category' in data:
            template.category = data['category']
        if 'product' in data:
            template.product = data['product']
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
            'message': 'Template updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating template: {str(e)}")
        return jsonify({'error': 'Failed to update template'}), 500

@admin_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete an email template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({
            'message': 'Template deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting template: {str(e)}")
        return jsonify({'error': 'Failed to delete template'}), 500

@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    try:
        settings = SystemSettings.query.all()
        
        settings_dict = {}
        for setting in settings:
            value = setting.value
            
            # Convert value based on data type
            if setting.data_type == 'int':
                value = int(value) if value else 0
            elif setting.data_type == 'float':
                value = float(value) if value else 0.0
            elif setting.data_type == 'bool':
                value = value.lower() == 'true' if value else False
            elif setting.data_type == 'json':
                import json
                value = json.loads(value) if value else {}
            
            settings_dict[setting.key] = {
                'value': value,
                'data_type': setting.data_type,
                'description': setting.description,
                'updated_at': setting.updated_at.isoformat()
            }
        
        return jsonify({
            'settings': settings_dict
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting settings: {str(e)}")
        return jsonify({'error': 'Failed to get settings'}), 500

@admin_bp.route('/settings', methods=['POST'])
def update_settings():
    """Update system settings"""
    try:
        data = request.get_json()
        
        for key, setting_data in data.items():
            value = setting_data.get('value')
            data_type = setting_data.get('data_type', 'string')
            description = setting_data.get('description', '')
            
            # Convert value to string for storage
            if data_type == 'json':
                import json
                value = json.dumps(value)
            else:
                value = str(value)
            
            # Update or create setting
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.data_type = data_type
                setting.description = description
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    key=key,
                    value=value,
                    data_type=data_type,
                    description=description
                )
                db.session.add(setting)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': 'Failed to update settings'}), 500

@admin_bp.route('/gmail-accounts/authenticate', methods=['POST'])
def authenticate_gmail_account():
    """Start Gmail account authentication flow"""
    try:
        data = request.get_json()
        account_name = data.get('account_name')
        
        if not account_name:
            return jsonify({'error': 'Account name is required'}), 400
        
        accounts = current_app.config.get('GMAIL_ACCOUNTS', {})
        if account_name not in accounts:
            return jsonify({'error': 'Invalid account name'}), 400
        
        email_address = accounts[account_name]
        
        # Create OAuth flow
        from google_auth_oauthlib.flow import Flow
        
        flow = Flow.from_client_secrets_file(
            current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            scopes=[
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ]
        )
        
        # Set redirect URI
        flow.redirect_uri = f"{request.host_url}auth/callback"
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            login_hint=email_address
        )
        
        # Store state and account info in session or cache
        # For now, we'll use a simple approach
        import json
        state_data = {
            'account_name': account_name,
            'email_address': email_address,
            'state': state
        }
        
        # Store in a temporary file (in production, use Redis or database)
        state_file = f"/tmp/oauth_state_{state}.json"
        with open(state_file, 'w') as f:
            json.dump(state_data, f)
        
        return jsonify({
            'auth_url': authorization_url,
            'state': state,
            'account': account_name,
            'email': email_address
        })
        
    except Exception as e:
        current_app.logger.error(f"Error starting Gmail authentication: {str(e)}")
        return jsonify({'error': f'Failed to start authentication: {str(e)}'}), 500

@admin_bp.route('/gmail-accounts/status', methods=['GET'])
def get_gmail_accounts_status():
    """Get status of Gmail accounts"""
    try:
        accounts = current_app.config.get('GMAIL_ACCOUNTS', {})
        token_dir = current_app.config.get('GMAIL_TOKEN_DIR')
        
        account_status = []
        for account_name, email_address in accounts.items():
            token_file = f"{token_dir}/{account_name}_token.json"
            
            # Check if token file exists
            import os
            is_authenticated = os.path.exists(token_file)
            
            # Get email count for this account
            from app.models import Email
            email_count = Email.query.filter_by(account=account_name).count()
            
            account_status.append({
                'name': account_name,
                'email': email_address,
                'is_authenticated': is_authenticated,
                'email_count': email_count,
                'token_file': token_file
            })
        
        return jsonify({
            'accounts': account_status,
            'total': len(accounts)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting Gmail accounts status: {str(e)}")
        return jsonify({'error': 'Failed to get accounts status'}), 500

@admin_bp.route('/logs', methods=['GET'])
def get_processing_logs():
    """Get processing logs with filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)
        action = request.args.get('action')
        status = request.args.get('status')
        email_id = request.args.get('email_id', type=int)
        
        # Build query
        query = ProcessingLog.query
        
        if action:
            query = query.filter(ProcessingLog.action == action)
        if status:
            query = query.filter(ProcessingLog.status == status)
        if email_id:
            query = query.filter(ProcessingLog.email_id == email_id)
        
        # Order by most recent
        query = query.order_by(ProcessingLog.created_at.desc())
        
        # Paginate
        logs = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        log_list = []
        for log in logs.items:
            log_list.append({
                'id': log.id,
                'email_id': log.email_id,
                'action': log.action,
                'status': log.status,
                'message': log.message,
                'details': log.details,
                'processing_time': log.processing_time,
                'api_calls_made': log.api_calls_made,
                'created_at': log.created_at.isoformat()
            })
        
        return jsonify({
            'logs': log_list,
            'pagination': {
                'page': logs.page,
                'pages': logs.pages,
                'per_page': logs.per_page,
                'total': logs.total,
                'has_next': logs.has_next,
                'has_prev': logs.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting processing logs: {str(e)}")
        return jsonify({'error': 'Failed to get logs'}), 500

@admin_bp.route('/system/cleanup', methods=['POST'])
def cleanup_system():
    """Clean up old data"""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 90)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Clean up old processing logs
        old_logs = ProcessingLog.query.filter(
            ProcessingLog.created_at < cutoff_date
        ).count()
        
        ProcessingLog.query.filter(
            ProcessingLog.created_at < cutoff_date
        ).delete()
        
        # Clean up old emails (optional - be careful with this)
        cleanup_emails = data.get('cleanup_emails', False)
        old_emails = 0
        
        if cleanup_emails:
            from app.models import Email
            old_emails = Email.query.filter(
                Email.created_at < cutoff_date,
                Email.status == 'processed'
            ).count()
            
            Email.query.filter(
                Email.created_at < cutoff_date,
                Email.status == 'processed'
            ).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cleanup completed successfully',
            'logs_deleted': old_logs,
            'emails_deleted': old_emails,
            'cutoff_date': cutoff_date.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during cleanup: {str(e)}")
        return jsonify({'error': 'Failed to cleanup system'}), 500

@admin_bp.route('/system/backup', methods=['POST'])
def backup_system():
    """Create system backup"""
    try:
        import os
        import subprocess
        from datetime import datetime
        
        # Create backup directory
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/gmail_ai_agent_backup_{timestamp}.sql"
        
        # Database backup command (MySQL)
        db_config = current_app.config
        cmd = [
            'mysqldump',
            '-h', db_config.get('MYSQL_HOST', 'localhost'),
            '-u', db_config.get('MYSQL_USER', 'root'),
            f"-p{db_config.get('MYSQL_PASSWORD', '')}",
            db_config.get('MYSQL_DB', 'gmail_ai_agent')
        ]
        
        # Execute backup
        with open(backup_file, 'w') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            # Get file size
            file_size = os.path.getsize(backup_file)
            
            return jsonify({
                'message': 'Backup created successfully',
                'backup_file': backup_file,
                'file_size': file_size,
                'timestamp': timestamp
            })
        else:
            return jsonify({
                'error': 'Backup failed',
                'details': result.stderr
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error creating backup: {str(e)}")
        return jsonify({'error': 'Failed to create backup'}), 500

@admin_bp.route('/test-ai', methods=['POST'])
def test_ai_service():
    """Test AI service functionality"""
    try:
        data = request.get_json()
        test_text = data.get('text', 'Test email for classification')
        
        # Initialize AI service
        ai_service = AIService(
            openai_api_key=current_app.config.get('OPENAI_API_KEY'),
            anthropic_api_key=current_app.config.get('ANTHROPIC_API_KEY'),
            model=current_app.config.get('AI_MODEL', 'gpt-4')
        )
        
        # Test email data
        test_email = {
            'sender_email': 'test@example.com',
            'sender_name': 'Test User',
            'subject': 'Test Subject',
            'body_text': test_text,
            'account': 'test'
        }
        
        # Test classification
        classification = ai_service.classify_email(test_email)
        
        # Test response generation
        response = ai_service.generate_response(test_email, classification)
        
        return jsonify({
            'status': 'success',
            'classification': classification,
            'response': response,
            'model_used': ai_service.model
        })
        
    except Exception as e:
        current_app.logger.error(f"Error testing AI service: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
