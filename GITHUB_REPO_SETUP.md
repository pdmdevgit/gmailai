# 🔧 Configuração do Repositório GitHub

## ❌ Problema Identificado

**Erro no Coolify**: `fatal: Remote branch main not found in upstream origin`

**Causa**: O repositório `https://github.com/pdmdevgit/gmailai` ainda não existe ou não foi configurado corretamente.

## 🚀 Solução: Criar e Configurar o Repositório

### **Passo 1: Criar Repositório no GitHub**

#### **1.1 - Acessar GitHub**
1. **Login**: https://github.com/pdmdevgit
2. **New Repository** → **Create a new repository**

#### **1.2 - Configurar Repositório**
```
Repository name: gmailai
Description: Gmail AI Agent with Learning System for Prof. Diogo Moreira
Visibility: ✅ Private
Initialize: ✅ Add a README file
Add .gitignore: Python
Add a license: MIT License (opcional)
```

3. **Create repository**

### **Passo 2: Upload do Código**

#### **2.1 - Clone do Repositório**
```bash
# No seu computador local
git clone https://github.com/pdmdevgit/gmailai.git
cd gmailai
```

#### **2.2 - Copiar Arquivos do Sistema**
Copie todos os arquivos da pasta `gmail-ai-agent/` para o repositório:

```bash
# Estrutura que deve ser copiada:
gmailai/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── services/
│   │   ├── gmail_service.py
│   │   ├── learning_service.py
│   │   ├── ai_service.py
│   │   └── email_processor.py
│   ├── api/
│   │   ├── email_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── admin_routes.py
│   │   └── learning_routes.py
│   ├── templates/
│   │   └── dashboard.html
│   └── routes.py
├── static/
│   ├── css/
│   └── js/
├── config/
│   └── config.py
├── database/
│   └── init.sql
├── nginx/
│   └── nginx.conf
├── app.py
├── monitor.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── install.sh
├── README.md
└── .gitignore
```

#### **2.3 - Commit e Push**
```bash
# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Gmail AI Agent with Learning System

- Complete Flask application with Gmail integration
- Learning system for email pattern analysis
- AI-powered response generation
- Docker containerization
- Coolify deployment ready
- Private repository setup"

# Push para GitHub
git push origin main
```

### **Passo 3: Verificar Repositório**

#### **3.1 - Confirmar Upload**
1. **Acessar**: https://github.com/pdmdevgit/gmailai
2. **Verificar**: Todos os arquivos estão presentes
3. **Branch**: Confirmar que está na branch `main`
4. **Commits**: Verificar que o commit inicial foi feito

#### **3.2 - Configurar Branch Padrão**
1. **Settings** → **Branches**
2. **Default branch**: Confirmar que é `main`
3. **Branch protection** (opcional): Configurar regras se necessário

### **Passo 4: Configurar Personal Access Token**

#### **4.1 - Criar Token**
1. **GitHub** → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token** → **Generate new token (classic)**
3. **Note**: `Coolify Gmail AI Agent`
4. **Expiration**: `1 year`
5. **Scopes**:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:org` (Read org and team membership)
   - ✅ `user:email` (Access user email addresses)
   - ✅ `read:user` (Read user profile data)
6. **Generate token** → **COPIAR O TOKEN** (só aparece uma vez!)

### **Passo 5: Reconfigurar Coolify**

#### **5.1 - Deletar Resource Atual**
1. **Coolify** → **Projects** → **Gmail AI Agent**
2. **Resources** → **gmail-ai-agent** → **Settings** → **Delete Resource**

#### **5.2 - Recriar Source**
1. **Sources** → **GitHub Private** → **Edit**
2. **GitHub Personal Access Token**: Cole o novo token
3. **Test Connection** → Deve aparecer "✅ Connected"

#### **5.3 - Criar Nova Resource**
1. **Projects** → **Gmail AI Agent** → **+ New Resource** → **Application**
2. **Resource Name**: `gmail-ai-agent`
3. **Source**: `GitHub Private`
4. **Repository**: `pdmdevgit/gmailai`
5. **Branch**: `main`
6. **Build Pack**: `Docker Compose`

#### **5.4 - Verificar Configuração**
1. **Configuration** → Deve carregar sem erros
2. **Repository**: Deve mostrar os arquivos
3. **Branch**: Deve mostrar `main` disponível

### **Passo 6: Deploy**

#### **6.1 - Configurar Environment Variables**
```env
# Produção
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=sua_chave_secreta_super_segura

# Database
MYSQL_ROOT_PASSWORD=senha_mysql_muito_segura
MYSQL_DATABASE=gmail_ai_agent
MYSQL_USER=gmail_user
MYSQL_PASSWORD=senha_user_mysql_segura

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

#### **6.2 - Configurar Domínio**
1. **Domains** → **+ Add Domain**
2. **Domain**: `gmailai.devpdm.com`
3. **SSL**: ✅ Enable Let's Encrypt

#### **6.3 - Deploy**
1. **Deploy** → **Deploy Now**
2. **Aguardar build** (5-10 minutos)
3. **Verificar logs** em tempo real

## 🔍 Verificações Pós-Setup

### **Repositório GitHub**
```bash
# Verificar se repositório existe
curl -H "Authorization: token SEU_TOKEN" https://api.github.com/repos/pdmdevgit/gmailai

# Deve retornar informações do repositório, não erro 404
```

### **Coolify Connection**
1. **Sources** → **GitHub Private** → **Test Connection**
2. **Deve retornar**: ✅ Connected

### **Repository Access**
1. **Projects** → **Gmail AI Agent** → **Resources** → **gmail-ai-agent**
2. **Configuration** → **Deve carregar sem erros**
3. **Files** → **Deve mostrar estrutura do projeto**

## 🚨 Troubleshooting

### **Problema: Repository Not Found**
```bash
# Verificar se usuário tem acesso
# Verificar se token tem permissões corretas
# Verificar se repositório é realmente privado
```

### **Problema: Branch Not Found**
```bash
# Verificar se branch main existe
git ls-remote --heads https://github.com/pdmdevgit/gmailai.git

# Deve mostrar: refs/heads/main
```

### **Problema: Authentication Failed**
```bash
# Verificar se token não expirou
# Verificar se token tem scopes corretos
# Recriar token se necessário
```

## ✅ Checklist Final

### **GitHub Setup**
- ✅ Repositório `pdmdevgit/gmailai` criado
- ✅ Repositório configurado como privado
- ✅ Código completo uploaded
- ✅ Branch `main` existe e é padrão
- ✅ Personal Access Token criado

### **Coolify Setup**
- ✅ Source configurado com token válido
- ✅ Connection test passando
- ✅ Resource criada sem erros
- ✅ Repository files visíveis
- ✅ Branch `main` disponível

### **Deploy Ready**
- ✅ Environment variables configuradas
- ✅ Domain configurado
- ✅ SSL habilitado
- ✅ Deploy iniciado com sucesso

## 🎉 Resultado Esperado

Após seguir este guia:

1. **Repositório GitHub**: `https://github.com/pdmdevgit/gmailai` funcionando
2. **Coolify**: Conectado sem erros ao repositório
3. **Deploy**: Funcionando em `https://gmailai.devpdm.com`
4. **Learning System**: Operacional e analisando histórico

**🚀 O erro "Remote branch main not found" será resolvido e o deploy funcionará perfeitamente!**
