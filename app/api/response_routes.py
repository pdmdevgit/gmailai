from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from app.models import db, Email, EmailResponse, EmailTemplate
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
import re

response_bp = Blueprint('response_api', __name__)

@response_bp.route('/generate', methods=['POST'])
def generate_response():
    """Generate AI response for an email"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_id = data.get('email_id')
        template_id = data.get('template_id')
        
        if not email_id:
            return jsonify({'error': 'email_id is required'}), 400
        
        # Get email
        email = Email.query.get_or_404(email_id)
        
        # Get template if provided
        template = None
        if template_id:
            template = EmailTemplate.query.get_or_404(template_id)
        
        # Check if response already exists
        existing_response = EmailResponse.query.filter_by(email_id=email_id).first()
        if existing_response and existing_response.status != 'rejected':
            return jsonify({'error': 'Response already exists for this email'}), 400
        
        # Initialize AI service
        ai_service = AIService(
            openai_api_key=current_app.config.get('OPENAI_API_KEY'),
            anthropic_api_key=current_app.config.get('ANTHROPIC_API_KEY'),
            model=current_app.config.get('AI_MODEL', 'gpt-4')
        )
        
        # Extract sender name for personalization
        sender_name = email.sender_name or email.sender_email.split('@')[0]
        
        # Prepare context for AI
        context = {
            'sender_name': sender_name,
            'sender_email': email.sender_email,
            'subject': email.subject,
            'body': email.body_text,
            'classification': {
                'type': email.classification_type,
                'priority': email.classification_priority,
                'product': email.classification_product,
                'sentiment': email.classification_sentiment
            }
        }
        
        # Prepare email data for AI service
        email_data = {
            'gmail_id': email.gmail_id,
            'sender_name': email.sender_name,
            'sender_email': email.sender_email,
            'subject': email.subject,
            'body_text': email.body_text,
            'account': email.account
        }
        
        # Prepare classification data
        classification_data = {
            'type': email.classification_type,
            'priority': email.classification_priority,
            'product': email.classification_product,
            'sentiment': email.classification_sentiment,
            'confidence': email.classification_confidence
        }
        
        # Generate response using AI service
        if template:
            # Convert template to expected format
            template_data = {
                'subject_template': template.subject_template,
                'body_template': template.body_template,
                'name': template.name
            }
            ai_response = ai_service.generate_response(email_data, classification_data, template_data)
        else:
            ai_response = ai_service.generate_response(email_data, classification_data)
        
        if not ai_response:
            return jsonify({'error': 'Failed to generate AI response'}), 500
        
        response_text = ai_response.get('body_text', '')
        response_subject = ai_response.get('subject', f"Re: {email.subject}")
        confidence = ai_response.get('confidence', 0.0)
        
        # Create response record
        email_response = EmailResponse(
            email_id=email_id,
            subject=response_subject,
            body_text=response_text,
            body_html=f"<p>{response_text.replace(chr(10), '</p><p>')}</p>",
            status='draft',
            ai_model=current_app.config.get('AI_MODEL', 'gpt-4'),
            template_used=template.name if template else 'custom',
            generation_confidence=confidence,
            created_at=datetime.utcnow()
        )
        
        db.session.add(email_response)
        db.session.commit()
        
        return jsonify({
            'id': email_response.id,
            'email_id': email_id,
            'subject': response_subject,
            'body_text': response_text,
            'status': 'draft',
            'confidence': confidence,
            'template_used': template.name if template else 'custom',
            'created_at': email_response.created_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating response: {str(e)}")
        return jsonify({'error': f'Failed to generate response: {str(e)}'}), 500

@response_bp.route('/', methods=['GET'])
def get_responses():
    """Get email responses with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        account = request.args.get('account')
        days_back = request.args.get('days_back', 30, type=int)
        search = request.args.get('search')
        
        # Build query
        query = EmailResponse.query.join(Email)
        
        # Apply filters
        if status:
            query = query.filter(EmailResponse.status == status)
        
        if account:
            query = query.filter(Email.account == account)
        
        # Date filter
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(EmailResponse.created_at >= cutoff_date)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    EmailResponse.subject.ilike(search_term),
                    EmailResponse.body_text.ilike(search_term),
                    Email.sender_email.ilike(search_term),
                    Email.subject.ilike(search_term)
                )
            )
        
        # Order by most recent
        query = query.order_by(desc(EmailResponse.created_at))
        
        # Paginate
        responses = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format response
        response_list = []
        for response in responses.items:
            email = response.email
            response_data = {
                'id': response.id,
                'email_id': response.email_id,
                'subject': response.subject,
                'body_preview': response.body_text[:200] + '...' if len(response.body_text) > 200 else response.body_text,
                'status': response.status,
                'ai_model': response.ai_model,
                'template_used': response.template_used,
                'generation_confidence': response.generation_confidence,
                'approved_by': response.approved_by,
                'approved_at': response.approved_at.isoformat() if response.approved_at else None,
                'sent_at': response.sent_at.isoformat() if response.sent_at else None,
                'created_at': response.created_at.isoformat(),
                'updated_at': response.updated_at.isoformat() if response.updated_at else None,
                'email': {
                    'id': email.id,
                    'account': email.account,
                    'sender_email': email.sender_email,
                    'sender_name': email.sender_name,
                    'subject': email.subject,
                    'received_at': email.received_at.isoformat(),
                    'classification_type': email.classification_type,
                    'classification_priority': email.classification_priority
                }
            }
            response_list.append(response_data)
        
        return jsonify({
            'responses': response_list,
            'pagination': {
                'page': responses.page,
                'pages': responses.pages,
                'per_page': responses.per_page,
                'total': responses.total,
                'has_next': responses.has_next,
                'has_prev': responses.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting responses: {str(e)}")
        return jsonify({'error': 'Failed to get responses'}), 500

@response_bp.route('/<int:response_id>', methods=['GET'])
def get_response_detail(response_id):
    """Get detailed response information"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        email = response.email
        
        response_data = {
            'id': response.id,
            'email_id': response.email_id,
            'subject': response.subject,
            'body_text': response.body_text,
            'body_html': response.body_html,
            'status': response.status,
            'ai_model': response.ai_model,
            'template_used': response.template_used,
            'generation_confidence': response.generation_confidence,
            'approved_by': response.approved_by,
            'approved_at': response.approved_at.isoformat() if response.approved_at else None,
            'sent_at': response.sent_at.isoformat() if response.sent_at else None,
            'created_at': response.created_at.isoformat(),
            'updated_at': response.updated_at.isoformat() if response.updated_at else None,
            'email': {
                'id': email.id,
                'gmail_id': email.gmail_id,
                'thread_id': email.thread_id,
                'account': email.account,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'subject': email.subject,
                'body_text': email.body_text,
                'received_at': email.received_at.isoformat(),
                'classification': {
                    'type': email.classification_type,
                    'priority': email.classification_priority,
                    'product': email.classification_product,
                    'sentiment': email.classification_sentiment,
                    'confidence': email.classification_confidence
                }
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting response detail: {str(e)}")
        return jsonify({'error': 'Failed to get response details'}), 500

@response_bp.route('/<int:response_id>/approve', methods=['POST'])
def approve_response(response_id):
    """Approve a response for sending"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        data = request.get_json() or {}
        
        if response.status == 'sent':
            return jsonify({'error': 'Response already sent'}), 400
        
        approved_by = data.get('approved_by', 'admin')
        
        response.status = 'approved'
        response.approved_by = approved_by
        response.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': response.id,
            'status': response.status,
            'approved_by': response.approved_by,
            'approved_at': response.approved_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error approving response: {str(e)}")
        return jsonify({'error': 'Failed to approve response'}), 500

@response_bp.route('/<int:response_id>/reject', methods=['POST'])
def reject_response(response_id):
    """Reject a response"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        data = request.get_json() or {}
        
        if response.status == 'sent':
            return jsonify({'error': 'Cannot reject sent response'}), 400
        
        response.status = 'rejected'
        response.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': response.id,
            'status': response.status,
            'updated_at': response.updated_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error rejecting response: {str(e)}")
        return jsonify({'error': 'Failed to reject response'}), 500

@response_bp.route('/<int:response_id>/send', methods=['POST'])
def send_response(response_id):
    """Send an approved response"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        
        if response.status != 'approved':
            return jsonify({'error': 'Response must be approved before sending'}), 400
        
        email = response.email
        
        # Initialize Gmail service
        gmail_service = GmailService(
            credentials_file=current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            token_dir=current_app.config.get('GMAIL_TOKEN_DIR')
        )
        
        # Send email
        success = gmail_service.send_email(
            account_name=email.account,
            to_email=email.sender_email,
            subject=response.subject,
            body_text=response.body_text,
            body_html=response.body_html,
            reply_to_id=email.gmail_id
        )
        
        if success:
            response.status = 'sent'
            response.sent_at = datetime.utcnow()
            email.status = 'responded'
            db.session.commit()
            
            return jsonify({
                'id': response.id,
                'status': response.status,
                'sent_at': response.sent_at.isoformat()
            })
        else:
            return jsonify({'error': 'Failed to send email'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error sending response: {str(e)}")
        return jsonify({'error': 'Failed to send response'}), 500

@response_bp.route('/<int:response_id>', methods=['PUT'])
def update_response(response_id):
    """Update a response before sending"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        data = request.get_json()
        
        if response.status == 'sent':
            return jsonify({'error': 'Cannot update sent response'}), 400
        
        # Update fields
        if 'subject' in data:
            response.subject = data['subject']
        if 'body_text' in data:
            response.body_text = data['body_text']
        if 'body_html' in data:
            response.body_html = data['body_html']
        
        # Reset approval if content changed
        if any(field in data for field in ['subject', 'body_text', 'body_html']):
            if response.status == 'approved':
                response.status = 'draft'
                response.approved_by = None
                response.approved_at = None
        
        response.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': response.id,
            'subject': response.subject,
            'body_text': response.body_text,
            'body_html': response.body_html,
            'status': response.status,
            'updated_at': response.updated_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating response: {str(e)}")
        return jsonify({'error': 'Failed to update response'}), 500

@response_bp.route('/<int:response_id>', methods=['DELETE'])
def delete_response(response_id):
    """Delete a response (only if not sent)"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        
        if response.status == 'sent':
            return jsonify({'error': 'Cannot delete sent response'}), 400
        
        db.session.delete(response)
        db.session.commit()
        
        return jsonify({'message': 'Response deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting response: {str(e)}")
        return jsonify({'error': 'Failed to delete response'}), 500

@response_bp.route('/stats', methods=['GET'])
def get_response_stats():
    """Get response statistics"""
    try:
        # Get date range
        days_back = request.args.get('days_back', 30, type=int)
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Basic counts
        total_responses = EmailResponse.query.filter(
            EmailResponse.created_at >= cutoff_date
        ).count()
        
        draft_responses = EmailResponse.query.filter(
            and_(
                EmailResponse.status == 'draft',
                EmailResponse.created_at >= cutoff_date
            )
        ).count()
        
        approved_responses = EmailResponse.query.filter(
            and_(
                EmailResponse.status == 'approved',
                EmailResponse.created_at >= cutoff_date
            )
        ).count()
        
        sent_responses = EmailResponse.query.filter(
            and_(
                EmailResponse.status == 'sent',
                EmailResponse.created_at >= cutoff_date
            )
        ).count()
        
        rejected_responses = EmailResponse.query.filter(
            and_(
                EmailResponse.status == 'rejected',
                EmailResponse.created_at >= cutoff_date
            )
        ).count()
        
        # Average confidence
        avg_confidence = db.session.query(
            db.func.avg(EmailResponse.generation_confidence)
        ).filter(
            EmailResponse.created_at >= cutoff_date
        ).scalar() or 0.0
        
        # Response rate (sent / total emails with responses)
        emails_with_responses = db.session.query(Email.id).join(EmailResponse).filter(
            EmailResponse.created_at >= cutoff_date
        ).distinct().count()
        
        response_rate = (sent_responses / emails_with_responses * 100) if emails_with_responses > 0 else 0
        
        return jsonify({
            'total_responses': total_responses,
            'by_status': {
                'draft': draft_responses,
                'approved': approved_responses,
                'sent': sent_responses,
                'rejected': rejected_responses
            },
            'average_confidence': round(avg_confidence, 2),
            'response_rate': round(response_rate, 1),
            'period_days': days_back
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting response stats: {str(e)}")
        return jsonify({'error': 'Failed to get response statistics'}), 500
