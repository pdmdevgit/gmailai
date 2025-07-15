# Troubleshooting: Containers em Restart Loop 🔄

## 🚨 **Problema Identificado**

Seus containers estão em **restart loop**:
- `web-f04ww0cgw084os08k4wk4g08` - Restarting (1)
- `monitor-f04ww0cgw084os08k4wk4g08` - Restarting (1)

Isso significa que a aplicação está **crashando** logo após iniciar.

---

## 🔍 **Diagnóstico Imediato**

### **1. Ver Logs dos Containers:**
```bash
# Logs do container web (aplicação principal)
docker logs web-f04ww0cgw084os08k4wk4g08-014528469641

# Logs do container monitor
docker logs monitor-f04ww0cgw084os08k4wk4g08-014528483294

# Ver logs em tempo real
docker logs -f web-f04ww0cgw084os08k4wk4g08-014528469641
```

### **2. Verificar Variáveis de Ambiente:**
```bash
# Ver variáveis do container web
docker inspect web-f04ww0cgw084os08k4wk4g08-014528469641 | grep -A 20 "Env"
```

---

## 🛠️ **Possíveis Causas e Soluções**

### **Causa 1: Variáveis de Ambiente Faltando**
**Sintomas:** Erro de configuração, chaves de API não encontradas

**Solução:**
1. **No Coolify:** Vá para Environment Variables
2. **Adicione as variáveis obrigatórias:**
```env
OPENAI_API_KEY=sk-your-key-here
MYSQL_ROOT_PASSWORD=gmail_ai_root_pass
MYSQL_USER=gmail_ai_user
MYSQL_PASSWORD=gmail_ai_user_pass
MYSQL_DB=gmail_ai_agent
SECRET_KEY=your-super-secret-key-here
```

### **Causa 2: Banco de Dados Não Inicializado**
**Sintomas:** Erro de conexão MySQL, tabelas não existem

**Solução:**
```bash
# Conectar no container MySQL
docker exec -it mysql-f04ww0cgw084os08k4wk4g08-014528458865 mysql -u root -p

# Verificar se database existe
SHOW DATABASES;

# Se não existir, criar:
CREATE DATABASE gmail_ai_agent;
USE gmail_ai_agent;

# Sair
exit
```

### **Causa 3: Dependências Python Faltando**
**Sintomas:** ModuleNotFoundError, ImportError

**Solução:**
```bash
# Rebuild da imagem
docker-compose build --no-cache web
docker-compose up -d
```

### **Causa 4: Porta Já Em Uso**
**Sintomas:** Address already in use

**Solução:**
```bash
# Ver processos usando porta 5000
lsof -i :5000
netstat -tlnp | grep :5000

# Matar processo se necessário
kill -9 PID_DO_PROCESSO
```

---

## 🚀 **Soluções Rápidas**

### **Solução 1: Restart Completo**
```bash
# Parar todos os containers do projeto
docker stop $(docker ps | grep f04ww0cgw084os08k4wk4g08 | awk '{print $1}')

# Remover containers
docker rm $(docker ps -a | grep f04ww0cgw084os08k4wk4g08 | awk '{print $1}')

# No Coolify: Redeploy do projeto
```

### **Solução 2: Verificar Configuração no Coolify**
1. **Acesse Coolify:** `http://31.97.84.68:8000`
2. **Vá para seu projeto** Gmail AI Agent
3. **Verifique Environment Variables**
4. **Adicione variáveis faltando**
5. **Redeploy**

### **Solução 3: Debug Manual**
```bash
# Executar container manualmente para debug
docker run -it --rm f04ww0cgw084os08k4wk4g08-web /bin/bash

# Dentro do container, testar:
python app.py
```

---

## 📋 **Comandos de Debug Completo**

### **Execute estes comandos e me envie a saída:**

```bash
# 1. Logs detalhados dos containers
echo "=== LOGS WEB CONTAINER ==="
docker logs --tail=50 web-f04ww0cgw084os08k4wk4g08-014528469641

echo "=== LOGS MONITOR CONTAINER ==="
docker logs --tail=50 monitor-f04ww0cgw084os08k4wk4g08-014528483294

echo "=== LOGS MYSQL CONTAINER ==="
docker logs --tail=20 mysql-f04ww0cgw084os08k4wk4g08-014528458865

# 2. Verificar variáveis de ambiente
echo "=== ENVIRONMENT VARIABLES ==="
docker inspect web-f04ww0cgw084os08k4wk4g08-014528469641 | grep -A 30 '"Env"'

# 3. Verificar conectividade MySQL
echo "=== MYSQL CONNECTION TEST ==="
docker exec mysql-f04ww0cgw084os08k4wk4g08-014528458865 mysql -u root -pgmail_ai_root_pass -e "SHOW DATABASES;"
```

---

## 🎯 **Configuração Mínima Necessária**

### **No Coolify, certifique-se de ter estas variáveis:**

```env
# Obrigatórias para funcionar
MYSQL_ROOT_PASSWORD=gmail_ai_root_pass
MYSQL_USER=gmail_ai_user
MYSQL_PASSWORD=gmail_ai_user_pass
MYSQL_DB=gmail_ai_agent
SECRET_KEY=your-super-secret-key-here

# Para funcionalidades completas (pode adicionar depois)
OPENAI_API_KEY=sk-your-openai-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

## 🔧 **Próximos Passos**

1. **Execute os comandos de debug** acima
2. **Me envie os logs** para identificar o erro específico
3. **Verifique variáveis** no Coolify
4. **Redeploy** após correções

### **Muito Provável:**
O problema é **variáveis de ambiente faltando** ou **configuração incorreta** no Coolify.

### **Acesso ao Coolify:**
- URL: `http://31.97.84.68:8000`
- Vá para Environment Variables do projeto
- Adicione as variáveis obrigatórias
- Redeploy

**Execute os comandos de debug e me envie os resultados para resolvermos rapidamente!**
