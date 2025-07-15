from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Email(db.Model):
    """Model for storing email data"""
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    gmail_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    thread_id = db.Column(db.String(255), nullable=False, index=True)
    account = db.Column(db.String(50), nullable=False, index=True)  # contato, cursos, diogo, sac
    
    # Email content
    sender_email = db.Column(db.String(255), nullable=False, index=True)
    sender_name = db.Column(db.String(255))
    subject = db.Column(db.Text)
    body_text = db.Column(db.Text)
    body_html = db.Column(db.Text)
    
    # Timestamps
    received_at = db.Column(db.DateTime, nullable=False, index=True)
    processed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Classification
    classification_type = db.Column(db.String(50), index=True)  # vendas, suporte, informacao
    classification_priority = db.Column(db.String(20), index=True)  # alta, media, baixa
    classification_product = db.Column(db.String(50))  # coaching, acelerador
    classification_sentiment = db.Column(db.String(20))  # positivo, neutro, negativo
    classification_confidence = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='pending', index=True)  # pending, processed, responded
    needs_human_review = db.Column(db.Boolean, default=False, index=True)
    
    # Relationships
    responses = db.relationship('EmailResponse', backref='email', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Email {self.gmail_id}: {self.subject[:50]}>'

class EmailResponse(db.Model):
    """Model for storing generated responses"""
    __tablename__ = 'email_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'), nullable=False)
    
    # Response content
    subject = db.Column(db.Text)
    body_text = db.Column(db.Text)
    body_html = db.Column(db.Text)
    
    # Generation info
    ai_model = db.Column(db.String(50))
    template_used = db.Column(db.String(100))
    generation_confidence = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, approved, sent, rejected
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailResponse {self.id}: {self.status}>'

class EmailTemplate(db.Model):
    """Model for storing email templates"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # vendas, suporte, etc
    product = db.Column(db.String(50))  # coaching, acelerador
    
    # Template content
    subject_template = db.Column(db.Text)
    body_template = db.Column(db.Text)
    variables = db.Column(db.JSON)  # Variables that can be replaced
    
    # Usage stats
    usage_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class ProcessingLog(db.Model):
    """Model for logging processing activities"""
    __tablename__ = 'processing_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'))
    
    # Log details
    action = db.Column(db.String(50), nullable=False)  # classify, generate_response, send, etc
    status = db.Column(db.String(20), nullable=False)  # success, error, warning
    message = db.Column(db.Text)
    details = db.Column(db.JSON)
    
    # Performance metrics
    processing_time = db.Column(db.Float)  # seconds
    api_calls_made = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProcessingLog {self.action}: {self.status}>'

class SystemSettings(db.Model):
    """Model for storing system settings"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, int, float, bool, json
    description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}: {self.value}>'

# Helper functions
def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    
def create_tables(app):
    """Create all tables"""
    with app.app_context():
        db.create_all()
        
def seed_templates():
    """Seed initial email templates"""
    templates = [
        {
            'name': 'interesse_coaching',
            'category': 'vendas',
            'product': 'coaching',
            'subject_template': 'Re: Sua consulta sobre Coaching para Concursos',
            'body_template': '''Olá {nome},

Obrigado pelo seu interesse no meu trabalho!

Vi que você está interessado(a) em acelerar sua aprovação em concursos fiscais. É exatamente isso que faço há anos - ajudo pessoas determinadas a conquistarem a aprovação em 9 meses, não em 3-5 anos como a média.

Minha metodologia é baseada na minha própria experiência de aprovação e nos resultados de centenas de alunos que já aprovei em carreiras como:
- SEFAZ (diversos estados)
- Receita Federal
- TCE/TCU
- TRF/TRE

O Coaching Individual (R$ 2.997) inclui:
✓ Mentoria personalizada semanal
✓ Plano de estudos customizado
✓ Metodologia dos 9 passos
✓ Suporte psicológico para manter a motivação
✓ Análise de editais e estratégias específicas

Que tal conversarmos sobre seu objetivo específico? 

Responda me contando:
1. Qual concurso você tem como meta?
2. Há quanto tempo estuda?
3. Qual sua maior dificuldade hoje?

Abraço,
Prof. Diogo Moreira''',
            'variables': ['nome', 'concurso_interesse']
        },
        {
            'name': 'interesse_acelerador',
            'category': 'vendas', 
            'product': 'acelerador',
            'subject_template': 'Re: Acelerador - Metodologia dos 9 Passos',
            'body_template': '''Olá {nome},

Que bom saber do seu interesse no Acelerador!

Este curso foi criado com base na metodologia que me levou à aprovação e que já aprovou centenas de alunos em concursos fiscais de alto nível.

O Acelerador (R$ 497) é perfeito para quem quer:
✓ Aprender a metodologia dos 9 passos
✓ Organizar os estudos de forma eficiente  
✓ Eliminar o "estudo burro" que não gera resultados
✓ Focar apenas no que realmente importa para aprovação

Alguns resultados dos meus alunos:
- Vitória Barbosa: aprovada SEFAZ-BA
- Thales: aprovado em TCE-RS, MPU, TRF-3, TRF-4, TRE-PA

A próxima turma está com vagas limitadas. 

Quer garantir sua vaga? Responda este email e te envio o link de inscrição.

Abraço,
Prof. Diogo Moreira''',
            'variables': ['nome']
        }
    ]
    
    for template_data in templates:
        template = EmailTemplate.query.filter_by(name=template_data['name']).first()
        if not template:
            template = EmailTemplate(**template_data)
            db.session.add(template)
    
    db.session.commit()
