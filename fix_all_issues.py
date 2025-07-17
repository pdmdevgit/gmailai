#!/usr/bin/env python3
"""
Script para corrigir todos os problemas identificados no Gmail AI Agent
"""

import os
import json

def fix_javascript_functions():
    """Corrigir funções JavaScript que estão faltando"""
    
    js_fixes = """
    // Adicionar funções que estão faltando no objeto window.app
    
    // Função para visualizar resposta
    async viewResponse(responseId) {
        if (window.dashboard) {
            try {
                const response = await window.dashboard.apiCall(`/api/responses/${responseId}`);
                window.dashboard.showAlert(`Visualizando resposta: ${response.subject}`, 'info');
            } catch (error) {
                window.dashboard.showError('Erro ao carregar resposta');
            }
        }
    },
    
    // Função para aprovar resposta
    async approveResponse(responseId) {
        if (window.dashboard) {
            try {
                await window.dashboard.apiCall(`/api/responses/${responseId}/approve`, 'POST', {
                    approved_by: 'admin'
                });
                window.dashboard.showSuccess('Resposta aprovada com sucesso!');
                window.dashboard.loadCurrentSection();
            } catch (error) {
                window.dashboard.showError('Erro ao aprovar resposta');
            }
        }
    },
    
    // Função para enviar resposta
    async sendResponse(responseId) {
        if (window.dashboard) {
            try {
                await window.dashboard.apiCall(`/api/responses/${responseId}/send`, 'POST');
                window.dashboard.showSuccess('Resposta enviada com sucesso!');
                window.dashboard.loadCurrentSection();
            } catch (error) {
                window.dashboard.showError('Erro ao enviar resposta');
            }
        }
    },
    
    // Função para visualizar template
    async viewTemplate(templateId) {
        if (window.dashboard) {
            try {
                const template = await window.dashboard.apiCall(`/api/templates/${templateId}`);
                window.dashboard.showAlert(`Visualizando template: ${template.name}`, 'info');
            } catch (error) {
                window.dashboard.showError('Erro ao carregar template');
            }
        }
    },
    
    // Função para alternar status do template
    async toggleTemplate(templateId) {
        if (window.dashboard) {
            try {
                await window.dashboard.apiCall(`/api/templates/${templateId}/toggle`, 'POST');
                window.dashboard.showSuccess('Status do template alterado!');
                window.dashboard.loadCurrentSection();
            } catch (error) {
                window.dashboard.showError('Erro ao alterar template');
            }
        }
    }
    """
    
    return js_fixes

