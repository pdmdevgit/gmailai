# Gmail AI Agent

Sistema de automação de emails com IA para monitoramento e resposta automática de 4 contas Gmail do domínio @profdiogomoreira.com.br.

## Visão Geral

O Gmail AI Agent é uma solução completa para automatizar respostas de emails focada no negócio de preparação para concursos públicos do Prof. Diogo Moreira. O sistema utiliza IA (OpenAI GPT-4 e Claude) para classificar emails e gerar respostas personalizadas.

## Funcionalidades Principais

### 📧 Monitoramento de Emails
- **4 Contas Gmail:** contato, cursos, diogo, sac @profdiogomoreira.com.br
- **Classificação Automática:** Por tipo, prioridade e produto de interesse
- **Processamento Inteligente:** Análise de sentimento e contexto

### 🤖 IA Integration
- **OpenAI GPT-4:** Geração de respostas personalizadas
- **Claude (Anthropic):** Alternativa de IA
- **Templates Inteligentes:** Baseados no estilo do Prof. Diogo
- **Aprendizado Contínuo:** Sistema de feedback

### 📊 Interface Web
- **Dashboard:** Estatísticas e métricas em tempo real
- **Aprovação:** Sistema de review antes do envio
- **Histórico:** Log completo de interações
- **Admin Panel:** Gerenciamento de contas e templates

### 💼 Business Logic
- **Produtos:** Coaching Individual (R$ 2.997) e Acelerador (R$ 497)
- **Nicho:** Concursos fiscais (SEFAZ, Receita Federal, TCE, TRF)
- **Tom:** Profissional, empático e motivador
- **Cases:** Depoimentos de sucesso integrados

## Arquitetura Técnica

### Stack Tecnológico
- **Backend:** Python Flask
- **Banco de Dados:** MySQL 8.0
- **Cache:** Redis
- **Frontend:** HTML5 + JavaScript + Bootstrap
- **IA APIs:** OpenAI GPT-4, Claude (Anthropic)
- **Email:** Gmail API + OAuth 2.0
- **Containerização:** Docker + Docker Compose

### Estrutura do Projeto
```
gmail-ai-agent/
├── app/                    # Aplicação Flask
│   ├── __init__.py
│   ├── routes.py
│   ├── api/               # APIs REST
│   ├── models/            # Modelos de dados
│   ├── services/          # Serviços (Gmail, IA, etc)
│   └── templates/         # Templates HTML
├── config/                # Configurações
├── database/              # Scripts SQL
├── static/                # CSS, JS, imagens
├── nginx/                 # Configuração Nginx
├── docker-compose.yml     # Orquestração containers
├── Dockerfile            # Build da aplicação
└── requirements.txt      # Dependências Python
```

## Instalação e Deploy

### Pré-requisitos
- Docker e Docker Compose
- Chaves de API (OpenAI, Google)
- VPS ou servidor com pelo menos 2GB RAM

### 1. Clone do Repositório
```bash
git clone https://github.com/pdmdevgit/gmailai.git
cd gmailai
```

### 2. Configuração de Variáveis
Crie um arquivo `.env`:
```env
# IA APIs
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Gmail API
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Banco de Dados
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_USER=gmail_ai_user
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=gmail_ai_agent

# Segurança
SECRET_KEY=your-super-secret-key-here
```

### 3. Deploy com Docker
```bash
# Build e inicialização
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f web
```

### 4. Configuração Inicial
1. Acesse `http://seu-servidor:5000`
2. Configure as 4 contas Gmail no admin
3. Personalize templates conforme necessário
4. Teste funcionalidades principais

## Configuração Gmail API

### 1. Google Cloud Console
1. Crie um projeto no Google Cloud Console
2. Ative a Gmail API
3. Crie credenciais OAuth 2.0
4. Configure URLs de redirecionamento

### 2. Configuração no Sistema
1. Acesse `/admin` na aplicação
2. Vá para "Gmail Accounts"
3. Adicione cada conta com suas credenciais
4. Autorize acesso via OAuth

## Templates de Email

### Tipos Disponíveis
1. **Interesse em Coaching** - Respostas persuasivas
2. **Dúvidas sobre Acelerador** - Informações técnicas
3. **Questões de Metodologia** - Respostas educativas
4. **Problemas Técnicos** - Suporte estruturado
5. **Follow-up de Vendas** - Sequências nurturing
6. **Agendamento** - Integração com calendário

### Personalização
- Tom profissional do Prof. Diogo
- Depoimentos de aprovados
- CTAs específicos por produto
- Metodologia dos 9 passos

## Monitoramento e Logs

### Logs Disponíveis
```bash
# Logs da aplicação
docker-compose logs web

# Logs do monitor
docker-compose logs monitor

# Logs do banco
docker-compose logs mysql
```

### Métricas
- Emails processados por dia
- Taxa de aprovação de rascunhos
- Tempo de resposta médio
- Conversão por tipo de email

## Manutenção

### Backup
```bash
# Backup do banco de dados
docker exec mysql_container mysqldump -u root -p gmail_ai_agent > backup.sql

# Backup de tokens
cp -r config/tokens/ backup_tokens/
```

### Atualizações
```bash
# Atualizar código
git pull origin main

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

## ROI Esperado

### Benefícios
- **30-50% aumento** na conversão de leads
- **80% redução** no tempo de resposta
- **Melhoria na qualidade** das respostas
- **Escalabilidade** para alto volume

### Métricas de Sucesso
- Response Time < 2 minutos
- Accuracy > 85% de aprovação
- Coverage > 70% de classificação automática
- Uptime > 99.5%

## Suporte e Documentação

### Arquivos de Referência
- `project_structure.md` - Estrutura detalhada
- `LEARNING_SYSTEM.md` - Sistema de aprendizado IA
- `VPS_PANEL_RECOMMENDATION.md` - Recomendações de VPS

### Troubleshooting
1. Verificar logs dos containers
2. Testar conectividade com APIs
3. Validar configurações de ambiente
4. Verificar permissões Gmail API

## Licença

Este projeto é proprietário e desenvolvido especificamente para o negócio do Prof. Diogo Moreira.
