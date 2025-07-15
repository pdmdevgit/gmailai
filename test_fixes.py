#!/usr/bin/env python3
"""
Script para testar as correções implementadas
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_import():
    """Testa se o config pode ser importado corretamente"""
    try:
        from config.config import config
        print("✅ Config import: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ Config import: FAILED - {e}")
        return False

def test_openai_import():
    """Testa se o OpenAI pode ser importado corretamente"""
    try:
        from openai import OpenAI
        print("✅ OpenAI import: SUCCESS")
        return True
    except ImportError as e:
        print(f"❌ OpenAI import: FAILED - {e}")
        return False

def test_ai_service_init():
    """Testa se o AIService pode ser inicializado"""
    try:
        from app.services.ai_service import AIService
        
        # Test without API keys (should not fail)
        ai_service = AIService()
        print("✅ AIService initialization: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ AIService initialization: FAILED - {e}")
        return False

def test_logging_setup():
    """Testa se o logging pode ser configurado"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Test logging setup
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        logger = logging.getLogger('test')
        logger.info("Test log message")
        print("✅ Logging setup: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Logging setup: FAILED - {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🔍 Testando correções implementadas...\n")
    
    tests = [
        test_config_import,
        test_openai_import,
        test_ai_service_init,
        test_logging_setup
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"📊 Resultados: {success_count}/{total_count} testes passaram")
    
    if success_count == total_count:
        print("🎉 Todas as correções estão funcionando!")
        return 0
    else:
        print("⚠️  Algumas correções precisam de ajustes")
        return 1

if __name__ == '__main__':
    sys.exit(main())
