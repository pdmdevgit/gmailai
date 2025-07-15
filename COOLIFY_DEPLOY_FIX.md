# Coolify Deploy Fix - Aplicação Não Está Rodando

## Problema Identificado

### ❌ **Situação Atual:**
```bash
docker ps | grep -E "(web|gmail|ai)"
19fce829bfc9   ghcr.io/coollabsio/coolify-helper:1.0.8
```

**Apenas o `coolify-helper` está rodando, não a aplicação Gmail AI Agent!**

### ✅ **O que deveria estar rodando:**
```bash
# Containers esperados:
gmail_ai_web     - Aplicação principal
gmail_ai_mysql   - Banco de dados
gmail_ai_redis   - Cache
gmail_ai_monitor - Monitor de emails
```

## Diagnóstico e Correção

### 1. Verificar Status no Painel Coolify

**Acesse o painel do Coolify e verifique:**

1. **Status do Deploy:**
   - Vá para seu projeto Gmail AI Agent
   - Verifique se o deploy foi concluído com sucesso
   - Procure por mensagens de erro

2. **Logs do Deploy:**
   - Clique em "Logs" ou "Build Logs"
   - Procure por erros de build ou deploy
   - Anote qualquer erro encontrado

### 2. Comandos de Verificação no VPS

```bash
# Ver todos os containers (não apenas os ativos)
docker ps -a

# Ver containers parados/com erro
docker ps -a --filter "status=exited"

# Ver logs do sistema Docker
journalctl -u docker --since "1 hour ago"

# Ver uso de recursos
docker system df
docker system prune -f  # Se necessário limpar
```

### 3. Verificar Configuração do Coolify

#### **A. Verificar Arquivo de Configuração**

No painel do Coolify, verifique se está usando:
- **Source:** GitHub repository correto
- **Branch:** main
- **Build Pack:** Docker ou Docker Compose
- **Dockerfile:** Presente e correto

#### **B. Verificar Variáveis de Ambiente**

Certifique-se de que estas variáveis estão configuradas no Coolify:

```env
# Obrigatórias
MYSQL_ROOT_PASSWORD=gmail_ai_root_pass
MYSQL_PASSWORD=gmail_ai_pass
MYSQL_USER=gmail_ai_user
MYSQL_DB=gmail_ai_agent
REDIS_PASSWORD=gmail_ai_redis_pass
SECRET_KEY=your-secret-key-here

# Opcionais (mas recomendadas)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
FLASK_ENV=production
```

### 4. Soluções Específicas

#### **Solução 1: Redeploy Completo**

1. **No painel do Coolify:**
   - Vá para "Settings" do projeto
   - Clique em "Redeploy" ou "Force Redeploy"
   - Aguarde o processo completo

2. **Verificar logs durante o deploy:**
   - Acompanhe os logs em tempo real
   - Anote qualquer erro que aparecer

#### **Solução 2: Verificar Configuração Docker Compose**

O Coolify deve estar usando o `docker-compose.yml`. Verifique se:

1. **Arquivo está na raiz do repositório** ✅
2. **Sintaxe está correta** ✅
3. **Portas estão mapeadas corretamente** ✅

#### **Solução 3: Deploy Manual para Teste**

Se o Coolify não estiver funcionando, teste manualmente:

```bash
# Clonar o repositório
cd /tmp
git clone https://github.com/pdmdevgit/gmailai.git
cd gmailai

# Testar build local
docker-compose build

# Testar deploy local
docker-compose up -d

# Verificar se funciona
docker ps
curl http://localhost:5000/ping
```

### 5. Problemas Comuns e Soluções

#### **Problema A: Build Falha**

**Sintomas:** Logs mostram erro durante build
```
ERROR: failed to solve: failed to read dockerfile
```

**Solução:**
- Verificar se Dockerfile está na raiz
- Verificar sintaxe do Dockerfile
- Verificar se requirements.txt existe

#### **Problema B: Dependências Faltando**

**Sintomas:** 
```
ModuleNotFoundError during build
Package not found
```

**Solução:**
- Verificar requirements.txt
- Rebuild com --no-cache

#### **Problema C: Porta Não Exposta**

**Sintomas:** Container roda mas não aceita conexões

**Solução:**
- Verificar EXPOSE 5000 no Dockerfile ✅
- Verificar ports no docker-compose.yml ✅
- Verificar FLASK_RUN_HOST=0.0.0.0 ✅

#### **Problema D: Variáveis de Ambiente**

**Sintomas:** Aplicação inicia mas falha ao conectar banco

**Solução:**
- Configurar todas as variáveis no Coolify
- Verificar nomes das variáveis
- Testar conexão com banco

### 6. Comandos de Debug Específicos

```bash
# 1. Ver todos os containers do sistema
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# 2. Ver redes Docker
docker network ls

# 3. Ver volumes Docker
docker volume ls

# 4. Ver logs do Docker daemon
sudo journalctl -u docker --since "30 minutes ago"

# 5. Verificar espaço em disco
df -h
docker system df
```

### 7. Configuração Correta no Coolify

#### **Configurações Recomendadas:**

1. **General Settings:**
   - Name: Gmail AI Agent
   - Source: GitHub
   - Repository: pdmdevgit/gmailai
   - Branch: main

2. **Build Settings:**
   - Build Pack: Docker Compose
   - Docker Compose File: docker-compose.yml
   - Build Command: (deixar vazio)

3. **Environment Variables:**
   ```
   MYSQL_ROOT_PASSWORD=gmail_ai_root_pass
   MYSQL_PASSWORD=gmail_ai_pass
   MYSQL_USER=gmail_ai_user
   MYSQL_DB=gmail_ai_agent
   REDIS_PASSWORD=gmail_ai_redis_pass
   SECRET_KEY=change-this-secret-key-123
   FLASK_ENV=production
   ```

4. **Port Configuration:**
   - Container Port: 5000
   - Public Port: 5000 (ou automático)
   - Protocol: HTTP

### 8. Verificação Final

Após aplicar as correções, você deve ver:

```bash
docker ps
# Saída esperada:
CONTAINER ID   IMAGE                    COMMAND                  STATUS
abc123         gmail-ai-agent_web       "python app.py"          Up 2 minutes
def456         mysql:8.0                "docker-entrypoint.s…"   Up 2 minutes
ghi789         redis:7-alpine           "docker-entrypoint.s…"   Up 2 minutes
```

### 9. Próximos Passos

1. **Acesse o painel do Coolify**
2. **Verifique os logs de deploy**
3. **Configure as variáveis de ambiente**
4. **Faça um redeploy completo**
5. **Acompanhe os logs durante o deploy**
6. **Teste o acesso após deploy bem-sucedido**

### 10. Comandos para Executar Agora

```bash
# 1. Ver status completo dos containers
docker ps -a

# 2. Ver logs recentes do Docker
sudo journalctl -u docker --since "1 hour ago" | tail -50

# 3. Verificar espaço em disco
df -h

# 4. Limpar containers antigos se necessário
docker system prune -f
```

## Resumo

**O problema é que o Coolify não está fazendo deploy da aplicação corretamente. Apenas o helper está rodando, não os containers da aplicação Gmail AI Agent.**

**Siga os passos acima para diagnosticar e corrigir o problema no painel do Coolify.**
