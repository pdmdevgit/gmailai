# Gmail AI Agent - Estrutura do Projeto

## 📁 Estrutura Completa de Arquivos

```
gmail-ai-agent/
├── 📄 README.md                          # Documentação principal
├── 📄 requirements.txt                   # Dependências Python
├── 📄 .env.example                       # Exemplo de variáveis de ambiente
├── 📄 app.py                            # Aplicação Flask principal
├── 📄 monitor.py                        # Serviço de monitoramento
├── 📄 install.sh                        # Script de instalação automatizada
├── 📄 docker-compose.yml                # Configuração Docker
├── 📄 Dockerfile                        # Imagem Docker
├── 📄 project_structure.md              # Este arquivo
│
├── 📁 app/                              # Aplicação principal
│   ├── 📄 __init__.py                   # Factory da aplicação Flask
│   ├── 📄 routes.py                     # Rotas principais
│   │
│   ├── 📁 models/                       # Modelos de dados
│   │   └── 📄 __init__.py               # Modelos SQLAlchemy
│   │
│   ├── 📁 services/                     # Serviços de negócio
│   │   ├── 📄 gmail_service.py          # Integração Gmail API
│   │   ├── 📄 ai_service.py             # Integração IA (OpenAI/Claude)
│   │   └── 📄 email_processor.py        # Processamento de emails
│   │
│   ├── 📁 api/                          # APIs REST
│   │   ├── 📄 email_routes.py           # Endpoints de emails
│   │   ├── 📄 dashboard_routes.py       # Endpoints do dashboard
│   │   └── 📄 admin_routes.py           # Endpoints administrativos
│   │
│   └── 📁 templates/                    # Templates HTML
│       └── 📄 dashboard.html            # Interface principal
│
├── 📁 config/                           # Configurações
│   ├── 📄 config.py                     # Configurações da aplicação
│   ├── 📄 gmail_credentials.json        # Credenciais Gmail (não incluído)
│   └── 📁 tokens/                       # Tokens OAuth (criado automaticamente)
│
├── 📁 database/                         # Scripts de banco
│   └── 📄 init.sql                      # Inicialização do banco
│
├── 📁 static/                           # Arquivos estáticos
│   ├── 📁 css/
│   │   └── 📄 dashboard.css             # Estilos personalizados
│   ├── 📁 js/
│   │   └── 📄 dashboard.js              # JavaScript do dashboard
│   └── 📁 images/                       # Imagens (criado automaticamente)
│
├── 📁 nginx/                            # Configuração Nginx
│   └── 📄 nginx.conf                    # Configuração de produção
│
└── 📁 logs/                             # Logs (criado automaticamente)
    ├── 📄 gmail_ai_agent.log            # Log da aplicação
    ├── 📄 monitor.log                   # Log do monitor
    └── 📄 health.log                    # Log de health checks
```

## 🔧 Componentes Principais

### 1. **Aplicação Web (Flask)**
- **Arquivo**: `app.py`
- **Função**: Interface web principal e API REST
- **Porta**: 5000
- **Features**: Dashboard, gerenciamento de emails, aprovação de respostas

### 2. **Monitor de Emails**
- **Arquivo**: `monitor.py`
- **Função**: Processamento automático de emails
- **Execução**: Contínua (daemon)
- **Features**: Classificação IA, geração de respostas, monitoramento

### 3. **Serviços Core**

#### Gmail Service (`app/services/gmail_service.py`)
- Autenticação OAuth 2.0
- Leitura de emails
- Envio de respostas
- Gerenciamento de labels

#### AI Service (`app/services/ai_service.py`)
- Classificação de emails
- Geração de respostas
- Análise de sentimento
- Integração OpenAI/Claude

#### Email Processor (`app/services/email_processor.py`)
- Pipeline completo de processamento
- Orquestração de serviços
- Logging e métricas
- Aprovação automática

### 4. **Interface Web**