def create_complete_dashboard_js():
    """Criar arquivo JavaScript completo e funcional"""
    
    complete_js = '''// Gmail AI Agent Dashboard JavaScript
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

        // Show selected section
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
            const overview = await this.apiCall('/api/dashboard/overview');
            this.updateOverviewStats(overview);
            await this.loadRecentEmails();
            await this.loadRecentResponses();
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.showError('Erro ao carregar dashboard');
        }
    }

    updateOverviewStats(data) {
        if (data && data.summary) {
            const totalEmailsEl = document.getElementById('total-emails');
            const emailsTodayEl = document.getElementById('emails-today');
            const totalResponsesEl = document.getElementById('total-responses');
            const responsesTodayEl = document.getElementById('responses-today');
            const responseRateEl = document.getElementById('response-rate');
            const pendingResponsesEl = document.getElementById('pending-responses');

            if (totalEmailsEl) totalEmailsEl.textContent = data.summary.total_emails || 0;
            if (emailsTodayEl) emailsTodayEl.textContent = data.summary.emails_today || 0;
            if (totalResponsesEl) totalResponsesEl.textContent = data.summary.total_responses || 0;
            if (responsesTodayEl) responsesTodayEl.textContent = data.summary.responses_today || 0;
            if (responseRateEl) responseRateEl.textContent = `${data.processing?.response_rate || 0}%`;
            if (pendingResponsesEl) pendingResponsesEl.textContent = data.summary.pending_responses || 0;
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

    async loadEmails() {
        try {
            this.showLoading('emails-table-container');
            
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage
            });

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

        const tableHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>De</th>
                            <th>Assunto</th>
                            <th>Data</th>
                            <th>Status</th>
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
                                        <small class="text-muted">${email.body_preview || ''}</small>
                                    </div>
                                </td>
                                <td>
                                    <small>${this.formatDate(email.received_at)}</small>
                                </td>
                                <td>
                                    <span class="badge bg-${this.getStatusColor(email.status)}">${this.getStatusText(email.status)}</span>
                                </td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="app.viewEmail('${email.id}')">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                        <button class="btn btn-outline-success" onclick="app.generateResponse('${email.id}')">
                                            <i class="fas fa-reply"></i>
                                        </button>
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

    async loadResponses() {
        try {
            this.showLoading('responses-table-container');
            
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage
            });

            const data = await this.apiCall(`/api/responses/?${params}`);
            this.renderResponses(data);
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

        const tableHtml = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Para</th>
                            <th>Assunto</th>
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
                                        <strong>${response.subject}</strong><br>
                                        <small class="text-muted">${response.body_preview || ''}</small>
                                    </div>
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
                                        ${response.status === 'draft' ? `
                                            <button class="btn btn-outline-success" onclick="app.approveResponse('${response.id}')">
                                                <i class="fas fa-check"></i>
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
            this.showLoading('templates-grid-container');
            
            const params = new URLSearchParams({
                page: this.currentPage,
                per_page: this.itemsPerPage
            });

            const data = await this.apiCall(`/api/templates/?${params}`);
            this.renderTemplates(data);
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
                                <span class="badge bg-${template.is_active ? 'success' : 'secondary'}">
                                    ${template.is_active ? 'Ativo' : 'Inativo'}
                                </span>
                            </div>
                            <div class="card-body">
                                <p class="card-text text-muted small">
                                    ${template.description || 'Sem descrição'}
                                </p>
                                <div class="template-preview bg-light p-2 rounded small" style="max-height: 100px; overflow: hidden;">
                                    ${template.body_preview || ''}
                                </div>
                            </div>
                            <div class="card-footer">
                                <div class="d-flex justify-content-between align-items-center">
                                    <small class="text-muted">Usado ${template.usage_count || 0} vezes</small>
                                    <div class="btn-group btn-group-sm">
                                        <button class="btn btn-outline-primary" onclick="app.viewTemplate('${template.id}')">
                                            <i class="fas fa-eye"></i>
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

    async processEmails() {
        try {
            this.showAlert('Processando emails...', 'info');
            const result = await this.apiCall('/api/emails/process', 'POST');
            this.showSuccess(`Processamento concluído! ${result.processed_count || 0} emails processados`);
            setTimeout(() => this.loadDashboard(), 2000);
        } catch (error) {
            console.error('Error processing emails:', error);
            this.showError('Erro ao processar emails');
        }
    }

    async testAI() {
        try {
            const result = await this.apiCall('/api/admin/test-ai', 'POST', {
                test_message: 'Teste de conectividade com IA'
            });
            this.showSuccess('Teste de IA realizado com sucesso!');
        } catch (error) {
            console.error('Error testing AI:', error);
            this.showError('Erro ao testar IA');
        }
    }

    // Utility methods
    async apiCall(url, method = 'GET', data = null) {
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

    getActiveFilters() {
        return {
            status: document.getElementById('status-filter')?.value,
            account: document.getElementById('account-filter')?.value,
            search: document.getElementById('search-input')?.value
        };
    }

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
            'draft': 'warning',
            'approved': 'success',
            'sent': 'primary',
            'rejected': 'danger'
        };
        return colors[status] || 'secondary';
    }

    getResponseStatusText(status) {
        const texts = {
            'draft': 'Rascunho',
            'approved': 'Aprovada',
            'sent': 'Enviada',
            'rejected': 'Rejeitada'
        };
        return texts[status] || status;
    }

    updatePagination(pagination) {
        const container = document.getElementById('paginationContainer');
        if (!container || !pagination) return;

        const { page, pages, has_prev, has_next } = pagination;
        
        let paginationHtml = '<nav><ul class="pagination justify-content-center">';
        
        paginationHtml += `
            <li class="page-item ${!has_prev ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${page - 1}">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        const startPage = Math.max(1, page - 2);
        const endPage = Math.min(pages, page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `
                <li class="page-item ${i === page ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }
        
        paginationHtml += `
            <li class="page-item ${!has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${page + 1}">
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

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer') || document.body;
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 9999;" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
        
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    startAutoRefresh() {
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            }
        }, 300000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.dashboard = new GmailAIDashboard();
    
    // Create app object with all necessary functions
    window.app = {
        dashboard: window.dashboard,
        
        processEmails: function() {
            return window.dashboard.processEmails();
        },
        
        filterEmails: function() {
            window.dashboard.currentPage = 1;
            return window.dashboard.loadEmails();
        },
        
        clearFilters: function() {
            const filters = ['account-filter', 'status-filter', 'search-input'];
            filters.forEach(filterId => {
                const element = document.getElementById(filterId);
                if (element) {
                    element.value = '';
                }
            });
            window.dashboard.currentPage = 1;
            return window.dashboard.loadEmails();
        },
        
        viewEmail: function(emailId) {
            window.dashboard.showAlert('Visualizando email...', 'info');
        },
        
        generateResponse: async function(emailId) {
            try {
                window.dashboard.showAlert('Gerando resposta...', 'info');
                const response = await window.dashboard.apiCall(`/api/emails/${emailId}/responses`, 'POST', {
                    custom_instructions: 'Gerar resposta profissional e cordial'
                });
                window.dashboard.showSuccess('Resposta gerada com sucesso!');
                window.dashboard.loadCurrentSection();
            } catch (error) {
                window.dashboard.showError('Erro ao gerar resposta');
            }
        },
        
        testAI: function() {
            return window.dashboard.testAI();
        },
        
        viewResponse: async function(responseId) {
            try {
                const response = await window.dashboard.apiCall(`/api/responses/${responseId}`);
                window.dashboard.showAlert(`Visualizando resposta: ${response.subject}`, 'info');
            } catch (error) {
                window
