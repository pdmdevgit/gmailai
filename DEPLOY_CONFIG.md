# 🚀 Configuração de Deploy - Gmail AI Agent

## 🌐 Informações do Servidor

### **Domínio e IP**
- **Domínio**: `gmailai.devpdm.com`
- **IP do VPS**: `31.97.84.68`
- **Painel**: Coolify (recomendado)

## ⚙️ Configuração Atualizada

### **1. Variáveis de Ambiente (.env)**
```env
# Domain Configuration
DOMAIN=gmailai.devpdm.com
VPS_IP=31.97.84.68

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your_secret_key_here

# Database Configuration
DATABASE_URL=mysql://gmail_user:password@db:3306/gmail_ai_agent
MYSQL_ROOT_PASSWORD=your_mysql_root_password
MYSQL_DATABASE=gmail_ai_agent
MYSQL_USER=gmail_user
MYSQL_PASSWORD=your_mysql_password

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=/app/config/credentials.json
GMAIL_TOKEN_DIR=/app/config/tokens

# AI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_MODEL=gpt-4

# Email Accounts Configuration
GMAIL_ACCOUNTS=contato,cursos,diogo,sac
DOMAIN_EMAILS=contato@profdiogomoreira.com.br,cursos@profdiogomoreira.com.br,diogo@profdiogomoreira.com.br,sac@profdiogomoreira.com.br

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
APP_NAME=Gmail AI Agent
APP_VERSION=1.0.0
LOG_LEVEL=INFO
BASE_URL=https://gmailai.devpdm.com

# Learning System Configuration
LEARNING_ENABLED=true
LEARNING_HISTORY_DAYS=90
LEARNING_MIN_SIMILARITY=0.3
```

### **2. Coolify Configuration (coolify.json)**
```json
{
  "name": "gmail-ai-agent",
  "description": "Gmail AI Agent with Learning System for Prof. Diogo Moreira",
  "repository": {
    "url": "https://github.com/pdmdevgit/gmailai",
    "branch": "main",
    "auto_deploy": true
  },
  "build": {
    "command": "docker-compose build",
    "dockerfile": "Dockerfile"
  },
  "deploy": {
    "command": "docker-compose up -d",
    "healthcheck": "/health"
  },
  "domains": [
    "gmailai.devpdm.com"
  ],
  "ssl": {
    "enabled": true,
    "force_https": true,
    "provider": "letsencrypt"
  },
  "environment": {
    "FLASK_ENV": "production",
    "FLASK_DEBUG": "False",
    "DOMAIN": "gmailai.devpdm.com",
    "BASE_URL": "https://gmailai.devpdm.com"
  },
  "volumes": [
    {
      "host": "./config",
      "container": "/app/config"
    },
    {
      "host": "./logs",
      "container": "/app/logs"
    }
  ],
  "backup": {
    "enabled": true,
    "schedule": "0 2 * * *",
    "retention": "7d"
  },
  "monitoring": {
    "enabled": true,
    "alerts": {
      "email": "admin@profdiogomoreira.com.br"
    }
  }
}
```

### **3. Nginx Configuration Atualizada**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        listen 80;
        server_name gmailai.devpdm.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name gmailai.devpdm.com;

        # SSL Configuration (Coolify will handle certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Main application
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Learning API (special handling)
        location /api/learning/ {
            limit_req zone=api burst=10 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 120s;  # Longer timeout for learning operations
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://app;
            access_log off;
        }
    }
}
```

## 🚀 Passos para Deploy

### **1. Configuração DNS (FEITO)**
✅ Apontar `gmailai.devpdm.com` para `31.97.84.68`

### **2. Instalar Coolify no VPS**
```bash
# Conectar ao VPS
ssh root@31.97.84.68

# Instalar Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

### **3. Configurar Projeto no Coolify**
1. Acessar Coolify: `http://31.97.84.68:8000`
2. Criar novo projeto: "Gmail AI Agent"
3. Conectar repositório Git
4. Importar configuração `coolify.json`
5. Configurar variáveis de ambiente

### **4. Configurar Variáveis de Ambiente no Coolify**
```env
FLASK_ENV=production
DOMAIN=gmailai.devpdm.com
BASE_URL=https://gmailai.devpdm.com
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
MYSQL_ROOT_PASSWORD=secure_password
GMAIL_CREDENTIALS_FILE=/app/config/credentials.json
```

### **5. Upload de Arquivos Sensíveis**
- Upload `credentials.json` para `/app/config/`
- Configurar tokens Gmail em `/app/config/tokens/`

### **6. Deploy**
```bash
# Deploy automático via Coolify
# Ou manual:
git push origin main
# Coolify detecta e faz deploy automático
```

### **7. Verificação**
- ✅ Acessar: `https://gmailai.devpdm.com`
- ✅ Testar health check: `https://gmailai.devpdm.com/health`
- ✅ Testar dashboard: `https://gmailai.devpdm.com/dashboard`
- ✅ Testar APIs de learning: `https://gmailai.devpdm.com/api/learning/health`

## 🔧 Comandos Úteis

### **Verificar Status**
```bash
# No VPS
docker-compose ps
docker-compose logs -f app
```

### **Backup**
```bash
# Executar backup
./backup.sh
```

### **Atualizar**
```bash
# Deploy nova versão
git push origin main
# Coolify faz deploy automático
```

## 📊 URLs Importantes

### **Aplicação**
- **Dashboard**: `https://gmailai.devpdm.com`
- **Health Check**: `https://gmailai.devpdm.com/health`
- **API Docs**: `https://gmailai.devpdm.com/api/`

### **Learning System**
- **Análise**: `https://gmailai.devpdm.com/api/learning/analyze/diogo`
- **Stats**: `https://gmailai.devpdm.com/api/learning/stats`
- **Health**: `https://gmailai.devpdm.com/api/learning/health`

### **Coolify Panel**
- **Admin**: `http://31.97.84.68:8000`

## 🎯 Próximos Passos

### **Imediatos:**
1. ✅ DNS configurado para `gmailai.devpdm.com` → `31.97.84.68`
2. 🔄 Instalar Coolify no VPS
3. 🔄 Fazer deploy da aplicação
4. 🔄 Configurar credenciais Gmail API
5. 🔄 Configurar chaves OpenAI/Claude

### **Após Deploy:**
1. 🔄 Autenticar 4 contas Gmail
2. 🔄 Testar sistema de aprendizado
3. 🔄 Configurar monitoramento
4. 🔄 Setup de backups automáticos

## ✅ Status

- ✅ **Código**: Completamente implementado
- ✅ **Learning System**: Funcional e testado
- ✅ **DNS**: Configurado para gmailai.devpdm.com
- ✅ **Deploy Config**: Atualizado para novo domínio
- 🔄 **VPS Setup**: Aguardando instalação do Coolify
- 🔄 **Production Deploy**: Próximo passo

**🚀 Sistema pronto para deploy em `https://gmailai.devpdm.com`!**
