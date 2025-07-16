#!/bin/bash

# Gmail AI Agent - SSL Setup Script
# Configura SSL automaticamente para gmailai.devpdm.com

set -e

echo "🔒 Gmail AI Agent - Configuração SSL Automática"
echo "================================================"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa ser executado como root (sudo)"
    exit 1
fi

# Verificar se o domínio resolve
echo "🔍 Verificando DNS para gmailai.devpdm.com..."
if ! nslookup gmailai.devpdm.com > /dev/null 2>&1; then
    echo "❌ Erro: gmailai.devpdm.com não resolve. Verifique o DNS."
    exit 1
fi

echo "✅ DNS OK"

# Instalar certbot se não estiver instalado
echo "📦 Verificando/Instalando Certbot..."
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
else
    echo "✅ Certbot já instalado"
fi

# Verificar se nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "📦 Instalando Nginx..."
    apt install -y nginx
fi

# Criar configuração básica do Nginx para gmailai.devpdm.com
echo "⚙️ Criando configuração Nginx..."

cat > /etc/nginx/sites-available/gmailai.devpdm.com << 'EOF'
# Gmail AI Agent - HTTP (será convertido para HTTPS pelo certbot)
server {
    listen 80;
    server_name gmailai.devpdm.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
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
EOF

# Ativar site
echo "🔗 Ativando configuração..."
ln -sf /etc/nginx/sites-available/gmailai.devpdm.com /etc/nginx/sites-enabled/

# Testar configuração
echo "🧪 Testando configuração Nginx..."
if ! nginx -t; then
    echo "❌ Erro na configuração do Nginx"
    exit 1
fi

# Recarregar Nginx
echo "🔄 Recarregando Nginx..."
systemctl reload nginx

# Verificar se a aplicação está rodando na porta 5000
echo "🔍 Verificando se a aplicação está rodando na porta 5000..."
if ! netstat -tlnp | grep :5000 > /dev/null; then
    echo "⚠️ Aviso: Aplicação não está rodando na porta 5000"
    echo "   Certifique-se de que o container Docker está rodando"
fi

# Obter certificado SSL
echo "🔒 Obtendo certificado SSL com Let's Encrypt..."
echo "   Isso pode levar alguns minutos..."

# Solicitar email se não fornecido
if [ -z "$SSL_EMAIL" ]; then
    read -p "📧 Digite seu email para o certificado SSL: " SSL_EMAIL
fi

# Executar certbot
if certbot --nginx -d gmailai.devpdm.com --non-interactive --agree-tos --email "$SSL_EMAIL"; then
    echo "✅ Certificado SSL configurado com sucesso!"
else
    echo "❌ Erro ao obter certificado SSL"
    echo "Verifique se:"
    echo "  - O domínio gmailai.devpdm.com aponta para este servidor"
    echo "  - A porta 80 está acessível externamente"
    echo "  - Não há firewall bloqueando"
    exit 1
fi

# Configurar renovação automática
echo "🔄 Configurando renovação automática..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Testar HTTPS
echo "🧪 Testando HTTPS..."
sleep 5

if curl -s -I https://gmailai.devpdm.com/health | grep -q "200 OK"; then
    echo "✅ HTTPS funcionando perfeitamente!"
    echo ""
    echo "🎉 Configuração SSL Concluída!"
    echo "================================"
    echo "✅ Certificado SSL ativo"
    echo "✅ HTTPS funcionando: https://gmailai.devpdm.com"
    echo "✅ OAuth callback: https://gmailai.devpdm.com/auth/callback"
    echo "✅ Renovação automática configurada"
    echo ""
    echo "📝 Próximos passos:"
    echo "1. Configure no Google Console:"
    echo "   https://gmailai.devpdm.com/auth/callback"
    echo "2. Teste a autenticação OAuth"
    echo ""
else
    echo "⚠️ HTTPS configurado, mas aplicação pode não estar respondendo"
    echo "Verifique se o container Docker está rodando na porta 5000"
fi

echo "🔍 Informações do certificado:"
certbot certificates | grep gmailai.devpdm.com -A 5

echo ""
echo "✅ Script concluído!"
