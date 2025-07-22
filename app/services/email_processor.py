import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError

from app.models import db, Email, EmailResponse, EmailTemplate, ProcessingLog
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.services.learning_service import LearningService

logger = logging.getLogger(__name__)

class EmailProcessor:
    """Main service for processing emails end-to-end"""
    
    def __init__(self, gmail_service: GmailService, ai_service: AIService, learning_service: LearningService = None):
        self.gmail_service = gmail_service
        self.ai_service = ai_service
        self.learning_service = learning_service or LearningService(gmail_service)
        self.processing_stats = {
            'processed': 0,
            'classified': 0,
            'responses_generated': 0,
            'errors': 0
        }
    
    def process_account_emails(self, account_name: str, max_emails: int = 50) -> Dict:
        """Process all unread emails for an account"""
        logger.info(f"Starting email processing for account: {account_name}")
        
        try:
            # Get unread emails
            unread_emails = self.gmail_service.get_unread_emails(account_name, max_emails)
            
            if not unread_emails:
                logger.info(f"No unread emails found for {account_name}")
                return {'processed': 0, 'errors': 0}
            
            results = {
                'processed': 0,
                'classified': 0,
                'responses_generated': 0,
                'auto_responded': 0,
                'errors': 0,
                'emails': []
            }
            
            for email_data in unread_emails:
                try:
                    result = self.process_single_email(email_data)
                    results['emails'].append(result)
                    
                    if result['status'] == 'success':
                        results['processed'] += 1
                        if result.get('classified'):
                            results['classified'] += 1
                        if result.get('response_generated'):
                            results['responses_generated'] += 1
                        if result.get('auto_responded'):
                            results['auto_responded'] += 1
                    else:
                        results['errors'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing email {email_data.get('gmail_id', 'unknown')}: {str(e)}")
                    results['errors'] += 1
            
            logger.info(f"Completed processing for {account_name}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing account {account_name}: {str(e)}")
            return {'processed': 0, 'errors': 1}
    
    def process_single_email(self, email_data: Dict) -> Dict:
        """Process a single email through the complete pipeline"""
        gmail_id = email_data.get('gmail_id')
        account = email_data.get('account')
        
        try:
            # Check if email already exists
            existing_email = Email.query.filter_by(gmail_id=gmail_id).first()
            if existing_email:
                logger.info(f"Email {gmail_id} already processed")
                return {
                    'gmail_id': gmail_id,
                    'status': 'already_processed',
                    'email_id': existing_email.id
                }
            
            # Save email to database
            email_record = self._save_email_to_db(email_data)
            if not email_record:
                return {'gmail_id': gmail_id, 'status': 'error', 'message': 'Failed to save email'}
            
            # Log processing start
            self._log_processing_action(email_record.id, 'process_start', 'success', 'Email processing started')
            
            # Classify email
            classification = self._classify_email(email_record, email_data)
            
            # Generate response if appropriate
            response_result = self._generate_response_if_needed(email_record, email_data, classification)
            
            # Update email status
            email_record.status = 'processed'
            email_record.processed_at = datetime.utcnow()
            db.session.commit()
            
            # REMOVIDO: Não marcar automaticamente como lido
            # O usuário deve ter controle total sobre quais emails são marcados como lidos
            
            # Add processing label (mantido para organização)
            self.gmail_service.add_label(account, gmail_id, 'AI-Processed')
            
            result = {
                'gmail_id': gmail_id,
                'email_id': email_record.id,
                'status': 'success',
                'classified': classification is not None,
                'response_generated': response_result.get('generated', False),
                'auto_responded': response_result.get('auto_sent', False),
                'classification': classification,
                'response_id': response_result.get('response_id')
            }
            
            self._log_processing_action(email_record.id, 'process_complete', 'success', 'Email processing completed', result)
            return result
            
        except Exception as e:
            logger.error(f"Error in process_single_email for {gmail_id}: {str(e)}")
            if 'email_record' in locals():
                self._log_processing_action(email_record.id, 'process_error', 'error', str(e))
            return {'gmail_id': gmail_id, 'status': 'error', 'message': str(e)}
    
    def _save_email_to_db(self, email_data: Dict) -> Optional[Email]:
        """Save email data to database"""
        try:
            email = Email(
                gmail_id=email_data['gmail_id'],
                thread_id=email_data['thread_id'],
                account=email_data['account'],
                sender_email=email_data['sender_email'],
                sender_name=email_data.get('sender_name', ''),
                subject=email_data.get('subject', ''),
                body_text=email_data.get('body_text', ''),
                body_html=email_data.get('body_html', ''),
                received_at=email_data['received_at']
            )
            
            db.session.add(email)
            db.session.commit()
            
            logger.info(f"Email {email_data['gmail_id']} saved to database with ID {email.id}")
            return email
            
        except IntegrityError as e:
            db.session.rollback()
            logger.warning(f"Email {email_data['gmail_id']} already exists in database")
            return Email.query.filter_by(gmail_id=email_data['gmail_id']).first()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving email to database: {str(e)}")
            return None
    
    def _classify_email(self, email_record: Email, email_data: Dict) -> Optional[Dict]:
        """Classify email using AI service"""
        try:
            start_time = datetime.utcnow()
            
            # Get AI classification
            classification = self.ai_service.classify_email(email_data)
            
            # Update email record with classification
            email_record.classification_type = classification.get('type')
            email_record.classification_priority = classification.get('priority')
            email_record.classification_product = classification.get('product')
            email_record.classification_sentiment = classification.get('sentiment')
            email_record.classification_confidence = classification.get('confidence', 0.0)
            
            db.session.commit()
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._log_processing_action(
                email_record.id, 
                'classify', 
                'success', 
                f"Email classified as {classification.get('type')}", 
                classification,
                processing_time
            )
            
            logger.info(f"Email {email_record.gmail_id} classified: {classification}")
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying email {email_record.gmail_id}: {str(e)}")
            self._log_processing_action(email_record.id, 'classify', 'error', str(e))
            return None
    
    def _generate_response_if_needed(self, email_record: Email, email_data: Dict, classification: Dict) -> Dict:
        """Generate response if email meets criteria"""
        result = {'generated': False, 'auto_sent': False, 'response_id': None}
        
        try:
            # Check if response should be generated
            if not self._should_generate_response(classification):
                logger.info(f"Email {email_record.gmail_id} does not need automatic response")
                return result
            
            # Get appropriate template
            template = self._get_template_for_classification(classification)
            
            # Generate response using AI with learning
            start_time = datetime.utcnow()
            generated_response = self.ai_service.generate_response_with_learning(
                email_data, classification, self.learning_service, template
            )
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Save response to database
            response_record = EmailResponse(
                email_id=email_record.id,
                subject=generated_response.get('subject', ''),
                body_text=generated_response.get('body_text', ''),
                body_html=generated_response.get('body_html', ''),
                ai_model=self.ai_service.model,
                template_used=generated_response.get('template_used', ''),
                generation_confidence=generated_response.get('confidence', 0.0),
                status='draft'
            )
            
            db.session.add(response_record)
            db.session.commit()
            
            result['generated'] = True
            result['response_id'] = response_record.id
            
            self._log_processing_action(
                email_record.id,
                'generate_response',
                'success',
                'Response generated successfully',
                {'response_id': response_record.id, 'confidence': generated_response.get('confidence')},
                processing_time,
                api_calls_made=1
            )
            
            # Check if should auto-send
            if self._should_auto_send_response(classification, generated_response):
                auto_send_result = self._auto_send_response(email_record, response_record, email_data)
                result['auto_sent'] = auto_send_result
            
            logger.info(f"Response generated for email {email_record.gmail_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response for email {email_record.gmail_id}: {str(e)}")
            self._log_processing_action(email_record.id, 'generate_response', 'error', str(e))
            return result
    
    def _should_generate_response(self, classification: Dict) -> bool:
        """Determine if email should get an automatic response"""
        if not classification:
            return False
        
        # Don't respond to spam
        if classification.get('type') == 'spam':
            return False
        
        # Always respond to high priority sales emails
        if classification.get('type') == 'vendas' and classification.get('priority') == 'alta':
            return True
        
        # Respond to medium priority sales with high confidence
        if (classification.get('type') == 'vendas' and 
            classification.get('priority') == 'media' and 
            classification.get('confidence', 0) > 0.8):
            return True
        
        # Respond to support requests
        if classification.get('type') == 'suporte':
            return True
        
        # Respond to information requests with specific product interest
        if (classification.get('type') == 'informacao' and 
            classification.get('product') in ['coaching', 'acelerador']):
            return True
        
        return False
    
    def _should_auto_send_response(self, classification: Dict, generated_response: Dict) -> bool:
        """Determine if response should be sent automatically"""
        # Only auto-send if both classification and generation confidence are high
        classification_confidence = classification.get('confidence', 0.0)
        generation_confidence = generated_response.get('confidence', 0.0)
        
        # High confidence threshold for auto-sending
        if classification_confidence > 0.9 and generation_confidence > 0.9:
            # Auto-send for information requests and low-risk scenarios
            if classification.get('type') in ['informacao', 'suporte']:
                return True
        
        return False
    
    def _get_template_for_classification(self, classification: Dict) -> Optional[Dict]:
        """Get appropriate template based on classification"""
        try:
            query = EmailTemplate.query.filter_by(is_active=True)
            
            # Filter by category
            if classification.get('type'):
                query = query.filter_by(category=classification.get('type'))
            
            # Filter by product if specified
            if classification.get('product') and classification.get('product') != 'none':
                query = query.filter_by(product=classification.get('product'))
            
            template = query.first()
            
            if template:
                return {
                    'name': template.name,
                    'subject_template': template.subject_template,
                    'body_template': template.body_template,
                    'variables': template.variables
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return None
    
    def _auto_send_response(self, email_record: Email, response_record: EmailResponse, email_data: Dict) -> bool:
        """Automatically send response"""
        try:
            success = self.gmail_service.send_email(
                account_name=email_record.account,
                to_email=email_record.sender_email,
                subject=response_record.subject,
                body_text=response_record.body_text,
                body_html=response_record.body_html,
                reply_to_id=email_record.gmail_id
            )
            
            if success:
                response_record.status = 'sent'
                response_record.sent_at = datetime.utcnow()
                email_record.status = 'responded'
                db.session.commit()
                
                self._log_processing_action(
                    email_record.id,
                    'auto_send',
                    'success',
                    'Response sent automatically'
                )
                
                logger.info(f"Auto-sent response for email {email_record.gmail_id}")
                return True
            else:
                self._log_processing_action(
                    email_record.id,
                    'auto_send',
                    'error',
                    'Failed to send response automatically'
                )
                return False
                
        except Exception as e:
            logger.error(f"Error auto-sending response: {str(e)}")
            self._log_processing_action(email_record.id, 'auto_send', 'error', str(e))
            return False
    
    def _log_processing_action(self, email_id: int, action: str, status: str, message: str, 
                             details: Dict = None, processing_time: float = None, api_calls_made: int = 0):
        """Log processing action"""
        try:
            log = ProcessingLog(
                email_id=email_id,
                action=action,
                status=status,
                message=message,
                details=details,
                processing_time=processing_time,
                api_calls_made=api_calls_made
            )
            
            db.session.add(log)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error logging processing action: {str(e)}")
    
    def get_processing_stats(self) -> Dict:
        """Get processing statistics"""
        return self.processing_stats.copy()
    
    def approve_response(self, response_id: int, approved_by: str) -> bool:
        """Approve a generated response for sending"""
        try:
            response = EmailResponse.query.get(response_id)
            if not response:
                return False
            
            response.status = 'approved'
            response.approved_by = approved_by
            response.approved_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Response {response_id} approved by {approved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving response {response_id}: {str(e)}")
            return False
    
    def send_approved_response(self, response_id: int) -> bool:
        """Send an approved response"""
        try:
            response = EmailResponse.query.get(response_id)
            if not response or response.status != 'approved':
                return False
            
            email = response.email
            
            success = self.gmail_service.send_email(
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
                
                self._log_processing_action(
                    email.id,
                    'manual_send',
                    'success',
                    f'Response sent manually by {response.approved_by}'
                )
                
                logger.info(f"Manually sent response {response_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending approved response {response_id}: {str(e)}")
            return False
    
    def analyze_account_learning(self, account_name: str, days_back: int = 90) -> Dict:
        """
        Analisa padrões de aprendizado para uma conta específica
        Funcionalidade principal para responder sua pergunta sobre histórico!
        """
        try:
            logger.info(f"Analyzing learning patterns for account: {account_name}")
            
            # Obter insights de aprendizado
            learning_insights = self.learning_service.generate_learning_insights(account_name)
            
            # Analisar padrões de resposta
            response_patterns = self.learning_service.analyze_response_patterns(account_name, days_back)
            
            # Estatísticas do banco de dados
            db_stats = self._get_account_db_stats(account_name)
            
            analysis = {
                'account': account_name,
                'analysis_period_days': days_back,
                'learning_insights': learning_insights,
                'response_patterns': response_patterns,
                'database_stats': db_stats,
                'recommendations': self._generate_learning_recommendations(response_patterns, db_stats),
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Learning analysis completed for {account_name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing account learning for {account_name}: {e}")
            return {'error': str(e)}
    
    def update_learning_from_feedback(self, response_id: int, feedback_type: str, 
                                    feedback_data: Dict = None) -> bool:
        """
        Atualiza o aprendizado baseado no feedback de uma resposta
        """
        try:
            response = EmailResponse.query.get(response_id)
            if not response:
                return False
            
            # Analisar efetividade da resposta
            effectiveness = self.ai_service.analyze_response_effectiveness(
                {
                    'subject': response.subject,
                    'body_text': response.body_text,
                    'call_to_action': response.template_used
                },
                follow_up_received=(feedback_type == 'follow_up_received'),
                response_time_hours=feedback_data.get('response_time_hours') if feedback_data else None
            )
            
            # Log do feedback para aprendizado futuro
            self._log_processing_action(
                response.email_id,
                'learning_feedback',
                'success',
                f'Feedback received: {feedback_type}',
                {
                    'feedback_type': feedback_type,
                    'feedback_data': feedback_data,
                    'effectiveness_analysis': effectiveness
                }
            )
            
            logger.info(f"Learning feedback updated for response {response_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating learning feedback: {e}")
            return False
    
    def get_similar_historical_responses(self, email_content: str, account_name: str, 
                                       limit: int = 5) -> List[Dict]:
        """
        Busca respostas históricas similares para referência
        """
        try:
            similar_responses = self.learning_service.find_similar_responses(
                email_content, account_name, similarity_threshold=0.2
            )
            
            # Enriquecer com dados do banco
            enriched_responses = []
            for response in similar_responses[:limit]:
                gmail_id = response.get('gmail_id')
                if gmail_id:
                    email_record = Email.query.filter_by(gmail_id=gmail_id).first()
                    if email_record:
                        # Buscar resposta associada
                        email_response = EmailResponse.query.filter_by(email_id=email_record.id).first()
                        if email_response:
                            enriched_responses.append({
                                'original_email': {
                                    'subject': email_record.subject,
                                    'body_text': email_record.body_text[:300],
                                    'sender': email_record.sender_name,
                                    'received_at': email_record.received_at.isoformat()
                                },
                                'response_sent': {
                                    'subject': email_response.subject,
                                    'body_text': email_response.body_text[:500],
                                    'template_used': email_response.template_used,
                                    'confidence': email_response.generation_confidence,
                                    'sent_at': email_response.sent_at.isoformat() if email_response.sent_at else None
                                },
                                'similarity_score': response.get('similarity_score', 0)
                            })
            
            return enriched_responses
            
        except Exception as e:
            logger.error(f"Error getting similar historical responses: {e}")
            return []
    
    def _get_account_db_stats(self, account_name: str) -> Dict:
        """Obter estatísticas do banco de dados para a conta"""
        try:
            total_emails = Email.query.filter_by(account=account_name).count()
            processed_emails = Email.query.filter_by(account=account_name, status='processed').count()
            responded_emails = Email.query.filter_by(account=account_name, status='responded').count()
            
            # Estatísticas de respostas
            responses_query = db.session.query(EmailResponse).join(Email).filter(Email.account == account_name)
            total_responses = responses_query.count()
            sent_responses = responses_query.filter(EmailResponse.status == 'sent').count()
            draft_responses = responses_query.filter(EmailResponse.status == 'draft').count()
            
            # Estatísticas de classificação
            classification_stats = db.session.query(
                Email.classification_type,
                db.func.count(Email.id).label('count')
            ).filter_by(account=account_name).group_by(Email.classification_type).all()
            
            return {
                'total_emails': total_emails,
                'processed_emails': processed_emails,
                'responded_emails': responded_emails,
                'response_rate': (responded_emails / total_emails * 100) if total_emails > 0 else 0,
                'total_responses_generated': total_responses,
                'sent_responses': sent_responses,
                'draft_responses': draft_responses,
                'auto_send_rate': (sent_responses / total_responses * 100) if total_responses > 0 else 0,
                'classification_breakdown': {stat.classification_type: stat.count for stat in classification_stats}
            }
            
        except Exception as e:
            logger.error(f"Error getting account DB stats: {e}")
            return {}
    
    def _generate_learning_recommendations(self, response_patterns: Dict, db_stats: Dict) -> List[str]:
        """Gerar recomendações baseadas nos padrões aprendidos"""
        recommendations = []
        
        try:
            # Recomendações baseadas na taxa de resposta
            response_rate = db_stats.get('response_rate', 0)
            if response_rate < 50:
                recommendations.append("Taxa de resposta baixa - considere ajustar critérios de resposta automática")
            
            # Recomendações baseadas nos padrões de resposta
            avg_length = response_patterns.get('response_length_stats', {}).get('avg_length', 0)
            if avg_length > 800:
                recommendations.append("Respostas muito longas - considere templates mais concisos")
            elif avg_length < 200:
                recommendations.append("Respostas muito curtas - adicione mais informações úteis")
            
            # Recomendações baseadas na diversidade de saudações
            greeting_count = len(response_patterns.get('greeting_patterns', []))
            if greeting_count < 3:
                recommendations.append("Pouca variedade nas saudações - diversifique para evitar repetição")
            
            # Recomendações baseadas na taxa de envio automático
            auto_send_rate = db_stats.get('auto_send_rate', 0)
            if auto_send_rate < 30:
                recommendations.append("Taxa de envio automático baixa - ajuste critérios de confiança")
            elif auto_send_rate > 80:
                recommendations.append("Taxa de envio automático alta - verifique qualidade das respostas")
            
            # Recomendações baseadas na classificação
            classification_breakdown = db_stats.get('classification_breakdown', {})
            spam_rate = classification_breakdown.get('spam', 0) / sum(classification_breakdown.values()) * 100 if classification_breakdown else 0
            if spam_rate > 20:
                recommendations.append("Alta taxa de spam - ajuste filtros de classificação")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Erro ao gerar recomendações - verifique logs")
        
        return recommendations
