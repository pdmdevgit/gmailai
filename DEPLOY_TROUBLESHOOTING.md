# Deploy Troubleshooting Guide - Coolify

## Problemas Resolvidos

### 1. MySQL Health Check ✅
**Problema:** Container MySQL falhava no health check
**Solução:** Ajustado health check para incluir credenciais de autenticação

### 2. Web Container Health Check ✅
**Problema:** Container web falhava no health check por timeout
**Solução:** Aumentado timeout e período de inicialização

## Instruções de Deploy

### Passo 1: Adicionar Variáveis de Ambiente no Coolify
No painel do Coolify, adicione as seguintes variáveis de ambiente:

```
OPENAI_API_KEY=sua_chave_openai_aqui
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
```

**Nota:** As chaves de API devem ser adicionadas manualmente no painel do Coolify por segurança.

### Passo 2: Iniciar Deploy
1. Acesse o painel do Coolify
2. Selecione o projeto "gmail-ai-agent"
3. Clique em "Deploy"
4. Monitore os logs em tempo real

### Passo 3: Verificar Status dos Containers
Após o deploy, verifique se todos os containers estão rodando:
- ✅ MySQL (deve passar no health check)
- ✅ Redis (deve passar no health check)
- ✅ Web (deve passar no health check após ~60 segundos)
- ✅ Monitor (depende dos outros containers)

### Passo 4: Testar Aplicação
1. Acesse a URL fornecida pelo Coolify
2. Verifique se a dashboard carrega
3. Teste o endpoint de health: `/health`

## Configurações Atuais

### Health Checks Configurados:
- **MySQL:** 30s start period, 10s interval, 10 retries
- **Redis:** 3s timeout, 5 retries
- **Web:** 60s start period, 30s interval, 5 retries

### Variáveis de Ambiente Definidas:
- SECRET_KEY
- MYSQL_ROOT_PASSWORD
- MYSQL_DB
- MYSQL_USER
- MYSQL_PASSWORD
- REDIS_PASSWORD
- FLASK_ENV=production
- AI_MODEL=gpt-4
- EMAIL_CHECK_INTERVAL=300
- MAX_EMAILS_PER_BATCH=50

## Logs Importantes para Monitorar

### Durante o Deploy:
1. **MySQL:** Deve mostrar "mysql Healthy"
2. **Redis:** Deve mostrar "redis Healthy"
3. **Web:** Deve mostrar "web Started" (pode demorar até 60s para ficar healthy)

### Se Houver Erro:
1. Verifique se as variáveis de ambiente foram adicionadas
2. Verifique os logs específicos do container que falhou
3. Aguarde o tempo de start_period antes de considerar falha

## Próximos Passos Após Deploy Bem-Sucedido

1. **Configurar Gmail API:**
   - Adicionar credenciais OAuth
   - Configurar contas de email

2. **Testar Funcionalidades:**
   - Dashboard principal
   - Endpoints de API
   - Processamento de emails

3. **Monitoramento:**
   - Verificar logs da aplicação
   - Monitorar performance dos containers
   - Verificar conectividade com APIs externas

## Comandos Úteis para Debug

### Verificar Status dos Containers:
```bash
docker ps
```

### Ver Logs de um Container Específico:
```bash
docker logs <container_name>
```

### Testar Conectividade:
```bash
curl http://localhost:5000/health
