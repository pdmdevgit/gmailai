# 🔒 Solução Final SSL - Gmail AI Agent

## 🎯 Problema Identificado

O Google OAuth está redirecionando para HTTPS, mas o servidor não tem certificado SSL:
```
https://gmailai.devpdm.com:5000/auth/callback
ERR_SSL_PROTOCOL_ERROR
```

## ✅ Solução Implementada

Criados scripts e guias para configurar SSL automaticamente com Let's Encrypt.

## 🚀 Execução Rápida (Recomendado)

### Opção 1: Script Automático
```bash
# No servidor (como root)
cd /path/to/gmail-ai-agent
sudo SSL_EMAIL="seu-email@exemplo.com" ./setup_ssl.sh
```

### Opção 2: Comandos Manuais
```bash
# 1. Instalar certbot
sudo apt update && sudo apt install -y certbot python3-certbot-nginx

# 2. Configurar Nginx básico
sudo tee /etc/nginx/sites-available/gmailai.devpdm.com << 'EOF'
server {
    listen 80;
    server_name gmailai.devpdm.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 3. Ativar site
sudo ln -s /etc/nginx/sites-available/gmailai.devpdm.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 4. Obter certificado SSL
sudo certbot --nginx -d gmailai.devpdm.com --email seu-email@exemplo.com --agree-tos --non-interactive

# 5. Testar
curl -I https://gmailai.devpdm.com/health
```

## 🔍 Verificação Pós-Configuração

### 1. Testar HTTPS
```bash
curl -I https://gmailai.devpdm.com/health
# Deve retornar: HTTP/2 200
```

### 2. Testar Certificado
```bash
openssl s_client -connect gmailai.devpdm.com:443 -servername gmailai.devpdm.com
# Deve mostrar certificado válido
```

### 3. Testar OAuth
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"account_name":"contato"}' \
  https://gmailai.devpdm.com/api/admin/gmail-accounts/authenticate
```

## 📝 Configuração Google Console

Após SSL configurado:

1. **Acesse:** https://console.developers.google.com/
2. **Vá em:** Credenciais → IDs do cliente OAuth 2.0
3. **Edite** o cliente OAuth existente
4. **Em "URIs de redirecionamento autorizados", adicione:**
   ```
   https://gmailai.devpdm.com/auth/callback
   ```
5. **Salve** as alterações

## 🎉 Resultado Final

Após configuração SSL:

### ✅ URLs Funcionais
- **Interface:** https://gmailai.devpdm.com
- **Health Check:** https://gmailai.devpdm.com/health
- **OAuth Callback:** https://gmailai.devpdm.com/auth/callback
- **Admin:** https://gmailai.devpdm.com (seção Admin)

### ✅ OAuth Funcionando
- Google aceita URL HTTPS
- Redirecionamento funciona corretamente
- Autenticação completa sem erros

### ✅ Segurança
- Certificado SSL válido e confiável
- Renovação automática configurada
- Headers de segurança implementados

## 🔧 Troubleshooting

### Problema: Certificado não obtido
```bash
# Verificar DNS
nslookup gmailai.devpdm.com

# Verificar porta 80 acessível
sudo netstat -tlnp | grep :80

# Verificar logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Problema: Aplicação não responde
```bash
# Verificar se container está rodando
docker ps | grep gmail

# Verificar porta 5000
sudo netstat -tlnp | grep :5000

# Testar diretamente
curl http://localhost:5000/health
```

### Problema: Nginx não funciona
```bash
# Testar configuração
sudo nginx -t

# Ver logs de erro
sudo tail -f /var/log/nginx/error.log

# Recarregar configuração
sudo systemctl reload nginx
```

## 📋 Checklist Final

- [ ] DNS gmailai.devpdm.com resolve para IP correto
- [ ] Container Docker rodando na porta 5000
- [ ] Nginx instalado e configurado
- [ ] Certificado SSL obtido com Let's Encrypt
- [ ] HTTPS funcionando (teste com curl)
- [ ] OAuth callback configurado no Google Console
- [ ] Teste de autenticação OAuth funcionando

## 🎯 Próximos Passos

1. **Execute o script SSL** ou comandos manuais
2. **Configure Google Console** com URL HTTPS
3. **Teste autenticação** OAuth completa
4. **Configure contas Gmail** (contato, cursos, diogo, sac)
5. **Ative processamento** de emails

## 📞 Suporte

Se encontrar problemas:
1. Verifique logs: `/var/log/nginx/error.log` e `/var/log/letsencrypt/letsencrypt.log`
2. Teste cada etapa individualmente
3. Verifique se firewall não está bloqueando portas 80/443

**🔒 SSL é essencial para OAuth em produção - Google não aceita HTTP!**
