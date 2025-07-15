# Como Encontrar a URL da Aplicação no Coolify

## Passo a Passo para Acessar sua Aplicação

### 1. No Painel Principal do Coolify

1. **Faça login** no seu painel do Coolify
2. **Localize seu projeto** "Gmail AI Agent" na lista de aplicações
3. **Clique no projeto** para abrir os detalhes

### 2. Na Página do Projeto

Você encontrará a URL da aplicação em várias seções:

#### **Opção A: Seção "Domains" ou "URLs"**
- Procure por uma aba chamada **"Domains"**, **"URLs"** ou **"Endpoints"**
- A URL principal da aplicação estará listada aqui
- Geralmente no formato: `https://seu-projeto.seu-dominio.com`

#### **Opção B: Seção "Overview" ou "Dashboard"**
- Na página principal do projeto
- Procure por um botão **"Open Application"** ou **"Visit Site"**
- Ou uma URL clicável próxima ao status do deploy

#### **Opção C: Seção "Configuration"**
- Vá para **"Settings"** ou **"Configuration"**
- Procure por **"Public URL"** ou **"Application URL"**

### 3. Formatos Típicos de URL

Dependendo da configuração do Coolify, sua URL pode ser:

```
# Subdomínio automático
https://gmailai-[hash].seu-coolify-domain.com

# Domínio personalizado (se configurado)
https://gmailai.profdiogomoreira.com.br

# IP + Porta (se não houver domínio)
http://31.97.84.68:5000
```

### 4. Verificar se a Aplicação Está Funcionando

Após encontrar a URL, teste os seguintes endpoints:

#### **Endpoint de Ping (Mais Simples)**
```
https://sua-url/ping
```
**Resposta esperada:**
```json
{
  "status": "ok",
  "timestamp": "2025-01-15T00:17:00.000000"
}
```

#### **Endpoint de Health**
```
https://sua-url/health
```
**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T00:17:00.000000",
  "database": "connected",
  "version": "1.0.0"
}
```

#### **Dashboard Principal**
```
https://sua-url/
```
**Deve mostrar:** Interface do Gmail AI Agent

### 5. Troubleshooting - Se Não Encontrar a URL

#### **Verificar Configuração de Porta**
1. Vá para **"Settings"** do projeto
2. Procure por **"Port Configuration"** ou **"Exposed Ports"**
3. Confirme se a porta **5000** está exposta
4. Se necessário, adicione: `5000:5000`

#### **Verificar Status dos Containers**
1. Vá para **"Logs"** ou **"Containers"**
2. Verifique se todos os containers estão **"Running"**:
   - ✅ MySQL: Running
   - ✅ Redis: Running
   - ✅ Web: Running
   - ✅ Monitor: Running

#### **Configurar Domínio Personalizado (Opcional)**
1. Vá para **"Domains"** ou **"URLs"**
2. Clique em **"Add Domain"**
3. Configure: `gmailai.profdiogomoreira.com.br`
4. Configure SSL automático

### 6. Configuração de Proxy Reverso

Se você quiser usar um subdomínio do seu domínio principal:

#### **No CyberPanel (Hostinger)**
1. Acesse o **CyberPanel**
2. Vá em **"Websites"** > **"Create Website"**
3. Crie: `gmailai.profdiogomoreira.com.br`
4. Configure **proxy reverso** para apontar para a URL do Coolify

#### **Configuração de DNS**
```
# No painel de DNS do domínio
gmailai.profdiogomoreira.com.br CNAME sua-url-coolify.com
```

### 7. URLs de Teste Recomendadas

Após encontrar sua URL principal, teste estas rotas:

```bash
# Teste básico
curl https://sua-url/ping

# Teste de saúde
curl https://sua-url/health

# Teste do dashboard
curl https://sua-url/

# Teste da API
curl https://sua-url/api/stats
```

### 8. Exemplo de URLs Funcionais

Baseado no seu setup, suas URLs provavelmente serão:

```
# URL principal da aplicação
https://[projeto-id].coolify.seu-vps.com

# Ou se configurou domínio personalizado
https://gmailai.profdiogomoreira.com.br

# Endpoints específicos
https://sua-url/ping          # Teste simples
https://sua-url/health        # Status da aplicação
https://sua-url/dashboard     # Interface principal
https://sua-url/api/emails    # API de emails
```

## Próximos Passos Após Encontrar a URL

1. **Teste todos os endpoints** para confirmar funcionamento
2. **Configure as chaves de API** se ainda não foram adicionadas
3. **Teste a integração** com Gmail API
4. **Configure o domínio personalizado** se desejado
5. **Ative o health check** do web container novamente

## Suporte

Se ainda não conseguir encontrar a URL:
1. **Verifique os logs** do deploy no Coolify
2. **Confirme se todos os containers** estão rodando
3. **Verifique a configuração de rede** do projeto
4. **Entre em contato** com o suporte do Coolify se necessário
