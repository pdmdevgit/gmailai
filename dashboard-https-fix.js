// Gmail AI Agent Dashboard - JavaScript com HTTPS forçado
class GmailAIAgent {
    constructor() {
        this.currentSection = 'dashboard';
        this.currentPage = 1;
        this.perPage = 20;
        this.init();
    }

    init() {
        this.setupNavigation();
        this.loadDashboard();
        this.setupEventListeners();
    }

    // FUNÇÃO CORRIGIDA - FORÇA HTTPS SEMPRE
    async apiCall(url, method = 'GET', data = null) {
        // FORÇA HTTPS SEMPRE - sem exceções
        const baseUrl = 'https://gmailai.devpdm.com';
        
        // Remove qualquer protocolo da URL se existir
        let cleanUrl = url.replace(/^https?:\/\/[^\/]+/, '');
        if (!cleanUrl.startsWith('/')) {
            cleanUrl = '/' + cleanUrl;
        }
        
        // Constrói URL final sempre com HTTPS
        const finalUrl = baseUrl + cleanUrl;
        
        console.log('API Call URL:', finalUrl);
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(finalUrl, options);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Call Error:', error);
            throw error;
        }
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section');
                this.navigateToSection(section);
            });
        });
    }

    navigateToSection(section) {
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to clicked item
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Hide all sections
        document.querySelectorAll('.section').forEach(sec => {
            sec.style.display = 'none';
        });

        // Show selected section
        const targetSection = document.getElementById(`${section}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        this.currentSection = section;
        this.currentPage = 1;

        // Load section data
        switch (section) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'emails':
                this.loadEmails();
                break;
            case 'responses':
                this.loadResponses();
                break;
            case 'templates':
                this.loadTemplates();
                break;
            case 'admin':
                this.loadAdmin();
                break;
        }
    }

    async loadDashboard() {
        try {
            const data = await this.apiCall('/api/dashboard/');
            this.updateDashboardStats(data);
            this.updateCharts(data);
            this.loadRecentEmails();
            this.loadRecentResponses();
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Erro ao carregar dashboard');
        }
    }

    async loadEmails() {
        try {
            this.showLoading('emails-content');
            const data = await this.apiCall(`/api/emails/?page=${this.currentPage}&per_page=${this.perPage}`);
            this.displayEmails(data);
        } catch (error) {
            console.error('Error loading emails:', error);
            this.showError('Erro ao carregar emails', 'emails-content');
        }
    }

    async loadResponses() {
        try {
            this.showLoading('responses-content');
            const data = await this.apiCall(`/api/responses/?page=${this.currentPage}&per_page=${this.perPage}`);
            this.displayResponses(data);
        } catch (error) {
            console.error('Error loading responses:', error);
            this.showError('Erro ao carregar respostas', 'responses-content');
        }
    }

    async loadTemplates() {
        try {
            this.showLoading('templates-content');
            const data = await this.apiCall('/api/templates/');
            this.displayTemplates(data);
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showError('Erro ao carregar templates', 'templates-content');
        }
    }

    async loadAdmin() {
        try {
            this.showLoading('admin-content');
            const [templatesData, gmailData] = await Promise.all([
                this.apiCall('/api/admin/templates/'),
                this.apiCall('/api/admin/gmail-status/')
            ]);
            this.displayAdminData(templatesData, gmailData);
        } catch (error) {
            console.error('Error loading admin:', error);
            this.showError('Erro ao carregar admin', 'admin-content');
        }
    }

    updateDashboardStats(data) {
        if (data.summary) {
            document.getElementById('total-emails').textContent = data.summary.total_emails || 0;
            document.getElementById('total-responses').textContent = data.summary.total_responses || 0;
        }
        
        if (data.classification) {
            document.getElementById('pending-count').textContent = data.classification.high_priority || 0;
            document.getElementById('classification-rate').textContent = '100%';
        }
    }

    displayEmails(data) {
        const container = document.getElementById('emails-content');
        if (!data.emails || data.emails.length === 0) {
            container.innerHTML = '<p>Nenhum email encontrado.</p>';
            return;
        }

        let html = '<div class="emails-list">';
        data.emails.forEach(email => {
            html += `
                <div class="email-item">
                    <div class="email-header">
                        <strong>${email.sender || 'Remetente desconhecido'}</strong>
                        <span class="email-date">${email.received_at || 'Data desconhecida'}</span>
                    </div>
                    <div class="email-subject">${email.subject || 'Sem assunto'}</div>
                    <div class="email-classification">
                        <span class="badge ${email.classification || 'unknown'}">${email.classification || 'Não classificado'}</span>
                        <span class="priority ${email.priority || 'normal'}">${email.priority || 'Normal'}</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        if (data.pagination) {
            html += this.createPagination(data.pagination);
        }

        container.innerHTML = html;
    }

    displayResponses(data) {
        const container = document.getElementById('responses-content');
        if (!data.responses || data.responses.length === 0) {
            container.innerHTML = '<p>Nenhuma resposta encontrada.</p>';
            return;
        }

        let html = '<div class="responses-list">';
        data.responses.forEach(response => {
            html += `
                <div class="response-item">
                    <div class="response-header">
                        <strong>Para: ${response.recipient || 'Destinatário desconhecido'}</strong>
                        <span class="response-date">${response.created_at || 'Data desconhecida'}</span>
                    </div>
                    <div class="response-subject">${response.subject || 'Sem assunto'}</div>
                    <div class="response-status">
                        <span class="badge ${response.status || 'pending'}">${response.status || 'Pendente'}</span>
                        <button class="btn btn-sm btn-primary" onclick="app.approveResponse(${response.id})">
                            Aprovar
                        </button>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        if (data.pagination) {
            html += this.createPagination(data.pagination);
        }

        container.innerHTML = html;
    }

    displayTemplates(data) {
        const container = document.getElementById('templates-content');
        if (!data.templates || data.templates.length === 0) {
            container.innerHTML = '<p>Nenhum template encontrado.</p>';
            return;
        }

        let html = '<div class="templates-list">';
        data.templates.forEach(template => {
            html += `
                <div class="template-item">
                    <div class="template-header">
                        <strong>${template.name || 'Template sem nome'}</strong>
                        <span class="template-type">${template.type || 'Tipo desconhecido'}</span>
                    </div>
                    <div class="template-description">${template.description || 'Sem descrição'}</div>
                    <div class="template-actions">
                        <button class="btn btn-sm btn-secondary" onclick="app.editTemplate(${template.id})">
                            Editar
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="app.deleteTemplate(${template.id})">
                            Excluir
                        </button>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;
    }

    displayAdminData(templatesData, gmailData) {
        const container = document.getElementById('admin-content');
        let html = '<div class="admin-sections">';
        
        // Gmail Status
        html += '<div class="admin-section"><h3>Status das Contas Gmail</h3>';
        if (gmailData.accounts) {
            gmailData.accounts.forEach(account => {
                html += `
                    <div class="gmail-account">
                        <strong>${account.name}</strong>: 
                        <span class="${account.is_authenticated ? 'authenticated' : 'not-authenticated'}">
                            ${account.is_authenticated ? 'Autenticado' : 'Não autenticado'}
                        </span>
                        (${account.email_count || 0} emails)
                    </div>
                `;
            });
        }
        html += '</div>';

        // Templates Admin
        html += '<div class="admin-section"><h3>Gerenciar Templates</h3>';
        if (templatesData.templates) {
            templatesData.templates.forEach(template => {
                html += `
                    <div class="admin-template">
                        <strong>${template.name}</strong> - ${template.type}
                        <button class="btn btn-sm btn-primary" onclick="app.editAdminTemplate(${template.id})">
                            Editar
                        </button>
                    </div>
                `;
            });
        }
        html += '</div>';

        html += '</div>';
        container.innerHTML = html;
    }

    createPagination(pagination) {
        if (!pagination || pagination.pages <= 1) return '';

        let html = '<div class="pagination">';
        
        if (pagination.page > 1) {
            html += `<button class="btn btn-sm btn-secondary" onclick="app.changePage(${pagination.page - 1})">Anterior</button>`;
        }
        
        html += `<span class="page-info">Página ${pagination.page} de ${pagination.pages}</span>`;
        
        if (pagination.page < pagination.pages) {
            html += `<button class="btn btn-sm btn-secondary" onclick="app.changePage(${pagination.page + 1})">Próxima</button>`;
        }
        
        html += '</div>';
        return html;
    }

    changePage(page) {
        this.currentPage = page;
        switch (this.currentSection) {
            case 'emails':
                this.loadEmails();
                break;
            case 'responses':
                this.loadResponses();
                break;
        }
    }

    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '<div class="loading">Carregando...</div>';
        }
    }

    showError(message, containerId = null) {
        const errorHtml = `<div class="error">${message}</div>`;
        if (containerId) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = errorHtml;
            }
        } else {
            console.error(message);
        }
    }

    setupEventListeners() {
        // Process emails button
        const processBtn = document.getElementById('process-emails-btn');
        if (processBtn) {
            processBtn.addEventListener('click', () => this.processEmails());
        }

        // Filter and search functionality
        const filterBtn = document.getElementById('filter-btn');
        if (filterBtn) {
            filterBtn.addEventListener('click', () => this.applyFilters());
        }

        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearFilters());
        }
    }

    async processEmails() {
        try {
            const result = await this.apiCall('/api/emails/process', 'POST');
            alert('Emails processados com sucesso!');
            this.loadDashboard();
        } catch (error) {
            console.error('Error processing emails:', error);
            alert('Erro ao processar emails');
        }
    }

    async approveResponse(responseId) {
        try {
            await this.apiCall(`/api/responses/${responseId}/approve`, 'POST');
            alert('Resposta aprovada!');
            this.loadResponses();
        } catch (error) {
            console.error('Error approving response:', error);
            alert('Erro ao aprovar resposta');
        }
    }

    async loadRecentEmails() {
        try {
            const data = await this.apiCall('/api/emails/?page=1&per_page=5');
            // Update recent emails section
        } catch (error) {
            console.error('Error loading recent emails:', error);
        }
    }

    async loadRecentResponses() {
        try {
            const data = await this.apiCall('/api/responses/?page=1&per_page=5');
            // Update recent responses section
        } catch (error) {
            console.error('Error loading recent responses:', error);
        }
    }

    updateCharts(data) {
        // Chart update logic would go here
        console.log('Charts updated with data:', data);
    }
}

// Initialize the application
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new GmailAIAgent();
});
