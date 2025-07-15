# 📧 Guia de Configuração Gmail API - Passo a Passo

## 🎯 Quando Configurar
**IMPORTANTE:** Configure as credenciais Gmail **APÓS** a aplicação estar rodando sem erros básicos. Primeiro vamos fazer o deploy funcionar, depois integramos com Gmail.

## 📋 Etapas de Configuração

### **Fase 1: Deploy Básico (ATUAL)**
✅ Corrigir erros de import e configuração  
✅ Aplicação rodando sem crashes  
✅ Interface web acessível  
⏳ **VOCÊ ESTÁ AQUI**

### **Fase 2: Configuração Gmail API (PRÓXIMA)**
🔄 Criar projeto no Google Cloud Console  
🔄 Ativar Gmail API  
🔄 Configurar credenciais OAuth 2.0  
🔄 Fazer upload dos arquivos de credenciais  

---

## 🚀 Passo a Passo - Configuração Gmail

### **1. Google Cloud Console Setup**

#### **1.1 Criar Projeto:**
1. Acesse: https://console.cloud.google.com/
2. Clique em "Novo Projeto"
3. Nome: `Gmail AI Agent - Prof Diogo`
4. Clique em "Criar"

#### **1.2 Ativar Gmail API:**
1. No menu lateral: **APIs e Serviços** > **Biblioteca**
2. Pesquise: `Gmail API`
3. Clique em **Gmail API** > **Ativar**

#### **1.3 Configurar Tela de Consentimento:**
1. **APIs e Serviços** > **Tela de consentimento OAuth**
2. Escolha: **Externo**
3. Preencha:
   - **Nome do app:** `Gmail AI Agent`
   - **Email de suporte:** `diogo@profdiogomoreira.com.br`
   - **Domínios autorizados:** `profdiogomoreira.com.br`
   - **Email do desenvolvedor:** `diogo@profdiogomoreira.com.br`
4. **Salvar e continuar**

#### **1.4 Adicionar Escopos:**
1. Clique em **Adicionar ou remover escopos**
2. Adicione estes escopos:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/gmail.compose
   https://www.googleapis.com/auth/gmail.modify
   ```
3. **Salvar e continuar**

#### **1.5 Criar Credenciais OAuth:**
1. **APIs e Serviços** > **Credenciais**
2. **+ Criar Credenciais** > **ID do cliente OAuth 2.0**
3. Tipo: **Aplicação da Web**
4. Nome: `Gmail AI Agent Web Client`
5. **URIs de redirecionamento autorizados:**
   ```
   https://gmailai.pdmdev.com/auth/callback
   http://31.97.84.68:5000/auth/callback
   http://localhost:5000/auth/callback
   ```
6. **Criar**
7. **BAIXAR JSON** - salve como `gmail_credentials.json`

### **2. Upload das Credenciais no VPS**

#### **2.1 Criar Diretório de Config:**
```bash
# No VPS
mkdir -p /root/gmail-ai-agent/config
mkdir -p /root/gmail-ai-agent/config/tokens
```

#### **2.2 Upload do Arquivo de Credenciais:**
```bash
# No seu computador local (onde baixou o JSON)
scp gmail_credentials.json root@31.97.84.68:/root/gmail-ai-agent/config/

# Ou use o editor nano no VPS:
nano /root/gmail-ai-agent/config/gmail_credentials.json
# Cole o conteúdo do JSON baixado
```

#### **2.3 Configurar Permissões:**
```bash
# No VPS
chmod 600 /root/gmail-ai-agent/config/gmail_credentials.json
chmod 700 /root/gmail-ai-agent/config/tokens
```

### **3. Configuração das Contas Gmail**

#### **3.1 Autorizar Cada Conta:**
Para cada conta (`contato@`, `cursos@`, `diogo@`, `sac@`):

1. **Acesse a aplicação:** `https://gmailai.pdmdev.com/auth/gmail`
2. **Escolha a conta** a ser autorizada
3. **Aceite as permissões** solicitadas
4. **Repita para todas as 4 contas**

#### **3.2 Verificar Tokens Gerados:**
```bash
# No VPS - verificar se tokens foram criados
ls -la /root/gmail-ai-agent/config/tokens/
# Deve mostrar arquivos como:
# token_contato.json
# token_cursos.json
# token_diogo.json
# token_sac.json
```

### **4. Variáveis de Ambiente (Opcional)**

#### **4.1 No Coolify:**
Se quiser usar variáveis de ambiente em vez de arquivos:

```bash
# No painel do Coolify, adicione estas variáveis:
GMAIL_CREDENTIALS_FILE=/app/config/gmail_credentials.json
GMAIL_TOKEN_DIR=/app/config/tokens
OPENAI_API_KEY=sua_chave_openai_aqui
```

### **5. Teste da Integração**

#### **5.1 Verificar Logs:**
```bash
# Verificar se Gmail API está funcionando
docker logs --tail=50 $(docker ps | grep web-f04ww0cgw084os08k4wk4g08 | awk '{print $1}')
```

#### **5.2 Testar Endpoints:**
```bash
# Testar listagem de emails
curl -X GET "https://gmailai.pdmdev.com/api/emails/list?account=contato"

# Testar classificação
curl -X POST "https://gmailai.pdmdev.com/api/emails/classify" \
  -H "Content-Type: application/json" \
  -d '{"subject": "Interesse em coaching", "body": "Gostaria de saber mais sobre o coaching"}'
```

---

## 🔒 Segurança e Boas Práticas

### **Arquivos Sensíveis:**
- ✅ `gmail_credentials.json` - Nunca commitar no Git
- ✅ `tokens/*.json` - Nunca commitar no Git
- ✅ Usar `.gitignore` para excluir estes arquivos

### **Backup:**
```bash
# Fazer backup das credenciais
tar -czf gmail_credentials_backup.tar.gz /root/gmail-ai-agent/config/
```

### **Renovação de Tokens:**
- Tokens OAuth expiram periodicamente
- A aplicação deve renovar automaticamente
- Se houver problemas, re-autorize as contas

---

## 🎯 Próximos Passos

### **Agora (Fase 1):**
1. ✅ Aguardar aplicação rodar sem erros
2. ✅ Testar interface web básica
3. ✅ Verificar logs limpos

### **Depois (Fase 2):**
1. 🔄 Seguir este guia para configurar Gmail
2. 🔄 Autorizar as 4 contas
3. 🔄 Testar integração completa

---

## 📞 Suporte

Se tiver problemas:
1. **Verifique logs** da aplicação
2. **Confirme permissões** dos arquivos
3. **Re-autorize contas** se necessário
4. **Verifique quotas** da Gmail API no Google Cloud Console

**IMPORTANTE:** Primeiro vamos garantir que a aplicação básica está funcionando, depois configuramos o Gmail! 🚀
