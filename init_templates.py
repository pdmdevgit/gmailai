#!/usr/bin/env python3
"""
Script para inicializar templates no banco de dados
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, EmailTemplate

def init_templates():
    """Inicializar templates padrão"""
    app = create_app()
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        
        # Templates padrão
        templates = [
            {
                'name': 'interesse_coaching',
                'category': 'vendas',
                'product': 'coaching',
                'subject_template': 'Re: Sua consulta sobre Coaching para Concursos',
                'body_template': '''Olá {{nome}},

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
                'variables': ['nome', 'concurso_interesse'],
                'is_active': True
            },
            {
                'name': 'interesse_acelerador',
                'category': 'vendas', 
                'product': 'acelerador',
                'subject_template': 'Re: Acelerador - Metodologia dos 9 Passos',
                'body_template': '''Olá {{nome}},

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
                'variables': ['nome'],
                'is_active': True
            },
            {
                'name': 'resposta_padrao',
                'category': 'suporte',
                'subject_template': 'Re: {{assunto_original}}',
                'body_template': '''Olá {{nome}},

Obrigado por entrar em contato!

Recebi sua mensagem e vou analisá-la com atenção. Em breve retorno com uma resposta personalizada.

Enquanto isso, se for urgente, pode me chamar no WhatsApp ou acessar nossa área de membros para mais informações.

Abraço,
Prof. Diogo Moreira''',
                'variables': ['nome', 'assunto_original'],
                'is_active': True
            }
        ]
        
        # Inserir templates
        for template_data in templates:
            existing = EmailTemplate.query.filter_by(name=template_data['name']).first()
            if not existing:
                template = EmailTemplate(**template_data)
                db.session.add(template)
                print(f"✅ Template '{template_data['name']}' criado")
            else:
                print(f"⚠️ Template '{template_data['name']}' já existe")
        
        db.session.commit()
        print(f"\n🎉 Inicialização de templates concluída!")
        
        # Mostrar estatísticas
        total = EmailTemplate.query.count()
        active = EmailTemplate.query.filter_by(is_active=True).count()
        print(f"📊 Total de templates: {total}")
        print(f"📊 Templates ativos: {active}")

if __name__ == '__main__':
    init_templates()
