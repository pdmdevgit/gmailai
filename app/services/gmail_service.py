import os
import json
import base64
import email
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import html2text

logger = logging.getLogger(__name__)

class GmailService:
    """Service for Gmail API operations"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_file: str, token_dir: str):
        self.credentials_file = credentials_file
        self.token_dir = token_dir
        self.services = {}  # Cache for authenticated services
        
        # Ensure token directory exists
        os.makedirs(token_dir, exist_ok=True)
    
    def authenticate_account(self, account_name: str, email_address: str) -> bool:
        """Authenticate a Gmail account and store credentials"""
        try:
            token_file = os.path.join(self.token_dir, f'{account_name}_token.json')
            creds = None
            
            # Load existing token
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            
            # If no valid credentials, run OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Build service and cache it
            service = build('gmail', 'v1', credentials=creds)
            self.services[account_name] = service
            
            logger.info(f"Successfully authenticated {account_name} ({email_address})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate {account_name}: {str(e)}")
            return False
    
    def get_service(self, account_name: str):
        """Get authenticated Gmail service for account"""
        if account_name not in self.services:
            raise ValueError(f"Account {account_name} not authenticated")
        return self.services[account_name]
    
    def get_unread_emails(self, account_name: str, max_results: int = 50) -> List[Dict]:
        """Get unread emails from account"""
        try:
            service = self.get_service(account_name)
            
            # Search for unread emails
            results = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(service, message['id'])
                if email_data:
                    email_data['account'] = account_name
                    emails.append(email_data)
            
            logger.info(f"Retrieved {len(emails)} unread emails from {account_name}")
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error for {account_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting emails from {account_name}: {str(e)}")
            return []
    
    def _get_email_details(self, service, message_id: str) -> Optional[Dict]:
        """Get detailed email information"""
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            header_dict = {h['name'].lower(): h['value'] for h in headers}
            
            # Extract email content
            body_text, body_html = self._extract_email_body(message['payload'])
            
            # Parse date
            date_str = header_dict.get('date', '')
            received_at = self._parse_email_date(date_str)
            
            email_data = {
                'gmail_id': message_id,
                'thread_id': message['threadId'],
                'sender_email': self._extract_email_address(header_dict.get('from', '')),
                'sender_name': self._extract_sender_name(header_dict.get('from', '')),
                'subject': header_dict.get('subject', ''),
                'body_text': body_text,
                'body_html': body_html,
                'received_at': received_at,
                'labels': message.get('labelIds', [])
            }
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error getting email details for {message_id}: {str(e)}")
            return None
    
    def _extract_email_body(self, payload) -> tuple:
        """Extract text and HTML body from email payload"""
        body_text = ""
        body_html = ""
        
        def extract_parts(part):
            nonlocal body_text, body_html
            
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    body_text += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            elif part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data', '')
                if data:
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    body_html += html_content
                    # Convert HTML to text as fallback
                    if not body_text:
                        h = html2text.HTML2Text()
                        h.ignore_links = True
                        body_text += h.handle(html_content)
            
            # Handle multipart
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_parts(subpart)
        
        extract_parts(payload)
        
        return body_text.strip(), body_html.strip()
    
    def _extract_email_address(self, from_header: str) -> str:
        """Extract email address from From header"""
        if '<' in from_header and '>' in from_header:
            start = from_header.find('<') + 1
            end = from_header.find('>')
            return from_header[start:end].strip()
        return from_header.strip()
    
    def _extract_sender_name(self, from_header: str) -> str:
        """Extract sender name from From header"""
        if '<' in from_header:
            return from_header[:from_header.find('<')].strip().strip('"')
        return ""
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        try:
            # Remove timezone info for simplicity
            if '(' in date_str:
                date_str = date_str[:date_str.find('(')].strip()
            
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.utcnow()
    
    def send_email(self, account_name: str, to_email: str, subject: str, 
                   body_text: str, body_html: str = None, reply_to_id: str = None) -> bool:
        """Send email from account"""
        try:
            service = self.get_service(account_name)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add text part
            text_part = MIMEText(body_text, 'plain', 'utf-8')
            message.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, 'html', 'utf-8')
                message.attach(html_part)
            
            # Set reply headers if replying
            if reply_to_id:
                original_message = service.users().messages().get(
                    userId='me', id=reply_to_id
                ).execute()
                
                headers = original_message['payload'].get('headers', [])
                header_dict = {h['name'].lower(): h['value'] for h in headers}
                
                message['In-Reply-To'] = header_dict.get('message-id', '')
                message['References'] = header_dict.get('references', '') + ' ' + header_dict.get('message-id', '')
            
            # Send message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            send_message = {'raw': raw_message}
            
            if reply_to_id:
                send_message['threadId'] = original_message['threadId']
            
            result = service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            logger.info(f"Email sent successfully from {account_name} to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email from {account_name}: {str(e)}")
            return False
    
    def mark_as_read(self, account_name: str, message_id: str) -> bool:
        """Mark email as read"""
        try:
            service = self.get_service(account_name)
            
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def add_label(self, account_name: str, message_id: str, label_name: str) -> bool:
        """Add label to email"""
        try:
            service = self.get_service(account_name)
            
            # Get or create label
            labels = service.users().labels().list(userId='me').execute()
            label_id = None
            
            for label in labels.get('labels', []):
                if label['name'] == label_name:
                    label_id = label['id']
                    break
            
            if not label_id:
                # Create label
                label_object = {
                    'name': label_name,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
                created_label = service.users().labels().create(
                    userId='me',
                    body=label_object
                ).execute()
                label_id = created_label['id']
            
            # Add label to message
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding label to email: {str(e)}")
            return False
    
    def get_email_history(self, account_name: str, days_back: int = 30) -> List[Dict]:
        """Get email history for the specified number of days"""
        try:
            service = self.get_service(account_name)
            
            # Calculate date range
            start_date = datetime.utcnow() - timedelta(days=days_back)
            query = f'after:{start_date.strftime("%Y/%m/%d")}'
            
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=500
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(service, message['id'])
                if email_data:
                    email_data['account'] = account_name
                    emails.append(email_data)
            
            logger.info(f"Retrieved {len(emails)} emails from last {days_back} days for {account_name}")
            return emails
            
        except Exception as e:
            logger.error(f"Error getting email history for {account_name}: {str(e)}")
            return []
    
    def get_sent_emails_history(self, account_name: str, max_results: int = 200, days_back: int = 90) -> List[Dict]:
        """
        Busca histórico de emails enviados para análise de padrões de resposta
        Essencial para o sistema aprender com suas próprias respostas
        """
        try:
            service = self.get_service(account_name)
            
            # Calcular data limite
            start_date = datetime.utcnow() - timedelta(days=days_back)
            date_str = start_date.strftime('%Y/%m/%d')
            
            # Buscar emails enviados
            results = service.users().messages().list(
                userId='me',
                q=f'in:sent after:{date_str}',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            sent_emails = []
            
            for message in messages:
                email_data = self._get_email_details(service, message['id'])
                if email_data:
                    email_data['account'] = account_name
                    email_data['is_sent'] = True
                    sent_emails.append(email_data)
            
            logger.info(f"Retrieved {len(sent_emails)} sent emails from last {days_back} days for {account_name}")
            return sent_emails
            
        except Exception as e:
            logger.error(f"Error fetching sent emails for {account_name}: {e}")
            return []
    
    def get_conversation_thread(self, account_name: str, thread_id: str) -> List[Dict]:
        """
        Busca thread completa de conversa para context awareness
        Permite entender o contexto completo da conversa
        """
        try:
            service = self.get_service(account_name)
            
            thread = service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = thread.get('messages', [])
            conversation = []
            
            for message in messages:
                email_data = self._get_email_details(service, message['id'])
                if email_data:
                    email_data['account'] = account_name
                    # Identificar se é enviado ou recebido
                    labels = message.get('labelIds', [])
                    email_data['is_sent'] = 'SENT' in labels
                    conversation.append(email_data)
            
            # Ordenar por data
            conversation.sort(key=lambda x: x['received_at'])
            
            logger.info(f"Retrieved conversation thread with {len(conversation)} messages")
            return conversation
            
        except Exception as e:
            logger.error(f"Error fetching conversation thread: {e}")
            return []
    
    def search_similar_emails(self, account_name: str, keywords: List[str], days_back: int = 180) -> List[Dict]:
        """
        Busca emails similares baseado em palavras-chave
        Útil para encontrar padrões de resposta para tipos específicos de consulta
        """
        try:
            service = self.get_service(account_name)
            
            # Construir query de busca
            start_date = datetime.utcnow() - timedelta(days=days_back)
            date_str = start_date.strftime('%Y/%m/%d')
            
            # Combinar keywords
            keyword_query = ' OR '.join([f'"{keyword}"' for keyword in keywords])
            query = f'({keyword_query}) after:{date_str}'
            
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            similar_emails = []
            
            for message in messages:
                email_data = self._get_email_details(service, message['id'])
                if email_data:
                    email_data['account'] = account_name
                    similar_emails.append(email_data)
            
            logger.info(f"Found {len(similar_emails)} similar emails for keywords: {keywords}")
            return similar_emails
            
        except Exception as e:
            logger.error(f"Error searching similar emails: {e}")
            return []
    
    def get_response_patterns(self, account_name: str, days_back: int = 90) -> Dict:
        """
        Analisa padrões de resposta baseado no histórico de emails enviados
        Retorna estatísticas e padrões comuns
        """
        try:
            sent_emails = self.get_sent_emails_history(account_name, max_results=300, days_back=days_back)
            
            patterns = {
                'total_sent': len(sent_emails),
                'common_subjects': {},
                'common_phrases': {},
                'response_times': [],
                'email_lengths': [],
                'greeting_patterns': [],
                'closing_patterns': []
            }
            
            for email in sent_emails:
                subject = email.get('subject', '').lower()
                body = email.get('body_text', '')
                
                # Analisar assuntos comuns
                if subject:
                    patterns['common_subjects'][subject] = patterns['common_subjects'].get(subject, 0) + 1
                
                # Analisar comprimento dos emails
                patterns['email_lengths'].append(len(body))
                
                # Extrair saudações (primeiras 2 linhas)
                lines = body.split('\n')[:2]
                if lines:
                    greeting = ' '.join(lines).strip()[:100]
                    if greeting:
                        patterns['greeting_patterns'].append(greeting)
                
                # Extrair despedidas (últimas 2 linhas)
                lines = body.split('\n')[-2:]
                if lines:
                    closing = ' '.join(lines).strip()[:100]
                    if closing:
                        patterns['closing_patterns'].append(closing)
            
            # Calcular estatísticas
            if patterns['email_lengths']:
                patterns['avg_email_length'] = sum(patterns['email_lengths']) / len(patterns['email_lengths'])
            
            logger.info(f"Analyzed response patterns for {account_name}: {patterns['total_sent']} emails")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing response patterns: {e}")
            return {}
