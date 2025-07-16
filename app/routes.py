from flask import Blueprint, render_template, jsonify, current_app, request, send_from_directory, make_response
from app.models import db, Email, EmailResponse, ProcessingLog
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page"""
    response = make_response(render_template('dashboard.html'))
    # Add anti-cache headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with anti-cache headers"""
    try:
        static_folder = os.path.join(current_app.root_path, '..', 'static')
        response = make_response(send_from_directory(static_folder, filename))
        
        # Force no cache for JavaScript and CSS files
        if filename.endswith(('.js', '.css')):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            response.headers['ETag'] = f'"{datetime.utcnow().timestamp()}"'
        
        return response
    except Exception as e:
        current_app.logger.error(f"Error serving static file {filename}: {str(e)}")
        return "File not found", 404

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
        db_error = None
    except Exception as e:
        db_status = 'disconnected'
        db_error = str(e)
    
    # Always return 200 for basic health check
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'database_error': db_error,
        'version': '1.0.0'
    })

@main_bp.route('/ping')
def ping():
    """Simple ping endpoint for basic health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })

@main_bp.route('/stats')
def get_stats():
    """Get system statistics"""
    try:
        # Calculate date ranges
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Email statistics
        total_emails = Email.query.count()
        emails_today = Email.query.filter(
            func.date(Email.created_at) == today
        ).count()
        emails_week = Email.query.filter(
            Email.created_at >= week_ago
        ).count()
        emails_month = Email.query.filter(
            Email.created_at >= month_ago
        ).count()
        
        # Classification statistics
        classified_emails = Email.query.filter(
            Email.classification_type.isnot(None)
        ).count()
        
        classification_breakdown = db.session.query(
            Email.classification_type,
            func.count(Email.id).label('count')
        ).filter(
            Email.classification_type.isnot(None)
        ).group_by(Email.classification_type).all()
        
        # Response statistics
        total_responses = EmailResponse.query.count()
        approved_responses = EmailResponse.query.filter_by(status='approved').count()
        sent_responses = EmailResponse.query.filter_by(status='sent').count()
        draft_responses = EmailResponse.query.filter_by(status='draft').count()
        
        # Account breakdown
        account_breakdown = db.session.query(
            Email.account,
            func.count(Email.id).label('count')
        ).group_by(Email.account).all()
        
        # Priority breakdown
        priority_breakdown = db.session.query(
            Email.classification_priority,
            func.count(Email.id).label('count')
        ).filter(
            Email.classification_priority.isnot(None)
        ).group_by(Email.classification_priority).all()
        
        # Recent activity
        recent_emails = Email.query.order_by(desc(Email.created_at)).limit(10).all()
        recent_responses = EmailResponse.query.order_by(desc(EmailResponse.created_at)).limit(10).all()
        
        stats = {
            'emails': {
                'total': total_emails,
                'today': emails_today,
                'week': emails_week,
                'month': emails_month,
                'classified': classified_emails,
                'classification_rate': round((classified_emails / total_emails * 100) if total_emails > 0 else 0, 2)
            },
            'responses': {
                'total': total_responses,
                'approved': approved_responses,
                'sent': sent_responses,
                'draft': draft_responses,
                'approval_rate': round((approved_responses / total_responses * 100) if total_responses > 0 else 0, 2)
            },
            'breakdown': {
                'by_account': [{'account': acc, 'count': count} for acc, count in account_breakdown],
                'by_classification': [{'type': cls, 'count': count} for cls, count in classification_breakdown],
                'by_priority': [{'priority': pri, 'count': count} for pri, count in priority_breakdown]
            },
            'recent_activity': {
                'emails': [{
                    'id': email.id,
                    'sender': email.sender_email,
                    'subject': email.subject[:50] + '...' if len(email.subject) > 50 else email.subject,
                    'account': email.account,
                    'classification': email.classification_type,
                    'created_at': email.created_at.isoformat()
                } for email in recent_emails],
                'responses': [{
                    'id': response.id,
                    'email_id': response.email_id,
                    'status': response.status,
                    'confidence': response.generation_confidence,
                    'created_at': response.created_at.isoformat()
                } for response in recent_responses]
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@main_bp.route('/accounts')
def get_accounts():
    """Get configured Gmail accounts"""
    accounts = current_app.config.get('GMAIL_ACCOUNTS', {})
    
    account_info = []
    for account_name, email_address in accounts.items():
        # Get email count for each account
        email_count = Email.query.filter_by(account=account_name).count()
        recent_count = Email.query.filter(
            Email.account == account_name,
            Email.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        account_info.append({
            'name': account_name,
            'email': email_address,
            'total_emails': email_count,
            'recent_emails': recent_count
        })
    
    return jsonify({
        'accounts': account_info,
        'total_accounts': len(accounts)
    })

@main_bp.route('/system-info')
def get_system_info():
    """Get system information"""
    try:
        # Get configuration info (without sensitive data)
        config_info = {
            'environment': current_app.config.get('FLASK_ENV', 'unknown'),
            'debug': current_app.config.get('DEBUG', False),
            'ai_model': current_app.config.get('AI_MODEL', 'unknown'),
            'email_check_interval': current_app.config.get('EMAIL_CHECK_INTERVAL', 300),
            'max_emails_per_batch': current_app.config.get('MAX_EMAILS_PER_BATCH', 50),
            'classification_threshold': current_app.config.get('CLASSIFICATION_CONFIDENCE_THRESHOLD', 0.7),
            'auto_response_threshold': current_app.config.get('AUTO_RESPONSE_THRESHOLD', 0.85)
        }
        
        # Get recent processing logs
        recent_logs = ProcessingLog.query.order_by(desc(ProcessingLog.created_at)).limit(20).all()
        
        # Calculate processing performance
        successful_actions = ProcessingLog.query.filter_by(status='success').count()
        total_actions = ProcessingLog.query.count()
        success_rate = round((successful_actions / total_actions * 100) if total_actions > 0 else 0, 2)
        
        # Average processing times
        avg_processing_time = db.session.query(
            func.avg(ProcessingLog.processing_time)
        ).filter(
            ProcessingLog.processing_time.isnot(None)
        ).scalar()
        
        system_info = {
            'configuration': config_info,
            'performance': {
                'success_rate': success_rate,
                'total_actions': total_actions,
                'successful_actions': successful_actions,
                'avg_processing_time': round(avg_processing_time or 0, 2)
            },
            'recent_logs': [{
                'id': log.id,
                'action': log.action,
                'status': log.status,
                'message': log.message,
                'processing_time': log.processing_time,
                'created_at': log.created_at.isoformat()
            } for log in recent_logs]
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        current_app.logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'error': 'Failed to get system information'}), 500

@main_bp.route('/auth/callback')
def oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        import json
        import os
        from google_auth_oauthlib.flow import Flow
        from google.oauth2.credentials import Credentials
        
        # Get state parameter
        state = request.args.get('state')
        if not state:
            return "Error: Missing state parameter", 400
        
        # Load state data with fallback
        state_file = f"/tmp/oauth_states/oauth_state_{state}.json"
        state_data = None
        
        # Try to load from file first
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
            except Exception as e:
                current_app.logger.error(f"Error reading OAuth state file: {str(e)}")
        
        # Fallback to app config
        if not state_data and hasattr(current_app, 'oauth_states'):
            state_data = current_app.oauth_states.get(state)
        
        if not state_data:
            return "Error: Invalid or expired state", 400
        
        account_name = state_data['account_name']
        email_address = state_data['email_address']
        
        # Create flow
        flow = Flow.from_client_secrets_file(
            current_app.config.get('GMAIL_CREDENTIALS_FILE'),
            scopes=[
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ],
            state=state
        )
        
        # Set redirect URI - use HTTPS in production
        if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https' or 'devpdm.com' in request.host:
            redirect_uri = f"https://{request.host}/auth/callback"
        else:
            redirect_uri = f"{request.host_url}auth/callback"
        
        flow.redirect_uri = redirect_uri
        
        # Exchange authorization code for credentials
        flow.fetch_token(authorization_response=request.url)
        
        # Save credentials
        token_dir = current_app.config.get('GMAIL_TOKEN_DIR')
        os.makedirs(token_dir, exist_ok=True)
        
        token_file = os.path.join(token_dir, f'{account_name}_token.json')
        with open(token_file, 'w') as f:
            f.write(flow.credentials.to_json())
        
        # Clean up state file and app config
        try:
            if os.path.exists(state_file):
                os.remove(state_file)
        except Exception:
            pass
        
        if hasattr(current_app, 'oauth_states') and state in current_app.oauth_states:
            del current_app.oauth_states[state]
        
        # Return success page
        return f"""
        <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .success {{ color: green; font-size: 24px; margin-bottom: 20px; }}
                .info {{ color: #666; margin-bottom: 30px; }}
                .button {{ 
                    background-color: #007bff; 
                    color: white; 
                    padding: 10px 20px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                }}
            </style>
        </head>
        <body>
            <div class="success">✓ Authentication Successful!</div>
            <div class="info">
                Account <strong>{account_name}</strong> ({email_address}) has been authenticated successfully.
            </div>
            <a href="/" class="button">Return to Dashboard</a>
            <script>
                // Auto-close window after 3 seconds if opened in popup
                if (window.opener) {{
                    setTimeout(() => window.close(), 3000);
                }}
            </script>
        </body>
        </html>
        """
        
    except Exception as e:
        current_app.logger.error(f"OAuth callback error: {str(e)}")
        return f"Authentication failed: {str(e)}", 500
