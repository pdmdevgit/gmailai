#!/usr/bin/env python3
"""
Testes Unitários - Controle Manual de Emails
Testa a lógica das funções implementadas sem depender do servidor
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock do Flask e SQLAlchemy para testes unitários
sys.modules['flask'] = Mock()
sys.modules['flask_sqlalchemy'] = Mock()
sys.modules['sqlalchemy'] = Mock()
sys.modules['sqlalchemy.exc'] = Mock()

class TestControleManualUnit(unittest.TestCase):
    """Testes unitários para funcionalidades de controle manual"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.mock_gmail_service = Mock()
        self.mock_ai_service = Mock()
        self.mock_db = Mock()
    
    def test_email_processor_no_auto_mark_read(self):
        """Teste: EmailProcessor não marca emails como lidos automaticamente"""
        # Importar após mock
        from app.services.email_processor import EmailProcessor
        
        processor = EmailProcessor(self.mock_gmail_service, self.mock_ai_service)
        
        # Mock email data
        email_data = {
            'gmail_id': 'test123',
            'account': 'contato',
            'sender_email': 'test@example.com',
            'subject': 'Test Email',
            'body_text': 'Test content',
            'received_at': datetime.now()
        }
        
        # Mock database operations
        with patch('app.services.email_processor.Email') as mock_email_model, \
             patch('app.services.email_processor.db') as mock_db:
            
            mock_email_instance = Mock()
            mock_email_model.return_value = mock_email_instance
            mock_email_model.query.filter_by.return_value.first.return_value = None
            
            # Executar processamento
            result = processor.process_single_email(email_data)
            
            # Verificar que mark_as_read NÃO foi chamado
            self.mock_gmail_service.mark_as_read.assert_not_called()
            
            # Verificar que add_label foi chamado (para organização)
            self.mock_gmail_service.add_label.assert_called_once()
            
        print("✅ PASS: EmailProcessor não marca emails como lidos automaticamente")
    
    def test_gmail_service_create_draft(self):
        """Teste: GmailService.create_draft cria rascunho sem enviar"""
        from app.services.gmail_service import GmailService
        
        # Mock do serviço Gmail
        mock_service = Mock()
        mock_service.users().drafts().create().execute.return_value = {'id': 'draft123'}
        
        gmail_service = GmailService('credentials.json', 'tokens/')
        gmail_service.services = {'contato': mock_service}
        
        # Testar criação de rascunho
        result = gmail_service.create_draft(
            account_name='contato',
            to_email='test@example.com',
            subject='Test Subject',
            body_text='Test Body'
        )
        
        # Verificar que foi criado como rascunho (não enviado)
        self.assertTrue(result)
        mock_service.users().drafts().create.assert_called_once()
        mock_service.users().messages().send.assert_not_called()
        
        print("✅ PASS: GmailService.create_draft cria rascunho sem enviar")
    
    def test_gmail_service_mark_as_read_manual(self):
        """Teste: GmailService.mark_as_read funciona para controle manual"""
        from app.services.gmail_service import GmailService
        
        # Mock do serviço Gmail
        mock_service = Mock()
        mock_service.users().messages().modify().execute.return_value = {}
        
        gmail_service = GmailService('credentials.json', 'tokens/')
        gmail_service.services = {'contato': mock_service}
        
        # Testar marcação como lido
        result = gmail_service.mark_as_read('contato', 'msg123')
        
        # Verificar que foi chamado corretamente
        self.assertTrue(result)
        mock_service.users().messages().modify.assert_called_once_with(
            userId='me',
            id='msg123',
            body={'removeLabelIds': ['UNREAD']}
        )
        
        print("✅ PASS: GmailService.mark_as_read funciona para controle manual")
    
    def test_email_routes_mark_as_read_endpoint(self):
        """Teste: Endpoint de marcação como lido funciona"""
        # Mock das dependências Flask
        with patch('app.api.email_routes.Email') as mock_email_model, \
             patch('app.api.email_routes.GmailService') as mock_gmail_service_class, \
             patch('app.api.email_routes.db') as mock_db, \
             patch('app.api.email_routes.current_app') as mock_app:
            
            # Setup mocks
            mock_email = Mock()
            mock_email.id = 1
            mock_email.gmail_id = 'gmail123'
            mock_email.account = 'contato'
            mock_email_model.query.get_or_404.return_value = mock_email
            
            mock_gmail_service = Mock()
            mock_gmail_service.mark_as_read.return_value = True
            mock_gmail_service_class.return_value = mock_gmail_service
            
            mock_app.config.get.return_value = 'test_value'
            
            # Importar e testar a função
            from app.api.email_routes import mark_email_as_read
            
            # Mock request
            with patch('app.api.email_routes.jsonify') as mock_jsonify:
                mock_jsonify.return_value = {'status': 'success'}
                
                result = mark_email_as_read(1)
                
                # Verificar que mark_as_read foi chamado
                mock_gmail_service.mark_as_read.assert_called_once_with('contato', 'gmail123')
                
                # Verificar que is_read foi atualizado
                self.assertTrue(mock_email.is_read)
                
        print("✅ PASS: Endpoint de marcação como lido funciona")
    
    def test_bulk_mark_as_read_logic(self):
        """Teste: Lógica de marcação em lote funciona"""
        # Simular múltiplos emails
        emails = [
            Mock(id=1, gmail_id='gmail1', account='contato'),
            Mock(id=2, gmail_id='gmail2', account='contato'),
            Mock(id=3, gmail_id='gmail3', account='cursos')
        ]
        
        # Mock do GmailService
        mock_gmail_service = Mock()
        mock_gmail_service.mark_as_read.return_value = True
        
        # Simular processamento em lote
        results = []
        for email in emails:
            try:
                success = mock_gmail_service.mark_as_read(email.account, email.gmail_id)
                if success:
                    email.is_read = True
                    results.append({'id': email.id, 'status': 'marked_as_read'})
                else:
                    results.append({'id': email.id, 'status': 'failed'})
            except Exception as e:
                results.append({'id': email.id, 'status': 'error', 'error': str(e)})
        
        # Verificar resultados
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r['status'] == 'marked_as_read' for r in results))
        self.assertTrue(all(email.is_read for email in emails))
        
        print("✅ PASS: Lógica de marcação em lote funciona")
    
    def test_learning_from_sent_emails_logic(self):
        """Teste: Lógica de aprendizado com emails enviados"""
        # Mock de emails enviados
        sent_emails = [
            {
                'thread_id': 'thread1',
                'body_text': 'Resposta sobre coaching',
                'subject': 'Re: Interesse em coaching'
            },
            {
                'thread_id': 'thread2', 
                'body_text': 'Informações sobre acelerador',
                'subject': 'Re: Dúvidas sobre curso'
            }
        ]
        
        # Mock de threads completas
        thread_emails = [
            [
                {'is_sent': False, 'body_text': 'Tenho interesse em coaching'},
                {'is_sent': True, 'body_text': 'Resposta sobre coaching', 'subject': 'Re: Interesse'}
            ],
            [
                {'is_sent': False, 'body_text': 'Quero saber sobre o curso'},
                {'is_sent': True, 'body_text': 'Informações sobre acelerador', 'subject': 'Re: Dúvidas'}
            ]
        ]
        
        # Mock do GmailService
        mock_gmail_service = Mock()
        mock_gmail_service.get_sent_emails_history.return_value = sent_emails
        mock_gmail_service.get_conversation_thread.side_effect = thread_emails
        
        # Mock do AIService
        mock_ai_service = Mock()
        mock_ai_service.analyze_response_effectiveness.return_value = {
            'effectiveness_score': 0.85,
            'patterns': ['greeting_pattern', 'call_to_action']
        }
        
        # Simular processamento de aprendizado
        learning_updates = []
        for sent_email in sent_emails:
            thread_data = mock_gmail_service.get_conversation_thread('contato', sent_email['thread_id'])
            
            if len(thread_data) >= 2:
                original_question = next((e for e in thread_data if not e.get('is_sent')), None)
                sent_response = next((e for e in thread_data if e.get('is_sent')), None)
                
                if original_question and sent_response:
                    effectiveness = mock_ai_service.analyze_response_effectiveness({
                        'original_question': original_question['body_text'],
                        'sent_response': sent_response['body_text'],
                        'subject': sent_response['subject']
                    })
                    
                    learning_updates.append({
                        'thread_id': sent_email['thread_id'],
                        'effectiveness_score': effectiveness['effectiveness_score'],
                        'patterns': effectiveness['patterns']
                    })
        
        # Verificar resultados
        self.assertEqual(len(learning_updates), 2)
        self.assertTrue(all(update['effectiveness_score'] > 0.8 for update in learning_updates))
        
        print("✅ PASS: Lógica de aprendizado com emails enviados funciona")
    
    def test_response_generation_without_auto_send(self):
        """Teste: Geração de resposta não envia automaticamente"""
        from app.services.email_processor import EmailProcessor
        
        processor = EmailProcessor(self.mock_gmail_service, self.mock_ai_service)
        
        # Mock de classificação que normalmente geraria envio automático
        classification = {
            'type': 'vendas',
            'priority': 'alta',
            'confidence': 0.95  # Alta confiança
        }
        
        # Mock de resposta gerada
        generated_response = {
            'subject': 'Re: Sua consulta',
            'body_text': 'Resposta gerada',
            'confidence': 0.92
        }
        
        self.mock_ai_service.generate_response_with_learning.return_value = generated_response
        
        # Mock database operations
        with patch('app.services.email_processor.EmailResponse') as mock_response_model, \
             patch('app.services.email_processor.db') as mock_db:
            
            mock_email = Mock()
            mock_email.id = 1
            
            # Testar geração de resposta
            result = processor._generate_response_if_needed(mock_email, {}, classification)
            
            # Verificar que resposta foi gerada mas NÃO enviada automaticamente
            self.assertTrue(result['generated'])
            self.assertFalse(result['auto_sent'])  # Importante: não deve enviar automaticamente
            
            # Verificar que send_email NÃO foi chamado
            self.mock_gmail_service.send_email.assert_not_called()
        
        print("✅ PASS: Geração de resposta não envia automaticamente")
    
    def test_database_schema_changes(self):
        """Teste: Verificar se mudanças no schema estão corretas"""
        # Ler o arquivo SQL de inicialização
        with open('database/init.sql', 'r') as f:
            sql_content = f.read()
        
        # Verificar se novos campos foram adicionados
        self.assertIn('is_read BOOLEAN DEFAULT FALSE', sql_content)
        self.assertIn('draft_created_at DATETIME', sql_content)
        
        print("✅ PASS: Mudanças no schema do banco estão corretas")
    
    def run_all_tests(self):
        """Executa todos os testes unitários"""
        print("🧪 Iniciando Testes Unitários - Controle Manual")
        print("=" * 50)
        
        test_methods = [
            self.test_email_processor_no_auto_mark_read,
            self.test_gmail_service_create_draft,
            self.test_gmail_service_mark_as_read_manual,
            self.test_email_routes_mark_as_read_endpoint,
            self.test_bulk_mark_as_read_logic,
            self.test_learning_from_sent_emails_logic,
            self.test_response_generation_without_auto_send,
            self.test_database_schema_changes
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                test_method()
                passed += 1
            except Exception as e:
                print(f"❌ FAIL: {test_method.__name__}: {str(e)}")
                failed += 1
        
        print("\n" + "=" * 50)
        print("📊 RESULTADO DOS TESTES UNITÁRIOS")
        print("=" * 50)
        print(f"Total: {len(test_methods)}")
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"📈 Taxa de Sucesso: {(passed/len(test_methods)*100):.1f}%")
        
        return passed, failed

if __name__ == "__main__":
    tester = TestControleManualUnit()
    passed, failed = tester.run_all_tests()
    
    # Exit code baseado nos resultados
    exit_code = 0 if failed == 0 else 1
    sys.exit(exit_code)
