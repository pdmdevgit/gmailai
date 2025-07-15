# Troubleshooting Final - Aplicação Não Responde na Porta 5000

## Problema Atual

```bash
curl http://localhost:5000/ping
# Connection refused - aplicação não está respondendo
```

## Diagnóstico Passo a Passo

### 1. Verificar Status dos Containers

```bash
# Ver containers ativos
docker ps

# Ver logs do container web
docker logs web-[CONTAINER_ID]

# Entrar no container para debug
docker exec -it web-[CONTAINER_ID] /bin/bash
```

### 2. Comandos de Debug Específicos

```bash
# Dentro do container web:
ps aux | grep python
netstat -tlnp | grep :5000
curl http://localhost:5000/ping

# Testar se Flask está rodando
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

### 3. Verificar Logs da Aplicação

```bash
# Ver logs detalhados
docker logs --tail 50 web-[CONTAINER_ID]

# Procurar por estas mensagens:
# ✅ "Starting Gmail AI Agent on 0.0.0.0:5000"
# ✅ "Database tables created successfully"
# ✅ "* Running on all addresses (0.0.0.0)"
# ❌ Erros de importação
# ❌ Erros de conexão com banco
```

### 4. Soluções Rápidas

#### Solução 1: Restart do Container
```bash
docker restart web-[CONTAINER_ID]
```

#### Solução 2: Rebuild Completo
```bash
# No diretório do projeto
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Solução 3: Verificar Variáveis de Ambiente
```bash
docker exec web-[CONTAINER_ID] env | grep -E "(FLASK|MYSQL|REDIS)"
```

### 5. Teste Manual da Aplicação

```bash
# Entrar no container
docker exec -it web-[CONTAINER_ID] /bin/bash

# Testar importações
python -c "
try:
    from app import create_app
    print('✅ Import successful')
    app = create_app()
    print('✅ App creation successful')
except Exception as e:
    print('❌ Error:', e)
"

# Testar Flask manualmente
python -c "
from app import create_app
app = create_app()
app.run(host='0.0.0.0', port=5000, debug=True)
"
```

## Possíveis Causas e Soluções

### Causa 1: Erro de Importação
**Sintomas:** Logs mostram ModuleNotFoundError
**Solução:** Verificar se config/__init__.py existe e imports estão corretos

### Causa 2: Banco de Dados Não Conecta
**Sintomas:** Erro de conexão MySQL
**Solução:** 
```bash
# Testar conexão com MySQL
docker exec mysql-[CONTAINER_ID] mysql -u gmail_ai_user -p -e "SELECT 1"
```

### Causa 3: Porta Ocupada
**Sintomas:** Address already in use
**Solução:**
```bash
# Verificar o que está usando a porta
netstat -tlnp | grep :5000
# Matar processo se necessário
```

### Causa 4: Aplicação Não Inicia
**Sintomas:** Container roda mas processo Python não inicia
**Solução:** Verificar CMD no Dockerfile e app.py

## Comandos de Emergência

### Se nada funcionar, teste local:

```bash
# Clonar repo localmente
cd /tmp
git clone https://github.com/pdmdevgit/gmailai.git
cd gmailai

# Testar build
docker-compose build

# Testar localmente
docker-compose up

# Ver se funciona
curl http://localhost:5000/ping
```

## Verificação Final

Quando funcionando, você deve ver:

```bash
# Logs saudáveis:
Starting Gmail AI Agent on 0.0.0.0:5000
Database tables created successfully
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000

# Teste bem-sucedido:
curl http://localhost:5000/ping
{"status": "ok", "timestamp": "2025-01-15T00:30:00.000000"}
```

## Próximos Passos

1. Execute os comandos de diagnóstico acima
2. Identifique a causa específica nos logs
3. Aplique a solução correspondente
4. Teste novamente o acesso
5. Se persistir, faça rebuild completo

## Comandos para Executar Agora

```bash
# 1. Ver containers
docker ps

# 2. Ver logs (substitua CONTAINER_ID)
docker logs web-CONTAINER_ID

# 3. Entrar no container
docker exec -it web-CONTAINER_ID /bin/bash

# 4. Dentro do container, testar
curl http://localhost:5000/ping
ps aux | grep python
