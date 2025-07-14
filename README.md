# 🚀 Gmail AI Agent

Sistema de automação de emails com IA e aprendizado baseado no histórico para Prof. Diogo Moreira.

## 📋 Sobre o Projeto

O Gmail AI Agent é um sistema inteligente que monitora e responde automaticamente emails de 4 contas Gmail do domínio @profdiogomoreira.com.br, utilizando IA para gerar respostas personalizadas baseadas no histórico de comunicações.

### 🎯 Objetivos Principais

- **Agilizar respostas** para interessados em cursos de preparação para concursos públicos
- **Melhorar qualidade** das respostas baseando-se no estilo do Prof. Diogo
- **Classificar automaticamente** tipos de emails (vendas, suporte, informações)
- **Gerar rascunhos inteligentes** que mantenham o tom profissional e persuasivo

## 🧠 Sistema de Aprendizado

### **Funcionalidades de Learning**

- ✅ **Análise do histórico** de emails enviados (últimos 90 dias)
- ✅ **Extração de padrões** de saudação, despedida e estilo único
- ✅ **Busca por similaridade** usando algoritmos TF-IDF
- ✅ **Context awareness** para threads de conversa
- ✅ **Geração inteligente** mantendo personalidade
- ✅ **Sistema de feedback** para melhoria contínua

### **Como o Sistema Aprende**

1. **Análise**: Lê histórico de emails enviados
2. **Extração**: Identifica padrões únicos de comunicação
3. **Similaridade**: Encontra respostas similares para contexto
4. **Contexto**: Analisa thread completa da conversa
5. **Geração**: Cria resposta mantendo estilo pessoal
6. **Feedback**: Aprende com resultados para melhorar

## 🏗️ Arquitetura

### **Stack Tecnológico**
- **Backend**: Python Flask
- **Frontend**: HTML5 + JavaScript + Bootstrap
- **Database**: MySQL
- **Queue**: Redis
- **AI**: OpenAI GPT-4 / Anthropic Claude
- **Email**: Gmail API
- **Deploy**: Docker + Coolify

### **Contas Monitoradas**
- `contato@profdiogomoreira.com.br` - Contatos gerais e vendas
- `cursos@profdiogomoreira.com.br` - Informações sobre cursos
- `diogo@profdiogomoreira.com.br` - Comunicação direta
- `sac@profdiogomoreira.com.br` - Suporte ao cliente

## 🚀 Deploy

### **Servidor**
- **IP**: `31.97.84.68`
- **Domínio**: `gmailai.devpdm.com`
- **Painel**: Coolify

### **Guias de Deploy**
- 📖 `GITHUB_REPO_SETUP.md` - Configuração inicial do repositório
- 📖 `COOLIFY_PRIVATE_REPO_GUIDE.md` - Deploy detalhado no Coolify
- 📖 `QUICK_DEPLOY_GUIDE.md` - Deploy rápido em 6 passos
- 📖 `FINAL_DEPLOYMENT_INFO.md` - Informações consolidadas

## 🔧 Configuração Local

### **Pré-requisitos**
- Python 3.9+
- MySQL
- Redis
- Gmail API credentials
- OpenAI/Anthropic API keys

### **Instalação**
```bash
# Clone do repositório
git clone https://github.com/pdmdevgit/gmailai.git
cd gmailai

# Instalar dependências
pip install -r requirements.txt

# Configurar environment variables
cp .env.example .env
# Editar .env com suas credenciais

# Inicializar database
mysql -u root -p < database/init.sql

# Executar aplicação
python app.py
```

## 📊 APIs Disponíveis

### **Core APIs**
- `GET /health` - Health check geral
- `GET /` - Dashboard principal
- `GET /api/emails` - Listar emails
- `POST /api/emails/process` - Processar email

### **Learning APIs**
- `GET /api/learning/health` - Health check do learning
- `GET /api/learning/stats` - Estatísticas gerais
- `GET /api/learning/analyze/{account}` - Análise de conta
- `POST /api/learning/similar-responses` - Buscar similares
- `POST /api/learning/generate-with-learning` - Gerar com aprendizado
- `POST /api/learning/feedback` - Sistema de feedback

## 🔐 Segurança

### **Repositório Privado**
- Código e credenciais protegidos
- Acesso controlado via Personal Access Token
- Environment variables seguras
- Compliance com LGPD

### **Configuração de Acesso**
1. Personal Access Token com scopes: `repo`, `read:org`, `user:email`
2. Environment variables via Coolify
3. SSL/TLS automático via Let's Encrypt
4. Firewall e monitoramento ativo

## 📈 Métricas de Sucesso

- **Response Time**: < 2 minutos para classificação
- **Accuracy**: > 85% de respostas aprovadas sem edição
- **Coverage**: 70%+ dos emails classificados automaticamente
- **Uptime**: 99.5% de disponibilidade
- **Performance**: Suporte a 100+ emails/dia por conta

## 🎯 Business Logic

### **Produtos**
- **Coaching Individual**: R$ 1.497 (mentoria personalizada)
- **Acelerador**: R$ 497 (curso metodologia)

### **Diferencial**
- Aprovação em 9 meses (vs média 3-5 anos)
- Metodologia testada e comprovada
- Foco em concursos fiscais de alta remuneração
- Approach psicológico + técnico

### **Cases de Sucesso**
- Vitória Barbosa (SEFAZ-BA)
- Thales (TCE-RS, MPU, TRF-3, TRF-4, TRE-PA)
- Histórico de aprovações em carreiras top

## 📚 Documentação

### **Documentos Técnicos**
- `LEARNING_SYSTEM.md` - Sistema de aprendizado detalhado
- `LEARNING_IMPLEMENTATION_SUMMARY.md` - Resumo da implementação
- `VPS_PANEL_RECOMMENDATION.md` - Análise de painéis
- `TESTING_REPORT.md` - Relatório de testes

### **Documentos de Deploy**
- `GITHUB_REPO_SETUP.md` - Setup do repositório
- `COOLIFY_PRIVATE_REPO_GUIDE.md` - Deploy no Coolify
- `DEPLOY_CONFIG.md` - Configurações específicas
- `FINAL_DEPLOYMENT_INFO.md` - Informações finais

## 🤝 Contribuição

Este é um repositório privado para uso exclusivo do Prof. Diogo Moreira. 

### **Desenvolvimento**
- Branch principal: `main`
- Deploy automático via webhook
- Testes obrigatórios antes de merge
- Code review necessário

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema:
- **Email**: suporte@profdiogomoreira.com.br
- **Sistema**: https://gmailai.devpdm.com
- **Monitoramento**: Via Coolify dashboard

## 📄 Licença

Propriedade privada do Prof. Diogo Moreira. Todos os direitos reservados.

---

**🚀 Gmail AI Agent - Automatizando comunicações com inteligência artificial e aprendizado contínuo!**
