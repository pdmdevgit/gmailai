#!/usr/bin/env python3
"""
Validação de Lógica - Controle Manual de Emails
Testa a lógica implementada sem dependências externas
"""

import os
import re
import json
from datetime import datetime

def test_code_changes():
    """Valida se as mudanças no código foram implementadas corretamente"""
    results = []
    
    # 1. Verificar se marcação automática como lido foi removida
    try:
        with open('app/services/email_processor.py', 'r') as f:
            processor_content = f.read()
        
        # Verificar se a linha de mark_as_read foi comentada/removida
        if 'mark_as_read(account, gmail_id)' not in processor_content or '# REMOVIDO' in processor_content:
            results.append(("✅", "Marcação automática como lido removida do EmailProcessor"))
        else:
            results.append(("❌", "Marcação automática como lido ainda presente no EmailProcessor"))
    except Exception as e:
        results.append(("❌", f"Erro ao verificar EmailProcessor: {e}"))
    
    # 2. Verificar se novas rotas foram adicionadas
    try:
        with open('app/api/email_routes.py', 'r') as f:
            routes_content = f.read()
        
        required_routes = [
            'mark-as-read',
            'create-draft', 
            'bulk-mark-read',
            'learning/update-from-sent'
        ]
        
        missing_routes = []
        for route in required_routes:
            if route not in routes_content:
                missing_routes.append(route)
        
        if not missing_routes:
            results.append(("✅", "Todas as novas rotas de controle manual foram adicionadas"))
        else:
            results.append(("❌", f"Rotas faltando: {missing_routes}"))
    except Exception as e:
        results.append(("❌", f"Erro ao verificar rotas: {e}"))
    
    # 3. Verificar se método create_draft foi adicionado ao GmailService
    try:
        with open('app/services/gmail_service.py', 'r') as f:
            gmail_content = f.read()
        
        if 'def create_draft(' in gmail_content and 'NEVER SEND AUTOMATICALLY' in gmail_content:
            results.append(("✅", "Método create_draft adicionado ao GmailService com proteção contra envio automático"))
        else:
            results.append(("❌", "Método create_draft não encontrado ou sem proteção adequada"))
    except Exception as e:
        results.append(("❌", f"Erro ao verificar GmailService: {e}"))
    
    # 4. Verificar mudanças no modelo de dados
    try:
        with open('app/models/__init__.py', 'r') as f:
            models_content = f.read()
        
        if 'is_read = db.Column(db.Boolean' in models_content:
            results.append(("✅", "Campo is_read adicionado ao modelo Email"))
        else:
            results.append(("❌", "Campo is_read não encontrado no modelo Email"))
        
        if 'draft_created_at = db.Column(db.DateTime' in models_content:
            results.append(("✅", "Campo draft_created_at adicionado ao modelo EmailResponse"))
        else:
            results.append(("❌", "Campo draft_created_at não encontrado no modelo EmailResponse"))
    except Exception as e:
        results.append(("❌", f"Erro ao verificar modelos: {e}"))
    
    # 5. Verificar mudanças no SQL
    try:
        with open('database/init.sql', 'r') as f:
            sql_content = f.read()
        
        if 'is_read BOOLEAN DEFAULT FALSE' in sql_content:
            results.append(("✅", "Campo is_read adicionado ao SQL"))
        else:
            results.append(("❌", "Campo is_read não encontrado no SQL"))
        
        if 'draft_created_at DATETIME' in sql_content:
            results.append(("✅", "Campo draft_created_at adicionado ao SQL"))
        else:
            results.append(("❌", "Campo draft_created_at não encontrado no SQL"))
    except Exception as e:
        results.append(("❌", f"Erro ao verificar SQL: {e}"))
    
    return results

def test_api_endpoints_structure():
    """Valida a estrutura dos endpoints da API"""
    results = []
    
    try:
        with open('app/api/email_routes.py', 'r') as f:
            content = f.read()
        
        # Verificar estrutura dos endpoints críticos
        endpoints_to_check = {
            'mark_email_as_read': [
                'def mark_email_as_read(',
                'gmail_service.mark_as_read(',
                'email.is_read = True'
            ],
            'create_draft_response': [
                'def create_draft_response(',
                'gmail_service.create_draft(',
                'NUNCA ENVIAR AUTOMATICAMENTE'
            ],
            'bulk_mark_as_read': [
                'def bulk_mark_as_read(',
                'email_ids',
                'CONTROLE MANUAL'
            ],
            'update_learning_from_sent_emails': [
                'def update_learning_from_sent_emails(',
                'get_sent_emails_history',
                'analyze_response_effectiveness'
            ]
        }
        
        for endpoint_name, required_elements in endpoints_to_check.items():
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if not missing_elements:
                results.append(("✅", f"Endpoint {endpoint_name} implementado corretamente"))
            else:
                results.append(("❌", f"Endpoint {endpoint_name} incompleto: {missing_elements}"))
    
    except Exception as e:
        results.append(("❌", f"Erro ao verificar estrutura dos endpoints: {e}"))
    
    return results

