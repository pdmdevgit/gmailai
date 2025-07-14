#!/bin/bash

# Gmail AI Agent - Installation Script
# Automated setup for CyberPanel/VPS environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="gmail-ai-agent"
PROJECT_DIR="/home/profdiogomoreira.com.br/public_html/$PROJECT_NAME"
PYTHON_VERSION="3.9"
MYSQL_DB="gmail_ai_agent"
MYSQL_USER="gmail_ai_user"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

check_cyberpanel() {
    if [ ! -d "/usr/local/CyberCP" ]; then
        log_warning "CyberPanel not detected. Continuing with standard installation..."
        return 1
    fi
    log_info "CyberPanel detected"
    return 0
}

install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    sudo apt-get update
    sudo apt-get install -y \
        python3.9 \
        python3.9-venv \
        python3.9-dev \
        python3-pip \
        mysql-client \
        redis-tools \
        curl \
        wget \
        git \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        supervisor \
        nginx
    
    log_success "System dependencies installed"
}

setup_python_environment() {
    log_info "Setting up Python virtual environment..."
    
    # Create project directory
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown -R $USER:$USER "$PROJECT_DIR"
    
    # Create virtual environment
    cd "$PROJECT_DIR"
    python3.9 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    log_success "Python environment created"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

setup_database() {
    log_info "Setting up MySQL database..."
    
    # Generate random password
    MYSQL_PASSWORD=$(openssl rand -base64 32)
    
    # Create database and user
    mysql -u root -p << EOF
CREATE DATABASE IF NOT EXISTS $MYSQL_DB;
CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';
GRANT ALL PRIVILEGES ON $MYSQL_DB.* TO '$MYSQL_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    # Save credentials
    cat > "$PROJECT_DIR/.env" << EOF
# Flask Configuration
SECRET_KEY=$(openssl rand -base64 32)
FLASK_ENV=production

# Database Configuration
MYSQL_HOST=localhost
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_DB=$MYSQL_DB

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=config/gmail_credentials.json
GMAIL_TOKEN_DIR=config/tokens

# AI API Keys (CONFIGURE THESE)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
AI_MODEL=gpt-4

# Business Configuration
BUSINESS_NAME=Prof. Diogo Moreira
BUSINESS_DOMAIN=profdiogomoreira.com.br

# Monitoring Settings
EMAIL_CHECK_INTERVAL=300
MAX_EMAILS_PER_BATCH=50

# Rate Limiting
GMAIL_API_RATE_LIMIT=250
AI_API_RATE_LIMIT=60

# Classification Settings
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.7
AUTO_RESPONSE_THRESHOLD=0.85
EOF
    
    log_success "Database configured"
    log_warning "Database password saved to .env file"
}

setup_redis() {
    log_info "Configuring Redis..."
    
    # Start Redis service
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    
    log_success "Redis configured"
}

initialize_application() {
    log_info "Initializing application..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Initialize database
    python app.py &
    APP_PID=$!
    sleep 10
    kill $APP_PID
    
    log_success "Application initialized"
}

setup_supervisor() {
    log_info "Setting up Supervisor for process management..."
    
    # Create supervisor config for web app
    sudo tee /etc/supervisor/conf.d/gmail-ai-web.conf > /dev/null << EOF
[program:gmail-ai-web]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/app.py
directory=$PROJECT_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/web.log
environment=PATH="$PROJECT_DIR/venv/bin"
EOF
    
    # Create supervisor config for monitor
    sudo tee /etc/supervisor/conf.d/gmail-ai-monitor.conf > /dev/null << EOF
[program:gmail-ai-monitor]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/monitor.py
directory=$PROJECT_DIR
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_DIR/logs/monitor.log
environment=PATH="$PROJECT_DIR/venv/bin"
EOF
    
    # Create logs directory
    mkdir -p "$PROJECT_DIR/logs"
    
    # Reload supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    
    log_success "Supervisor configured"
}

setup_nginx() {
    log_info "Setting up Nginx reverse proxy..."
    
    # Create Nginx config
    sudo tee /etc/nginx/sites-available/gmail-ai-agent > /dev/null << EOF
server {
    listen 80;
    server_name profdiogomoreira.com.br www.profdiogomoreira.com.br;
    
    location /gmail-ai-agent {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /gmail-ai-agent/static {
        alias $PROJECT_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/gmail-ai-agent /etc/nginx/sites-enabled/
    
    # Test and reload Nginx
    sudo nginx -t
    sudo systemctl reload nginx
    
    log_success "Nginx configured"
}

setup_ssl() {
    log_info "Setting up SSL certificate..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Get SSL certificate
    sudo certbot --nginx -d profdiogomoreira.com.br -d www.profdiogomoreira.com.br --non-interactive --agree-tos --email admin@profdiogomoreira.com.br
    
    log_success "SSL certificate configured"
}

setup_firewall() {
    log_info "Configuring firewall..."
    
    # Allow necessary ports
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 3306/tcp
    sudo ufw allow 6379/tcp
    sudo ufw allow 5000/tcp
    
    # Enable firewall
    sudo ufw --force enable
    
    log_success "Firewall configured"
}

setup_cron_jobs() {
    log_info "Setting up cron jobs..."
    
    # Add cron job for health checks
    (crontab -l 2>/dev/null; echo "*/5 * * * * cd $PROJECT_DIR && ./venv/bin/python monitor.py --health-check >> logs/health.log 2>&1") | crontab -
    
    # Add cron job for cleanup
    (crontab -l 2>/dev/null; echo "0 2 * * * cd $PROJECT_DIR && ./venv/bin/python monitor.py --cleanup >> logs/cleanup.log 2>&1") | crontab -
    
    log_success "Cron jobs configured"
}

create_management_scripts() {
    log_info "Creating management scripts..."
    
    # Start script
    cat > "$PROJECT_DIR/start.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
sudo supervisorctl start gmail-ai-web gmail-ai-monitor
echo "Gmail AI Agent started"
EOF
    
    # Stop script
    cat > "$PROJECT_DIR/stop.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
sudo supervisorctl stop gmail-ai-web gmail-ai-monitor
echo "Gmail AI Agent stopped"
EOF
    
    # Restart script
    cat > "$PROJECT_DIR/restart.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
sudo supervisorctl restart gmail-ai-web gmail-ai-monitor
echo "Gmail AI Agent restarted"
EOF
    
    # Status script
    cat > "$PROJECT_DIR/status.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "=== Gmail AI Agent Status ==="
sudo supervisorctl status gmail-ai-web gmail-ai-monitor
echo ""
echo "=== Recent Logs ==="
tail -n 10 logs/web.log
echo ""
tail -n 10 logs/monitor.log
EOF
    
    # Make scripts executable
    chmod +x "$PROJECT_DIR"/*.sh
    
    log_success "Management scripts created"
}

print_final_instructions() {
    log_success "Installation completed successfully!"
    echo ""
    echo "=== NEXT STEPS ==="
    echo ""
    echo "1. Configure API Keys:"
    echo "   Edit $PROJECT_DIR/.env and add your API keys:"
    echo "   - OPENAI_API_KEY=your-key-here"
    echo "   - ANTHROPIC_API_KEY=your-key-here"
    echo ""
    echo "2. Add Gmail Credentials:"
    echo "   - Download credentials.json from Google Cloud Console"
    echo "   - Copy to $PROJECT_DIR/config/gmail_credentials.json"
    echo ""
    echo "3. Start the services:"
    echo "   cd $PROJECT_DIR"
    echo "   ./start.sh"
    echo ""
    echo "4. Access the dashboard:"
    echo "   https://profdiogomoreira.com.br/gmail-ai-agent"
    echo ""
    echo "5. Authenticate Gmail accounts:"
    echo "   Go to Admin section and authenticate each account"
    echo ""
    echo "=== MANAGEMENT COMMANDS ==="
    echo "Start:   ./start.sh"
    echo "Stop:    ./stop.sh"
    echo "Restart: ./restart.sh"
    echo "Status:  ./status.sh"
    echo ""
    echo "=== LOG FILES ==="
    echo "Web App: $PROJECT_DIR/logs/web.log"
    echo "Monitor: $PROJECT_DIR/logs/monitor.log"
    echo "Health:  $PROJECT_DIR/logs/health.log"
    echo ""
    log_warning "Remember to configure your API keys before starting!"
}

# Main installation process
main() {
    log_info "Starting Gmail AI Agent installation..."
    
    check_root
    check_cyberpanel
    
    install_system_dependencies
    setup_python_environment
    install_python_dependencies
    setup_database
    setup_redis
    initialize_application
    setup_supervisor
    setup_nginx
    setup_ssl
    setup_firewall
    setup_cron_jobs
    create_management_scripts
    
    print_final_instructions
}

# Run installation
main "$@"
