#!/usr/bin/env python3
"""
Gmail AI Agent - Email Monitor
Automated email processing service
"""

import os
import sys
import time
import logging
import schedule
from datetime import datetime
from threading import Thread

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.gmail_service import GmailService
from app.services.ai_service import AIService
from app.services.email_processor import EmailProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EmailMonitor:
    """Email monitoring and processing service"""
    
    def __init__(self):
        self.app = create_app()
        self.running = False
        self.gmail_service = None
        self.ai_service = None
        self.processor = None
        self.setup_services()
    
    def setup_services(self):
        """Initialize services"""
        try:
            with self.app.app_context():
                # Initialize Gmail service
                self.gmail_service = GmailService(
                    credentials_file=self.app.config.get('GMAIL_CREDENTIALS_FILE'),
                    token_dir=self.app.config.get('GMAIL_TOKEN_DIR')
                )
                
                # Initialize AI service
                self.ai_service = AIService(
                    openai_api_key=self.app.config.get('OPENAI_API_KEY'),
                    anthropic_api_key=self.app.config.get('ANTHROPIC_API_KEY'),
                    model=self.app.config.get('AI_MODEL', 'gpt-4')
                )
                
                # Initialize email processor
                self.processor = EmailProcessor(self.gmail_service, self.ai_service)
                
                # Authenticate Gmail accounts
                self.authenticate_accounts()
                
                logger.info("Services initialized successfully")
                
        except Exception as e:
            logger.error(f"Error setting up services: {str(e)}")
            raise
    
    def authenticate_accounts(self):
        """Authenticate all Gmail accounts"""
        accounts = self.app.config.get('GMAIL_ACCOUNTS', {})
        
        for account_name, email_address in accounts.items():
            try:
                success = self.gmail_service.authenticate_account(account_name, email_address)
                if success:
                    logger.info(f"Successfully authenticated {account_name}")
                else:
                    logger.warning(f"Failed to authenticate {account_name}")
            except Exception as e:
                logger.error(f"Error authenticating {account_name}: {str(e)}")
    
    def process_all_accounts(self):
        """Process emails for all accounts"""
        logger.info("Starting email processing cycle")
        
        with self.app.app_context():
            accounts = self.app.config.get('GMAIL_ACCOUNTS', {})
            max_emails = self.app.config.get('MAX_EMAILS_PER_BATCH', 50)
            
            total_processed = 0
            total_errors = 0
            
            for account_name in accounts.keys():
                try:
                    logger.info(f"Processing emails for account: {account_name}")
                    
                    results = self.processor.process_account_emails(account_name, max_emails)
                    
                    processed = results.get('processed', 0)
                    errors = results.get('errors', 0)
                    
                    total_processed += processed
                    total_errors += errors
                    
                    logger.info(f"Account {account_name}: {processed} processed, {errors} errors")
                    
                except Exception as e:
                    logger.error(f"Error processing account {account_name}: {str(e)}")
                    total_errors += 1
            
            logger.info(f"Processing cycle completed: {total_processed} processed, {total_errors} errors")
            
            # Log statistics
            stats = self.processor.get_processing_stats()
            logger.info(f"Session stats: {stats}")
    
    def health_check(self):
        """Perform system health check"""
        try:
            with self.app.app_context():
                # Check database connection
                from app.models import db
                db.session.execute('SELECT 1')
                
                # Check Gmail API connectivity
                accounts = self.app.config.get('GMAIL_ACCOUNTS', {})
                for account_name in accounts.keys():
                    try:
                        service = self.gmail_service.get_service(account_name)
                        # Simple API call to test connectivity
                        service.users().getProfile(userId='me').execute()
                    except Exception as e:
                        logger.warning(f"Gmail API issue for {account_name}: {str(e)}")
                
                logger.info("Health check passed")
                return True
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def cleanup_old_data(self):
        """Clean up old processing logs and data"""
        try:
            with self.app.app_context():
                from app.models import ProcessingLog
                from datetime import timedelta
                
                # Delete logs older than 30 days
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                
                deleted_count = ProcessingLog.query.filter(
                    ProcessingLog.created_at < cutoff_date
                ).delete()
                
                from app.models import db
                db.session.commit()
                
                logger.info(f"Cleaned up {deleted_count} old processing logs")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def start_monitoring(self):
        """Start the monitoring service"""
        logger.info("Starting Gmail AI Agent Monitor")
        
        # Schedule email processing
        interval = self.app.config.get('EMAIL_CHECK_INTERVAL', 300)  # 5 minutes default
        schedule.every(interval).seconds.do(self.process_all_accounts)
        
        # Schedule health checks every hour
        schedule.every().hour.do(self.health_check)
        
        # Schedule cleanup every day at 2 AM
        schedule.every().day.at("02:00").do(self.cleanup_old_data)
        
        # Initial health check
        self.health_check()
        
        # Initial processing
        self.process_all_accounts()
        
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            self.stop_monitoring()
        except Exception as e:
            logger.error(f"Monitor error: {str(e)}")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        logger.info("Stopping Gmail AI Agent Monitor")
        self.running = False
    
    def run_once(self):
        """Run processing once (for testing)"""
        logger.info("Running email processing once")
        self.process_all_accounts()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gmail AI Agent Monitor')
    parser.add_argument('--once', action='store_true', help='Run processing once and exit')
    parser.add_argument('--health-check', action='store_true', help='Run health check and exit')
    parser.add_argument('--cleanup', action='store_true', help='Run cleanup and exit')
    
    args = parser.parse_args()
    
    try:
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        monitor = EmailMonitor()
        
        if args.health_check:
            success = monitor.health_check()
            sys.exit(0 if success else 1)
        elif args.cleanup:
            monitor.cleanup_old_data()
            sys.exit(0)
        elif args.once:
            monitor.run_once()
            sys.exit(0)
        else:
            monitor.start_monitoring()
            
    except Exception as e:
        logger.error(f"Failed to start monitor: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
