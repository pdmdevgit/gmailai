from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_
from app.models import db, Email, EmailResponse, ProcessingLog, EmailTemplate

dashboard_bp = Blueprint('dashboard_api', __name__)

@dashboard_bp.route('/overview')
def get_overview():
    """Get dashboard overview statistics"""
    try:
        # Calculate date ranges
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Email counts
        total_emails = Email.query.count()
        emails_today = Email.query.filter(func.date(Email.created_at) == today).count()
        emails_yesterday = Email.query.filter(func.date(Email.created_at) == yesterday).count()
        emails_week = Email.query.filter(Email.created_at >= week_ago).count()
        
        # Response counts
        total_responses = EmailResponse.query.count()
        responses_today = EmailResponse.query.filter(func.date(EmailResponse.created_at) == today).count()
        sent_responses = EmailResponse.query.filter_by(status='sent').count()
        pending_responses = EmailResponse.query.filter_by(status='draft').count()
        
        # Processing statistics
        processed_emails = Email.query.filter_by(status='processed').count()
        responded_emails = Email.query.filter_by(status='responded').count()
        pending_emails = Email.query.filter_by(status='pending').count()
        
        # Classification statistics
        classified_emails = Email.query.filter(Email.classification_type.isnot(None)).count()
        high_priority = Email.query.filter_by(classification_priority='alta').count()
        sales_emails = Email.query.filter_by(classification_type='vendas').count()
        
        # Calculate rates
        processing_rate = round((processed_emails / total_emails * 100) if total_emails > 0 else 0, 1)
        response_rate = round((sent_responses / total_emails * 100) if total_emails > 0 else 0, 1)
        classification_rate = round((classified_emails / total_emails * 100) if total_emails > 0 else 0, 1)
        
        # Growth calculations
        email_growth = emails_today - emails_yesterday
        email_growth_pct = round((email_growth / emails_yesterday * 100) if emails_yesterday > 0 else 0, 1)
        
        overview = {
            'summary': {
                'total_emails': total_emails,
                'emails_today': emails_today,
                'email_growth': email_growth,
                'email_growth_pct': email_growth_pct,
                'total_responses': total_responses,
                'responses_today': responses_today,
                'pending_responses': pending_responses
            },
            'processing': {
                'processed': processed_emails,
                'responded': responded_emails,
                'pending': pending_emails,
                'processing_rate': processing_rate,
                'response_rate': response_rate
            },
            'classification': {
                'classified': classified_emails,
                'classification_rate': classification_rate,
                'high_priority': high_priority,
                'sales_emails': sales_emails
            },
            'timeframes': {
                'today': emails_today,
                'yesterday': emails_yesterday,
                'week': emails_week,
                'month': Email.query.filter(Email.created_at >= month_ago).count()
            }
        }
        
        return jsonify(overview)
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard overview: {str(e)}")
        return jsonify({'error': 'Failed to get overview'}), 500

