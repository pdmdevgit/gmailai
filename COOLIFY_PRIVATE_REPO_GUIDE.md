# 🔐 Coolify - Configuração de Repositório Privado

## 📋 Informações do Repositório

- **Repositório**: `https://github.com/pdmdevgit/gmailai` (PRIVADO)
- **Plataforma**: GitHub
- **Acesso**: Requer autenticação

## 🔑 Pré-requisitos

### **1. GitHub Personal Access Token**
Você precisará criar um Personal Access Token no GitHub:

1. **Acesse**: https://github.com/settings/tokens
2. **Generate new token** → **Generate new token (classic)**
3. **Note**: "Coolify Gmail AI Agent"
4. **Expiration**: 1 year (ou conforme preferir)
5. **Scopes necessários**:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `user:email` (Access user email addresses)
   - ✅ `read:user` (Read user profile data)

6. **Generate token** e **COPIE O TOKEN** (só aparece uma vez!)

### **2. SSH Key (Alternativa)**
Ou você pode usar SSH Key:

1. **Gerar SSH Key no VPS**:
```bash
ssh-keygen -t ed25519 -C "coolify@gmailai"
cat ~/.ssh/id_ed25519.pub
```

2. **Adicionar no GitHub**:
   - Settings → SSH and GPG keys → New SSH key
   - Cole a chave pública

## 🚀 Configuração Passo-a-Passo no Coolify

### **Passo 1: Acessar Coolify**
```bash
# Conectar ao VPS
ssh root@31.97.84.68

# Acessar Coolify
http://31.97.84.68:8000
```

### **Passo 2: Configurar Source (Git)**

#### **2.1 - Adicionar Source**
1. **Dashboard** → **Sources** → **+ New Source**
2. **Source Type**: `GitHub`
3. **Name**: `GitHub Private`
4. **Description**: `GitHub private repository access`

#### **2.2 - Configurar Autenticação**

**Opção A: Personal Access Token (Recomendado)**
1. **Authentication Type**: `GitHub App` ou `Personal Access Token`
2. **GitHub Personal Access Token**: Cole o token criado
3. **Test Connection** → Deve aparecer "✅ Connected"

**Opção B: SSH Key**
1. **Authentication Type**: `SSH Key`
2. **SSH Private Key**: Cole a chave privada
3. **SSH Public Key**: Cole a chave pública
4. **Test Connection**

### **Passo 3: Criar Projeto**

#### **3.1 - New Project**
1. **Dashboard** → **+ New Project**
2. **Project Name**: `Gmail AI Agent`
3. **Description**: `Sistema de automação Gmail com IA e aprendizado`
4. **Create Project**

#### **3.2 - Add Resource**
1. **+ New Resource** → **Application**
2. **Resource Name**: `gmail-ai-agent`
3. **Source**: Selecionar `GitHub Private` (criado no passo 2)

### **Passo 4: Configurar Repositório**

#### **4.1 - Repository Settings**
1. **Repository**: `pdmdevgit/gmailai`
2. **Branch**: `main`
3. **Build Pack**: `Docker Compose`
4. **Docker Compose File**: `docker-compose.yml` (padrão)
5. **Dockerfile**: `Dockerfile` (padrão)

#### **4.2 - Build Configuration**
```yaml
# Build Settings
Build Command: docker-compose build
Start Command: docker-compose up -d
Port: 5000
Health Check Path: /health
```

### **Passo 5: Configurar Domínio**

#### **5.1 - Domain Settings**
1. **Domains** → **+ Add Domain**
2. **Domain**: `gmailai.devpdm.com`
3. **SSL**: ✅ Enable
4. **Force HTTPS**: ✅ Enable
5. **Let's Encrypt**: ✅ Enable

### **Passo 6: Environment Variables**

#### **6.1 - Adicionar Variáveis**
**Produção**:
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_secreta_super_segura_aqui
```

**Database**:
```env
MYSQL_ROOT_PASSWORD=senha_mysql_muito_segura
MYSQL_DATABASE=gmail_ai_agent
MYSQL_USER=gmail_user
MYSQL_PASSWORD=senha_user_mysql_segura
DATABASE_URL=mysql://gmail_user:senha_user_mysql_segura@db:3306/gmail_ai_agent
```

**APIs** (CONFIGURAR COM SUAS CHAVES):
```env
OPENAI_API_KEY=sk-sua_chave_openai_aqui
ANTHROPIC_API_KEY=sk-sua_chave_anthropic_aqui
AI_MODEL=gpt-4
```

**Gmail API**:
```env
GMAIL_CREDENTIALS_FILE=/app/config/credentials.json
GMAIL_TOKEN_DIR=/app/config/tokens
GMAIL_ACCOUNTS=contato,cursos,diogo,sac
```

**Application**:
```env
DOMAIN=gmailai.devpdm.com
BASE_URL=https://gmailai.devpdm.com
APP_NAME=Gmail AI Agent
LOG_LEVEL=INFO
```

**Learning System**:
```env
LEARNING_ENABLED=true
LEARNING_HISTORY_DAYS=90
LEARNING_MIN_SIMILARITY=0.3
```

**Redis**:
```env
REDIS_URL=redis://redis:6379/0
```

### **Passo 7: Configurar Volumes**

#### **7.1 - Persistent Volumes**
1. **Storages** → **+ Add Storage**
2. **Volumes necessários**:
```yaml
- Name: gmail-config
  Mount Path: /app/config
  Host Path: ./config

