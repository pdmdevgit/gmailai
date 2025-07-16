#!/bin/bash

echo "🔄 FORÇANDO LIMPEZA COMPLETA DE CACHE - Gmail AI Agent"
echo "=================================================="

# Get container ID
CONTAINER_ID=$(docker ps | grep gmail-ai-agent | awk '{print $1}' | head -1)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Container não encontrado. Tentando encontrar por nome..."
    CONTAINER_ID=$(docker ps -a | grep -E "(gmail|ai|agent)" | awk '{print $1}' | head -1)
fi

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Nenhum container encontrado!"
    echo "📋 Containers disponíveis:"
    docker ps -a
    exit 1
fi

echo "🎯 Container encontrado: $CONTAINER_ID"

echo ""
echo "1️⃣ Parando container..."
docker stop $CONTAINER_ID

echo ""
echo "2️⃣ Removendo container..."
docker rm $CONTAINER_ID

echo ""
echo "3️⃣ Limpando cache do Docker..."
docker system prune -f

echo ""
echo "4️⃣ Removendo imagens antigas..."
docker image prune -f

echo ""
echo "5️⃣ Reconstruindo imagem..."
cd /root/gmail-ai-agent
docker build --no-cache -t gmail-ai-agent .

echo ""
echo "6️⃣ Iniciando novo container..."
docker run -d \
  --name gmail-ai-agent-new \
  --restart unless-stopped \
  -p 5000:5000 \
  -e MYSQL_HOST=mysql \
  -e MYSQL_USER=gmail_ai_user \
  -e MYSQL_PASSWORD=gmail_ai_pass_2024_secure \
  -e MYSQL_DB=gmail_ai_agent \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e FLASK_ENV=production \
  --network coolify \
  gmail-ai-agent

echo ""
echo "7️⃣ Aguardando inicialização..."
sleep 10

echo ""
echo "8️⃣ Verificando status..."
NEW_CONTAINER_ID=$(docker ps | grep gmail-ai-agent | awk '{print $1}' | head -1)
if [ ! -z "$NEW_CONTAINER_ID" ]; then
    echo "✅ Container iniciado com sucesso: $NEW_CONTAINER_ID"
    echo ""
    echo "📊 Status do container:"
    docker ps | grep gmail-ai-agent
    echo ""
    echo "📋 Logs recentes:"
    docker logs --tail=10 $NEW_CONTAINER_ID
else
    echo "❌ Falha ao iniciar container!"
    echo "📋 Logs de erro:"
    docker logs gmail-ai-agent-new
fi

echo ""
echo "🎉 PROCESSO CONCLUÍDO!"
echo "🌐 Acesse: https://gmailai.devpdm.com"
echo "💡 Dica: Use Ctrl+Shift+R para forçar refresh no browser"
echo ""
echo "🔍 Para monitorar logs em tempo real:"
echo "docker logs -f \$(docker ps | grep gmail-ai-agent | awk '{print \$1}')"
