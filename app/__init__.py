import os
import sys
import logging
from flask import Flask
from flask_migrate import Migrate

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import config with fallback
try:
    from config.config import config
    print("Successfully imported config from config.config")
except (ImportError, ModuleNotFoundError) as e:
    print(f"Could not import config.config: {e}")
    print("Using fallback configuration")
    
    # Fallback config for Docker environment
    class Config:
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        MYSQL_HOST = os.environ.get('MYSQL_HOST', 'mysql')
        MYSQL_USER = os.environ.get('MYSQL_USER', 'gmail_ai_user')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'gmail_ai_pass')
        MYSQL_DB = os.environ.get('MYSQL_DB', 'gmail_ai_agent')
        REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DB}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        DEBUG = os.environ.get('FLASK_ENV') == 'development'
        
        # Gmail API Configuration
        GMAIL_CREDENTIALS_FILE = os.environ.get('GMAIL_CREDENTIALS_FILE', 'config/gmail_credentials.json')
        GMAIL_TOKEN_DIR = os.environ.get('GMAIL_TOKEN_DIR', 'config/tokens')
        
        # Gmail Accounts to Monitor
        GMAIL_ACCOUNTS = {
            'contato': 'contato@profdiogomoreira.com.br',
            'cursos': 'cursos@profdiogomoreira.com.br', 
            'diogo': 'diogo@profdiogomoreira.com.br',
            'sac': 'sac@profdiogomoreira.com.br'
        }
        
        # AI Configuration
        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
        AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4')
        
        # Business Configuration
        BUSINESS_NAME = "Prof. Diogo Moreira"
        BUSINESS_DOMAIN = "profdiogomoreira.com.br"
        
        # Products Configuration
        PRODUCTS = {
        'coaching': {
            'name': 'Coaching Individual',
            'price': 2997,
            'description': 'Mentoria personalizada para aprovação em concursos fiscais'
        },
            'acelerador': {
                'name': 'Acelerador',
                'price': 497,
                'description': 'Curso com metodologia dos 9 passos para concursos'
            }
        }
        
        # Email Classification Settings
        CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.7
        AUTO_RESPONSE_THRESHOLD = 0.85
        
        # Rate Limiting
        GMAIL_API_RATE_LIMIT = 250
        AI_API_RATE_LIMIT = 60
        
        # Monitoring Settings
        EMAIL_CHECK_INTERVAL = 300
        MAX_EMAILS_PER_BATCH = 50
    
    config = {
        'production': Config(),
        'development': Config(),
        'default': Config()
    }

from app.models import db, init_db

# Configure logging with error handling
def setup_logging():
    """Setup logging with fallback to console only if file logging fails"""
    handlers = [logging.StreamHandler()]  # Always have console logging
    
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        # Try to create file handler
        file_handler = logging.FileHandler('logs/gmail_ai_agent.log')
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        # If file logging fails, just use console logging
        print(f"Warning: Could not setup file logging: {e}")
        print("Using console logging only")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

# Setup logging
setup_logging()

migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Configure Flask to use static files from project root
    static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    app = Flask(__name__, 
                static_folder=static_path,
                template_folder='templates')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.api.email_routes import email_bp
    from app.api.dashboard_routes import dashboard_bp
    from app.api.admin_routes import admin_bp
    from app.api.learning_routes import learning_bp
    
    app.register_blueprint(email_bp, url_prefix='/api/emails')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(learning_bp, url_prefix='/api/learning')
    
    # Register main routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    return app
