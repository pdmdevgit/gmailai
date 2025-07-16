22// Gmail AI Agent Dashboard JavaScript
// Prof. Diogo Moreira Email Management System

class GmailAIDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.currentPage = 1;
        this.itemsPerPage = 20;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.getAttribute('data-section');
                if (section) {
                    this.showSection(section);
                }
            });
        });

        // Process emails button
        const processBtn = document.getElementById('processEmailsBtn');
        if (processBtn) {
            processBtn.addEventListener('click', () => this.processEmails());
        }

        // Bulk actions
        const bulkActionBtn = document.getElementById('bulkActionBtn');
        if (bulkActionBtn) {
            bulkActionBtn.addEventListener('click', () => this.performBulkAction());
        }

        // Search and filters
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchEmails(e.target.value);
            });
        }

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.getAttribute('data-filter');
                this.applyFilter(filter);
            });
        });

        // Pagination
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('page-link')) {
                e.preventDefault();
                const page = parseInt(e.target.getAttribute('data-page'));
                if (page) {
                    this.currentPage = page;
                    this.loadCurrentSection();
                }
            }
        });
    }

    showSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        const activeLink = document.querySelector(`[data-section="${section}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // Hide all sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.style.display = 'none';
        });

        // Show selected section - fix ID format
        const sectionElement = document.getElementById(`${section}-section`);
        if (sectionElement) {
            sectionElement.style.display = 'block';
        }

        this.currentSection = section;
        this.currentPage = 1;
        this.loadCurrentSection();
    }

    async loadCurrentSection() {
        switch (this.currentSection) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'emails':
                await this.loadEmails();
                break;
            case 'responses':
                await this.loadResponses();
                break;
            case 'templates':
                await this.loadTemplates();
                break;
            case 'admin':
                await this.loadAdmin();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Load overview stats
            const overview = await this.apiCall('/api/dashboard/overview');
            this.updateOverviewStats(overview);

            // Load recent emails and responses
            await this.loadRecentEmails();
            await this.loadRecentResponses();

            // Load charts
            await this.loadCharts();
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Erro ao carregar dashboard');
        }
    }

    updateOverviewStats(data) {
        if (data && data.summary) {
            // Update cards with correct IDs from HTML
            const totalEmailsEl = document.getElementById('total-emails');
            const emailsTodayEl = document.getElementById('emails-today');
            const emailGrowthEl = document.getElementById('email-growth');
            const totalResponsesEl = document.getElementById('total-responses');
            const responsesTodayEl = document.getElementById('responses-today');
            const responseRateEl = document.getElementById('response-rate');
            const pendingResponsesEl = document.getElementById('pending-responses');
            const classificationRateEl = document.getElementById('classification-rate');

            if (totalEmailsEl) totalEmailsEl.textContent = data.summary.total_emails || 0;
            if (emailsTodayEl) emailsTodayEl.textContent = data.summary.emails_today || 0;
            if (emailGrowthEl) emailGrowthEl.textContent = `+${data.summary.email_growth_pct || 0}%`;
            if (totalResponsesEl) totalResponsesEl.textContent = data.summary.total_responses || 0;
            if (responsesTodayEl) responsesTodayEl.textContent = data.summary.responses_today || 0;
            if (responseRateEl) responseRateEl.textContent = `${data.processing.response_rate || 0}%`;
            if (pendingResponsesEl) pendingResponsesEl.textContent = data.summary.pending_responses || 0;
            if (classificationRateEl) classificationRateEl.textContent = `${data.classification.classification_rate || 0}%`;
        }
    }

    async loadRecentEmails() {
        try {
            const emails = await this.apiCall('/api/emails?per_page=5');
            this.updateRecentEmails(emails.emails || []);
        } catch (error) {
            console.error('Error loading recent emails:', error);
        }
    }

    async loadRecentResponses() {
        try {
            const responses = await this.apiCall('/api/responses?per_page=5');
            this.updateRecentResponses(responses.responses || []);
        } catch (error) {
            console.error('Error loading recent responses:', error);
        }
    }

    updateRecentEmails(emails) {
        const container = document.getElementById('recent-emails');
        if (container && emails.length > 0) {
            container.innerHTML = emails.map(email => `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${email.sender_name || email.sender_email}</h6>
                        <small>${this.formatTime(email.received_at)}</small>
                    </div>
                    <p class="mb-1">${email.subject}</p>
                    <small class="text-muted">${email.body_preview ? email.body_preview.substring(0, 100) + '...' : ''}</small>
                </div>
            `).join('');
        } else if (container) {
            container.innerHTML = '<div class="text-center text-muted py-3">Nenhum email recente</div>';
        }
    }

    updateRecentResponses(responses) {
        const container = document.getElementById('recent-responses');
        if (container && responses.length > 0) {
            container.innerHTML = responses.map(response => `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Para: ${response.email.sender_name}</h6>
                        <small>${this.formatTime(response.created_at)}</small>
                    </div>
                    <p class="mb-1">Re: ${response.email.subject}</p>
                    <small class="text-muted">
                        <span class="badge bg-${this.getResponseStatusColor(response.status)}">${this.getResponseStatusText(response.status)}</span>
                    </small>
                </div>
            `).join('');
        } else if (container) {
            container.innerHTML = '<div class="text-center text-muted py-3">Nenhuma resposta recente</div>';
        }
    }

    updateRecentActivity(data) {
        const container = document.getElementById('recentActivity');
        if (container && data && data.length > 0) {
            container.innerHTML = data.map(item => `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-${this.getActivityIcon(item.type)}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${item.title}</div>
                        <div class="activity-time">${this.formatTime(item.timestamp)}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    async loadCharts() {
        try {
            // Create simple charts with mock data for now
            this.renderVolumeChart();
            this.renderClassificationChart();
        } catch (error) {
            console.error('Error loading charts:', error);
        }
    }

    renderVolumeChart() {
        const ctx = document.getElementById('emailVolumeChart');
        if (ctx) {
            // Create chart with sample data
            const last7Days = [];
            const emailCounts = [];
            for (let i = 6; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                last7Days.push(date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }));
                emailCounts.push(Math.floor(Math.random() * 20) + 5);
            }

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: last7Days,
                    datasets: [{
                        label: 'Emails por Dia',
                        data: emailCounts,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    renderClassificationChart() {
        const ctx = document.getElementById('classificationChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Vendas', 'Suporte', 'Informação', 'Outros'],
                    datasets: [{
                        data: [45, 25, 20, 10],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107', 
                            '#17a2b8',
                            '#6c757d'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }

    async loadEmails() {
        try {
            this.showLoading('emails-table-container');
            
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage
            });

            // Add filters if any
            const activeFilters = this.getActiveFilters();
            Object.keys(activeFilters).forEach(key => {
                if (activeFilters[key]) {
                    params.append(key, activeFilters[key]);
                }
            });

            const data = await this.apiCall(`/api/emails/?${params}`);
            this.renderEmails(data);
        } catch (error) {
            console.error('Error loading emails:', error);
            this.showError('Erro ao carregar emails');
        }
    }

    renderEmails(data) {
        const container = document.getElementById('emails-table-container');
        if (!container) return;

        if (!data || !data.emails || data.emails.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <h5>Nenhum email encontrado</h5>
                    <p class="text-muted">Não há emails para exibir no momento.</p>
                </div>
            `;
            return;
        }

        // Create table
        const tableHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>De</th>
                            <th>Assunto</th>
                            <th>Data</th>
                            <th>Status</th>
                            <th>Tipo</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.emails.map(email => `
                            <tr data-email-id="${email.id}">
                                <td>
                                    <div>
                                        <strong>${email.sender_name || email.sender_email}</strong><br>
                                        <small class="text-muted">${email.sender_email}</small>
                                    </div>
                                </td>
                                <td>
                                    <div>
                                        <strong>${email.subject}</strong><br>
                                        <small class="text-muted">${email.body_preview ? email.body_preview.substring(0, 80) + '...' : ''}</small>
                                    </div>
                                </td>
                                <td>
                                    <small>${this.formatDate(email.received_at)}</small>
                                </td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(email.status)}">${this.getStatusText(email.status)}</span>
                                </td>
                                <td>
                                    ${email.classification && email.classification.type ? 
                                        `<span class="badge bg-info">${email.classification.type}</span>` : 
                                        '<span class="badge bg-secondary">N/A</span>'
                                    }
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="app.viewEmail('${email.id}')">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        ${email.status === 'pending' || email.status === 'processed' ? `
                                            <button class="btn btn-outline-success" onclick="app.generateResponse('${email.id}')">
                                                <i class="fas fa-reply"></i>
                                            </button>
                                        ` : ''}
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHtml;

        // Update pagination
        this.updatePagination(data.pagination);
    }

    async viewEmail(emailId) {
        try {
            const email = await this.apiCall(`/api/emails/${emailId}`);
            this.showEmailModal(email);
        } catch (error) {
            console.error('Error loading email:', error);
            this.showError('Erro ao carregar email');
        }
    }

    showEmailModal(email) {
        const modal = document.getElementById('emailModal');
        if (modal) {
            document.getElementById('modalEmailSubject').textContent = email.subject;
            document.getElementById('modalEmailFrom').textContent = `${email.sender_name} <${email.sender_email}>`;
            document.getElementById('modalEmailDate').textContent = this.formatDate(email.received_at);
            document.getElementById('modalEmailBody').innerHTML = email.body_html || email.body_text;
            
            // Show modal (assuming Bootstrap modal)
            $(modal).modal('show');
        }
    }

    async generateResponse(emailId) {
        try {
            this.showLoading();
            const email = await this.apiCall(`/api/emails/${emailId}`);
            this.showResponseModal(email);
        } catch (error) {
            console.error('Error loading email for response:', error);
            this.showError('Erro ao carregar email');
        }
    }

    showResponseModal(email) {
        const modal = document.getElementById('responseModal');
        if (modal) {
            document.getElementById('responseEmailId').value = email.id;
            document.getElementById('responseEmailSubject').textContent = email.subject;
            document.getElementById('responseEmailFrom').textContent = `${email.sender_name} <${email.sender_email}>`;
            
            // Clear previous response
            document.getElementById('responseContent').value = '';
            
            // Show modal
            $(modal).modal('show');
        }
    }

    async sendResponse(emailId, responseData) {
        try {
            this.showLoading();
            
            const requestData = {
                response_text: responseData.content,
                template_id: responseData.template_id || null,
                send_immediately: responseData.send_immediately || false
            };

            const response = await this.apiCall(`/api/emails/${emailId}/responses`, 'POST', requestData);
            
            this.showSuccess('Resposta gerada com sucesso!');
            this.loadCurrentSection(); // Refresh current view
            
            // Close modal
            $('#responseModal').modal('hide');
            
            return response;
        } catch (error) {
            console.error('Error sending response:', error);
            this.showError('Erro ao enviar resposta');
        }
    }

    async markForResponse(emailId) {
        try {
            const response = await this.apiCall(`/api/emails/${emailId}/mark-for-response`, 'POST');
            this.showSuccess('Email marcado para resposta');
            this.loadCurrentSection();
            return response;
        } catch (error) {
            console.error('Error marking email for response:', error);
            this.showError('Erro ao marcar email');
        }
    }

    async skipResponse(emailId, reason = '') {
        try {
            const response = await this.apiCall(`/api/emails/${emailId}/skip-response`, 'POST', {
                reason: reason
            });
            this.showSuccess('Email marcado como ignorado');
            this.loadCurrentSection();
            return response;
        } catch (error) {
            console.error('Error skipping email:', error);
            this.showError('Erro ao ignorar email');
        }
    }

    async performBulkAction() {
        try {
            const selectedEmails = this.getSelectedEmails();
            const action = document.getElementById('bulkActionSelect').value;
            
            if (selectedEmails.length === 0) {
                this.showError('Selecione pelo menos um email');
                return;
            }

            const response = await this.apiCall('/api/emails/bulk-actions', 'POST', {
                email_ids: selectedEmails,
                action: action
            });

            this.showSuccess(`Ação executada em ${selectedEmails.length} emails`);
            this.loadCurrentSection();
            
            return response;
        } catch (error) {
            console.error('Error performing bulk action:', error);
            this.showError('Erro ao executar ação em lote');
        }
    }

    async processEmails() {
        try {
            this.showLoading();
            const result = await this.apiCall('/api/emails/process', 'POST');
            
            this.showSuccess(`Processamento iniciado! ${result.processed_count || 0} emails processados`);
            
            // Refresh dashboard after processing
            setTimeout(() => {
                this.loadDashboard();
            }, 2000);
            
            return result;
        } catch (error) {
            console.error('Error processing emails:', error);
            this.showError('Erro ao processar emails');
        }
    }

    getSelectedEmails() {
        const checkboxes = document.querySelectorAll('.email-checkbox:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    getActiveFilters() {
        return {
            status: document.getElementById('status-filter')?.value,
            classification: document.getElementById('type-filter')?.value,
            account: document.getElementById('account-filter')?.value,
            search: document.getElementById('search-input')?.value
        };
    }

    async loadResponses() {
        try {
            const container = document.getElementById('responses-section');
            if (container) {
                this.showLoading('responses-section');
                
                const params = new URLSearchParams({
                    page: this.currentPage,
                    per_page: this.itemsPerPage
                });

                const data = await this.apiCall(`/api/responses/?${params}`);
                this.renderResponses(data);
            }
        } catch (error) {
            console.error('Error loading responses:', error);
            this.showError('Erro ao carregar respostas');
        }
    }

    renderResponses(data) {
        const container = document.getElementById('responses-table-container');
        if (!container) return;

        if (!data || !data.responses || data.responses.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-reply fa-3x text-muted mb-3"></i>
                    <h5>Nenhuma resposta encontrada</h5>
                    <p class="text-muted">Não há respostas para exibir no momento.</p>
                </div>
            `;
            return;
        }

        // Create table
        const tableHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Para</th>
                            <th>Assunto</th>
                            <th>Template</th>
                            <th>Data</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.responses.map(response => `
                            <tr data-response-id="${response.id}">
                                <td>
                                    <div>
                                        <strong>${response.email.sender_name || response.email.sender_email}</strong><br>
                                        <small class="text-muted">${response.email.sender_email}</small>
                                    </div>
                                </td>
                                <td>
                                    <div>
                                        <strong>Re: ${response.email.subject}</strong><br>
                                        <small class="text-muted">${response.response_text ? response.response_text.substring(0, 60) + '...' : ''}</small>
                                    </div>
                                </td>
                                <td>
                                    ${response.template ? 
                                        `<span class="badge bg-info">${response.template.name}</span>` : 
                                        '<span class="badge bg-secondary">Manual</span>'
                                    }
                                </td>
                                <td>
                                    <small>${this.formatDate(response.created_at)}</small>
                                </td>
                                <td>
                                    <span class="badge bg-${this.getResponseStatusColor(response.status)}">${this.getResponseStatusText(response.status)}</span>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="app.viewResponse('${response.id}')">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        ${response.status === 'pending' ? `
                                            <button class="btn btn-outline-success" onclick="app.approveResponse('${response.id}')">
                                                <i class="fas fa-check"></i>
                                            </button>
                                            <button class="btn btn-outline-warning" onclick="app.editResponse('${response.id}')">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                        ` : ''}
                                        ${response.status === 'approved' ? `
                                            <button class="btn btn-outline-primary" onclick="app.sendResponse('${response.id}')">
                                                <i class="fas fa-paper-plane"></i>
                                            </button>
                                        ` : ''}
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = tableHtml;
        this.updatePagination(data.pagination);
    }

    async loadTemplates() {
        try {
            const container = document.getElementById('templates-section');
            if (container) {
                this.showLoading('templates-section');
                
                const params = new URLSearchParams({
                    page: this.currentPage,
                    per_page: this.itemsPerPage
                });

                const data = await this.apiCall(`/api/templates/?${params}`);
                this.renderTemplates(data);
            }
        } catch (error) {
            console.error('Error loading templates:', error);
            this.showError('Erro ao carregar templates');
        }
    }

    renderTemplates(data) {
        const container = document.getElementById('templates-grid-container');
        if (!container) return;

        if (!data || !data.templates || data.templates.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                    <h5>Nenhum template encontrado</h5>
                    <p class="text-muted">Não há templates para exibir no momento.</p>
                    <button class="btn btn-primary" onclick="app.showCreateTemplateModal()">
                        <i class="fas fa-plus"></i> Criar Template
                    </button>
                </div>
            `;
            return;
        }

        const templatesHtml = `
            <div class="row">
                ${data.templates.map(template => `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="card h-100" data-template-id="${template.id}">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">${template.name}</h6>
                                <div>
                                    <span class="badge bg-${template.is_active ? 'success' : 'secondary'}">
                                        ${template.is_active ? 'Ativo' : 'Inativo'}
                                    </span>
                                    <span class="badge bg-info ms-1">${template.category}</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <p class="card-text text-muted small">
                                    ${template.description || 'Sem descrição'}
                                </p>
                                <div class="template-preview bg-light p-2 rounded small" style="max-height: 100px; overflow: hidden;">
                                    ${template.content.substring(0, 150)}...
                                </div>
                            </div>
                            <div class="card-footer">
                                <div class="d-flex justify-content-between align-items-center">
                                    <small class="text-muted">Usado ${template.usage_count || 0} vezes</small>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="app.viewTemplate('${template.id}')">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-warning" onclick="app.editTemplate('${template.id}')">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button class="btn btn-outline-${template.is_active ? 'secondary' : 'success'}" onclick="app.toggleTemplate('${template.id}')">
                                            <i class="fas fa-${template.is_active ? 'pause' : 'play'}"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = templatesHtml;
        this.updatePagination(data.pagination);
    }

    async loadAdmin() {
        try {
            const container = document.getElementById('admin-section');
            if (container) {
                this.showLoading('admin-section');
                
                // For now, show a simple admin interface
                container.innerHTML = `
                    <div class="row">
                        <div class="col-md-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5>Administração do Sistema</h5>
                                </div>
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h6>Status do Sistema</h6>
                                            <ul class="list-group">
                                                <li class="list-group-item d-flex justify-content-between">
                                                    Gmail API <span class="badge bg-success">Conectado</span>
                                                </li>
                                                <li class="list-group-item d-flex justify-content-between">
                                                    IA Service <span class="badge bg-success">Ativo</span>
                                                </li>
                                                <li class="list-group-item d-flex justify-content-between">
                                                    Banco de Dados <span class="badge bg-success">Online</span>
                                                </li>
                                            </ul>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>Ações Rápidas</h6>
                                            <div class="d-grid gap-2">
                                                <button class="btn btn-primary" onclick="app.processEmails()">
                                                    <i class="fas fa-sync me-1"></i>Processar Emails
                                                </button>
                                                <button class="btn btn-info" onclick="app.testAI()">
                                                    <i class="fas fa-flask me-1"></i>Testar IA
                                                </button>
                                                <button class="btn btn-warning" onclick="app.clearCache()">
                                                    <i class="fas fa-trash me-1"></i>Limpar Cache
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading admin:', error);
            this.showError('Erro ao carregar administração');
        }
    }

    renderAdmin(accountsStatus, settings) {
        const container = document.getElementById('adminContent');
        if (!container) return;

        const adminHtml = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Contas Gmail</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderGmailAccounts(accountsStatus)}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5>Configurações do Sistema</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderSystemSettings(settings)}
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = adminHtml;
    }

    renderGmailAccounts(accounts) {
        if (!accounts || accounts.length === 0) {
            return '<p class="text-muted">Nenhuma conta configurada</p>';
        }

        return accounts.map(account => `
            <div class="gmail-account-item mb-3">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${account.email}</strong>
                        <br>
                        <span class="badge badge-${account.status === 'active' ? 'success' : 'danger'}">
                            ${account.status === 'active' ? 'Ativa' : 'Inativa'}
                        </span>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-primary" onclick="dashboard.authenticateGmail('${account.email}')">
                            <i class="fas fa-key"></i> Autenticar
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="dashboard.refreshGmail('${account.email}')">
                            <i class="fas fa-sync"></i> Atualizar
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderSystemSettings(settings) {
        return `
            <form id="systemSettingsForm">
                <div class="form-group">
                    <label>Modelo de IA</label>
                    <select class="form-control" name="ai_model">
                        <option value="gpt-4" ${settings?.ai_model === 'gpt-4' ? 'selected' : ''}>GPT-4</option>
                        <option value="gpt-3.5-turbo" ${settings?.ai_model === 'gpt-3.5-turbo' ? 'selected' : ''}>GPT-3.5 Turbo</option>
                        <option value="claude-3" ${settings?.ai_model === 'claude-3' ? 'selected' : ''}>Claude 3</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Intervalo de Verificação (minutos)</label>
                    <input type="number" class="form-control" name="check_interval" value="${settings?.check_interval || 5}" min="1" max="60">
                </div>
                <div class="form-group">
                    <label>Limite de Confiança para Auto-resposta</label>
                    <input type="number" class="form-control" name="auto_response_threshold" value="${settings?.auto_response_threshold || 0.85}" min="0" max="1" step="0.01">
                </div>
                <div class="form-group">
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" name="auto_processing" ${settings?.auto_processing ? 'checked' : ''}>
                        <label class="form-check-label">Processamento Automático</label>
                    </div>
                </div>
                <button type="button" class="btn btn-primary" onclick="dashboard.saveSettings()">
                    <i class="fas fa-save"></i> Salvar Configurações
                </button>
                <button type="button" class="btn btn-outline-info ml-2" onclick="dashboard.testAI()">
                    <i class="fas fa-flask"></i> Testar IA
                </button>
            </form>
        `;
    }

    async authenticateGmail(email) {
        try {
            const result = await this.apiCall('/api/admin/gmail-accounts/authenticate', 'POST', {
                email: email
            });
            
            if (result.auth_url) {
                // Open authentication URL in new window
                window.open(result.auth_url, 'gmail_auth', 'width=600,height=600');
                this.showInfo('Complete a autenticação na nova janela');
            }
        } catch (error) {
            console.error('Error authenticating Gmail:', error);
            this.showError('Erro ao autenticar Gmail');
        }
    }

    async refreshGmail(email) {
        try {
            await this.apiCall('/api/admin/gmail-accounts/refresh', 'POST', {
                email: email
            });
            
            this.showSuccess('Conta Gmail atualizada');
            this.loadAdmin();
        } catch (error) {
            console.error('Error refreshing Gmail:', error);
            this.showError('Erro ao atualizar Gmail');
        }
    }

    async saveSettings() {
        try {
            const form = document.getElementById('systemSettingsForm');
            const formData = new FormData(form);
            const settings = Object.fromEntries(formData.entries());
            
            // Convert checkbox to boolean
            settings.auto_processing = formData.has('auto_processing');
            
            await this.apiCall('/api/admin/settings', 'POST', settings);
            this.showSuccess('Configurações salvas com sucesso');
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showError('Erro ao salvar configurações');
        }
    }

    async testAI() {
        try {
            const result = await this.apiCall('/api/admin/test-ai', 'POST', {
                test_message: 'Este é um teste de conectividade com a IA'
            });
            
            this.showSuccess('Teste de IA realizado com sucesso');
            console.log('AI Test Result:', result);
        } catch (error) {
            console.error('Error testing AI:', error);
            this.showError('Erro ao testar IA');
        }
    }

    // Utility methods
    async apiCall(url, method = 'GET', data = null) {
        // Use same protocol as current page (HTTPS in production)
        const protocol = "https:";
        const baseUrl = "https://" + window.location.host;

        const fullUrl = url.startsWith('/') ? `${baseUrl}${url}` : url;

        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(fullUrl, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async viewResponse(responseId) {
        try {
            const response = await this.apiCall(`/api/responses/${responseId}`);
            this.showResponseViewModal(response);
        } catch (error) {
            console.error('Error loading response:', error);
            this.showError('Erro ao carregar resposta');
        }
    }

    showResponseViewModal(response) {
        const modal = document.getElementById('responseViewModal');
        if (modal) {
            document.getElementById('responseViewSubject').textContent = `Re: ${response.email.subject}`;
            document.getElementById('responseViewTo').textContent = `${response.email.sender_name} <${response.email.sender_email}>`;
            document.getElementById('responseViewDate').textContent = this.formatDate(response.created_at);
            document.getElementById('responseViewContent').innerHTML = response.response_text;
            
            $(modal).modal('show');
        }
    }

    async approveResponse(responseId) {
        try {
            await this.apiCall(`/api/responses/${responseId}/approve`, 'POST', {
                approved: true
            });
            this.showSuccess('Resposta aprovada');
            this.loadCurrentSection();
        } catch (error) {
            console.error('Error approving response:', error);
            this.showError('Erro ao aprovar resposta');
        }
    }

    async sendResponse(responseId) {
        try {
            await this.apiCall(`/api/responses/${responseId}/send`, 'POST');
            this.showSuccess('Resposta enviada');
            this.loadCurrentSection();
        } catch (error) {
            console.error('Error sending response:', error);
            this.showError('Erro ao enviar resposta');
        }
    }

    async viewTemplate(templateId) {
        try {
            const template = await this.apiCall(`/api/templates/${templateId}`);
            this.showTemplateModal(template);
        } catch (error) {
            console.error('Error loading template:', error);
            this.showError('Erro ao carregar template');
        }
    }

    showTemplateModal(template) {
        const modal = document.getElementById('templateModal');
        if (modal) {
            document.getElementById('templateModalName').textContent = template.name;
            document.getElementById('templateModalCategory').textContent = template.category;
            document.getElementById('templateModalDescription').textContent = template.description || 'Sem descrição';
            document.getElementById('templateModalContent').innerHTML = template.content;
            
            $(modal).modal('show');
        }
    }

    async toggleTemplate(templateId) {
        try {
            await this.apiCall(`/api/templates/${templateId}/toggle`, 'POST');
            this.showSuccess('Status do template alterado');
            this.loadCurrentSection();
        } catch (error) {
            console.error('Error toggling template:', error);
            this.showError('Erro ao alterar template');
        }
    }

    // Helper methods
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    }

    formatTime(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Agora mesmo';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} min atrás`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h atrás`;
        return date.toLocaleDateString('pt-BR');
    }

    getActivityIcon(type) {
        const icons = {
            'email_received': 'envelope',
            'response_generated': 'reply',
            'response_sent': 'paper-plane',
            'classification': 'tags',
            'error': 'exclamation-triangle'
        };
        return icons[type] || 'info-circle';
    }

    getStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'processed': 'info',
            'responded': 'success',
            'ignored': 'secondary',
            'error': 'danger'
        };
        return colors[status] || 'secondary';
    }

    getStatusText(status) {
        const texts = {
            'pending': 'Pendente',
            'processed': 'Processado',
            'responded': 'Respondido',
            'ignored': 'Ignorado',
            'error': 'Erro'
        };
        return texts[status] || status;
    }

    getResponseStatusColor(status) {
        const colors = {
            'pending': 'warning',
            'approved': 'success',
            'sent': 'primary',
            'rejected': 'danger'
        };
        return colors[status] || 'secondary';
    }

    getResponseStatusText(status) {
        const texts = {
            'pending': 'Pendente',
            'approved': 'Aprovada',
            'sent': 'Enviada',
            'rejected': 'Rejeitada'
        };
        return texts[status] || status;
    }

    updatePagination(pagination) {
        const container = document.getElementById('paginationContainer');
        if (!container || !pagination) return;

        const { current_page, total_pages, has_prev, has_next } = pagination;
        
        let paginationHtml = '<nav><ul class="pagination justify-content-center">';
        
        // Previous button
        paginationHtml += `
            <li class="page-item ${!has_prev ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${current_page - 1}" ${!has_prev ? 'tabindex="-1"' : ''}>
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers
        const startPage = Math.max(1, current_page - 2);
        const endPage = Math.min(total_pages, current_page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === current_page ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }
        
        // Next button
        paginationHtml += `
            <li class="page-item ${!has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${current_page + 1}" ${!has_next ? 'tabindex="-1"' : ''}>
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationHtml += '</ul></nav>';
        container.innerHTML = paginationHtml;
    }

    showLoading(containerId = null) {
        const loadingHtml = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Carregando...</span>
                </div>
                <p class="mt-2">Carregando...</p>
            </div>
        `;
        
        if (containerId) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = loadingHtml;
            }
        }
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showInfo(message) {
        this.showAlert(message, 'info');
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer') || document.body;
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert">
                    <span>&times;</span>
                </button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    startAutoRefresh() {
        // Refresh dashboard every 5 minutes
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            }
        }, 300000);
    }

    searchEmails(query) {
        // Debounce search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.currentPage = 1;
            this.loadEmails();
        }, 500);
    }

    applyFilter(filter) {
        // Update filter UI
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
        
        // Reset page and reload
        this.currentPage = 1;
        this.loadCurrentSection();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new GmailAIDashboard();
    window.app = window.dashboard; // Create app alias for HTML onclick handlers
});

