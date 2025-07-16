#!/usr/bin/env python3
"""
Debug da API de templates
"""

import requests
import json

def test_templates_api():
    """Testar API de templates"""
    base_url = "https://gmailai.devpdm.com"
    
    print("🔍 TESTANDO API DE TEMPLATES")
    print("=" * 50)
    
    # Teste 1: GET templates
    print("\n1. Testando GET /api/templates/")
    try:
        response = requests.get(f"{base_url}/api/templates/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Templates encontrados: {len(data.get('templates', []))}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: POST criar template
    print("\n2. Testando POST /api/templates/ (criar template)")
    try:
        template_data = {
            "name": "teste_debug",
            "category": "teste",
            "subject_template": "Teste Debug",
            "body_template": "Este é um template de teste criado via debug",
            "variables": ["nome"],
            "is_active": True
        }
        
        response = requests.post(
            f"{base_url}/api/templates/", 
            json=template_data,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 201:
            print("✅ Template criado com sucesso!")
        else:
            print(f"❌ Erro ao criar: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: GET categories
    print("\n3. Testando GET /api/templates/categories")
    try:
        response = requests.get(f"{base_url}/api/templates/categories", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Categorias: {data.get('categories', [])}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 4: GET stats
    print("\n4. Testando GET /api/templates/stats")
    try:
        response = requests.get(f"{base_url}/api/templates/stats", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats: {data}")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TESTE CONCLUÍDO")

if __name__ == '__main__':
    test_templates_api()
