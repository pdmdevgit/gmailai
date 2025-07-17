#!/usr/bin/env python3
"""
Script para criar dados de exemplo para testes
"""

import os
import sys
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Email, EmailResponse, EmailTemplate

def create_sample_templates():
    """Criar templates de exemplo"""
    templates = [
        {
            'name': 'Resposta Geral',
            'category': 'geral',
            'subject_template': 'Re: {{original_subject}}',
            'body_template': '''Olá {{sender_name}},

Obrigado por entrar em contato conosco.

Recebemos sua mensagem e retornaremos em breve.

Atenciosamente,
Equipe {{business_name}}''',
            'variables': ['sender_name', 'original_subject', 'business_name'],
            'is_active': True
        },
        {
            'name': 'Informações sobre Coaching',
            'category': 'vendas',
            'subject_template': 'Re: Informações sobre Coaching Individual',
            'body_template': '''Olá {{sender_name}},

Obrigado pelo interesse no nosso Coaching Individual!

O programa inclui:
- Mentoria personalizada para concursos fiscais
- Metodologia comprovada
- Acompanhamento individual
- Investimento: R$ {{product_price}}

Gostaria de agendar uma conversa para conhecer melhor seu perfil?

Atenciosamente,
Prof. Diogo Moreira''',
            'variables': ['sender_name', 'product_price'],
            'is_active': True
        },
        {
            'name': 'Suporte Técnico',
            'category': 'suporte',
            'subject_template': 'Re: {{original_subject}} - Suporte',
            'body_template': '''Olá {{sender_name}},

Recebemos sua solicitação de suporte.

Nossa equipe técnica analisará sua questão e retornará em até 24 horas.

Se for urgente, entre em contato pelo WhatsApp: (11) 99999-9999

Atenciosamente,
Equipe de Suporte''',
            'variables': ['sender_name', 'original_subject'],
            'is_active': True
        },
        {
            'name': 'Agendamento de Reunião',
            'category': 'agendamento',
            'subject_template': 'Agendamento - {{meeting_type}}',
            'body_template': '''Olá {{sender_name}},

Vamos agendar nossa conversa!

Opções disponíveis:
- Segunda a Sexta: 9h às 18h
- Duração: {{meeting_duration}} minutos
- Formato: {{meeting_format}}

Por favor, confirme o melhor horário para você.

Link para agendamento: {{scheduling_link}}

Atenciosamente,
Prof. Diogo Moreira''',
            'variables': ['sender_name', 'meeting_type', 'meeting_duration', 'meeting_format', 'scheduling_link'],
            'is_active': True
        },
        {
            'name': 'Informações sobre Cursos',
            'category': 'informacao',
            'subject_template': 'Re: Informações sobre nossos cursos',
            'body_template': '''Olá {{sender_name}},

Obrigado pelo interesse em nossos cursos!

Temos as seguintes opções:

1. **Coaching Individual** - R$ 2.997
   - Mentoria personalizada
   - Acompanhamento individual

2. **Acelerador** - R$ 497
   - Metodologia dos 9 passos
   - Grupo de estudos

Qual opção desperta mais seu interesse?

Atenciosamente,
Prof. Diogo Moreira''',
            'variables': ['sender_name'],
            'is_active': True
        }
    ]
    
    for template_data in templates:
        # Check if template already exists
        existing = EmailTemplate.query.filter_by(name=template_data['name']).first()
        if not existing:
            template = EmailTemplate(**template_data)
            db.session.add(template)
            print(f"Created template: {template_data['name']}")
        else:
            print(f"Template already exists: {template_data['name']}")
    
    db.session.commit()

def create_sample_responses():
    """Criar respostas de exemplo"""
    # Get some emails to create responses for
    emails = Email.query.limit(5).all()
    
    if not emails:
        print("No emails found to create sample responses")
        return
    
    templates = EmailTemplate.query.all()
    
    for i, email in enumerate(emails):
        # Check if response already exists
        existing = EmailResponse.query.filter_by(email_id=email.id).first()
        if existing:
            continue
            
        template = templates[i % len(templates)] if templates else None
        
        response = EmailResponse(
            email_id=email.id,
            subject=f"Re: {email.subject}",
            body_text=f"Olá {email.sender_name or 'Cliente'},\n\nObrigado por entrar em contato.\n\nAtenciosamente,\nEquipe Prof. Diogo Moreira",
            body_html=f"<p>Olá {email.sender_name or 'Cliente'},</p><p>Obrigado por entrar em contato.</p><p>Atenciosamente,<br>Equipe Prof. Diogo Moreira</p>",
            status=['draft', 'approved', 'sent'][i % 3],
            ai_model='gpt-4',
            template_used=template.name if template else None,
            generation_confidence=0.85 + (i * 0.02),
            approved_by='admin' if i % 3 != 0 else None,
            approved_at=datetime.utcnow() - timedelta(hours=i) if i % 3 != 0 else None,
            sent_at=datetime.utcnow() - timedelta(hours=i*2) if i % 3 == 2 else None
        )
        
        db.session.add(response)
        print(f"Created response for email: {email.subject}")
    
    db.session.commit()

def main():
    """Main function"""
    app = create_app()
    
    with app.app_context():
        print("Creating sample data...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Create sample templates
        print("\n=== Creating Sample Templates ===")
        create_sample_templates()
        
        # Create sample responses
        print("\n=== Creating Sample Responses ===")
        create_sample_responses()
        
        print("\n=== Sample Data Creation Complete ===")
        
        # Show stats
        template_count = EmailTemplate.query.count()
        response_count = EmailResponse.query.count()
        email_count = Email.query.count()
        
        print(f"Templates: {template_count}")
        print(f"Responses: {response_count}")
        print(f"Emails: {email_count}")

if __name__ == '__main__':
    main()