@dashboard_bp.route('/charts/email-volume')
def get_email_volume_chart():
    """Get email volume chart data"""
    try:
        # Get last 30 days of data
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=29)
        
        # Query daily email counts
        daily_counts = db.session.query(
            func.date(Email.created_at).label('date'),
            func.count(Email.id).label('count')
        ).filter(
            and_(
                func.date(Email.created_at) >= start_date,
                func.date(Email.created_at) <= end_date
            )
        ).group_by(func.date(Email.created_at)).all()
        
        # Create complete date range with zeros for missing days
        date_counts = {date: count for date, count in daily_counts}
        
        chart_data = []
        current_date = start_date
        while current_date <= end_date:
            chart_data.append({
                'date': current_date.isoformat(),
                'emails': date_counts.get(current_date, 0)
            })
            current_date += timedelta(days=1)
        
        return jsonify({
            'data': chart_data,
            'total_days': 30,
            'total_emails': sum(item['emails'] for item in chart_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting email volume chart: {str(e)}")
        return jsonify({'error': 'Failed to get chart data'}), 500

@dashboard_bp.route('/charts/classification-breakdown')
def get_classification_breakdown():
    """Get classification breakdown chart data"""
    try:
        # Get classification counts
        classification_data = db.session.query(
            Email.classification_type,
            func.count(Email.id).label('count')
        ).filter(
            Email.classification_type.isnot(None)
        ).group_by(Email.classification_type).all()
        
        # Get priority breakdown
        priority_data = db.session.query(
            Email.classification_priority,
            func.count(Email.id).label('count')
        ).filter(
            Email.classification_priority.isnot(None)
        ).group_by(Email.classification_priority).all()
        
        # Get sentiment breakdown
        sentiment_data = db.session.query(
            Email.classification_sentiment,
            func.count(Email.id).label('count')
        ).filter(
            Email.classification_sentiment.isnot(None)
        ).group_by(Email.classification_sentiment).all()
        
        # Get product interest breakdown
        product_data = db.session.query(
            Email.classification_product,
            func.count(Email.id).label('count')
        ).filter(
            and_(
                Email.classification_product.isnot(None),
                Email.classification_product != 'none'
            )
        ).group_by(Email.classification_product).all()
        
        breakdown = {
            'by_type': [{'label': cls or 'Unknown', 'value': count} for cls, count in classification_data],
            'by_priority': [{'label': pri or 'Unknown', 'value': count} for pri, count in priority_data],
            'by_sentiment': [{'label': sent or 'Unknown', 'value': count} for sent, count in sentiment_data],
            'by_product': [{'label': prod or 'Unknown', 'value': count} for prod, count in product_data]
        }
        
        return jsonify(breakdown)
        
    except Exception as e:
        current_app.logger.error(f"Error getting classification breakdown: {str(e)}")
        return jsonify({'error': 'Failed to get breakdown data'}), 500

@dashboard_bp.route('/charts/account-performance')
def get_account_performance():
    """Get account performance chart data"""
    try:
        # Get email counts by account
        account_emails = db.session.query(
            Email.account,
            func.count(Email.id).label('total_emails')
        ).group_by(Email.account).all()
        
        # Get response counts by account
        account_responses = db.session.query(
            Email.account,
            func.count(EmailResponse.id).label('total_responses')
        ).join(EmailResponse).group_by(Email.account).all()
        
        # Get sent responses by account
        account_sent = db.session.query(
            Email.account,
            func.count(EmailResponse.id).label('sent_responses')
        ).join(EmailResponse).filter(
            EmailResponse.status == 'sent'
        ).group_by(Email.account).all()
        
        # Combine data
        response_dict = {acc: count for acc, count in account_responses}
        sent_dict = {acc: count for acc, count in account_sent}
        
        performance_data = []
        for account, email_count in account_emails:
            responses = response_dict.get(account, 0)
            sent = sent_dict.get(account, 0)
            response_rate = round((responses / email_count * 100) if email_count > 0 else 0, 1)
            
            performance_data.append({
                'account': account,
                'emails': email_count,
                'responses': responses,
                'sent': sent,
                'response_rate': response_rate
            })
        
        return jsonify({
            'accounts': performance_data,
            'total_accounts': len(performance_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting account performance: {str(e)}")
        return jsonify({'error': 'Failed to get performance data'}), 500

@dashboard_bp.route('/recent-activity')
def get_recent_activity():
    """Get recent system activity"""
    try:
        # Recent emails
        recent_emails = Email.query.order_by(desc(Email.created_at)).limit(10).all()
        
        # Recent responses
        recent_responses = EmailResponse.query.order_by(desc(EmailResponse.created_at)).limit(10).all()
        
        # Recent processing logs
        recent_logs = ProcessingLog.query.order_by(desc(ProcessingLog.created_at)).limit(15).all()
        
        activity = {
            'emails': [{
                'id': email.id,
                'sender': email.sender_email,
                'subject': email.subject[:60] + '...' if len(email.subject) > 60 else email.subject,
                'account': email.account,
                'classification': email.classification_type,
                'priority': email.classification_priority,
                'status': email.status,
                'created_at': email.created_at.isoformat(),
                'time_ago': self._time_ago(email.created_at)
            } for email in recent_emails],
            
            'responses': [{
                'id': response.id,
                'email_id': response.email_id,
                'subject': response.subject[:60] + '...' if len(response.subject) > 60 else response.subject,
                'status': response.status,
                'confidence': response.generation_confidence,
                'created_at': response.created_at.isoformat(),
                'time_ago': self._time_ago(response.created_at)
            } for response in recent_responses],
            
            'logs': [{
                'id': log.id,
                'action': log.action,
                'status': log.status,
                'message': log.message[:100] + '...' if len(log.message) > 100 else log.message,
                'processing_time': log.processing_time,
                'created_at': log.created_at.isoformat(),
                'time_ago': self._time_ago(log.created_at)
            } for log in recent_logs]
        }
        
        return jsonify(activity)
        
    except Exception as e:
        current_app.logger.error(f"Error getting recent activity: {str(e)}")
        return jsonify({'error': 'Failed to get activity data'}), 500

@dashboard_bp.route('/performance-metrics')
def get_performance_metrics():
    """Get system performance metrics"""
    try:
        # Processing performance
        total_actions = ProcessingLog.query.count()
        successful_actions = ProcessingLog.query.filter_by(status='success').count()
        failed_actions = ProcessingLog.query.filter_by(status='error').count()
        
        success_rate = round((successful_actions / total_actions * 100) if total_actions > 0 else 0, 2)
        
        # Average processing times
        avg_processing_time = db.session.query(
            func.avg(ProcessingLog.processing_time)
        ).filter(
            ProcessingLog.processing_time.isnot(None)
        ).scalar()
        
        # Classification accuracy (based on confidence scores)
        avg_classification_confidence = db.session.query(
            func.avg(Email.classification_confidence)
        ).filter(
            Email.classification_confidence.isnot(None)
        ).scalar()
        
        # Response generation metrics
        avg_response_confidence = db.session.query(
            func.avg(EmailResponse.generation_confidence)
        ).filter(
            EmailResponse.generation_confidence.isnot(None)
        ).scalar()
        
        # API usage
        total_api_calls = db.session.query(
            func.sum(ProcessingLog.api_calls_made)
        ).scalar() or 0
        
        # Recent performance (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_actions = ProcessingLog.query.filter(
            ProcessingLog.created_at >= yesterday
        ).count()
        
        recent_successful = ProcessingLog.query.filter(
            and_(
                ProcessingLog.created_at >= yesterday,
                ProcessingLog.status == 'success'
            )
        ).count()
        
        recent_success_rate = round((recent_successful / recent_actions * 100) if recent_actions > 0 else 0, 2)
        
        metrics = {
            'overall': {
                'success_rate': success_rate,
                'total_actions': total_actions,
                'successful_actions': successful_actions,
                'failed_actions': failed_actions,
                'avg_processing_time': round(avg_processing_time or 0, 3),
                'total_api_calls': total_api_calls
            },
            'accuracy': {
                'avg_classification_confidence': round(avg_classification_confidence or 0, 3),
                'avg_response_confidence': round(avg_response_confidence or 0, 3)
            },
            'recent_24h': {
                'actions': recent_actions,
                'success_rate': recent_success_rate,
                'successful': recent_successful
            }
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({'error': 'Failed to get metrics'}), 500

@dashboard_bp.route('/alerts')
def get_alerts():
    """Get system alerts and notifications"""
    try:
        alerts = []
        
        # Check for high error rates
        recent_errors = ProcessingLog.query.filter(
            and_(
                ProcessingLog.created_at >= datetime.utcnow() - timedelta(hours=1),
                ProcessingLog.status == 'error'
            )
        ).count()
        
        if recent_errors > 5:
            alerts.append({
                'type': 'error',
                'title': 'High Error Rate',
                'message': f'{recent_errors} errors in the last hour',
                'severity': 'high',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for pending responses
        pending_responses = EmailResponse.query.filter_by(status='draft').count()
        if pending_responses > 10:
            alerts.append({
                'type': 'warning',
                'title': 'Many Pending Responses',
                'message': f'{pending_responses} responses awaiting approval',
                'severity': 'medium',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for unprocessed emails
        unprocessed_emails = Email.query.filter_by(status='pending').count()
        if unprocessed_emails > 20:
            alerts.append({
                'type': 'warning',
                'title': 'Unprocessed Emails',
                'message': f'{unprocessed_emails} emails pending processing',
                'severity': 'medium',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Check for low confidence classifications
        low_confidence = Email.query.filter(
            and_(
                Email.classification_confidence < 0.5,
                Email.classification_confidence.isnot(None),
                Email.created_at >= datetime.utcnow() - timedelta(days=1)
            )
        ).count()
        
        if low_confidence > 5:
            alerts.append({
                'type': 'info',
                'title': 'Low Confidence Classifications',
                'message': f'{low_confidence} emails classified with low confidence today',
                'severity': 'low',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({
            'alerts': alerts,
            'total': len(alerts)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting alerts: {str(e)}")
        return jsonify({'error': 'Failed to get alerts'}), 500

def _time_ago(timestamp):
    """Calculate human-readable time ago"""
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

# Add the helper method to the blueprint
dashboard_bp._time_ago = _time_ago
