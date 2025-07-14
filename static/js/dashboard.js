// Dashboard JavaScript
class GmailAIAgent {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('[data-section]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSection(e.target.dataset.section);
            });
        });

        // Filter events
        const filterElements = ['account-filter', 'status-filter', 'type-filter'];
        filterElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => this.filterEmails());
            }
        });

        // Search
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.filterEmails();
                }
            });
        }
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('fade-in');
        }

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

        this.currentSection = sectionName;

        // Load section-specific data
        switch (sectionName) {
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
            // Load overview data
            const overview = await this.apiCall('/api/dashboard/overview');
            this.updateOverviewCards(overview);

            // Load charts
            await this.loadCharts();

            // Load recent activity
            const activity = await this.apiCall('/api/dashboard/recent-activity');
            this.updateRecentActivity(activity);

        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showAlert('Erro ao carregar dashboard', 'danger');
        }
    }

    updateOverviewCards(data) {
        // Update summary cards
        this.updateElement('total-emails', data.summary?.total_emails || 0);
        this.updateElement('emails-today', data.summary?.emails_today || 0);
        this.updateElement('total-responses', data.summary?.total_responses || 0);
        this.updateElement('responses-today', data.summary?.responses_today || 0);
        this.updateElement('pending-responses', data.summary?.pending_responses || 0);

        // Update rates
        this.updateElement('classification-rate', `${data.classification?.classification_rate || 0}%`);
        this.updateElement('response-rate', `${data.processing?.response_rate || 0}%`);

        // Update growth
        const growth = data.summary?.email_growth_pct || 0;
        const growthElement = document.getElementById('email-growth');
        if (growthElement) {
            growthElement.textContent = `${growth > 0 ? '+' : ''}${growth}%`;
            growthElement.className = growth > 0 ? 'text-success' : growth < 0 ? 'text-danger' : '';
        }
    }

    async loadCharts() {
        try {
            // Email volume chart
            const volumeData = await this.apiCall('/api/dashboard/charts/email-volume');
            this.createEmailVolumeChart(volumeData);

            // Classification breakdown
            const classificationData = await this.apiCall('/api/dashboard/charts/classification-breakdown');
            this.createClassificationChart(classificationData);

        } catch (error) {
            console.error('Error loading charts:', error);
        }
    }

    createEmailVolumeChart(data) {
        const ctx = document.getElementById('emailVolumeChart');
        if (!ctx) return;

        if (this.charts.emailVolume) {
            this.charts.emailVolume.destroy();
        }

        this.charts.emailVolume = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.data.map(item => new Date(item.date).toLocaleDateString('pt-BR')),
                datasets: [{
                    label: 'Emails',
                    data: data.data.map(item => item.emails),
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    createClassificationChart(data) {
        const ctx = document.getElementById('classificationChart');
        if (!ctx) return;

        if (this.charts.classification) {
            this.charts.classification.destroy();
        }

        const colors = {
            'vendas': '#198754',
            'suporte': '#0dcaf0',
            'informacao': '#ffc107',
            'spam': '#dc3545',
            'agendamento': '#6f42c1'
        };

        this.charts.classification = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.by_type.map(item => item.label),
                datasets: [{
                    data: data.by_type.map(item => item.value),
                    backgroundColor: data.by_type.map(item => colors[item.label] || '#6c757d'),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    updateRecentActivity(data) {
        // Update recent emails
        const emailsContainer = document.getElementById('recent-emails');
        if (emailsContainer && data.emails) {
            emailsContainer.innerHTML = data.emails.map(email => `
                <div class="list-group-item email-preview" onclick="app.showEmailDetail(${email.id})">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="email-sender">${email.sender}</div>
                            <div class="email-subject">${email.subject}</div>
                            <div class="email-meta">
                                <span class="badge bg-${email.classification || 'secondary'}">${email.classification || 'N/A'}</span>
                                <span class="badge bg-${email.priority || 'secondary'}">${email.priority || 'N/A'}</span>
                                <small class="text-muted ms-2">${email.time_ago}</small>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">${email.account}</small>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        // Update recent responses
        const responsesContainer = document.getElementById('recent-responses');
        if (responsesContainer && data.responses) {
            responsesContainer.innerHTML = data.responses.map(response => `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <div class="fw-bold">${response.subject}</div>
                            <div class="small text-muted">Email ID: ${response.email_id}</div>
                            <div class="mt-1">
                                <span class="badge bg-${this.getStatusColor(response.status)}">${response.status}</span>
                                <div class="confidence-bar mt-1" style="width: 100px;">
                                    <div class="confidence-fill confidence-${this.getConfidenceLevel(response.confidence)}" 
                                         style="width: ${(response.confidence * 100)}%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">${response.time_ago}</small>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    async loadEmails(page = 1) {
        try {
            this.showLoading();
            
            const params = new URLSearchParams({
                page: page,
                per_page: 20
            });

            // Add filters
            const filters = this.getEmailFilters();
            Object.entries(filters).forEach(([key, value]) => {
                if (value) params.append(key, value);
            });

            const data = await this.apiCall(`/api/emails?${params}`);
            this.displayEmailsTable(data);

        } catch (error) {
            console.error('Error loading emails:', error);
            this.showAlert('Erro ao carregar emails', 'danger');
        } finally {
            this.hideLoading();
        }
    }

    getEmailFilters() {
        return {
            account: document.getElementById('account-filter')?.value || '',
            status: document.getElementById('status-filter')?.value || '',
            type: document.getElementById('type-filter')?.value || '',
            search: document.getElementById('search-input')?.value || ''
        };
    }

    displayEmailsTable(data) {
        const container = document.getElementById('emails-table-container');
        if (!container) return;

        const emails = data.emails || [];
        const pagination = data.pagination || {};

        container.innerHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Remetente</th>
                            <th>Assunto</th>
                            <th>Conta</th>
                            <th>Classificação</th>
                            <th>Prioridade</th>
                            <th>Status</th>
                            <th>Data</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${emails.map(email => `
                            <tr>
                                <td>
                                    <div class="fw-bold">${email.sender_name || email.sender_email}</div>
                                    <small class="text-muted">${email.sender_email}</small>
                                </td>
                                <td>
                                    <div class="text-truncate" style="max-width: 200px;" title="${email.subject}">
                                        ${email.subject}
                                    </div>
                                    <small class="text-muted">${email.body_preview}</small>
                                </td>
                                <td><span class="badge bg-primary">${email.account}</span></td>
                                <td>
                                    ${email.classification.type ? 
                                        `<span class="badge bg-${email.classification.type}">${email.classification.type}</span>` : 
                                        '<span class="badge bg-secondary">N/A</span>'
                                    }
                                </td>
                                <td>
                                    ${email.classification.priority ? 
                                        `<span class="badge bg-${email.classification.priority}">${email.classification.priority}</span>` : 
                                        '<span class="badge bg-secondary">N/A</span>'
                                    }
                                </td>
                                <td><span class="badge bg-${this.getStatusColor(email.status)}">${email.status}</span></td>
                                <td>
                                    <small>${new Date(email.received_at).toLocaleDateString('pt-BR')}</small><br>
                                    <small class="text-muted">${new Date(email.received_at).toLocaleTimeString('pt-BR')}</small>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="app.showEmailDetail(${email.id})">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-success" onclick="app.generateResponse(${email.id})">
                                            <i class="fas fa-reply"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            ${this.createPagination(pagination)}
        `;
    }

    createPagination(pagination) {
        if (!pagination.pages || pagination.pages <= 1) return '';

        const pages = [];
        const current = pagination.page;
        const total = pagination.pages;

        // Previous button
        pages.push(`
            <li class="page-item ${!pagination.has_prev ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadEmails(${current - 1})">Anterior</a>
            </li>
        `);

        // Page numbers
        for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
            pages.push(`
                <li class="page-item ${i === current ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="app.loadEmails(${i})">${i}</a>
                </li>
            `);
        }

        // Next button
        pages.push(`
            <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="app.loadEmails(${current + 1})">Próximo</a>
            </li>
        `);

        return `
            <nav aria-label="Paginação de emails">
                <ul class="pagination justify-content-center">
                    ${pages.join('')}
                </ul>
            </nav>
        `;
    }

    async showEmailDetail(emailId) {
        try {
            const email = await this.apiCall(`/api/emails/${emailId}`);
            
            // Create modal HTML
            const modalHtml = `
                <div class="modal fade" id="emailDetailModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Detalhes do Email</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>De:</strong> ${email.sender_name} <${email.sender_email}>
                                    </div>
                                    <div class="col-md-6">
                                        <strong>Conta:</strong> <span class="badge bg-primary">${email.account}</span>
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-12">
                                        <strong>Assunto:</strong> ${email.subject}
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-4">
                                        <strong>Tipo:</strong> 
                                        <span class="badge bg-${email.classification.type || 'secondary'}">
                                            ${email.classification.type || 'N/A'}
                                        </span>
                                    </div>
                                    <div class="col-md-4">
                                        <strong>Prioridade:</strong> 
                                        <span class="badge bg-${email.classification.priority || 'secondary'}">
                                            ${email.classification.priority || 'N/A'}
                                        </span>
                                    </div>
                                    <div class="col-md-4">
                                        <strong>Status:</strong> 
                                        <span class="badge bg-${this.getStatusColor(email.status)}">${email.status}</span>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <strong>Conteúdo:</strong>
                                    <div class="email-body mt-2">${email.body_text}</div>
                                </div>
                                ${email.responses.length > 0 ? `
                                    <div class="mb-3">
                                        <strong>Respostas (${email.responses.length}):</strong>
                                        ${email.responses.map(response => `
                                            <div class="card mt-2">
                                                <div class="card-body">
                                                    <div class="d-flex justify-content-between">
                                                        <h6 class="card-title">${response.subject}</h6>
                                                        <span class="badge bg-${this.getStatusColor(response.status)}">${response.status}</span>
                                                    </div>
                                                    <p class="card-text">${response.body_text.substring(0, 200)}...</p>
                                                    <small class="text-muted">
                                                        Confiança: ${Math.round(response.generation_confidence * 100)}% | 
                                                        Criado: ${new Date(response.created_at).toLocaleString('pt-BR')}
                                                    </small>
                                                </div>
                                            </div>
                                        `).join('')}
                                    </div>
                                ` : ''}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                                <button type="button" class="btn btn-success" onclick="app.generateResponse(${email.id})">
                                    <i class="fas fa-reply me-1"></i>Gerar Resposta
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal
            const existingModal = document.getElementById('emailDetailModal');
            if (existingModal) {
                existingModal.remove();
            }

            // Add modal to body
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('emailDetailModal'));
            modal.show();

        } catch (error) {
            console.error('Error loading email detail:', error);
            this.showAlert('Erro ao carregar detalhes do email', 'danger');
        }
    }

    async generateResponse(emailId) {
        try {
            this.showLoading();
            
            const response = await this.apiCall(`/api/emails/${emailId}/responses`, 'POST');
            
            this.showAlert('Resposta gerada com sucesso!', 'success');
            
            // Refresh current view
            if (this.currentSection === 'emails') {
                this.loadEmails();
            }

        } catch (error) {
            console.error('Error generating response:', error);
            this.showAlert('Erro ao gerar resposta', 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async processEmails() {
        try {
            this.showLoading();
            
            const result = await this.apiCall('/api/emails/process', 'POST');
            
            this.showAlert(`Processamento concluído! ${JSON.stringify(result.results)}`, 'success');
            
            // Refresh dashboard
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            } else if (this.currentSection === 'emails') {
                this.loadEmails();
            }

        } catch (error) {
            console.error('Error processing emails:', error);
            this.showAlert('Erro ao processar emails', 'danger');
        } finally {
            this.hideLoading();
        }
    }

    filterEmails() {
        this.loadEmails(1);
    }

    clearFilters() {
        document.getElementById('account-filter').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('type-filter').value = '';
        document.getElementById('search-input').value = '';
        this.loadEmails(1);
    }

    loadResponses() {
        // Placeholder for responses section
        console.log('Loading responses...');
    }

    loadTemplates() {
        // Placeholder for templates section
        console.log('Loading templates...');
    }

    loadAdmin() {
        // Placeholder for admin section
        console.log('Loading admin...');
    }

    // Utility methods
    async apiCall(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'processed': 'info',
            'responded': 'success',
            'draft': 'warning',
            'approved': 'info',
            'sent': 'success'
        };
        return colors[status] || 'secondary';
    }

    getConfidenceLevel(confidence) {
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.5) return 'medium';
        return 'low';
    }

    showLoading() {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }

    showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const container = document.querySelector('.container-fluid');
        container.insertAdjacentHTML('afterbegin', alertHtml);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    startAutoRefresh() {
        // Refresh dashboard every 5 minutes
        this.refreshInterval = setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            }
        }, 300000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// Initialize the application
const app = new GmailAIAgent();

// Global functions for onclick handlers
window.app = app;