#### Dashboard (`app/templates/dashboard.html`)
- Visão geral do sistema
- Métricas em tempo real
- Gráficos interativos
- Gerenciamento de emails

#### API REST (`app/api/`)
- Endpoints para emails
- Dashboard data
- Administração
- Autenticação

### 5. **Banco de Dados**

#### Tabelas Principais:
- `emails`: Emails recebidos
- `email_responses`: Respostas geradas
- `email_templates`: Templates de resposta
- `processing_logs`: Logs de processamento
- `system_settings`: Configurações do sistema

## 🚀 Fluxo de Funcionamento

### 1. **Monitoramento**
```
Monitor → Gmail API → Novos Emails → Banco de Dados
```

### 2. **Classificação**
```
Email → AI Service → Classificação → Atualização BD
```

### 3. **Geração de Resposta**
```
Email Classificado → Template Selection → AI Generation → Rascunho
```

### 4. **Aprovação e Envio**
```
Rascunho → Interface Web → Aprovação → Gmail API → Envio
```

## 📊 Métricas e Monitoramento

### KPIs Principais:
- **Taxa de Processamento**: Emails processados/hora
- **Taxa de Classificação**: % de emails classificados automaticamente
- **Taxa de Aprovação**: % de respostas aprovadas sem edição
- **Tempo de Resposta**: Tempo médio de processamento
- **Confiança IA**: Média de confiança das classificações

### Logs e Auditoria:
- Todas as ações são logadas
- Métricas de performance
- Rastreamento de erros
- Auditoria LGPD

## 🔒 Segurança

### Autenticação:
- OAuth 2.0 para Gmail
- Tokens seguros
- Refresh automático

### Dados:
- Criptografia em trânsito (HTTPS)
- Backup automático
- Retenção configurável
- Compliance LGPD

### Acesso:
- Firewall configurado
- Rate limiting
- IP whitelisting (admin)
- SSL/TLS

## 🛠️ Deployment

### Opções de Deploy:

#### 1. **Docker (Recomendado)**
```bash
docker-compose up -d
```

#### 2. **Instalação Manual**
```bash
./install.sh
```

#### 3. **CyberPanel Integration**
- Script otimizado para CyberPanel
- Configuração automática
- SSL Let's Encrypt
- Nginx reverse proxy

## 📈 Escalabilidade

### Horizontal:
- Múltiplas instâncias do monitor
- Load balancer Nginx
- Redis para cache/queue

### Vertical:
- Otimização de queries
- Índices de banco
- Cache de templates
- Batch processing

## 🔄 Manutenção

### Automática:
- Cleanup de logs antigos
- Health checks
- Backup de dados
- Restart em falhas

### Manual:
- Atualização de templates
- Configuração de contas
- Monitoramento de métricas
- Análise de performance

## 📞 Suporte

### Comandos Úteis:
```bash
# Status do sistema
./status.sh

# Logs em tempo real
tail -f logs/gmail_ai_agent.log

# Health check
python monitor.py --health-check

# Processamento manual
python monitor.py --once

# Backup
curl -X POST http://localhost:5000/api/admin/system/backup
```

### Troubleshooting:
1. **Verificar logs**: `logs/gmail_ai_agent.log`
2. **Testar conectividade**: Health check endpoint
3. **Verificar credenciais**: Tokens OAuth
4. **Monitorar recursos**: CPU, memória, disco
5. **Validar configuração**: Variáveis de ambiente

## 🎯 Próximos Passos

### Pós-Instalação:
1. ✅ Configurar chaves de API
2. ✅ Autenticar contas Gmail
3. ✅ Testar classificação
4. ✅ Validar templates
5. ✅ Monitorar métricas

### Otimizações:
- A/B testing de templates
- Machine learning personalizado
- Integração com CRM
- Análise preditiva
- Automação avançada

---

**Gmail AI Agent v1.0** - Sistema completo de automação de emails com IA 🚀
