#!/usr/bin/env python3
"""
Gmail AI Agent - Main Application
Prof. Diogo Moreira Email Automation System
"""

import os
import sys
import logging
from flask import Flask
from flask_migrate import Migrate

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, create_tables, seed_templates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_database(app):
    """Initialize database and seed initial data"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Seed initial templates
            seed_templates()
            logger.info("Initial templates seeded successfully")
            
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        raise

def main():
    """Main application entry point"""
    try:
        # Create Flask app
        app = create_app()
        
        # Setup database
        setup_database(app)
        
        # Get configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = app.config.get('DEBUG', False)
        
        logger.info(f"Starting Gmail AI Agent on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Environment: {app.config.get('FLASK_ENV', 'development')}")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
