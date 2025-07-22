# Controle Manual de Emails - Implementação Completa

## Problema Resolvido

O sistema estava marcando emails automaticamente como lidos durante o processamento, removendo o controle do usuário sobre quais emails foram realmente lidos e processados.

## Mudanças Implementadas

### 1. Remoção da Marcação Automática como Lido

**Arquivo:** `app/services/email_processor.py`
- **Removido:** Chamada automática para `mark_as_read()` durante o processamento
- **Mantido:** Label "AI-Processed" para organização
- **Resultado:** Emails permanecem como não lidos até decisão manual do usuário

### 2. Novas Rotas de Controle Manual

**Arquivo:** `app/api/email_routes.py`

#### Marcar Email como Lido (Individual)
```
POST /api/emails/{email_id}/mark-as-read
```
- Marca um email específico como lido no Gmail
- Atualiza status local no banco de dados
- Controle total do usuário

#### Marcar Múltiplos Emails como Lidos
```
POST /api/emails/bulk-mark-read
Body: {"email_ids": [1, 2, 3, 4]}
```
- Marca vários emails como lidos de uma vez
- Útil para processamento em lote

#### Criar Rascunho no Gmail
```
POST /api/emails/{email_id}/create-draft
```
- Cria rascunho no Gmail (NUNCA ENVIA AUTOMATICAMENTE)
- Requer resposta previamente aprovada
- Usuário deve acessar Gmail para revisar e enviar manualmente

#### Atualizar Aprendizado com Emails Enviados
```
POST /api/emails/learning/update-from-sent
Body: {"account": "contato", "days_back": 30}
```
- Analisa emails enviados manualmente pelo usuário
- Extrai padrões de resposta efetivos
- Melhora futuras gerações de resposta

### 3. Melhorias no Modelo de Dados

**Arquivo:** `app/models/__init__.py`

#### Tabela `emails`
- **Novo campo:** `is_read` (Boolean) - Controle local de leitura
- **Índice:** Otimização para consultas por status de leitura

#### Tabela `email_responses`
- **Novo campo:** `draft_created_at` (DateTime) - Timestamp de criação do rascunho
- **Status atualizado:** Inclui "draft_created" para rascunhos criados no Gmail

### 4. Funcionalidade de Rascunho no Gmail

**Arquivo:** `app/services/gmail_service.py`
- **Novo método:** `create_draft()` - Cria rascunho sem enviar
- **Segurança:** Impossível envio automático
- **Threading:** Mantém contexto da conversa

### 5. Aprendizado Inteligente

**Funcionalidade:** Análise de emails enviados manualmente
- Identifica conversas completas (pergunta + resposta)
- Analisa efetividade das respostas enviadas
- Extrai padrões para melhorar futuras gerações
- Aprende com o estilo real do usuário

## Fluxo de Trabalho Atualizado

### 1. Processamento de Emails
```
1. Sistema busca emails não lidos
2. Classifica e salva no banco
3. NÃO marca como lido automaticamente
4. Adiciona label "AI-Processed" para organização
```

### 2. Seleção Manual pelo Usuário
```
1. Usuário visualiza emails não lidos no dashboard
2. Escolhe quais emails processar
3. Marca emails selecionados como lidos (opcional)
4. Decide quais emails merecem resposta
```

### 3. Geração de Resposta
```
1. Usuário solicita geração de resposta para email específico
2. IA gera resposta baseada em aprendizado
3. Resposta fica como rascunho para aprovação
4. NUNCA é enviada automaticamente
```

### 4. Aprovação e Envio
```
1. Usuário revisa resposta gerada
2. Aprova ou edita conforme necessário
3. Cria rascunho no Gmail
4. Acessa Gmail para envio manual
```

### 5. Aprendizado Contínuo
```
1. Sistema analisa emails enviados manualmente
2. Identifica padrões de resposta efetivos
3. Melhora futuras gerações
4. Adapta-se ao estilo do usuário
```

## Benefícios da Implementação

### ✅ Controle Total
- Usuário decide quais emails ler
- Usuário decide quais emails responder
- Usuário decide quando enviar respostas

