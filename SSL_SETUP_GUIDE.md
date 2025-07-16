# Configuração SSL para gmailai.devpdm.com

## 🔒 Problema Identificado

O Google OAuth está redirecionando para HTTPS, mas o servidor `gmailai.devpdm.com:5000` não tem certificado SSL configurado, causando o erro:
```
ERR_SSL_PROTOCOL_ERROR
```

## 🚀 Solução: Configurar SSL com Let's Encrypt

### Passo 1: Instalar Certbot
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### Passo 2: Obter Certificado SSL
```bash
sudo certbot --nginx -d gmailai.devpdm.com
```

### Passo 3: Configurar Nginx para gmailai.devpdm.com

Criar arquivo: `/etc/nginx/sites-available/gmailai.devpdm.com`

```nginx
# HTTP to HTTPS Redirect
server {
    listen 80;
    server_name gmailai.devpdm.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name gmailai.devpdm.com;
    
    # SSL Configuration (será preenchido pelo certbot)
    ssl_certificate /etc/letsencrypt/live/gmailai.devpdm.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gmailai.devpdm.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy para aplicação Flask na porta 5000
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }
}
```

### Passo 4: Ativar Configuração
```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/gmailai.devpdm.com /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### Passo 5: Configurar Renovação Automática
```bash
# Testar renovação
sudo certbot renew --dry-run

# Adicionar ao crontab para renovação automática
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Alternativa: Configuração Manual Rápida

Se você tem acesso ao servidor, execute estes comandos:

```bash
# 1. Instalar certbot
sudo apt update && sudo apt install -y certbot python3-certbot-nginx

# 2. Obter certificado
sudo certbot --nginx -d gmailai.devpdm.com --non-interactive --agree-tos --email admin@devpdm.com

# 3. Verificar se funcionou
curl -I https://gmailai.devpdm.com
```

## 🎯 Resultado Esperado

Após a configuração SSL:
- ✅ `https://gmailai.devpdm.com` funcionará
- ✅ OAuth callback funcionará: `https://gmailai.devpdm.com/auth/callback`
- ✅ Google Console aceitará a URL HTTPS
- ✅ Certificado válido e confiável

## 🔍 Verificação

Teste se SSL está funcionando:
```bash
# Teste básico
curl -I https://gmailai.devpdm.com/health

# Teste detalhado do certificado
openssl s_client -connect gmailai.devpdm.com:443 -servername gmailai.devpdm.com
```

## 📝 Configuração no Google Console

Após SSL configurado, no Google Console:
1. Vá em "Credenciais" → "IDs do cliente OAuth 2.0"
2. Edite o cliente OAuth
3. Em "URIs de redirecionamento autorizados", adicione:
   ```
   https://gmailai.devpdm.com/auth/callback
   ```
4. Salve as alterações

## ⚠️ Importante

- O certificado Let's Encrypt é válido por 90 dias
- A renovação automática deve estar configurada
- Mantenha o Nginx atualizado para segurança
- Monitore os logs para possíveis problemas

Após configurar SSL, o OAuth funcionará perfeitamente com HTTPS!
