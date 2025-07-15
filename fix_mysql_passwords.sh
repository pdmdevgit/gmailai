#!/bin/bash

echo "=== MySQL Password Fix Script ==="
echo "Este script irá corrigir as senhas MySQL removendo o símbolo @ problemático"
echo ""

# Verificar se estamos no servidor correto
if [ ! -f /etc/hostname ] || [ "$(cat /etc/hostname)" != "devpdm" ]; then
    echo "❌ Este script deve ser executado no servidor VPS (devpdm)"
    exit 1
fi

echo "✅ Executando no servidor correto"
echo ""

# Parar containers atuais
echo "🛑 Parando containers atuais..."
docker stop $(docker ps -q --filter "name=web-f04ww0cgw084os08k4wk4g08")
docker stop $(docker ps -q --filter "name=mysql-f04ww0cgw084os08k4wk4g08")

echo "🗑️  Removendo containers antigos..."
docker rm $(docker ps -aq --filter "name=web-f04ww0cgw084os08k4wk4g08")
docker rm $(docker ps -aq --filter "name=mysql-f04ww0cgw084os08k4wk4g08")

echo "💾 Removendo volumes MySQL (para recriar com novas senhas)..."
docker volume ls | grep f04ww0cgw084os08k4wk4g08 | awk '{print $2}' | xargs -r docker volume rm

echo "🧹 Limpando imagens não utilizadas..."
docker image prune -f

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📋 PRÓXIMOS PASSOS MANUAIS:"
echo "1. Acesse o painel do Coolify"
echo "2. Vá para as variáveis de ambiente do projeto"
echo "3. Altere as seguintes variáveis:"
echo "   - MYSQL_ROOT_PASSWORD: S3cureR00tPass2024"
echo "   - MYSQL_PASSWORD: Us3rPassword2024"
echo "4. Salve as alterações"
echo "5. Force um redeploy do projeto"
echo ""
echo "🔄 O Coolify irá recriar todos os containers automaticamente com as novas senhas"
echo ""
