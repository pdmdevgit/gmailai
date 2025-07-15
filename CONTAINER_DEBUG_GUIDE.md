# Diagnóstico de Container - Aplicação Não Responde

## Situação Atual Identificada

### ✅ **O que está funcionando:**
- Docker-proxy escutando na porta 5000: `tcp 0.0.0.0:5000 LISTEN 660630/docker-proxy`
- Firewall desabilitado (não é problema de firewall)
- Iptables permitindo tráfego Docker

### ❌ **O problema:**
- Aplicação dentro do container não está respondendo
- `curl http://localhost:5000/ping` falha

## Comandos de Diagnóstico

### 1. Verificar Status dos Containers

```bash
# Ver todos os containers
docker ps -a

# Ver containers do projeto específico
docker ps -a | grep gmail

# Ver logs do container web
docker logs container_name_web
```

### 2. Entrar no Container para Debug

```bash
# Encontrar o nome do container web
docker ps | grep web

# Entrar no container
docker exec -it container_name_web /bin/bash

# Dentro do container, verificar se a aplicação está rodando
ps aux | grep python
netstat -tlnp | grep :5000
curl http://localhost:5000/ping
```

### 3. Verificar Logs Detalhados

```bash
# Logs em tempo real
docker logs -f container_name_web

# Últimas 100 linhas
docker logs --tail 100 container_name_web

# Logs com timestamp
docker logs -t container_name_web
```

## Possíveis Problemas e Soluções

### **Problema 1: Aplicação não iniciou**

**Sintomas:**
```bash
docker logs container_name_web
# Mostra erros de importação ou falha na inicialização
```

**Solução:**
```bash
# Reiniciar o container
docker restart container_name_web

# Ou recriar completamente
docker-compose down
docker-compose up -d
```

### **Problema 2: Aplicação travou/crashou**

**Sintomas:**
```bash
docker ps -a
# Container com status "Exited" ou "Restarting"
```

**Solução:**
```bash
# Ver por que parou
docker logs container_name_web

# Reiniciar
docker start container_name_web
```

### **Problema 3: Aplicação rodando mas não escutando**

**Sintomas:**
```bash
# Dentro do container:
ps aux | grep python  # Processo existe
netstat -tlnp | grep :5000  # Mas não escuta na porta
```

**Solução:**
Verificar se Flask está configurado para escutar em 0.0.0.0:5000

### **Problema 4: Dependências não instaladas**

**Sintomas:**
```bash
docker logs container_name_web
# ModuleNotFoundError ou ImportError
```

**Solução:**
```bash
# Reconstruir a imagem
docker-compose build --no-cache web
docker-compose up -d
```

## Comandos Específicos para seu Caso

### 1. Identificar o Container Web

```bash
# Listar containers do Coolify
docker ps | grep -E "(web|gmail|ai)"

# Exemplo de saída esperada:
# abc123_web_456  gmail-ai-agent_web  "python app.py"  Up 10 minutes  0.0.0.0:5000->5000/tcp
```

### 2. Verificar Logs da Aplicação

```bash
# Substitua CONTAINER_NAME pelo nome real
docker logs CONTAINER_NAME_WEB

# Procure por estas mensagens:
# ✅ "Starting Gmail AI Agent on 0.0.0.0:5000"
# ✅ "Database tables created successfully"
# ✅ "* Running on all addresses (0.0.0.0)"
# ❌ Erros de importação
# ❌ Erros de conexão com banco
```

### 3. Testar Dentro do Container

```bash
# Entrar no container
docker exec -it CONTAINER_NAME_WEB /bin/bash

# Dentro do container:
curl http://localhost:5000/ping
curl http://127.0.0.1:5000/ping

# Verificar se Flask está rodando
ps aux | grep python
netstat -tlnp | grep :5000
```

### 4. Verificar Variáveis de Ambiente

```bash
# Ver variáveis do container
docker exec CONTAINER_NAME_WEB env | grep -E "(FLASK|MYSQL|REDIS)"

# Deve mostrar:
# FLASK_APP=app
# FLASK_RUN_HOST=0.0.0.0
# FLASK_RUN_PORT=5000
# MYSQL_HOST=mysql
# etc.
```

## Soluções Rápidas

### **Solução 1: Restart Completo**

```bash
# No diretório do projeto
cd /path/to/gmail-ai-agent

# Parar tudo
docker-compose down

# Reconstruir e subir
docker-compose build --no-cache
docker-compose up -d

# Verificar logs
docker-compose logs -f web
```

### **Solução 2: Verificar Health Checks**

```bash
# Ver status de saúde dos containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Se algum estiver "unhealthy", verificar logs
docker logs container_name
```

### **Solução 3: Testar Conectividade de Rede**

```bash
# Verificar se containers estão na mesma rede
docker network ls
docker network inspect network_name

# Testar conectividade entre containers
docker exec container_mysql ping container_web
docker exec container_web ping container_mysql
```

## Comandos de Debug Avançado

### **1. Verificar Processo Python**

```bash
# Dentro do container
docker exec -it CONTAINER_NAME_WEB /bin/bash

# Ver processos Python
ps aux | grep python

# Ver portas abertas
netstat -tlnp

# Testar aplicação diretamente
python -c "
import requests
try:
    r = requests.get('http://localhost:5000/ping')
    print('Status:', r.status_code)
    print('Response:', r.text)
except Exception as e:
    print('Error:', e)
"
```

### **2. Verificar Configuração Flask**

```bash
# Dentro do container
docker exec -it CONTAINER_NAME_WEB python -c "
import os
print('FLASK_APP:', os.environ.get('FLASK_APP'))
print('FLASK_RUN_HOST:', os.environ.get('FLASK_RUN_HOST'))
print('FLASK_RUN_PORT:', os.environ.get('FLASK_RUN_PORT'))
"
```

### **3. Testar Importações**

```bash
# Dentro do container
docker exec -it CONTAINER_NAME_WEB python -c "
try:
    from app import create_app
    print('✅ Import successful')
    app = create_app()
    print('✅ App creation successful')
except Exception as e:
    print('❌ Error:', e)
"
```

## Próximos Passos

1. **Execute os comandos de diagnóstico** acima
2. **Copie os logs** do container web
3. **Identifique o erro específico** nos logs
4. **Aplique a solução correspondente**
5. **Teste novamente** o acesso

## Exemplo de Logs Saudáveis

Quando funcionando corretamente, você deve ver:

```
Starting Gmail AI Agent on 0.0.0.0:5000
Database tables created successfully
Initial templates seeded successfully
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.18.0.3:5000
```

## Comandos para Executar Agora

```bash
# 1. Ver containers ativos
docker ps

# 2. Ver logs do container web (substitua o nome)
docker logs NOME_DO_CONTAINER_WEB

# 3. Se necessário, reiniciar
docker restart NOME_DO_CONTAINER_WEB

# 4. Testar novamente
curl http://localhost:5000/ping
