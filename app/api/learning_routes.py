from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.services.learning_service import LearningService
from app.services.email_processor import EmailProcessor
# Import config with fallback
try:
    from config.config import Config
except (ImportError, ModuleNotFoundError):
    # Fallback config for Docker environment
    import os
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql')
        MYSQL_USER = os.environ.get('MYSQL_USER', 'gmail_ai_user')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'gmail_ai_pass')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'gmail_ai_agent')

logger = logging.getLogger(__name__)

learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')

# Initialize services
config = Config()
gmail_service = GmailService(
    credentials_file=config.GMAIL_CREDENTIALS_FILE,
    token_dir=config.GMAIL_TOKEN_DIR
)
ai_service = AIService(
    openai_api_key=config.OPENAI_API_KEY,
    anthropic_api_key=config.ANTHROPIC_API_KEY,
    model=config.AI_MODEL
)
learning_service = LearningService(gmail_service)
email_processor = EmailProcessor(gmail_service, ai_service, learning_service)

@learning_bp.route('/analyze/<account_name>', methods=['GET'])
def analyze_account_learning(account_name):
    """
    Analisa padrões de aprendizado para uma conta específica
    Esta é a funcionalidade principal que responde sua pergunta!
    """
    try:
        days_back = request.args.get('days_back', 90, type=int)
        
        # Validar conta
        valid_accounts = ['contato', 'cursos', 'diogo', 'sac']
        if account_name not in valid_accounts:
            return jsonify({
                'error': f'Conta inválida. Use: {", ".join(valid_accounts)}'
            }), 400
        
        # Realizar análise de aprendizado
        analysis = email_processor.analyze_account_learning(account_name, days_back)
        
        if 'error' in analysis:
            return jsonify({'error': analysis['error']}), 500
        
        return jsonify({
            'success': True,
            'data': analysis,
            'message': f'Análise de aprendizado concluída para {account_name}'
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_account_learning: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/patterns/<account_name>', methods=['GET'])
def get_response_patterns(account_name):
    """
    Obtém padrões de resposta aprendidos do histórico
    """
    try:
        days_back = request.args.get('days_back', 90, type=int)
        
        patterns = learning_service.analyze_response_patterns(account_name, days_back)
        
        return jsonify({
            'success': True,
            'data': patterns,
            'account': account_name,
            'period_days': days_back
        })
        
    except Exception as e:
        logger.error(f"Error getting response patterns: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/similar-responses', methods=['POST'])
def find_similar_responses():
    """
    Encontra respostas similares baseadas no conteúdo do email
    """
    try:
        data = request.get_json()
        
        if not data or 'email_content' not in data or 'account_name' not in data:
            return jsonify({
                'error': 'email_content e account_name são obrigatórios'
            }), 400
        
        email_content = data['email_content']
        account_name = data['account_name']
        limit = data.get('limit', 5)
        
        # Buscar respostas similares
        similar_responses = email_processor.get_similar_historical_responses(
            email_content, account_name, limit
        )
        
        return jsonify({
            'success': True,
            'data': similar_responses,
            'total_found': len(similar_responses),
            'query': {
                'account': account_name,
                'content_length': len(email_content),
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"Error finding similar responses: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/conversation-context/<thread_id>', methods=['GET'])
def get_conversation_context(thread_id):
    """
    Obtém contexto completo de uma conversa
    """
    try:
        account_name = request.args.get('account_name')
        if not account_name:
            return jsonify({'error': 'account_name é obrigatório'}), 400
        
        context = learning_service.get_conversation_context(thread_id, account_name)
        
        return jsonify({
            'success': True,
            'data': context,
            'thread_id': thread_id,
            'account': account_name
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation context: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/feedback', methods=['POST'])
def update_learning_feedback():
    """
    Atualiza aprendizado baseado no feedback de uma resposta
    """
    try:
        data = request.get_json()
        
        required_fields = ['response_id', 'feedback_type']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Campos obrigatórios: {", ".join(required_fields)}'
            }), 400
        
        response_id = data['response_id']
        feedback_type = data['feedback_type']
        feedback_data = data.get('feedback_data', {})
        
        # Validar tipo de feedback
        valid_feedback_types = [
            'follow_up_received', 'no_follow_up', 'positive_response', 
            'negative_response', 'conversion', 'complaint'
        ]
        
        if feedback_type not in valid_feedback_types:
            return jsonify({
                'error': f'Tipo de feedback inválido. Use: {", ".join(valid_feedback_types)}'
            }), 400
        
        # Atualizar aprendizado
        success = email_processor.update_learning_from_feedback(
            response_id, feedback_type, feedback_data
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Feedback de aprendizado atualizado com sucesso',
                'response_id': response_id,
                'feedback_type': feedback_type
            })
        else:
            return jsonify({'error': 'Falha ao atualizar feedback'}), 500
        
    except Exception as e:
        logger.error(f"Error updating learning feedback: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/insights/<account_name>', methods=['GET'])
def get_learning_insights(account_name):
    """
    Obtém insights de aprendizado para uma conta
    """
    try:
        insights = learning_service.generate_learning_insights(account_name)
        
        return jsonify({
            'success': True,
            'data': insights,
            'account': account_name,
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/history/<account_name>', methods=['GET'])
def get_sent_emails_history(account_name):
    """
    Obtém histórico de emails enviados para análise
    """
    try:
        days_back = request.args.get('days_back', 90, type=int)
        max_results = request.args.get('max_results', 100, type=int)
        
        # Limitar max_results para evitar sobrecarga
        max_results = min(max_results, 500)
        
        history = gmail_service.get_sent_emails_history(
            account_name, max_results, days_back
        )
        
        return jsonify({
            'success': True,
            'data': history,
            'total_emails': len(history),
            'account': account_name,
            'period_days': days_back
        })
        
    except Exception as e:
        logger.error(f"Error getting sent emails history: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/search-similar', methods=['POST'])
def search_similar_emails():
    """
    Busca emails similares baseado em palavras-chave
    """
    try:
        data = request.get_json()
        
        if not data or 'keywords' not in data or 'account_name' not in data:
            return jsonify({
                'error': 'keywords e account_name são obrigatórios'
            }), 400
        
        keywords = data['keywords']
        account_name = data['account_name']
        days_back = data.get('days_back', 180)
        
        if not isinstance(keywords, list):
            return jsonify({'error': 'keywords deve ser uma lista'}), 400
        
        similar_emails = gmail_service.search_similar_emails(
            account_name, keywords, days_back
        )
        
        return jsonify({
            'success': True,
            'data': similar_emails,
            'total_found': len(similar_emails),
            'search_params': {
                'keywords': keywords,
                'account': account_name,
                'days_back': days_back
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching similar emails: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/generate-with-learning', methods=['POST'])
def generate_response_with_learning():
    """
    Gera resposta usando aprendizado baseado no histórico
    Esta é a funcionalidade principal de geração inteligente!
    """
    try:
        data = request.get_json()
        
        required_fields = ['email_data', 'classification']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Campos obrigatórios: {", ".join(required_fields)}'
            }), 400
        
        email_data = data['email_data']
        classification = data['classification']
        template = data.get('template')
        
        # Gerar resposta com aprendizado
        generated_response = ai_service.generate_response_with_learning(
            email_data, classification, learning_service, template
        )
        
        return jsonify({
            'success': True,
            'data': generated_response,
            'learning_applied': generated_response.get('learning_applied', False),
            'similar_responses_found': generated_response.get('similar_responses_found', 0),
            'conversation_stage': generated_response.get('conversation_stage', 'unknown')
        })
        
    except Exception as e:
        logger.error(f"Error generating response with learning: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/stats', methods=['GET'])
def get_learning_stats():
    """
    Obtém estatísticas gerais do sistema de aprendizado
    """
    try:
        accounts = ['contato', 'cursos', 'diogo', 'sac']
        stats = {}
        
        for account in accounts:
            try:
                # Estatísticas básicas
                patterns = learning_service.analyze_response_patterns(account, days_back=30)
                
                stats[account] = {
                    'total_analyzed': patterns.get('total_analyzed', 0),
                    'greeting_patterns_count': len(patterns.get('greeting_patterns', [])),
                    'closing_patterns_count': len(patterns.get('closing_patterns', [])),
                    'avg_response_length': patterns.get('response_length_stats', {}).get('avg_length', 0),
                    'last_analysis': datetime.utcnow().isoformat()
                }
            except Exception as e:
                stats[account] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'data': stats,
            'total_accounts': len(accounts),
            'generated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting learning stats: {e}")
        return jsonify({'error': str(e)}), 500

@learning_bp.route('/health', methods=['GET'])
def learning_health_check():
    """
    Verifica saúde do sistema de aprendizado
    """
    try:
        health_status = {
            'learning_service': 'ok',
            'gmail_service': 'ok',
            'ai_service': 'ok',
            'dependencies': {
                'nltk': 'ok',
                'textblob': 'ok',
                'scikit_learn': 'ok'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Testar dependências
        try:
            import nltk
            import textblob
            import sklearn
        except ImportError as e:
            health_status['dependencies']['error'] = str(e)
            health_status['status'] = 'warning'
        
        return jsonify({
            'success': True,
            'data': health_status
        })
        
    except Exception as e:
        logger.error(f"Error in learning health check: {e}")
        return jsonify({'error': str(e)}), 500
