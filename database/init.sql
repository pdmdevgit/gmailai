-- Gmail AI Agent Database Initialization
-- Initial database schema and seed data

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS gmail_ai_agent;
USE gmail_ai_agent;

-- Set charset
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Create emails table
CREATE TABLE IF NOT EXISTS emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gmail_id VARCHAR(255) NOT NULL UNIQUE,
    thread_id VARCHAR(255) NOT NULL,
    account VARCHAR(50) NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255),
    subject TEXT,
    body_text LONGTEXT,
    body_html LONGTEXT,
    received_at DATETIME NOT NULL,
    processed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    classification_type VARCHAR(50),
    classification_priority VARCHAR(20),
    classification_product VARCHAR(50),
    classification_sentiment VARCHAR(20),
    classification_confidence FLOAT,
    status VARCHAR(20) DEFAULT 'pending',
    needs_human_review BOOLEAN DEFAULT FALSE,
    INDEX idx_gmail_id (gmail_id),
    INDEX idx_thread_id (thread_id),
    INDEX idx_account (account),
    INDEX idx_sender_email (sender_email),
    INDEX idx_received_at (received_at),
    INDEX idx_status (status),
    INDEX idx_classification_type (classification_type),
    INDEX idx_classification_priority (classification_priority),
    INDEX idx_needs_human_review (needs_human_review)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create email_responses table
