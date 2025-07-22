#!/usr/bin/env python3
"""
Script de Teste Completo - Controle Manual de Emails
Testa todas as funcionalidades implementadas para controle manual
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestControleManual:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name, status, message="", details=None):
        """Log resultado do teste"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
        if details:
            print(f"   Detalhes: {details}")
    
    def test_health_check(self):
        """Teste básico de conectividade"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("Health Check", "PASS", "Aplicação respondendo")
                return True
            else:
                self.log_test("Health Check", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Erro de conexão: {str(e)}")
            return False
    
    def test_database_connection(self):
        """Teste de conexão com banco de dados"""
        try:
            response = self.session.get(f"{self.api_url}/emails?per_page=1", timeout=10)
            if response.status_code == 200:
                self.log_test("Database Connection", "PASS", "Banco de dados acessível")
                return True
            else:
                self.log_test("Database Connection", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connection", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_email_listing(self):
        """Teste de listagem de emails"""
        try:
            response = self.session.get(f"{self.api_url}/emails", timeout=10)
            if response.status_code == 200:
                data = response.json()
                emails = data.get('emails', [])
                self.log_test("Email Listing", "PASS", f"Listou {len(emails)} emails", 
                            {'total_emails': len(emails), 'has_pagination': 'pagination' in data})
                return emails
            else:
                self.log_test("Email Listing", "FAIL", f"Status code: {response.status_code}")
                return []
        except Exception as e:
            self.log_test("Email Listing", "FAIL", f"Erro: {str(e)}")
            return []
    
    def test_email_processing(self):
        """Teste de processamento de emails (sem marcar como lido)"""
        try:
            payload = {
                "account": "contato",
                "max_emails": 5
            }
            response = self.session.post(f"{self.api_url}/emails/process", 
                                       json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                note = data.get('note', '')
                if 'NÃO marcados como lidos' in note:
                    self.log_test("Email Processing", "PASS", 
                                "Processamento sem marcação automática como lido",
                                {'results': data.get('results', {})})
                    return True
                else:
                    self.log_test("Email Processing", "WARN", 
                                "Processamento funcionou mas sem confirmação de não marcação")
                    return True
            else:
                self.log_test("Email Processing", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Email Processing", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_mark_as_read_individual(self, email_id):
        """Teste de marcação individual como lido"""
        try:
            response = self.session.post(f"{self.api_url}/emails/{email_id}/mark-as-read", 
                                       timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('is_read') == True:
                    self.log_test("Mark as Read (Individual)", "PASS", 
                                f"Email {email_id} marcado como lido",
                                {'email_id': email_id, 'gmail_id': data.get('gmail_id')})
                    return True
                else:
                    self.log_test("Mark as Read (Individual)", "FAIL", 
                                "Resposta não confirma marcação como lido")
                    return False
            else:
                self.log_test("Mark as Read (Individual)", "FAIL", 
                            f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Mark as Read (Individual)", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_bulk_mark_as_read(self, email_ids):
        """Teste de marcação em lote como lido"""
        try:
            payload = {"email_ids": email_ids[:3]}  # Testar com até 3 emails
            response = self.session.post(f"{self.api_url}/emails/bulk-mark-read", 
                                       json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                processed = data.get('processed', 0)
                results = data.get('results', [])
                success_count = len([r for r in results if r.get('status') == 'marked_as_read'])
                
                self.log_test("Bulk Mark as Read", "PASS", 
                            f"Processados {processed} emails, {success_count} marcados como lidos",
                            {'processed': processed, 'results': results})
                return True
            else:
                self.log_test("Bulk Mark as Read", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Bulk Mark as Read", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_response_generation(self, email_id):
        """Teste de geração de resposta"""
        try:
            payload = {
                "custom_instructions": "Teste de geração de resposta automática"
            }
            response = self.session.post(f"{self.api_url}/emails/{email_id}/responses", 
                                       json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                response_id = data.get('id')
                status = data.get('status')
                
                if response_id and status == 'draft':
                    self.log_test("Response Generation", "PASS", 
                                f"Resposta gerada com ID {response_id}",
                                {'response_id': response_id, 'status': status, 
                                 'confidence': data.get('confidence')})
                    return response_id
                else:
                    self.log_test("Response Generation", "FAIL", 
                                "Resposta gerada mas sem ID ou status incorreto")
                    return None
            else:
                error_data = response.json() if response.content else {}
                self.log_test("Response Generation", "FAIL", 
                            f"Status code: {response.status_code}",
                            {'error': error_data.get('error', 'Erro desconhecido')})
                return None
        except Exception as e:
            self.log_test("Response Generation", "FAIL", f"Erro: {str(e)}")
            return None
    
    def test_response_approval(self, response_id):
        """Teste de aprovação de resposta"""
        try:
            payload = {"approved_by": "test_user"}
            response = self.session.post(f"{self.api_url}/emails/responses/{response_id}/approve", 
                                       json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'approved':
                    self.log_test("Response Approval", "PASS", 
                                f"Resposta {response_id} aprovada",
                                {'response_id': response_id, 'approved_by': data.get('approved_by')})
                    return True
                else:
                    self.log_test("Response Approval", "FAIL", 
                                "Resposta não foi marcada como aprovada")
                    return False
            else:
                self.log_test("Response Approval", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Response Approval", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_draft_creation(self, email_id):
        """Teste de criação de rascunho (SEM ENVIO)"""
        try:
            response = self.session.post(f"{self.api_url}/emails/{email_id}/create-draft", 
                                       timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                message = data.get('message', '')
                
                if status == 'draft_created' and 'manualmente' in message:
                    self.log_test("Draft Creation", "PASS", 
                                "Rascunho criado no Gmail (sem envio automático)",
                                {'status': status, 'message': message})
                    return True
                else:
                    self.log_test("Draft Creation", "WARN", 
                                "Rascunho criado mas sem confirmação clara de não envio")
                    return True
            else:
                error_data = response.json() if response.content else {}
                self.log_test("Draft Creation", "FAIL", 
                            f"Status code: {response.status_code}",
                            {'error': error_data.get('error', 'Erro desconhecido')})
                return False
        except Exception as e:
            self.log_test("Draft Creation", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_learning_from_sent_emails(self):
        """Teste de aprendizado baseado em emails enviados"""
        try:
            payload = {
                "account": "contato",
                "days_back": 30
            }
            response = self.session.post(f"{self.api_url}/emails/learning/update-from-sent", 
                                       json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                sent_emails_found = data.get('sent_emails_found', 0)
                learning_updates = data.get('learning_updates', 0)
                
                self.log_test("Learning from Sent Emails", "PASS", 
                            f"Analisados {sent_emails_found} emails enviados, {learning_updates} atualizações de aprendizado",
                            {'sent_emails': sent_emails_found, 'updates': learning_updates})
                return True
            else:
                self.log_test("Learning from Sent Emails", "FAIL", 
                            f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Learning from Sent Emails", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_email_classification(self, email_id):
        """Teste de reclassificação de email"""
        try:
            response = self.session.post(f"{self.api_url}/emails/{email_id}/classify", 
                                       timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                classification = data.get('classification', {})
                
                if classification.get('type') and classification.get('confidence'):
                    self.log_test("Email Classification", "PASS", 
                                f"Email classificado como {classification.get('type')}",
                                {'classification': classification})
                    return True
                else:
                    self.log_test("Email Classification", "FAIL", 
                                "Classificação incompleta")
                    return False
            else:
                self.log_test("Email Classification", "FAIL", 
                            f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Email Classification", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_response_editing(self, response_id):
        """Teste de edição de resposta"""
        try:
            payload = {
                "subject": "Assunto Editado - Teste",
                "body_text": "Corpo da resposta editado para teste de funcionalidade."
            }
            response = self.session.put(f"{self.api_url}/emails/responses/{response_id}", 
                                      json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('subject') == payload['subject']:
                    self.log_test("Response Editing", "PASS", 
                                f"Resposta {response_id} editada com sucesso",
                                {'new_subject': data.get('subject')})
                    return True
                else:
                    self.log_test("Response Editing", "FAIL", 
                                "Edição não foi aplicada corretamente")
                    return False
            else:
                self.log_test("Response Editing", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Response Editing", "FAIL", f"Erro: {str(e)}")
            return False
    
    def test_bulk_actions(self, email_ids):
        """Teste de ações em lote"""
        try:
            payload = {
                "email_ids": email_ids[:2],
                "action": "mark_for_response"
            }
            response = self.session.post(f"{self.api_url}/emails/bulk-actions", 
                                       json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                processed = data.get('processed', 0)
                results = data.get('results', [])
                
                self.log_test("Bulk Actions", "PASS", 
                            f"Ação em lote processada para {processed} emails",
                            {'action': payload['action'], 'results': results})
                return True
            else:
                self.log_test("Bulk Actions", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Bulk Actions", "FAIL", f"Erro: {str(e)}")
            return False
    
    def run_complete_test_suite(self):
        """Executa suite completa de testes"""
        print("🚀 Iniciando Testes Completos - Controle Manual de Emails")
        print("=" * 60)
        
        # Testes básicos
        if not self.test_health_check():
            print("❌ Aplicação não está respondendo. Abortando testes.")
            return self.generate_report()
        
        if not self.test_database_connection():
            print("❌ Banco de dados não acessível. Abortando testes.")
            return self.generate_report()
        
        # Teste de listagem e obtenção de emails para testes
        emails = self.test_email_listing()
        if not emails:
            print("⚠️ Nenhum email encontrado. Alguns testes serão pulados.")
            email_ids = []
        else:
            email_ids = [email['id'] for email in emails[:5]]
        
        # Testes de processamento
        self.test_email_processing()
        
        # Testes de controle manual
        if email_ids:
            # Teste individual
            self.test_mark_as_read_individual(email_ids[0])
            
            # Teste em lote
            if len(email_ids) > 1:
                self.test_bulk_mark_as_read(email_ids[1:])
            
            # Teste de classificação
            self.test_email_classification(email_ids[0])
            
            # Teste de geração de resposta
            response_id = self.test_response_generation(email_ids[0])
            
            if response_id:
                # Teste de edição de resposta
                self.test_response_editing(response_id)
                
                # Teste de aprovação
                if self.test_response_approval(response_id):
                    # Teste de criação de rascunho
                    self.test_draft_creation(email_ids[0])
            
            # Teste de ações em lote
            if len(email_ids) > 1:
                self.test_bulk_actions(email_ids)
        
        # Teste de aprendizado
        self.test_learning_from_sent_emails()
        
        return self.generate_report()
    
    def generate_report(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        
        print(f"Total de Testes: {total_tests}")
        print(f"✅ Passou: {passed_tests}")
        print(f"❌ Falhou: {failed_tests}")
        print(f"⚠️ Avisos: {warning_tests}")
        print(f"📈 Taxa de Sucesso: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTES QUE FALHARAM:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"  - {test['test']}: {test['message']}")
        
        if warning_tests > 0:
            print("\n⚠️ TESTES COM AVISOS:")
            for test in self.test_results:
                if test['status'] == 'WARN':
                    print(f"  - {test['test']}: {test['message']}")
        
        # Salvar relatório detalhado
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed_tests,
                    'failed': failed_tests,
                    'warnings': warning_tests,
                    'success_rate': passed_tests/total_tests*100
                },
                'tests': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório detalhado salvo em: {report_file}")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0
        }

if __name__ == "__main__":
    # Configurar URL base se fornecida como argumento
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"🔧 Testando aplicação em: {base_url}")
    
    tester = TestControleManual(base_url)
    results = tester.run_complete_test_suite()
    
    # Exit code baseado nos resultados
    exit_code = 0 if results['failed'] == 0 else 1
    sys.exit(exit_code)
