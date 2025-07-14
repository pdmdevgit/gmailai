import os
import logging
from flask import Flask
from flask_migrate import Migrate
try:
    from config.config import config
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))
    from config import config
from app.models import db, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/gmail_ai_agent.log'),
        logging.StreamHandler()
    ]
)

migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_db(app)
    migrate.init_app(app, db)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
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