CREATE TABLE IF NOT EXISTS email_responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email_id INT NOT NULL,
    subject TEXT,
    body_text LONGTEXT,
    body_html LONGTEXT,
    ai_model VARCHAR(50),
    template_used VARCHAR(100),
    generation_confidence FLOAT,
    status VARCHAR(20) DEFAULT 'draft',
    approved_by VARCHAR(100),
    approved_at DATETIME,
    sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
    INDEX idx_email_id (email_id),
    INDEX idx_status (status),
    INDEX idx_approved_at (approved_at),
    INDEX idx_sent_at (sent_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create email_templates table
CREATE TABLE IF NOT EXISTS email_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    product VARCHAR(50),
    subject_template TEXT,
    body_template LONGTEXT,
    variables JSON,
    usage_count INT DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_product (product),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create processing_logs table
CREATE TABLE IF NOT EXISTS processing_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email_id INT,
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT,
    details JSON,
    processing_time FLOAT,
    api_calls_made INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE SET NULL,
    INDEX idx_email_id (email_id),
    INDEX idx_action (action),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create system_settings table
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    value TEXT,
    data_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_key (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert initial email templates
INSERT INTO email_templates (name, category, product, subject_template, body_template, variables) VALUES
(
    'interesse_coaching',
    'vendas',
    'coaching',
    'Re: Sua consulta sobre Coaching para Concursos',
    'Olá {nome},

Obrigado pelo seu interesse no meu trabalho!

Vi que você está interessado(a) em acelerar sua aprovação em concursos fiscais. É exatamente isso que faço há anos - ajudo pessoas determinadas a conquistarem a aprovação em 9 meses, não em 3-5 anos como a média.

Minha metodologia é baseada na minha própria experiência de aprovação e nos resultados de centenas de alunos que já aprovei em carreiras como:
- SEFAZ (diversos estados)
- Receita Federal
- TCE/TCU
- TRF/TRE

O Coaching Individual (R$ 2.997) inclui:
✓ Mentoria personalizada semanal
✓ Plano de estudos customizado
✓ Metodologia dos 9 passos
✓ Suporte psicológico para manter a motivação
✓ Análise de editais e estratégias específicas

Que tal conversarmos sobre seu objetivo específico? 

Responda me contando:
1. Qual concurso você tem como meta?
2. Há quanto tempo estuda?
3. Qual sua maior dificuldade hoje?

Abraço,
Prof. Diogo Moreira',
    JSON_OBJECT('nome', 'string', 'concurso_interesse', 'string')
),
(
    'interesse_acelerador',
    'vendas',
    'acelerador',
    'Re: Acelerador - Metodologia dos 9 Passos',
    'Olá {nome},

Que bom saber do seu interesse no Acelerador!

Este curso foi criado com base na metodologia que me levou à aprovação e que já aprovou centenas de alunos em concursos fiscais de alto nível.

O Acelerador (R$ 497) é perfeito para quem quer:
✓ Aprender a metodologia dos 9 passos
✓ Organizar os estudos de forma eficiente  
✓ Eliminar o "estudo burro" que não gera resultados
✓ Focar apenas no que realmente importa para aprovação

Alguns resultados dos meus alunos:
- Vitória Barbosa: aprovada SEFAZ-BA
- Thales: aprovado em TCE-RS, MPU, TRF-3, TRF-4, TRE-PA

A próxima turma está com vagas limitadas. 

Quer garantir sua vaga? Responda este email e te envio o link de inscrição.

Abraço,
Prof. Diogo Moreira',
    JSON_OBJECT('nome', 'string')
),
(
    'suporte_tecnico',
    'suporte',
    NULL,
    'Re: Sua dúvida - Suporte Técnico',
    'Olá {nome},

Recebi sua mensagem e vou te ajudar a resolver essa questão.

{resposta_especifica}

Se precisar de mais alguma coisa, é só me avisar. Estou aqui para te apoiar nessa jornada rumo à aprovação!

Abraço,
Prof. Diogo Moreira
Equipe de Suporte',
    JSON_OBJECT('nome', 'string', 'resposta_especifica', 'string')
),
(
    'informacoes_gerais',
    'informacao',
    NULL,
    'Re: Informações sobre Concursos Fiscais',
    'Olá {nome},

Obrigado pelo seu contato!

Sobre sua dúvida: {duvida_especifica}

Como especialista em concursos fiscais, posso te dizer que o segredo está em ter uma metodologia estruturada e foco nos pontos que realmente importam para aprovação.

Nos meus anos de experiência, desenvolvi uma abordagem que leva à aprovação em 9 meses (vs. a média de 3-5 anos), baseada em:

1. Planejamento estratégico personalizado
2. Técnicas de estudo eficientes
3. Preparação psicológica
4. Análise detalhada de editais
5. Simulados direcionados

Se quiser saber mais sobre como posso te ajudar especificamente, responda me contando:
- Qual seu objetivo (concurso específico)?
- Qual sua situação atual de estudos?
- Qual sua maior dificuldade?

Abraço,
Prof. Diogo Moreira',
    JSON_OBJECT('nome', 'string', 'duvida_especifica', 'string')
),
(
    'agendamento_call',
    'agendamento',
    NULL,
    'Re: Agendamento de Conversa',
    'Olá {nome},

Perfeito! Vamos marcar nossa conversa.

Tenho os seguintes horários disponíveis esta semana:
- {opcoes_horarios}

A conversa será por videochamada (Google Meet) e terá duração de aproximadamente 30 minutos.

Vamos conversar sobre:
✓ Seu objetivo específico
✓ Sua situação atual de estudos  
✓ Como posso te ajudar a acelerar sua aprovação
✓ Qual a melhor estratégia para seu perfil

Para confirmar, responda este email com:
1. Horário de sua preferência
2. Seu telefone para contato
3. Concurso que você tem como meta

Aguardo seu retorno!

Abraço,
Prof. Diogo Moreira',
    JSON_OBJECT('nome', 'string', 'opcoes_horarios', 'string')
);

-- Insert initial system settings
INSERT INTO system_settings (`key`, value, data_type, description) VALUES
('email_check_interval', '300', 'int', 'Intervalo de verificação de emails em segundos'),
('max_emails_per_batch', '50', 'int', 'Máximo de emails processados por lote'),
('classification_confidence_threshold', '0.7', 'float', 'Limite mínimo de confiança para classificação'),
('auto_response_threshold', '0.85', 'float', 'Limite mínimo de confiança para resposta automática'),
('gmail_api_rate_limit', '250', 'int', 'Limite de requisições Gmail API por 100 segundos'),
('ai_api_rate_limit', '60', 'int', 'Limite de requisições AI API por minuto'),
('system_status', 'active', 'string', 'Status geral do sistema'),
('last_maintenance', NOW(), 'string', 'Data da última manutenção'),
('backup_enabled', 'true', 'bool', 'Backup automático habilitado'),
('notification_email', 'admin@profdiogomoreira.com.br', 'string', 'Email para notificações do sistema');

-- Create indexes for better performance
CREATE INDEX idx_emails_composite ON emails(account, status, created_at);
CREATE INDEX idx_responses_composite ON email_responses(status, created_at);
CREATE INDEX idx_logs_composite ON processing_logs(action, status, created_at);

-- Create views for common queries
CREATE VIEW v_email_summary AS
SELECT 
    e.id,
    e.gmail_id,
    e.account,
    e.sender_email,
    e.sender_name,
    e.subject,
    e.received_at,
    e.status,
    e.classification_type,
    e.classification_priority,
    e.classification_confidence,
    COUNT(er.id) as response_count,
    MAX(er.created_at) as last_response_at
FROM emails e
LEFT JOIN email_responses er ON e.id = er.email_id
GROUP BY e.id;

CREATE VIEW v_processing_stats AS
SELECT 
    DATE(created_at) as date,
    action,
    status,
    COUNT(*) as count,
    AVG(processing_time) as avg_processing_time,
    SUM(api_calls_made) as total_api_calls
FROM processing_logs
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(created_at), action, status;

-- Create stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetAccountStats(IN account_name VARCHAR(50))
BEGIN
    SELECT 
        COUNT(*) as total_emails,
        COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_emails,
        COUNT(CASE WHEN status = 'processed' THEN 1 END) as processed_emails,
        COUNT(CASE WHEN status = 'responded' THEN 1 END) as responded_emails,
        AVG(classification_confidence) as avg_confidence,
        COUNT(CASE WHEN classification_type = 'vendas' THEN 1 END) as sales_emails,
        COUNT(CASE WHEN classification_priority = 'alta' THEN 1 END) as high_priority_emails
    FROM emails 
    WHERE account = account_name;
END //

CREATE PROCEDURE CleanupOldData(IN days_to_keep INT)
BEGIN
    DECLARE cutoff_date DATETIME;
    SET cutoff_date = DATE_SUB(NOW(), INTERVAL days_to_keep DAY);
    
    -- Delete old processing logs
    DELETE FROM processing_logs WHERE created_at < cutoff_date;
    
    -- Update template usage stats
    UPDATE email_templates et
    SET usage_count = (
        SELECT COUNT(*) 
        FROM email_responses er 
        WHERE er.template_used = et.name
    );
    
    SELECT ROW_COUNT() as deleted_records;
END //

DELIMITER ;

-- Insert sample data for testing (optional)
-- Uncomment the following lines for development/testing

/*
INSERT INTO emails (gmail_id, thread_id, account, sender_email, sender_name, subject, body_text, received_at, classification_type, classification_priority, classification_product, classification_sentiment, classification_confidence, status) VALUES
('test_001', 'thread_001', 'contato', 'joao@example.com', 'João Silva', 'Interesse em coaching', 'Olá, gostaria de saber mais sobre o coaching para concursos fiscais.', NOW(), 'vendas', 'alta', 'coaching', 'positivo', 0.95, 'processed'),
('test_002', 'thread_002', 'cursos', 'maria@example.com', 'Maria Santos', 'Dúvida sobre acelerador', 'Oi, queria entender melhor como funciona o curso acelerador.', NOW(), 'vendas', 'media', 'acelerador', 'neutro', 0.85, 'processed'),
('test_003', 'thread_003', 'sac', 'pedro@example.com', 'Pedro Costa', 'Problema com acesso', 'Não consigo acessar o material do curso.', NOW(), 'suporte', 'alta', NULL, 'negativo', 0.90, 'processed');
*/

-- Final optimizations
OPTIMIZE TABLE emails;
OPTIMIZE TABLE email_responses;
OPTIMIZE TABLE email_templates;
OPTIMIZE TABLE processing_logs;
OPTIMIZE TABLE system_settings;

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON gmail_ai_agent.* TO 'gmail_ai_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Success message
SELECT 'Gmail AI Agent database initialized successfully!' as message;
