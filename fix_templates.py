#!/usr/bin/env python3
"""
Script para corrigir problemas com templates
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, EmailTemplate
from sqlalchemy import text

def fix_templates():
    """Corrigir problemas com templates"""
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar se a tabela existe
            result = db.engine.execute(text("SHOW TABLES LIKE 'email_templates'"))
            table_exists = result.fetchone() is not None
            
            print(f"📋 Tabela email_templates existe: {table_exists}")
            
            if not table_exists:
                print("🔧 Criando tabela email_templates...")
                db.create_all()
                print("✅ Tabelas criadas!")
            
            # Verificar estrutura da tabela
            try:
                result = db.engine.execute(text("DESCRIBE email_templates"))
                columns = result.fetchall()
                print(f"📊 Colunas da tabela:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
            except Exception as e:
                print(f"❌ Erro ao verificar estrutura: {e}")
            
            # Tentar contar templates
            try:
                count = EmailTemplate.query.count()
                print(f"📈 Templates existentes: {count}")
            except Exception as e:
                print(f"❌ Erro ao contar templates: {e}")
                
                # Tentar recriar a tabela
                print("🔧 Tentando recriar tabela...")
                try:
                    db.engine.execute(text("DROP TABLE IF EXISTS email_templates"))
                    db.create_all()
                    print("✅ Tabela recriada!")
                except Exception as e2:
                    print(f"❌ Erro ao recriar tabela: {e2}")
            
            # Criar templates padrão
            templates = [
                {
                    'name': 'resposta_padrao',
                    'category': 'suporte',
                    'subject_template': 'Re: Sua mensagem',
                    'body_template': 'Olá! Obrigado por entrar em contato. Em breve retorno com uma resposta.',
                    'variables': ['nome'],
                    'is_active': True
                },
                {
                    'name': 'interesse_coaching',
                    'category': 'vendas',
                    'subject_template': 'Re: Coaching para Concursos',
                    'body_template': 'Olá! Vi seu interesse no coaching. Vamos conversar sobre seus objetivos?',
                    'variables': ['nome'],
                    'is_active': True
                }
            ]
            
            for template_data in templates:
                try:
                    existing = EmailTemplate.query.filter_by(name=template_data['name']).first()
                    if not existing:
                        template = EmailTemplate(**template_data)
                        db.session.add(template)
                        print(f"✅ Template '{template_data['name']}' criado")
                    else:
                        print(f"⚠️ Template '{template_data['name']}' já existe")
                except Exception as e:
                    print(f"❌ Erro ao criar template '{template_data['name']}': {e}")
            
            db.session.commit()
            print("🎉 Processo concluído!")
            
        except Exception as e:
            print(f"❌ Erro geral: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    fix_templates()
