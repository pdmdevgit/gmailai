import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'gmail_ai_agent'
    
    # Properly escape password for URL
    _escaped_password = quote_plus(MYSQL_PASSWORD) if MYSQL_PASSWORD else ''
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{_escaped_password}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Gmail API Configuration
    GMAIL_CREDENTIALS_FILE = os.environ.get('GMAIL_CREDENTIALS_FILE') or 'config/gmail_credentials.json'
    GMAIL_TOKEN_DIR = os.environ.get('GMAIL_TOKEN_DIR') or 'config/tokens'
    
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
    AI_MODEL = os.environ.get('AI_MODEL') or 'gpt-4'
    
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
    GMAIL_API_RATE_LIMIT = 250  # requests per user per 100 seconds
    AI_API_RATE_LIMIT = 60      # requests per minute
    
    # Monitoring Settings
    EMAIL_CHECK_INTERVAL = 300  # seconds (5 minutes)
    MAX_EMAILS_PER_BATCH = 50
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