// Global functions for onclick handlers
window.dashboard = null;
window.app = {
    processEmails: function() {
        if (window.dashboard) {
            return window.dashboard.processEmails();
        }
    },
    filterEmails: function() {
        if (window.dashboard) {
            window.dashboard.currentPage = 1;
            return window.dashboard.loadEmails();
        }
    },
    clearFilters: function() {
        // Clear all filter inputs
        const filters = ['account-filter', 'status-filter', 'type-filter', 'search-input'];
        filters.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                element.value = '';
            }
        });
        
        if (window.dashboard) {
            window.dashboard.currentPage = 1;
            return window.dashboard.loadEmails();
        }
    },
    viewEmail: function(emailId) {
        if (window.dashboard) {
            return window.dashboard.viewEmail(emailId);
        }
    },
    generateResponse: function(emailId) {
        if (window.dashboard) {
            return window.dashboard.generateResponse(emailId);
        }
    },
    testAI: function() {
        if (window.dashboard) {
            return window.dashboard.testAI();
        }
    },
    clearCache: function() {
        // Clear browser cache
        if ('caches' in window) {
            caches.keys().then(function(names) {
                for (let name of names) {
                    caches.delete(name);
                }
            });
        }
        
        // Force page reload
        window.location.reload(true);
    },
    
    // Response functions
    generateBulkResponses: function() {
        if (window.dashboard) {
            window.dashboard.showAlert('Gerando respostas em lote...', 'info');
            // TODO: Implement bulk response generation
        }
    },
    filterResponses: function() {
        if (window.dashboard) {
            window.dashboard.currentPage = 1;
            return window.dashboard.loadResponses();
        }
    },
    clearResponseFilters: function() {
        const filters = ['response-status-filter', 'response-template-filter', 'response-search-input'];
        filters.forEach(filterId => {
            const element = document.getElementById(filterId);
            if (element) {
                element.value = '';
            }
        });
        
        if (window.dashboard) {
            window.dashboard.currentPage = 1;
            return window.dashboard.loadResponses();
        }
    },
    viewResponse: function(responseId) {
        if (window.dashboard) {
            return window.dashboard.viewResponse(responseId);
        }
    },
    approveResponse: function(responseId) {
        if (window.dashboard) {
            return window.dashboard.approveResponse(responseId);
        }
    },
    editResponse: function(responseId) {
        if (window.dashboard) {
            window.dashboard.showAlert('Função de edição em desenvolvimento', 'info');
        }
    },
    sendResponse: function(responseId) {
        if (window.dashboard) {
            return window.dashboard.sendResponse(responseId);
        }
    },
    generateResponseFromModal: function() {
        const emailId = document.getElementById('responseEmailId').value;
        if (emailId && window.dashboard) {
            return window.dashboard.generateResponse(emailId);
        }
    },
    generateAIResponse: function() {
        const emailId = document.getElementById('responseEmailId').value;
        const template = document.getElementById('responseTemplate').value;
        
        if (window.dashboard) {
            window.dashboard.showAlert('Gerando resposta com IA...', 'info');
            // TODO: Implement AI response generation
        }
    },
    saveResponse: function() {
        const emailId = document.getElementById('responseEmailId').value;
        const content = document.getElementById('responseContent').value;
        const template = document.getElementById('responseTemplate').value;
        const sendImmediately = document.getElementById('sendImmediately').checked;
        
        if (!content.trim()) {
            if (window.dashboard) {
                window.dashboard.showAlert('Por favor, insira o conteúdo da resposta', 'warning');
            }
            return;
        }
        
        if (window.dashboard) {
            return window.dashboard.sendResponse(emailId, {
                content: content,
                template_id: template,
                send_immediately: sendImmediately
            });
        }
    },
    
    // Template functions
    showCreateTemplateModal: function() {
        // Clear form
        document.getElementById('templateId').value = '';
        document.getElementById('templateName').value = '';
        document.getElementById('templateCategory').value = 'vendas';
        document.getElementById('templateDescription').value = '';
        document.getElementById('templateContent').value = '';
        document.getElementById('templateActive').checked = true;
        document.getElementById('templateModalTitle').textContent = 'Novo Template';
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('templateModal'));
        modal.show();
    },
    filterTemplatesByCategory: function(category) {
        // Update active button
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        if (window.dashboard) {
            // TODO: Implement category filtering
            window.dashboard.showAlert(`Filtrando templates por: ${category}`, 'info');
        }
    },
    viewTemplate: function(templateId) {
        if (window.dashboard) {
            return window.dashboard.viewTemplate(templateId);
        }
    },
    editTemplate: function(templateId) {
        if (window.dashboard) {
            // TODO: Load template data and show modal
            window.dashboard.showAlert('Carregando template para edição...', 'info');
        }
    },
    toggleTemplate: function(templateId) {
        if (window.dashboard) {
            return window.dashboard.toggleTemplate(templateId);
        }
    },
    saveTemplate: function() {
        const templateId = document.getElementById('templateId').value;
        const name = document.getElementById('templateName').value;
        const category = document.getElementById('templateCategory').value;
        const description = document.getElementById('templateDescription').value;
        const content = document.getElementById('templateContent').value;
        const isActive = document.getElementById('templateActive').checked;
        
        if (!name.trim() || !content.trim()) {
            if (window.dashboard) {
                window.dashboard.showAlert('Por favor, preencha nome e conteúdo do template', 'warning');
            }
            return;
        }
        
        const templateData = {
            name: name,
            category: category,
            description: description,
            content: content,
            is_active: isActive
        };
        
        if (window.dashboard) {
            // TODO: Implement template saving
            window.dashboard.showAlert('Salvando template...', 'info');
            
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('templateModal'));
            if (modal) {
                modal.hide();
            }
        }
    }
};
