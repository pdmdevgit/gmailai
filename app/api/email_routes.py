from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, or_
from app.models import db, Email, EmailResponse, EmailTemplate
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.services.email_processor import EmailProcessor

email_bp = Blueprint('email_api', __name__)

@email_bp.route('/', methods=['GET'])
def get_emails():
    """Get emails with filtering and pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        account = request.args.get('account')
        status = request.args.get('status')
        classification_type = request.args.get('type')
        priority = request.args.get('priority')
        days_back = request.args.get('days_back', 30, type=int)
        search = request.args.get('search')
        
        # Build query
        query = Email.query
        
        # Apply filters
        if account:
            query = query.filter(Email.account == account)
        
        if status:
            query = query.filter(Email.status == status)
        
        if classification_type:
            query = query.filter(Email.classification_type == classification_type)
        
        if priority:
            query = query.filter(Email.classification_priority == priority)
        
        # Date filter
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(Email.created_at >= cutoff_date)
        
        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Email.sender_email.ilike(search_term),
                    Email.sender_name.ilike(search_term),
                    Email.subject.ilike(search_term),
                    Email.body_text.ilike(search_term)
                )
            )
        
        # Order by most recent
        query = query.order_by(desc(Email.created_at))
        
        # Paginate
        emails = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format response
        email_list = []
        for email in emails.items:
            email_data = {
                'id': email.id,
                'gmail_id': email.gmail_id,
                'account': email.account,
                'sender_email': email.sender_email,
                'sender_name': email.sender_name,
                'subject': email.subject,
                'body_preview': email.body_text[:200] + '...' if len(email.body_text) > 200 else email.body_text,
                'received_at': email.received_at.isoformat(),
                'processed_at': email.processed_at.isoformat() if email.processed_at else None,
                'status': email.status,
                'classification': {
                    'type': email.classification_type,
                    'priority': email.classification_priority,
                    'product': email.classification_product,
                    'sentiment': email.classification_sentiment,
                    'confidence': email.classification_confidence
                },
                'needs_human_review': email.needs_human_review,
                'response_count': len(email.responses)
            }
            email_list.append(email_data)
        
        return jsonify({
            'emails': email_list,
            'pagination': {
                'page': emails.page,
                'pages': emails.pages,
                'per_page': emails.per_page,
                'total': emails.total,
                'has_next': emails.has_next,
                'has_prev': emails.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting emails: {str(e)}")
        return jsonify({'error': 'Failed to get emails'}), 500

@email_bp.route('/<int:email_id>', methods=['GET'])
def get_email_detail(email_id):
    """Get detailed email information"""
    try:
        email = Email.query.get_or_404(email_id)
        
        # Get responses
        responses = []
        for response in email.responses:
            responses.append({
                'id': response.id,
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
                'created_at': response.created_at.isoformat()
            })
        
        email_data = {
            'id': email.id,
            'gmail_id': email.gmail_id,
            'thread_id': email.thread_id,
            'account': email.account,
            'sender_email': email.sender_email,
            'sender_name': email.sender_name,
            'subject': email.subject,
            'body_text': email.body_text,
            'body_html': email.body_html,
            'received_at': email.received_at.isoformat(),
            'processed_at': email.processed_at.isoformat() if email.processed_at else None,
            'created_at': email.created_at.isoformat(),
            'status': email.status,
            'classification': {
                'type': email.classification_type,
                'priority': email.classification_priority,
                'product': email.classification_product,
                'sentiment': email.classification_sentiment,
                'confidence': email.classification_confidence
            },
            'needs_human_review': email.needs_human_review,
            'responses': responses
        }
        
        return jsonify(email_data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting email detail: {str(e)}")
        return jsonify({'error': 'Failed to get email details'}), 500

@email_bp.route('/<int:email_id>/responses', methods=['POST'])
def generate_response(email_id):
    """Generate a new response for an email (MANUAL SELECTION ONLY)"""
    try:
        email = Email.query.get_or_404(email_id)
        data = request.get_json() or {}
        
        # Check if email is suitable for response generation
        if not _is_suitable_for_response(email):
            return jsonify({
                'error': 'Este email não é adequado para geração de resposta automática',
                'reason': 'Email classificado como spam, comercial ou não relevante para leads/alunos'
            }), 400
        
        # Check if response already exists
        existing_response = EmailResponse.query.filter_by(email_id=email.id).first()
        if existing_response:
            return jsonify({
                'error': 'Resposta já existe para este email',
                'existing_response_id': existing_response.id
            }), 400
        
        # Initialize AI service
        ai_service = AIService(
            openai_api_key=current_app.config.get('OPENAI_API_KEY'),
            anthropic_api_key=current_app.config.get('ANTHROPIC_API_KEY'),
            model=current_app.config.get('AI_MODEL', 'gpt-4')
        )
        
        # Prepare email data for AI
        email_data = {
            'gmail_id': email.gmail_id,
            'sender_email': email.sender_email,
            'sender_name': email.sender_name,
            'subject': email.subject,
            'body_text': email.body_text,
            'account': email.account
        }
        
        # Get classification
        classification = {
            'type': email.classification_type,
            'priority': email.classification_priority,
            'product': email.classification_product,
            'sentiment': email.classification_sentiment,
            'confidence': email.classification_confidence
        }
        
        # Get template if specified
        template = None
        if data.get('template_id'):
            template_record = EmailTemplate.query.get(data['template_id'])
            if template_record:
                template = {
                    'name': template_record.name,
                    'subject_template': template_record.subject_template,
                    'body_template': template_record.body_template,
                    'variables': template_record.variables
                }
        
        # Add custom instructions if provided
        custom_instructions = data.get('custom_instructions', '')
        
        # Generate response
        generated_response = ai_service.generate_response(
            email_data, 
            classification, 
            template,
            custom_instructions=custom_instructions
        )
        
        # Save response
        response_record = EmailResponse(
            email_id=email.id,
            subject=generated_response.get('subject', ''),
            body_text=generated_response.get('body_text', ''),
            body_html=generated_response.get('body_html', ''),
            ai_model=ai_service.model,
            template_used=generated_response.get('template_used', ''),
            generation_confidence=generated_response.get('confidence', 0.0),
            status='draft'
        )
        
        db.session.add(response_record)
        
        # Mark email as having response generated
        email.status = 'response_generated'
        
        db.session.commit()
        
        return jsonify({
            'id': response_record.id,
            'subject': response_record.subject,
            'body_text': response_record.body_text,
            'body_html': response_record.body_html,
            'confidence': response_record.generation_confidence,
            'status': response_record.status,
            'created_at': response_record.created_at.isoformat(),
            'message': 'Resposta gerada com sucesso! Revise e aprove antes de enviar.'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating response: {str(e)}")
        return jsonify({'error': 'Failed to generate response'}), 500

def _is_suitable_for_response(email):
    """Check if email is suitable for response generation (leads/students focus)"""
    
    # Skip spam and commercial emails
    if email.classification_type in ['spam', 'comercial', 'newsletter']:
        return False
    
    # Skip automated emails
    automated_senders = [
        'noreply', 'no-reply', 'donotreply', 'do-not-reply',
        'automated', 'system', 'notification', 'alert'
    ]
    
    sender_email_lower = email.sender_email.lower()
    for automated in automated_senders:
        if automated in sender_email_lower:
            return False
    
    # Skip known commercial domains
    commercial_domains = [
        'facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com',
        'mailchimp.com', 'constantcontact.com', 'aweber.com',
        'shopify.com', 'woocommerce.com', 'wordpress.com'
    ]
    
    sender_domain = sender_email_lower.split('@')[-1] if '@' in sender_email_lower else ''
    if sender_domain in commercial_domains:
        return False
    
    # Prioritize leads and students
    lead_indicators = [
        'duvida', 'dúvida', 'pergunta', 'curso', 'aula', 'material',
        'concurso', 'estudo', 'prova', 'questao', 'questão',
        'coaching', 'mentoria', 'ajuda', 'orientacao', 'orientação'
    ]
    
    content_to_check = f"{email.subject} {email.body_text}".lower()
    
    # If it's classified as sales or support with good confidence, likely a lead
    if email.classification_type in ['vendas', 'suporte'] and email.classification_confidence > 0.7:
        return True
    
    # Check for lead indicators in content
    for indicator in lead_indicators:
        if indicator in content_to_check:
            return True
    
    # If high priority, likely important
    if email.classification_priority == 'alta':
        return True
    
    # Default to requiring manual review for edge cases
    return False

@email_bp.route('/<int:email_id>/mark-for-response', methods=['POST'])
def mark_email_for_response(email_id):
    """Mark an email as suitable for response generation"""
    try:
        email = Email.query.get_or_404(email_id)
        data = request.get_json() or {}
        
        # Update email status
        email.needs_human_review = False
        email.status = 'ready_for_response'
        
        # Add note if provided
        if data.get('note'):
            # You could add a notes field to the Email model if needed
            pass
        
        db.session.commit()
        
        return jsonify({
            'id': email.id,
            'status': email.status,
            'message': 'Email marcado para geração de resposta'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking email for response: {str(e)}")
        return jsonify({'error': 'Failed to mark email for response'}), 500

@email_bp.route('/<int:email_id>/skip-response', methods=['POST'])
def skip_email_response(email_id):
    """Mark an email as not needing a response"""
    try:
        email = Email.query.get_or_404(email_id)
        data = request.get_json() or {}
        
        # Update email status
        email.status = 'no_response_needed'
        email.needs_human_review = False
        
        # Add reason if provided
        skip_reason = data.get('reason', 'Manual decision')
        
        db.session.commit()
        
        return jsonify({
            'id': email.id,
            'status': email.status,
            'skip_reason': skip_reason,
            'message': 'Email marcado como não necessitando resposta'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error skipping email response: {str(e)}")
        return jsonify({'error': 'Failed to skip email response'}), 500

@email_bp.route('/bulk-actions', methods=['POST'])
def bulk_email_actions():
    """Perform bulk actions on multiple emails"""
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        action = data.get('action')
        
        if not email_ids or not action:
            return jsonify({'error': 'email_ids and action are required'}), 400
        
        emails = Email.query.filter(Email.id.in_(email_ids)).all()
        
        if not emails:
            return jsonify({'error': 'No emails found'}), 404
        
        results = []
        
        for email in emails:
            try:
                if action == 'mark_for_response':
                    email.status = 'ready_for_response'
                    email.needs_human_review = False
                    results.append({'id': email.id, 'status': 'marked_for_response'})
                    
                elif action == 'skip_response':
                    email.status = 'no_response_needed'
                    email.needs_human_review = False
                    results.append({'id': email.id, 'status': 'skipped'})
                    
                elif action == 'generate_responses':
                    if _is_suitable_for_response(email):
                        # This would trigger response generation
                        email.status = 'ready_for_response'
                        results.append({'id': email.id, 'status': 'ready_for_generation'})
                    else:
                        results.append({'id': email.id, 'status': 'not_suitable'})
                        
            except Exception as e:
                results.append({'id': email.id, 'status': 'error', 'error': str(e)})
        
        db.session.commit()
        
        return jsonify({
            'action': action,
            'processed': len(results),
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk actions: {str(e)}")
        return jsonify({'error': 'Failed to perform bulk actions'}), 500

@email_bp.route('/responses/<int:response_id>/approve', methods=['POST'])
def approve_response(response_id):
    """Approve a response for sending"""
    try:
        response = EmailResponse.query.get_or_404(response_id)
        data = request.get_json()
        
        approved_by = data.get('approved_by', 'system')
        
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

@email_bp.route('/responses/<int:response_id>/send', methods=['POST'])
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

@email_bp.route('/responses/<int:response_id>', methods=['PUT'])
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
        
        response.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': response.id,
            'subject': response.subject,
            'body_text': response.body_text,
            'body_html': response.body_html,
            'updated_at': response.updated_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating response: {str(e)}")
        return jsonify({'error': 'Failed to update response'}), 500

@email_bp.route('/<int:email_id>/classify', methods=['POST'])
def reclassify_email(email_id):
    """Reclassify an email"""
    try:
        email = Email.query.get_or_404(email_id)
        
        # Initialize AI service
        ai_service = AIService(
            openai_api_key=current_app.config.get('OPENAI_API_KEY'),
            anthropic_api_key=current_app.config.get('ANTHROPIC_API_KEY'),
            model=current_app.config.get('AI_MODEL', 'gpt-4')
        )
        
        # Prepare email data
        email_data = {
            'gmail_id': email.gmail_id,
            'sender_email': email.sender_email,
            'sender_name': email.sender_name,
            'subject': email.subject,
            'body_text': email.body_text,
            'account': email.account
        }
        
        # Classify email
        classification = ai_service.classify_email(email_data)
        
        # Update email record
        email.classification_type = classification.get('type')
        email.classification_priority = classification.get('priority')
        email.classification_product = classification.get('product')
        email.classification_sentiment = classification.get('sentiment')
        email.classification_confidence = classification.get('confidence', 0.0)
        
        db.session.commit()
        
        return jsonify({
            'id': email.id,
            'classification': {
                'type': email.classification_type,
                'priority': email.classification_priority,
                'product': email.classification_product,
                'sentiment': email.classification_sentiment,
                'confidence': email.classification_confidence
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error reclassifying email: {str(e)}")
        return jsonify({'error': 'Failed to reclassify email'}), 500

@email_bp.route('/<int:email_id>/mark-as-read', methods=['POST'])
def mark_email_as_read(email_id):
    """Marcar email como lido no Gmail (CONTROLE MANUAL)"""
    try:
        email = Email.query.get_or_404(email_id)
        
        # Initialize Gmail service
        gmail_service = GmailService(
            credentials_file=current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            token_dir=current_app.config.get('GMAIL_TOKEN_DIR')
        )
        
        # Mark as read in Gmail
        success = gmail_service.mark_as_read(email.account, email.gmail_id)
        
        if success:
            # Update local status
            email.is_read = True
            db.session.commit()
            
            return jsonify({
                'id': email.id,
                'gmail_id': email.gmail_id,
                'is_read': True,
                'message': 'Email marcado como lido com sucesso'
            })
        else:
            return jsonify({'error': 'Falha ao marcar email como lido no Gmail'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error marking email as read: {str(e)}")
        return jsonify({'error': 'Failed to mark email as read'}), 500

@email_bp.route('/<int:email_id>/create-draft', methods=['POST'])
def create_draft_response(email_id):
    """Criar rascunho de resposta no Gmail (NUNCA ENVIAR AUTOMATICAMENTE)"""
    try:
        email = Email.query.get_or_404(email_id)
        data = request.get_json() or {}
        
        # Verificar se já existe uma resposta aprovada
        response = EmailResponse.query.filter_by(
            email_id=email.id, 
            status='approved'
        ).first()
        
        if not response:
            return jsonify({'error': 'Nenhuma resposta aprovada encontrada para este email'}), 400
        
        # Initialize Gmail service
        gmail_service = GmailService(
            credentials_file=current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            token_dir=current_app.config.get('GMAIL_TOKEN_DIR')
        )
        
        # Criar rascunho no Gmail (NÃO ENVIAR)
        draft_created = gmail_service.create_draft(
            account_name=email.account,
            to_email=email.sender_email,
            subject=response.subject,
            body_text=response.body_text,
            body_html=response.body_html,
            reply_to_id=email.gmail_id
        )
        
        if draft_created:
            # Atualizar status da resposta
            response.status = 'draft_created'
            response.draft_created_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'id': response.id,
                'email_id': email.id,
                'status': 'draft_created',
                'message': 'Rascunho criado no Gmail. Acesse sua conta para revisar e enviar manualmente.'
            })
        else:
            return jsonify({'error': 'Falha ao criar rascunho no Gmail'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error creating draft: {str(e)}")
        return jsonify({'error': 'Failed to create draft'}), 500

@email_bp.route('/bulk-mark-read', methods=['POST'])
def bulk_mark_as_read():
    """Marcar múltiplos emails como lidos (CONTROLE MANUAL)"""
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        
        if not email_ids:
            return jsonify({'error': 'email_ids é obrigatório'}), 400
        
        emails = Email.query.filter(Email.id.in_(email_ids)).all()
        
        if not emails:
            return jsonify({'error': 'Nenhum email encontrado'}), 404
        
        # Initialize Gmail service
        gmail_service = GmailService(
            credentials_file=current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            token_dir=current_app.config.get('GMAIL_TOKEN_DIR')
        )
        
        results = []
        
        for email in emails:
            try:
                success = gmail_service.mark_as_read(email.account, email.gmail_id)
                if success:
                    email.is_read = True
                    results.append({'id': email.id, 'status': 'marked_as_read'})
                else:
                    results.append({'id': email.id, 'status': 'failed'})
            except Exception as e:
                results.append({'id': email.id, 'status': 'error', 'error': str(e)})
        
        db.session.commit()
        
        return jsonify({
            'processed': len(results),
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk mark as read: {str(e)}")
        return jsonify({'error': 'Failed to mark emails as read'}), 500

@email_bp.route('/learning/update-from-sent', methods=['POST'])
def update_learning_from_sent_emails():
    """Atualizar aprendizado baseado em emails enviados manualmente"""
    try:
        data = request.get_json() or {}
        account = data.get('account')
        days_back = data.get('days_back', 30)
        
        if not account:
            return jsonify({'error': 'account é obrigatório'}), 400
        
        # Initialize services
        gmail_service = GmailService(
            credentials_file=current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            token_dir=current_app.config.get('GMAIL_TOKEN_DIR')
        )
        
        ai_service = AIService(
            openai_api_key=current_app.config.get('OPENAI_API_KEY'),
            anthropic_api_key=current_app.config.get('ANTHROPIC_API_KEY'),
            model=current_app.config.get('AI_MODEL', 'gpt-4')
        )
        
        # Buscar emails enviados recentemente
        sent_emails = gmail_service.get_sent_emails_history(account, max_results=100, days_back=days_back)
        
        learning_updates = []
        
        for sent_email in sent_emails:
            try:
                # Buscar thread completa para contexto
                thread_emails = gmail_service.get_conversation_thread(account, sent_email['thread_id'])
                
                if len(thread_emails) >= 2:  # Pelo menos pergunta e resposta
                    # Identificar pergunta original e resposta
                    original_question = None
                    sent_response = None
                    
                    for thread_email in thread_emails:
                        if not thread_email.get('is_sent', False):
                            original_question = thread_email
                        elif thread_email.get('is_sent', False):
                            sent_response = thread_email
                    
                    if original_question and sent_response:
                        # Analisar efetividade da resposta
                        effectiveness = ai_service.analyze_response_effectiveness(
                            {
                                'original_question': original_question['body_text'],
                                'sent_response': sent_response['body_text'],
                                'subject': sent_response['subject']
                            }
                        )
                        
                        learning_updates.append({
                            'thread_id': sent_email['thread_id'],
                            'original_question_preview': original_question['body_text'][:200],
                            'sent_response_preview': sent_response['body_text'][:200],
                            'effectiveness_score': effectiveness.get('effectiveness_score', 0),
                            'learned_patterns': effectiveness.get('patterns', [])
                        })
                        
            except Exception as e:
                current_app.logger.error(f"Error processing sent email for learning: {str(e)}")
                continue
        
        return jsonify({
            'account': account,
            'days_analyzed': days_back,
            'sent_emails_found': len(sent_emails),
            'learning_updates': len(learning_updates),
            'updates': learning_updates[:10],  # Primeiros 10 para preview
            'message': f'Aprendizado atualizado com base em {len(learning_updates)} conversas analisadas'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating learning from sent emails: {str(e)}")
        return jsonify({'error': 'Failed to update learning from sent emails'}), 500

@email_bp.route('/process', methods=['POST'])
def process_emails():
    """Manually trigger email processing (SEM MARCAR COMO LIDO)"""
    try:
        data = request.get_json() or {}
        account = data.get('account')
        max_emails = data.get('max_emails', 50)
        
        # Initialize services
        gmail_service = GmailService(
            credentials_file=current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            token_dir=current_app.config.get('GMAIL_TOKEN_DIR')
        )
        
        ai_service = AIService(
            openai_api_key=current_app.config.get('OPENAI_API_KEY'),
            anthropic_api_key=current_app.config.get('ANTHROPIC_API_KEY'),
            model=current_app.config.get('AI_MODEL', 'gpt-4')
        )
        
        processor = EmailProcessor(gmail_service, ai_service)
        
        if account:
            # Process specific account
            results = processor.process_account_emails(account, max_emails)
        else:
            # Process all accounts
            accounts = current_app.config.get('GMAIL_ACCOUNTS', {})
            results = {}
            
            for account_name in accounts.keys():
                try:
                    account_results = processor.process_account_emails(account_name, max_emails)
                    results[account_name] = account_results
                except Exception as e:
                    current_app.logger.error(f"Error processing account {account_name}: {str(e)}")
                    results[account_name] = {'processed': 0, 'errors': 1}
        
        return jsonify({
            'status': 'completed',
            'results': results,
            'timestamp': datetime.utcnow().isoformat(),
            'note': 'Emails processados mas NÃO marcados como lidos automaticamente'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in manual email processing: {str(e)}")
        return jsonify({'error': 'Failed to process emails'}), 500
