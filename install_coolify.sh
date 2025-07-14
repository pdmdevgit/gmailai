#!/bin/bash

# Gmail AI Agent - Installation Script for Coolify
# Optimized deployment for modern container-based hosting

set -e

echo "🚀 Gmail AI Agent - Coolify Installation Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

print_header "1. Environment Setup"

# Create project directory
PROJECT_DIR="$HOME/gmail-ai-agent"
print_status "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create necessary directories
print_status "Creating directory structure..."
mkdir -p {config/tokens,logs,database,static/{css,js,images},app/{api,services,models,templates}}

print_header "2. Environment Configuration"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating environment configuration file..."
    cat > .env << EOF
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Database Configuration
DATABASE_URL=mysql://gmail_user:$(openssl rand -hex 16)@db:3306/gmail_ai_agent
MYSQL_ROOT_PASSWORD=$(openssl rand -hex 16)
MYSQL_DATABASE=gmail_ai_agent
MYSQL_USER=gmail_user
MYSQL_PASSWORD=$(openssl rand -hex 16)

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=/app/config/credentials.json
GMAIL_TOKEN_DIR=/app/config/tokens

# AI API Configuration (CONFIGURE THESE)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
AI_MODEL=gpt-4

# Email Accounts Configuration
GMAIL_ACCOUNTS=contato,cursos,diogo,sac
DOMAIN=gmailai.devpdm.com
VPS_IP=31.97.84.68

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
APP_NAME=Gmail AI Agent
APP_VERSION=1.0.0
LOG_LEVEL=INFO

# Monitoring Configuration
ENABLE_MONITORING=true
HEALTH_CHECK_INTERVAL=300

# Learning System Configuration
LEARNING_ENABLED=true
LEARNING_HISTORY_DAYS=90
LEARNING_MIN_SIMILARITY=0.3
EOF
    print_status "Environment file created. Please update API keys in .env"
else
    print_warning ".env file already exists. Skipping creation."
fi

print_header "3. Docker Configuration"

# Create optimized Dockerfile for Coolify
print_status "Creating optimized Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p logs config/tokens static/uploads

# Set permissions
RUN chmod +x *.sh || true

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
EOF

# Create Docker Compose for Coolify
print_status "Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GMAIL_CREDENTIALS_FILE=${GMAIL_CREDENTIALS_FILE}
      - GMAIL_TOKEN_DIR=${GMAIL_TOKEN_DIR}
      - FLASK_ENV=${FLASK_ENV}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - gmail_uploads:/app/static/uploads
    depends_on:
      - db
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "3306:3306"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
  gmail_uploads:

networks:
  default:
    name: gmail-ai-agent-network
EOF

print_header "4. Coolify Configuration"

# Create Coolify configuration
print_status "Creating Coolify deployment configuration..."
cat > coolify.json << 'EOF'
{
  "name": "gmail-ai-agent",
  "description": "Gmail AI Agent with Learning System",
  "repository": {
    "url": "https://github.com/pdmdevgit/gmailai",
    "branch": "main",
    "auto_deploy": true
  },
  "build": {
    "command": "docker-compose build",
    "dockerfile": "Dockerfile"
  },
  "deploy": {
    "command": "docker-compose up -d",
    "healthcheck": "/health"
  },
  "domains": [
    "gmailai.devpdm.com"
  ],
  "ssl": {
    "enabled": true,
    "force_https": true,
    "provider": "letsencrypt"
  },
  "environment": {
    "FLASK_ENV": "production",
    "FLASK_DEBUG": "False"
  },
  "volumes": [
    {
      "host": "./config",
      "container": "/app/config"
    },
    {
      "host": "./logs",
      "container": "/app/logs"
    }
  ],
  "backup": {
    "enabled": true,
    "schedule": "0 2 * * *",
    "retention": "7d"
  },
  "monitoring": {
    "enabled": true,
    "alerts": {
      "email": "admin@profdiogomoreira.com.br"
    }
  }
}
EOF

print_header "5. Nginx Configuration for Coolify"

# Create nginx directory and config
mkdir -p nginx/ssl
print_status "Creating Nginx configuration..."
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        listen 80;
        server_name gmailai.devpdm.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name gmailai.devpdm.com;

        # SSL Configuration (Coolify will handle certificates)
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Main application
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API rate limiting
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check
        location /health {
            proxy_pass http://app;
            access_log off;
        }
    }
}
EOF

print_header "6. Deployment Scripts"

# Create deployment script
print_status "Creating deployment scripts..."
cat > deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying Gmail AI Agent..."

# Pull latest changes
git pull origin main

# Build and deploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "🌐 Application is running at: https://profdiogomoreira.com.br"
else
    echo "❌ Deployment failed - check logs"
    docker-compose logs
    exit 1
fi
EOF

chmod +x deploy.sh

# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/gmail-ai-agent"
DATE=$(date +%Y%m%d_%H%M%S)

echo "📦 Creating backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
docker-compose exec -T db mysqldump -u root -p$MYSQL_ROOT_PASSWORD gmail_ai_agent > "$BACKUP_DIR/database_$DATE.sql"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" config/

# Backup logs
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

echo "✅ Backup completed: $BACKUP_DIR"

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

print_header "7. Final Instructions"

print_status "Installation completed! Next steps:"
echo ""
echo "📋 COOLIFY SETUP CHECKLIST:"
echo ""
echo "1. 🔧 Configure API Keys in .env:"
echo "   - Add your OpenAI API key"
echo "   - Add your Anthropic API key (optional)"
echo ""
echo "2. 📧 Gmail API Setup:"
echo "   - Place credentials.json in config/ directory"
echo "   - Run authentication for 4 accounts"
echo ""
echo "3. 🚀 Deploy with Coolify:"
echo "   - Connect your Git repository"
echo "   - Import coolify.json configuration"
echo "   - Set environment variables"
echo "   - Deploy!"
echo ""
echo "4. 🌐 Domain Configuration:"
echo "   - Point gmailai.devpdm.com to VPS IP: 31.97.84.68"
echo "   - Coolify will handle SSL certificates automatically"
echo ""
echo "5. 📊 Monitoring:"
echo "   - Access dashboard at: https://gmailai.devpdm.com"
echo "   - Check logs in Coolify interface"
echo "   - Monitor learning system performance"
echo ""

print_warning "IMPORTANT: Update the API keys in .env before deploying!"
print_status "Documentation available in:"
echo "  - LEARNING_SYSTEM.md (Learning features)"
echo "  - VPS_PANEL_RECOMMENDATION.md (Coolify setup)"
echo "  - README.md (General documentation)"

echo ""
echo "🎉 Gmail AI Agent is ready for Coolify deployment!"
echo "🧠 The learning system will analyze your email history automatically!"
EOF

chmod +x install_coolify.sh