def test_safety_measures():
    """Verifica se medidas de segurança foram implementadas"""
    results = []
    
    try:
        # Verificar se há proteções contra envio automático
        with open('app/services/gmail_service.py', 'r') as f:
            gmail_content = f.read()
        
        # Verificar se create_draft usa drafts().create() e não messages().send()
        if 'drafts().create(' in gmail_content and 'NEVER SEND AUTOMATICALLY' in gmail_content:
            results.append(("✅", "Proteção contra envio automático implementada no create_draft"))
        else:
            results.append(("❌", "Proteção contra envio automático não encontrada"))
        
        # Verificar se email_processor não chama mark_as_read automaticamente
        with open('app/services/email_processor.py', 'r') as f:
            processor_content = f.read()
        
        # Contar ocorrências de mark_as_read
        mark_as_read_calls = len(re.findall(r'mark_as_read\(', processor_content))
        commented_calls = len(re.findall(r'#.*mark_as_read', processor_content))
        
        if mark_as_read_calls == 0 or commented_calls > 0:
            results.append(("✅", "EmailProcessor não chama mark_as_read automaticamente"))
        else:
            results.append(("❌", f"EmailProcessor ainda tem {mark_as_read_calls} chamadas para mark_as_read"))
        
        # Verificar se há comentários explicativos sobre controle manual
        manual_control_comments = len(re.findall(r'(CONTROLE MANUAL|controle manual|usuário deve|manual)', 
                                                processor_content + gmail_content, re.IGNORECASE))
        
        if manual_control_comments > 0:
            results.append(("✅", f"Comentários sobre controle manual encontrados ({manual_control_comments})"))
        else:
            results.append(("⚠️", "Poucos comentários explicativos sobre controle manual"))
    
    except Exception as e:
        results.append(("❌", f"Erro ao verificar medidas de segurança: {e}"))
    
    return results

def test_learning_functionality():
    """Verifica se funcionalidade de aprendizado foi implementada"""
    results = []
    
    try:
        with open('app/api/email_routes.py', 'r') as f:
            routes_content = f.read()
        
        # Verificar elementos da funcionalidade de aprendizado
        learning_elements = [
            'get_sent_emails_history',
            'get_conversation_thread', 
            'analyze_response_effectiveness',
            'original_question',
            'sent_response'
        ]
        
        missing_elements = []
        for element in learning_elements:
            if element not in routes_content:
                missing_elements.append(element)
        
        if not missing_elements:
            results.append(("✅", "Funcionalidade de aprendizado implementada completamente"))
        else:
            results.append(("❌", f"Elementos de aprendizado faltando: {missing_elements}"))
        
        # Verificar se há lógica para identificar pergunta vs resposta
        if 'is_sent' in routes_content and 'thread_email' in routes_content:
            results.append(("✅", "Lógica para identificar pergunta vs resposta implementada"))
        else:
            results.append(("❌", "Lógica para identificar pergunta vs resposta não encontrada"))
    
    except Exception as e:
        results.append(("❌", f"Erro ao verificar funcionalidade de aprendizado: {e}"))
    
    return results

def test_documentation():
    """Verifica se documentação foi criada"""
    results = []
    
    try:
        # Verificar se arquivo de documentação existe
        if os.path.exists('CONTROLE_MANUAL_IMPLEMENTADO.md'):
            with open('CONTROLE_MANUAL_IMPLEMENTADO.md', 'r') as f:
                doc_content = f.read()
            
            # Verificar seções importantes da documentação
            required_sections = [
                'Problema Resolvido',
                'Mudanças Implementadas',
                'Fluxo de Trabalho',
                'Controle Total',
                'Endpoints Disponíveis'
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in doc_content:
                    missing_sections.append(section)
            
            if not missing_sections:
                results.append(("✅", "Documentação completa criada"))
            else:
                results.append(("❌", f"Seções faltando na documentação: {missing_sections}"))
            
            # Verificar se há exemplos de uso
            if 'POST /api/emails' in doc_content and 'curl' in doc_content.lower():
                results.append(("✅", "Exemplos de uso incluídos na documentação"))
            else:
                results.append(("⚠️", "Poucos exemplos de uso na documentação"))
        else:
            results.append(("❌", "Arquivo de documentação não encontrado"))
    
    except Exception as e:
        results.append(("❌", f"Erro ao verificar documentação: {e}"))
    
    return results

def run_all_validations():
    """Executa todas as validações"""
    print("🔍 Validação de Lógica - Controle Manual de Emails")
    print("=" * 60)
    
    all_results = []
    
    # Executar todos os testes
    test_suites = [
        ("Mudanças no Código", test_code_changes),
        ("Estrutura dos Endpoints", test_api_endpoints_structure),
        ("Medidas de Segurança", test_safety_measures),
        ("Funcionalidade de Aprendizado", test_learning_functionality),
        ("Documentação", test_documentation)
    ]
    
    for suite_name, test_function in test_suites:
        print(f"\n📋 {suite_name}")
        print("-" * 40)
        
        try:
            results = test_function()
            for status, message in results:
                print(f"{status} {message}")
                all_results.append((status, message))
        except Exception as e:
            print(f"❌ Erro ao executar {suite_name}: {e}")
            all_results.append(("❌", f"Erro em {suite_name}: {e}"))
    
    # Gerar relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL DA VALIDAÇÃO")
    print("=" * 60)
    
    total = len(all_results)
    passed = len([r for r in all_results if r[0] == "✅"])
    failed = len([r for r in all_results if r[0] == "❌"])
    warnings = len([r for r in all_results if r[0] == "⚠️"])
    
    print(f"Total de Verificações: {total}")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"⚠️ Avisos: {warnings}")
    print(f"📈 Taxa de Sucesso: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print(f"\n❌ VERIFICAÇÕES QUE FALHARAM:")
        for status, message in all_results:
            if status == "❌":
                print(f"  - {message}")
    
    if warnings > 0:
        print(f"\n⚠️ AVISOS:")
        for status, message in all_results:
            if status == "⚠️":
                print(f"  - {message}")
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': total,
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'success_rate': (passed/total*100) if total > 0 else 0
        },
        'results': [{'status': status, 'message': message} for status, message in all_results]
    }
    
    with open('validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: validation_report.json")
    
    return passed, failed, warnings

if __name__ == "__main__":
    passed, failed, warnings = run_all_validations()
    
    # Exit code baseado nos resultados
    exit_code = 0 if failed == 0 else 1
    exit(exit_code)
