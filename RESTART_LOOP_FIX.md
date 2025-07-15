# Fix para Container em Loop de Restart - Exit Code 1

## Problema Identificado

```bash
c9cfed9f3516   ls0o44kswc4w8s440skkk04s-monitor   Restarting (1) 29 seconds ago
46e744149824   ls0o44kswc4w8s440skkk04s-web       Restarting (1) 28 seconds ago
```

**Status:** Containers web e monitor estão crashando e reiniciando continuamente com exit code 1.

## Diagnóstico Imediato

### 1. Ver Logs dos Containers

```bash
# Ver logs do container web
docker logs web-ls0o44kswc4w8s440skkk04s-004519754216

# Ver logs do container monitor
docker logs monitor-ls0o44kswc4w8s440skkk04s-004519768374

# Ver logs em tempo real
docker logs -f web-ls0o44kswc4w8s440skkk04s-004519754216
```

### 2. Possíveis Causas do Exit Code 1

#### **Causa A: Erro de Importação**
```python
ModuleNotFoundError: No module named 'config.config'
ImportError: cannot import name 'create_app'
```

#### **Causa B: Erro de Conexão com Banco**
```python
mysql.connector.errors.DatabaseError: 2003 (HY000): Can't connect to MySQL server
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError)
```

#### **Causa C: Dependências Faltando**
```python
ModuleNotFoundError: No module named 'flask'
ModuleNotFoundError: No module named 'pymysql'
```

#### **Causa D: Erro de Configuração**
```python
KeyError: 'SECRET_KEY'
ValueError: Invalid configuration
```

## Soluções por Causa

### **Solução A: Erro de Importação**

```bash
# Entrar no container (quando não estiver crashando)
docker exec -it web-ls0o44kswc4w8s440skkk04s-004519754216 /bin/bash

# Testar importações
python -c "
import sys
sys.path.insert(0, '/app')
try:
    from config.config import config
    print('✅ Config import OK')
except Exception as e:
    print('❌ Config error:', e)

try:
    from app import create_app
    print('✅ App import OK')
except Exception as e:
    print('❌ App error:', e)
"
```

### **Solução B: Erro de Banco**

```bash
# Testar conexão MySQL
docker exec mysql-ls0o44kswc4w8s440skkk04s-004519743068 mysql -u gmail_ai_user -p -e "SELECT 1"

# Verificar se banco existe
docker exec mysql-ls0o44kswc4w8s440skkk04s-004519743068 mysql -u root -p -e "SHOW DATABASES"

# Verificar variáveis de ambiente
docker exec web-ls0o44kswc4w8s440skkk04s-004519754216 env | grep MYSQL
```

### **Solução C: Dependências**

```bash
# Rebuild com cache limpo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### **Solução D: Configuração**

```bash
# Verificar variáveis de ambiente no Coolify
# Adicionar no painel:
SECRET_KEY=your-secret-key-here-123456789
MYSQL_HOST=mysql
MYSQL_USER=gmail_ai_user
MYSQL_PASSWORD=gmail_ai_pass
MYSQL_DB=gmail_ai_agent
```

## Comandos de Debug Específicos

### **1. Capturar Logs Completos**

```bash
# Logs dos últimos 100 linhas
docker logs --tail 100 web-ls0o44kswc4w8s440skkk04s-004519754216 > web_logs.txt
docker logs --tail 100 monitor-ls0o44kswc4w8s440skkk04s-004519768374 > monitor_logs.txt

# Ver logs com timestamp
docker logs -t web-ls0o44kswc4w8s440skkk04s-004519754216
```

### **2. Testar Aplicação Manualmente**

```bash
# Parar containers problemáticos
docker stop web-ls0o44kswc4w8s440skkk04s-004519754216
docker stop monitor-ls0o44kswc4w8s440skkk04s-004519768374

# Rodar manualmente para debug
docker run -it --rm \
  --network container:mysql-ls0o44kswc4w8s440skkk04s-004519743068 \
  ls0o44kswc4w8s440skkk04s-web \
  /bin/bash

# Dentro do container, testar:
python app.py
```

### **3. Verificar Dependências**

```bash
# Entrar no container
docker run -it --rm ls0o44kswc4w8s440skkk04s-web /bin/bash

# Verificar Python e dependências
python --version
pip list | grep -E "(flask|mysql|redis|openai)"

# Testar imports críticos
python -c "
import flask
import pymysql
import redis
import openai
print('✅ All imports OK')
"
```

## Soluções Rápidas

### **Solução 1: Restart com Logs**

```bash
# Parar tudo
docker-compose down

# Subir apenas MySQL e Redis primeiro
docker-compose up -d mysql redis

# Aguardar 30 segundos
sleep 30

# Subir web com logs
docker-compose up web
# (Ctrl+C para parar e ver logs)
```

### **Solução 2: Rebuild Completo**

```bash
# Limpar tudo
docker-compose down -v
docker system prune -f

# Rebuild
docker-compose build --no-cache

# Subir novamente
docker-compose up -d
```

### **Solução 3: Verificar Dockerfile**

Verificar se o Dockerfile tem:
```dockerfile
# Instalar dependências
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# Comando correto
CMD ["python", "app.py"]
```

## Comandos para Executar Agora

```bash
# 1. Ver logs detalhados (EXECUTE ESTE PRIMEIRO)
docker logs web-ls0o44kswc4w8s440skkk04s-004519754216

# 2. Ver logs do monitor
docker logs monitor-ls0o44kswc4w8s440skkk04s-004519768374

# 3. Verificar conexão MySQL
docker exec mysql-ls0o44kswc4w8s440skkk04s-004519743068 mysql -u root -p -e "SHOW DATABASES"

# 4. Se necessário, rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## O Que Procurar nos Logs

### **✅ Logs Saudáveis:**
```
Starting Gmail AI Agent on 0.0.0.0:5000
Database tables created successfully
* Running on all addresses (0.0.0.0)
```

### **❌ Logs com Problema:**
```
ModuleNotFoundError: No module named 'config'
mysql.connector.errors.DatabaseError
ImportError: cannot import name 'create_app'
KeyError: 'SECRET_KEY'
```

## Próximo Passo

**EXECUTE AGORA:**
```bash
docker logs web-ls0o44kswc4w8s440skkk04s-004519754216
```

Copie a saída completa para identificar a causa exata do crash.