- Name: gmail-logs  
  Mount Path: /app/logs
  Host Path: ./logs

- Name: mysql-data
  Mount Path: /var/lib/mysql
  Host Path: ./mysql_data
```

### **Passo 8: Deploy**

#### **8.1 - Primeira Deploy**
1. **Deploy** → **Deploy Now**
2. **Aguardar build** (5-10 minutos)
3. **Verificar logs** em tempo real
4. **Status**: Deve ficar "Running" ✅

#### **8.2 - Configurar Auto-Deploy**
1. **Settings** → **Auto Deploy**
2. **Enable Auto Deploy**: ✅
3. **Branch**: `main`
4. **Webhook**: Coolify criará automaticamente

### **Passo 9: Upload de Arquivos Sensíveis**

#### **9.1 - Gmail Credentials**
1. **File Manager** → **config/**
2. **Upload File** → `credentials.json`
3. **Conteúdo**:
```json
{
  "installed": {
    "client_id": "seu_client_id.apps.googleusercontent.com",
    "project_id": "seu_project_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "seu_client_secret",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

### **Passo 10: Configurar Webhook (Auto-Deploy)**

#### **10.1 - GitHub Webhook**
1. **GitHub** → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `https://coolify.seu-dominio.com/webhooks/github/pdmdevgit/gmailai`
3. **Content type**: `application/json`
4. **Secret**: (Coolify fornecerá)
5. **Events**: `Just the push event`
6. **Active**: ✅

## 🧪 Verificação Pós-Deploy

### **Testes Essenciais**
```bash
# 1. Health check geral
curl https://gmailai.devpdm.com/health

# 2. Health check do learning
curl https://gmailai.devpdm.com/api/learning/health

# 3. Dashboard
curl https://gmailai.devpdm.com/

# 4. Verificar logs
# Via Coolify interface: Logs → Real-time
```

### **Verificar Containers**
```bash
# SSH no VPS
ssh root@31.97.84.68

# Verificar containers
docker ps | grep gmail

# Logs específicos
docker logs gmail-ai-agent-app-1
docker logs gmail-ai-agent-db-1
docker logs gmail-ai-agent-redis-1
```

## 🔐 Segurança do Repositório Privado

### **Vantagens do Repo Privado**:
- ✅ **Código protegido**: Não visível publicamente
- ✅ **Credenciais seguras**: Environment variables não expostas
- ✅ **Controle de acesso**: Apenas usuários autorizados
- ✅ **Histórico privado**: Commits e mudanças privadas

### **Boas Práticas**:
- 🔑 **Rotate tokens**: Renovar Personal Access Token periodicamente
- 🔒 **Minimal permissions**: Usar apenas scopes necessários
- 📝 **Audit logs**: Monitorar acessos no GitHub
- 🚫 **Never commit secrets**: Usar apenas environment variables

## 🚨 Troubleshooting

### **Problemas Comuns**:

#### **1. ❌ ERRO: "Remote branch main not found in upstream origin"**
**Causa**: Repositório não existe ou não foi configurado corretamente.

**Solução**: 
📖 **Consulte o guia completo**: `GITHUB_REPO_SETUP.md`

**Passos rápidos**:
1. Criar repositório `https://github.com/pdmdevgit/gmailai`
2. Upload do código completo
3. Verificar branch `main` existe
4. Reconfigurar Coolify com novo token

#### **2. Authentication Failed**
```bash
# Verificar token
# GitHub → Settings → Personal access tokens
# Verificar se token não expirou
```

#### **3. Repository Not Found**
```bash
# Verificar se usuário tem acesso ao repo
# Verificar se repo name está correto: pdmdevgit/gmailai
```

#### **4. Build Failed**
```bash
# Verificar logs no Coolify
# Verificar se Dockerfile está correto
# Verificar se docker-compose.yml está válido
```

#### **5. Deploy Failed**
```bash
# Verificar environment variables
# Verificar se portas estão corretas
# Verificar volumes e permissões
```

## ✅ Checklist Final

### **Pré-Deploy**:
- ✅ Personal Access Token criado
- ✅ Source configurado no Coolify
- ✅ Projeto criado
- ✅ Repositório privado conectado
- ✅ Environment variables configuradas

### **Deploy**:
- ✅ Build bem-sucedido
- ✅ Containers rodando
- ✅ SSL ativo
- ✅ Domínio funcionando
- ✅ Health checks passando

### **Pós-Deploy**:
- ✅ Auto-deploy configurado
- ✅ Webhook ativo
- ✅ Arquivos sensíveis uploaded
- ✅ Gmail API configurada
- ✅ Learning system ativo

## 🎉 Resultado Final

Após seguir este guia:

- ✅ **Repositório privado** `https://github.com/pdmdevgit/gmailai` conectado
- ✅ **Deploy automático** configurado
- ✅ **Segurança máxima** com credenciais protegidas
- ✅ **Sistema operacional** em `https://gmailai.devpdm.com`
- ✅ **Learning system** analisando histórico de emails

**🔐 Seu código permanece PRIVADO e SEGURO enquanto o sistema funciona perfeitamente!**
