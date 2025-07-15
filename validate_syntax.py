#!/usr/bin/env python3
"""
Script para validar a sintaxe dos arquivos Python corrigidos
"""

import ast
import sys
import os

def validate_python_file(filepath):
    """Valida a sintaxe de um arquivo Python"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check syntax
        ast.parse(content)
        print(f"✅ {filepath}: Sintaxe válida")
        return True
    except SyntaxError as e:
        print(f"❌ {filepath}: Erro de sintaxe - {e}")
        return False
    except Exception as e:
        print(f"❌ {filepath}: Erro - {e}")
        return False

def main():
    """Valida os arquivos corrigidos"""
    print("🔍 Validando sintaxe dos arquivos corrigidos...\n")
    
    files_to_check = [
        'config/__init__.py',
        'config/config.py',
        'app/services/ai_service.py',
        'app/__init__.py'
    ]
    
    results = []
    for filepath in files_to_check:
        if os.path.exists(filepath):
            results.append(validate_python_file(filepath))
        else:
            print(f"⚠️  {filepath}: Arquivo não encontrado")
            results.append(False)
    
    print()
    success_count = sum(results)
    total_count = len(results)
    
    print(f"📊 Resultados: {success_count}/{total_count} arquivos válidos")
    
    if success_count == total_count:
        print("🎉 Todos os arquivos têm sintaxe válida!")
        return 0
    else:
        print("⚠️  Alguns arquivos têm problemas de sintaxe")
        return 1

if __name__ == '__main__':
    sys.exit(main())
