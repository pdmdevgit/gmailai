# Troubleshooting de Acesso à Aplicação

## Problema: Não consegue acessar a aplicação

### Sintomas:
- ❌ `gmailai.pdmdev.com` não acessível
- ❌ `http://31.97.84.68:5000` não acessível
- ✅ Deploy concluído com sucesso no Coolify

## Diagnóstico Passo a Passo

### 1. Verificar Status dos Containers no Coolify

1. **Acesse o painel do Coolify**
2. **Vá para seu projeto Gmail AI Agent**
3. **Verifique a aba "Containers" ou "Services"**
4. **Confirme se todos estão "Running":**
   - ✅ MySQL: Running
   - ✅ Redis: Running  
   - ✅ Web: Running
   - ✅ Monitor: Running

### 2. Verificar Logs dos Containers

#### **Logs do Container Web:**
```bash
# No painel do Coolify, clique em "Logs" do container web
# Procure por estas mensagens:
Starting Gmail AI Agent on 0.0.0.0:5000
Database tables created successfully
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://[::]:5000
```

#### **Mensagens de Erro Comuns:**
```bash
# Se vir estes erros:
ModuleNotFoundError: No module named 'app'
ImportError: cannot import name 'create_app'
mysql.connector.errors.DatabaseError: 2003 (HY000): Can't connect to MySQL server
```

### 3. Verificar Configuração de Rede no Coolify

#### **Opção A: Verificar Portas Expostas**
1. **Vá para "Settings" do projeto**
2. **Procure por "Port Configuration" ou "Exposed Ports"**
3. **Confirme se está configurado:**
   - Container Port: `5000`
   - Host Port: `5000` (ou outra porta)
   - Protocol: `HTTP`

#### **Opção B: Verificar Domínios**
1. **Vá para "Domains" ou "URLs"**
2. **Verifique se há um domínio configurado**
3. **Se não houver, adicione um:**
   - Domain: `gmailai.pdmdev.com`
   - Port: `5000`
   - SSL: Enabled

### 4. Testar Conectividade Direta

#### **Teste SSH no VPS:**
```bash
# Conecte via SSH ao seu VPS
ssh root@31.97.84.68

# Verifique se a porta 5000 está aberta
netstat -tlnp | grep :5000

# Teste local no VPS
curl http://localhost:5000/ping
curl http://127.0.0.1:5000/ping
```

#### **Teste de Firewall:**
```bash
# Verifique regras do firewall
ufw status
iptables -L

# Se necessário, abra a porta 5000
ufw allow 5000
```

### 5. Configuração de Proxy Reverso

Se o Coolify usa proxy reverso interno, pode ser necessário configurar:

#### **Verificar Configuração do Coolify:**
1. **Procure por "Proxy" ou "Traefik" nas configurações**
2. **Verifique se há labels corretos:**
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.gmailai.rule=Host(`gmailai.pdmdev.com`)"
     - "traefik.http.services.gmailai.loadbalancer.server.port=5000"
   ```

### 6. Soluções Específicas

#### **Solução 1: Recriar o Serviço**
1. **No Coolify, vá para "Settings"**
2. **Clique em "Redeploy" ou "Restart"**
3. **Aguarde o deploy completo**
4. **Teste novamente**

#### **Solução 2: Configurar Domínio Manualmente**
1. **Vá para "Domains"**
2. **Adicione:**
   - Domain: `gmailai.pdmdev.com`
   - Target: `http://web:5000`
   - SSL: Auto

#### **Solução 3: Usar IP + Porta Específica**
Se o Coolify atribuiu uma porta diferente:
```bash
# Verifique qual porta foi atribuída
# No painel do Coolify, procure por "External Port"
# Pode ser algo como:
http://31.97.84.68:32768
http://31.97.84.68:8080
```

### 7. Verificar Configuração DNS

#### **Para gmailai.pdmdev.com:**
```bash
# Verifique se o DNS está apontando corretamente
nslookup gmailai.pdmdev.com
dig gmailai.pdmdev.com

# Deve retornar:
# gmailai.pdmdev.com. IN A 31.97.84.68
```

#### **Configurar DNS (se necessário):**
1. **Acesse o painel de DNS do domínio pdmdev.com**
2. **Adicione registro A:**
   - Name: `gmailai`
   - Type: `A`
   - Value: `31.97.84.68`
   - TTL: `300`

### 8. Teste Final

Após aplicar as correções, teste nesta ordem:

```bash
# 1. Teste local no VPS
curl http://localhost:5000/ping

# 2. Teste por IP externo
curl http://31.97.84.68:5000/ping

# 3. Teste por domínio
curl http://gmailai.pdmdev.com/ping

# 4. Teste HTTPS (se SSL configurado)
curl https://gmailai.pdmdev.com/ping
```

### 9. Resposta Esperada

Quando funcionando corretamente, você deve ver:

```json
{
  "status": "ok",
  "timestamp": "2025-01-15T00:30:00.000000"
}
```

### 10. Próximos Passos

Após resolver o acesso:

1. **Teste o dashboard:** `https://sua-url/`
2. **Verifique health:** `https://sua-url/health`
3. **Configure as chaves de API** no Coolify
4. **Teste funcionalidades** da aplicação

## Comandos de Debug Úteis

```bash
# Ver logs em tempo real
docker logs -f container_name

# Entrar no container
docker exec -it container_name /bin/bash

# Verificar processos
docker ps -a

# Verificar redes
docker network ls
docker network inspect network_name
```

## Contato para Suporte

Se o problema persistir:
1. **Copie os logs** dos containers
2. **Faça screenshot** das configurações do Coolify
3. **Teste os comandos** de debug acima
4. **Documente** os resultados para análise
