# Configuração do Webhook Coolify no GitHub

## Passo a Passo para Configurar Auto-Deploy

### 1. No Painel do Coolify

1. **Acesse seu projeto** no Coolify
2. **Vá para a aba "Settings"** ou "Configurações"
3. **Procure por "Webhooks"** ou "Auto Deploy"
4. **Copie a URL do webhook** fornecida pelo Coolify
   - Geralmente tem o formato: `https://seu-coolify.com/webhooks/deploy/[project-id]`

### 2. No GitHub Repository

1. **Acesse o repositório** `https://github.com/pdmdevgit/gmailai`
2. **Clique em "Settings"** (no menu superior do repositório)
3. **No menu lateral esquerdo, clique em "Webhooks"**
4. **Clique em "Add webhook"**

### 3. Configurar o Webhook

Preencha os campos:

**Payload URL:**
```
[URL_DO_WEBHOOK_COOLIFY_AQUI]
```

**Content type:**
```
application/json
```

**Secret:** (opcional)
```
[deixe em branco ou use um secret se o Coolify fornecer]
```

**Which events would you like to trigger this webhook?**
- Selecione: **"Just the push event"**
- Ou: **"Let me select individual events"** e marque apenas **"Pushes"**

**Active:**
- ✅ Marque esta opção

### 4. Salvar e Testar

1. **Clique em "Add webhook"**
2. **Teste fazendo um push** para o repositório
3. **Verifique no Coolify** se o deploy automático foi acionado

## Configuração Alternativa (Se não houver webhook automático)

### Opção 1: Deploy Manual
1. No painel do Coolify
2. Clique em "Deploy" sempre que quiser atualizar
3. O Coolify irá buscar as últimas alterações do GitHub

### Opção 2: Configurar Polling
1. No Coolify, procure por "Auto Deploy" ou "Polling"
2. Configure para verificar o repositório a cada X minutos
3. Defina a branch (main) para monitorar

## Verificação da Configuração

### No GitHub:
1. Vá em Settings > Webhooks
2. Clique no webhook criado
3. Vá na aba "Recent Deliveries"
4. Verifique se há entregas bem-sucedidas (status 200)

### No Coolify:
1. Verifique se aparecem logs de deploy automático
2. Confirme se o deploy é acionado após commits

## Troubleshooting

### Webhook não funciona:
1. **Verifique a URL** do webhook no Coolify
2. **Confirme se o repositório é público** ou se o Coolify tem acesso
3. **Teste manualmente** fazendo um push pequeno
4. **Verifique os logs** no GitHub (Settings > Webhooks > Recent Deliveries)

### Deploy não acontece:
1. **Verifique se o branch está correto** (main)
2. **Confirme se há alterações** no código
3. **Verifique os logs do Coolify** para erros

## Configuração Recomendada

Para o projeto Gmail AI Agent, recomendo:

1. **Webhook ativo** para deploy automático
2. **Monitorar apenas a branch main**
3. **Deploy apenas em pushes** (não em pull requests)
4. **Manter logs ativos** para debug

## Próximos Passos Após Configurar Webhook

1. **Adicione as chaves de API** no painel do Coolify:
   - OPENAI_API_KEY
   - ANTHROPIC_API_KEY

2. **Faça um pequeno commit** para testar o webhook:
   ```bash
   git commit --allow-empty -m "Test webhook"
   git push origin main
   ```

3. **Verifique se o deploy automático funciona**

4. **Se funcionar, faça o deploy completo** com as correções implementadas
