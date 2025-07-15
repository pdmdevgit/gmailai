# Fix para MySQL Health Check Failure

## Problema Identificado

```
Container mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030  Error
dependency failed to start: container mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030 is unhealthy
```

**Status:** MySQL container está falhando no health check, impedindo que web e monitor iniciem.

## Causa Provável

O health check do MySQL está muito restritivo ou as credenciais estão incorretas.

## Solução Imediata

### **1. Verificar Docker Compose Health Check**

<read_file>
<path>gmail-ai-agent/docker-compose.yml</path>
</read_file>

### **2. Ajustar Health Check do MySQL**

Vou corrigir o health check para ser mais robusto:

```yaml
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: root_password_123
    MYSQL_DATABASE: gmail_ai_agent
    MYSQL_USER: gmail_ai_user
    MYSQL_PASSWORD: gmail_ai_pass
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-proot_password_123"]
    timeout: 20s
    retries: 10
    interval: 10s
    start_period: 40s
```

### **3. Comandos de Debug**

```bash
# Ver logs do MySQL
docker logs mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030

# Testar conexão manual
docker exec mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030 mysqladmin ping -h localhost -u root -p

# Ver status do health check
docker inspect mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030 | grep -A 10 Health
```

## Soluções Alternativas

### **Opção 1: Health Check Simplificado**
```yaml
healthcheck:
  test: ["CMD-SHELL", "mysqladmin ping -h localhost || exit 1"]
  timeout: 10s
  retries: 5
  interval: 10s
  start_period: 30s
```

### **Opção 2: Sem Health Check (Temporário)**
```yaml
# Comentar ou remover healthcheck temporariamente
# healthcheck:
#   test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
```

### **Opção 3: Health Check com TCP**
```yaml
healthcheck:
  test: ["CMD-SHELL", "nc -z localhost 3306 || exit 1"]
  timeout: 5s
  retries: 5
  interval: 10s
  start_period: 30s
```

## Variáveis de Ambiente Necessárias

Adicione no Coolify:

```env
MYSQL_ROOT_PASSWORD=root_password_123
MYSQL_DATABASE=gmail_ai_agent
MYSQL_USER=gmail_ai_user
MYSQL_PASSWORD=gmail_ai_pass
MYSQL_HOST=mysql
```

## Comandos para Executar

### **1. Ver Logs do MySQL**
```bash
docker logs mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030
```

### **2. Testar Conectividade**
```bash
# Dentro do container MySQL
docker exec -it mysql-awk0k4so0cgkc8gk00oc0kgo-010209682030 /bin/bash

# Testar conexão
mysql -u root -p
# Senha: root_password_123

# Verificar banco
SHOW DATABASES;
USE gmail_ai_agent;
SHOW TABLES;
```

### **3. Rebuild com Health Check Corrigido**
```bash
# Parar tudo
docker-compose down -v

# Rebuild
docker-compose build --no-cache

# Subir novamente
docker-compose up -d
```

## Próximos Passos

1. **Verificar logs do MySQL** para identificar erro específico
2. **Ajustar health check** conforme necessário
3. **Testar conectividade** manual
4. **Fazer redeploy** com correções

## Health Check Recomendado (Final)

```yaml
mysql:
  image: mysql:8.0
  environment:
    MYSQL_ROOT_PASSWORD: root_password_123
    MYSQL_DATABASE: gmail_ai_agent
    MYSQL_USER: gmail_ai_user
    MYSQL_PASSWORD: gmail_ai_pass
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-proot_password_123"]
    timeout: 20s
    retries: 10
    interval: 15s
    start_period: 60s  # Mais tempo para MySQL inicializar
  volumes:
    - mysql-data:/var/lib/mysql
    - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
```

Este health check:
- ✅ Usa credenciais corretas
- ✅ Timeout maior (20s)
- ✅ Mais tentativas (10)
- ✅ Start period maior (60s)
- ✅ Intervalo adequado (15s)
