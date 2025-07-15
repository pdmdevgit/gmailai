# MySQL Password Fix - Remover @ das Senhas

## Problema Identificado
O símbolo `@` nas senhas está causando problemas no parsing da URL de conexão MySQL, pois o `@` é usado como separador entre credenciais e hostname na URL.

## Senhas Atuais Problemáticas
- `MYSQL_ROOT_PASSWORD=S3cureR00tP@ssw0rd!2024` (contém @)
- `MYSQL_PASSWORD=Us3rP-ssw0rd!2024` (já foi corrigida, mas vamos simplificar mais)

## Novas Senhas Recomendadas (sem @)
- `MYSQL_ROOT_PASSWORD=S3cureR00tPass2024` 
- `MYSQL_PASSWORD=Us3rPassword2024`

## Passos para Aplicar a Correção

### 1. No Painel do Coolify
Acesse as variáveis de ambiente do seu projeto e altere:

**MySQL Service:**
- `MYSQL_ROOT_PASSWORD` → `S3cureR00tPass2024`
- `MYSQL_PASSWORD` → `Us3rPassword2024`

**Web Application:**
- `MYSQL_PASSWORD` → `Us3rPassword2024`

### 2. Forçar Rebuild dos Containers
Após alterar as senhas, você precisa:
1. Parar todos os containers
2. Remover os volumes do MySQL (para recriar com novas senhas)
3. Fazer rebuild completo

### 3. Comandos para Executar no VPS
```bash
# Parar containers
docker stop $(docker ps -q)

# Remover containers
docker rm $(docker ps -aq)

# Remover volumes MySQL (CUIDADO: isso apaga os dados!)
docker volume prune -f

# O Coolify irá recriar tudo automaticamente
```

## Vantagens das Novas Senhas
- ✅ Sem símbolos `@` que confundem o parser de URL
- ✅ Ainda seguras com maiúsculas, minúsculas e números
- ✅ Mantêm caracteres especiais seguros como `!` e números
- ✅ Fáceis de usar em URLs de conexão

## URL de Conexão Resultante
```
mysql+pymysql://gmail_ai_user:Us3rPassword2024@mysql:3306/gmail_ai_agent
```

## Teste de Validação
Após aplicar as mudanças, a aplicação deve:
1. Conectar no MySQL sem erros de parsing
2. Criar as tabelas automaticamente
3. Iniciar sem loops de restart
