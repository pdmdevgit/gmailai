# 📧 CONFIGURAÇÃO GMAIL API - GUIA FINAL ATUALIZADO

## ✅ STATUS ATUAL
- **Aplicação funcionando**: 100% operacional
- **Credenciais Gmail**: ✅ Enviadas para o VPS
- **Arquivo configurado**: `/root/gmail-ai-agent/config/gmail_credentials.json`
- **Permissões**: ✅ Configuradas corretamente (600)
- **Diretório tokens**: ✅ Criado (/root/gmail-ai-agent/config/tokens/)

## 🎯 INFORMAÇÕES CORRETAS DO PROJETO

### **Domínios e Emails:**
- **Email administrador**: `contato@profdiogomoreira.com.br`
- **Domínio Gmail AI Agent**: `pdmdev.com`
- **Site Prof. Diogo**: `profdiogomoreira.com.br` (blog e informações)
- **Contas Gmail para monitorar**:
  - `contato@profdiogomoreira.com.br`
  - `cursos@profdiogomoreira.com.br`
  - `diogo@profdiogomoreira.com.br`
  - `sac@profdiogomoreira.com.br`

### **URLs da Aplicação:**
- **URL principal**: `https://gmailai.pdmdev.com`
- **IP direto**: `http://31.97.84.68:5000`

## 🔧 CONFIGURAÇÃO DA TELA DE CONSENTIMENTO OAUTH

### **Informações Corretas para o Google Cloud:**

#### **Informações do Aplicativo:**
```
Nome do aplicativo: Gmail AI Agent - Prof. Diogo Moreira
Email de suporte: contato@profdiogomoreira.com.br
Domínio do aplicativo: pdmdev.com
Domínios autorizados: 
  - pdmdev.com
  - profdiogomoreira.com.br
Email do desenvolvedor: contato@profdiogomoreira.com.br
```

#### **URIs de Redirecionamento:**
```
https://gmailai.pdmdev.com/auth/callback
http://31.97.84.68:5000/auth/callback
http://localhost:8080
http://localhost:5000
```

#### **Usuários de Teste:**
```
contato@profdiogomoreira.com.br
cursos@profdiogomoreira.com.br
diogo@profdiogomoreira.com.br
sac@profdiogomoreira.com.br
```

#### **Escopos Necessários:**
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.compose
https://www.googleapis.com/auth/gmail.modify
```

## 🚀 PRÓXIMOS PASSOS PARA ATIVAR O GMAIL

### **1. Verificar se Credenciais Estão Corretas**
```bash
# No VPS - verificar arquivo
ssh root@31.97.84.68 "cat /root/gmail-ai-agent/config/gmail_credentials.json"
```

### **2. Reiniciar Aplicação (se necessário)**
```bash
# Reiniciar container para carregar credenciais
ssh root@31.97.84.68 "docker restart fd4bbf77cc47"
```

### **3. Testar Integração Gmail**
```bash
# Testar endpoint de autenticação
curl -X GET "http://31.97.84.68:5000/api/gmail/auth?account=contato"

# Ou via interface web
# Acesse: https://gmailai.pdmdev.com/admin
```

### **4. Autorizar Cada Conta Gmail**

Para cada conta (`contato@`, `cursos@`, `diogo@`, `sac@`):

1. **Acesse a aplicação**: `https://gmailai.pdmdev.com`
2. **Vá para seção Admin** ou use endpoint de auth
3. **Clique em "Autorizar Gmail"** para cada conta
4. **Faça login** com a conta específica
5. **Aceite as permissões** na tela de consentimento
6. **Token será salvo** automaticamente

## 🔍 VERIFICAÇÃO DE FUNCIONAMENTO

### **Arquivos que Devem Existir:**
```bash
# Credenciais principais
/root/gmail-ai-agent/config/gmail_credentials.json

# Tokens após autorização (criados automaticamente)
/root/gmail-ai-agent/config/tokens/contato_token.json
/root/gmail-ai-agent/config/tokens/cursos_token.json
/root/gmail-ai-agent/config/tokens/diogo_token.json
/root/gmail-ai-agent/config/tokens/sac_token.json
```

### **Logs de Sucesso Esperados:**
```
Gmail service initialized successfully
Authenticated account: contato@profdiogomoreira.com.br
Retrieved X unread emails from contato
Email classification completed
```

### **Testes de API:**
```bash
# Listar emails (após autorização)
curl -X GET "http://31.97.84.68:5000/api/emails/list?account=contato"

# Verificar status das contas
curl -X GET "http://31.97.84.68:5000/api/gmail/status"
```

## 🔒 SEGURANÇA E MANUTENÇÃO

### **Arquivos Sensíveis (Nunca Commitar):**
- ✅ `gmail_credentials.json` - Já no .gitignore
- ✅ `tokens/*.json` - Criados automaticamente, já protegidos

### **Renovação de Tokens:**
- **Automática**: A aplicação renova tokens expirados
- **Manual**: Re-autorizar conta se houver problemas

### **Backup das Credenciais:**
```bash
# Fazer backup
ssh root@31.97.84.68 "tar -czf gmail_backup.tar.gz /root/gmail-ai-agent/config/"
```

## 🎯 RESUMO DO QUE FOI FEITO

### ✅ **Concluído:**
1. **Aplicação funcionando** sem erros de deployment
2. **Credenciais Gmail enviadas** para o VPS
3. **Permissões configuradas** corretamente
4. **Estrutura pronta** para autorização das contas

### 🔄 **Próximo Passo (Você):**
1. **Autorizar as 4 contas Gmail** via interface web
2. **Testar funcionalidades** de email
3. **Configurar regras de classificação** (opcional)

## 📞 SUPORTE

**Se tiver problemas:**
- **Erro "App não verificado"**: Normal, clique em "Avançado" > "Ir para Gmail AI Agent"
- **Erro de redirect_uri**: Verifique se as URIs estão corretas no Google Cloud
- **Token expirado**: Re-autorize a conta específica

---

**🎉 RESULTADO:** Gmail AI Agent está 100% funcional e pronto para integração com Gmail. As credenciais estão configuradas corretamente com as informações do seu domínio pdmdev.com!
