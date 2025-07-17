// Correção definitiva para Mixed Content - Forçar HTTPS em todas as chamadas
(function() {
    'use strict';
    
    console.log('🔧 Aplicando correção definitiva de Mixed Content...');
    
    // Função para garantir HTTPS em URLs
    function forceHTTPS(url) {
        if (!url) return url;
        if (url.startsWith('http://')) {
            return url.replace('http://', 'https://');
        }
        if (url.startsWith('//')) {
            return 'https:' + url;
        }
        if (!url.startsWith('http')) {
            return 'https://' + window.location.host + url;
        }
        return url;
    }
    
    // Interceptar XMLHttpRequest
    const originalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function() {
        const xhr = new originalXHR();
        const originalOpen = xhr.open;
        
        xhr.open = function(method, url, async, user, password) {
            const secureUrl = forceHTTPS(url);
            console.log(`🔒 XMLHttpRequest interceptado: ${url} -> ${secureUrl}`);
            return originalOpen.call(this, method, secureUrl, async, user, password);
        };
        
        return xhr;
    };
    
    // Interceptar fetch
    const originalFetch = window.fetch;
    window.fetch = function(input, init) {
        let url = typeof input === 'string' ? input : input.url;
        const secureUrl = forceHTTPS(url);
        
        if (typeof input === 'string') {
            console.log(`🔒 Fetch interceptado: ${url} -> ${secureUrl}`);
            return originalFetch.call(this, secureUrl, init);
        } else {
            console.log(`🔒 Fetch interceptado (Request): ${url} -> ${secureUrl}`);
            return originalFetch.call(this, new Request(secureUrl, input), init);
        }
    };
    
    // Interceptar jQuery AJAX se disponível
    if (window.jQuery && window.jQuery.ajax) {
        const originalAjax = window.jQuery.ajax;
        window.jQuery.ajax = function(url, options) {
            if (typeof url === 'object') {
                options = url;
                url = options.url;
            }
            if (options && options.url) {
                options.url = forceHTTPS(options.url);
                console.log(`🔒 jQuery AJAX interceptado: ${url} -> ${options.url}`);
            } else if (url) {
                url = forceHTTPS(url);
                console.log(`🔒 jQuery AJAX interceptado: ${url}`);
            }
            return originalAjax.call(this, url, options);
        };
    }
    
    // Função para corrigir URLs já existentes
    function fixExistingURLs() {
        // Corrigir links em elementos
        const elements = document.querySelectorAll('[href], [src], [action]');
        elements.forEach(el => {
            ['href', 'src', 'action'].forEach(attr => {
                if (el.hasAttribute(attr)) {
                    const url = el.getAttribute(attr);
                    const secureUrl = forceHTTPS(url);
                    if (url !== secureUrl) {
                        el.setAttribute(attr, secureUrl);
                        console.log(`🔒 URL corrigida: ${attr}="${url}" -> "${secureUrl}"`);
                    }
                }
            });
        });
        
        // Corrigir URLs em estilos inline
        const styleElements = document.querySelectorAll('[style]');
        styleElements.forEach(el => {
            const style = el.getAttribute('style');
            if (style && style.includes('url(')) {
                const fixedStyle = style.replace(/url\(['"]?http:\/\/[^'"]*['"]?\)/g, (match) => {
                    return match.replace('http://', 'https://');
                });
                if (style !== fixedStyle) {
                    el.setAttribute('style', fixedStyle);
                    console.log('🔒 Estilo inline corrigido');
                }
            }
        });
    }
    
    // Aplicar correção imediatamente
    fixExistingURLs();
    
    // Aplicar correção periodicamente para elementos dinâmicos
    setInterval(fixExistingURLs, 1000);
    
    // Observar mudanças no DOM
    if (window.MutationObserver) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        fixExistingURLs();
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    console.log('✅ Correção definitiva de Mixed Content aplicada com sucesso!');
    
    // Forçar recarregamento das seções
    setTimeout(() => {
        console.log('🔄 Recarregando seções com HTTPS...');
        if (window.loadDashboardSection) {
            window.loadDashboardSection('dashboard');
        }
    }, 100);
})();
