# 🚀 Guia Rápido de Deploy - Gmail AI Agent

## 📋 Informações do Deploy

### **Servidor**
- **IP**: `31.97.84.68`
- **Domínio**: `gmailai.devpdm.com` ✅ (DNS configurado)
- **Painel**: Coolify (recomendado)

## ⚡ Deploy em 5 Passos

### **1. Conectar ao VPS e Instalar Coolify**
```bash
# Conectar ao servidor
ssh root@31.97.84.68

# Instalar Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Aguardar instalação (5-10 minutos)
```

### **2. Acessar Coolify**
- URL: `http://31.97.84.68:8000`
- Criar conta admin
- Configurar servidor local

### **3. Configurar Source (Repositório Privado)**
⚠️ **IMPORTANTE**: O repositório é PRIVADO - requer autenticação!

1. **Sources** → **+ New Source**
2. **Source Type**: `GitHub`
3. **Name**: `GitHub Private`
4. **Authentication**: Personal Access Token
5. **GitHub Token**: Cole seu Personal Access Token
6. **Test Connection** → ✅ Deve conectar

📖 **Para instruções detalhadas**: Consulte `COOLIFY_PRIVATE_REPO_GUIDE.md`

### **4. Criar Projeto no Coolify**
1. **New Project** → "Gmail AI Agent"
2. **Add Resource** → "Application"
3. **Source**: Selecionar `GitHub Private` (criado acima)
4. **Repository**: `pdmdevgit/gmailai`
5. **Branch**: `main`
6. **Build Pack**: Docker Compose

### **5. Configurar Environment Variables**
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_secreta_aqui

# Database
MYSQL_ROOT_PASSWORD=senha_mysql_segura
MYSQL_DATABASE=gmail_ai_agent
MYSQL_USER=gmail_user
MYSQL_PASSWORD=senha_user_mysql

# APIs
OPENAI_API_KEY=sk-sua_chave_openai
ANTHROPIC_API_KEY=sk-sua_chave_anthropic

# Gmail
GMAIL_CREDENTIALS_FILE=/app/config/credentials.json
GMAIL_TOKEN_DIR=/app/config/tokens

# Domain
DOMAIN=gmailai.devpdm.com
BASE_URL=https://gmailai.devpdm.com

# Learning
LEARNING_ENABLED=true
LEARNING_HISTORY_DAYS=90
```

### **6. Configurar Domínio e Deploy**
1. **Domains**: Adicionar `gmailai.devpdm.com`
2. **SSL**: Ativar Let's Encrypt
3. **Deploy**: Fazer primeiro deploy
4. **Upload**: Adicionar `credentials.json` via Coolify

## 🔧 Configurações Importantes

### **Volumes Necessários**
- `./config:/app/config` - Credenciais Gmail
- `./logs:/app/logs` - Logs da aplicação

### **Portas**
- **App**: 5000
- **MySQL**: 3306
- **Redis**: 6379
- **Nginx**: 80, 443

### **Health Checks**
- **App**: `GET /health`
- **Learning**: `GET /api/learning/health`

## 📁 Arquivos para Upload

### **1. credentials.json**
```json
{
  "installed": {
    "client_id": "seu_client_id.apps.googleusercontent.com",
    "project_id": "seu_project_id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "seu_client_secret"
  }
}
```

### **2. .env (via Coolify Environment Variables)**
- Configurar todas as variáveis listadas acima
- Não fazer upload do arquivo .env diretamente

## 🧪 Testes Pós-Deploy

### **1. Verificar Aplicação**
```bash
# Health check geral
curl https://gmailai.devpdm.com/health

# Health check do learning
curl https://gmailai.devpdm.com/api/learning/health

# Dashboard
curl https://gmailai.devpdm.com/
```

### **2. Testar APIs**
```bash
# Stats do learning
curl https://gmailai.devpdm.com/api/learning/stats

# Análise de conta (após autenticação Gmail)
curl https://gmailai.devpdm.com/api/learning/analyze/diogo
```

### **3. Verificar Logs**
- Acessar logs via Coolify interface
- Verificar conexão com MySQL
- Verificar conexão com Redis

## 🔐 Configuração Gmail API

### **Após Deploy Inicial:**

1. **Acessar container**:
```bash
# Via Coolify terminal ou SSH
docker exec -it gmail-ai-agent-app-1 bash
```

2. **Executar autenticação**:
```bash
cd /app
python3 -c "
from app.services.gmail_service import GmailService
gmail = GmailService('/app/config/credentials.json', '/app/config/tokens/')
gmail.authenticate_account('contato@profdiogomoreira.com.br')
"
```

3. **Repetir para todas as contas**:
- `contato@profdiogomoreira.com.br`
- `cursos@profdiogomoreira.com.br`
- `diogo@profdiogomoreira.com.br`
- `sac@profdiogomoreira.com.br`

## 📊 URLs Importantes

### **Aplicação**
- **Dashboard**: https://gmailai.devpdm.com
- **API Health**: https://gmailai.devpdm.com/health
- **Learning Health**: https://gmailai.devpdm.com/api/learning/health

### **Coolify Admin**
- **Panel**: http://31.97.84.68:8000

### **Monitoramento**
- **Logs**: Via Coolify interface
- **Metrics**: Via Coolify dashboard
- **Alerts**: Configurar email notifications

## 🚨 Troubleshooting

### **Problemas Comuns**

#### **1. SSL Certificate Error**
```bash
# Verificar DNS
nslookup gmailai.devpdm.com
# Deve retornar: 31.97.84.68

# Forçar renovação SSL no Coolify
```

#### **2. Database Connection Error**
```bash
# Verificar MySQL container
docker ps | grep mysql
docker logs gmail-ai-agent-db-1
```

#### **3. Gmail API Authentication**
```bash
# Verificar credentials.json
ls -la /app/config/
cat /app/config/credentials.json

# Verificar tokens
ls -la /app/config/tokens/
```

#### **4. Learning System Not Working**
```bash
# Verificar dependências NLP
pip list | grep -E "(nltk|textblob|scikit)"

# Testar learning service
curl https://gmailai.devpdm.com/api/learning/stats
```

## ✅ Checklist Final

### **Pré-Deploy**
- ✅ DNS configurado: `gmailai.devpdm.com` → `31.97.84.68`
- ✅ Coolify instalado no VPS
- ✅ Repositório Git configurado
- ✅ Chaves API obtidas (OpenAI/Anthropic)
- ✅ Gmail API credentials.json criado

### **Deploy**
- ⏳ Projeto criado no Coolify
- ⏳ Environment variables configuradas
- ⏳ Domínio e SSL configurados
- ⏳ Deploy realizado com sucesso

### **Pós-Deploy**
- ⏳ Health checks passando
- ⏳ Gmail API autenticada (4 contas)
- ⏳ Learning system funcionando
- ⏳ Dashboard acessível
- ⏳ Monitoramento configurado

## 🎉 Resultado Final

Após completar todos os passos:

- ✅ **Sistema funcionando**: https://gmailai.devpdm.com
- ✅ **Learning ativo**: Analisando histórico de emails
- ✅ **4 contas Gmail**: Monitoradas automaticamente
- ✅ **IA integrada**: Gerando respostas inteligentes
- ✅ **Dashboard operacional**: Interface web completa

**🚀 Gmail AI Agent estará OPERACIONAL e APRENDENDO com seu histórico de emails!**