### ✅ Segurança
- Impossível envio automático acidental
- Todas as respostas passam por aprovação manual
- Rascunhos criados no Gmail para revisão

### ✅ Aprendizado Inteligente
- IA aprende com respostas reais enviadas
- Melhora contínua da qualidade
- Adaptação ao estilo pessoal

### ✅ Organização
- Labels para identificar emails processados
- Status claros no banco de dados
- Histórico completo de ações

## Endpoints Disponíveis

### Controle de Leitura

#### Marcar Email Individual como Lido
```bash
curl -X POST http://localhost:5000/api/emails/123/mark-as-read \
  -H "Content-Type: application/json"
```

#### Marcar Múltiplos Emails como Lidos
```bash
curl -X POST http://localhost:5000/api/emails/bulk-mark-read \
  -H "Content-Type: application/json" \
  -d '{"email_ids": [123, 124, 125]}'
```

### Geração de Respostas

#### Gerar Resposta para Email
```bash
curl -X POST http://localhost:5000/api/emails/123/responses \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "custom_instructions": "Mencionar promoção especial"
  }'
```

#### Aprovar Resposta
```bash
curl -X POST http://localhost:5000/api/emails/responses/456/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "usuario@exemplo.com"}'
```

#### Editar Resposta
```bash
curl -X PUT http://localhost:5000/api/emails/responses/456 \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Novo assunto editado",
    "body_text": "Corpo da resposta editado"
  }'
```

### Criação de Rascunhos

#### Criar Rascunho no Gmail (SEM ENVIO)
```bash
curl -X POST http://localhost:5000/api/emails/123/create-draft \
  -H "Content-Type: application/json"
```

### Aprendizado

#### Atualizar Aprendizado com Emails Enviados
```bash
curl -X POST http://localhost:5000/api/emails/learning/update-from-sent \
  -H "Content-Type: application/json" \
  -d '{
    "account": "contato",
    "days_back": 30
  }'
```

### Processamento

#### Processar Emails (SEM MARCAR COMO LIDO)
```bash
curl -X POST http://localhost:5000/api/emails/process \
  -H "Content-Type: application/json" \
  -d '{
    "account": "contato",
    "max_emails": 50
  }'
```

### Ações em Lote

#### Marcar Emails para Resposta
```bash
curl -X POST http://localhost:5000/api/emails/bulk-actions \
  -H "Content-Type: application/json" \
  -d '{
    "email_ids": [123, 124, 125],
    "action": "mark_for_response"
  }'
```

#### Pular Resposta para Emails
```bash
curl -X POST http://localhost:5000/api/emails/bulk-actions \
  -H "Content-Type: application/json" \
  -d '{
    "email_ids": [126, 127],
    "action": "skip_response"
  }'
```

## Configurações Importantes

### Gmail API Scopes Necessários
```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',    # Ler emails
    'https://www.googleapis.com/auth/gmail.send',       # Enviar emails
    'https://www.googleapis.com/auth/gmail.modify'      # Modificar labels/status
]
```

### Variáveis de Ambiente
```
GMAIL_CREDENTIALS_FILE=config/gmail_credentials.json
GMAIL_TOKEN_DIR=config/tokens
OPENAI_API_KEY=sua_chave_openai
AI_MODEL=gpt-4
```

## Próximos Passos

1. **Testar funcionalidades** em ambiente de desenvolvimento
2. **Migrar banco de dados** para incluir novos campos
3. **Atualizar interface** para incluir novos controles
4. **Treinar usuários** no novo fluxo de trabalho
5. **Monitorar aprendizado** e ajustar conforme necessário

## Conclusão

A implementação garante que o usuário tenha controle total sobre:
- ✅ Quais emails são marcados como lidos
- ✅ Quais emails recebem resposta
- ✅ Quando as respostas são enviadas
- ✅ Como a IA aprende e melhora

O sistema agora funciona como um assistente inteligente que **sugere** e **prepara**, mas **nunca age automaticamente** sem aprovação explícita do usuário.
