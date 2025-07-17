// Fix Mixed Content Issues - Force HTTPS for all API calls
// Gmail AI Agent - Prof. Diogo Moreira

// Override the apiCall method to force HTTPS
(function() {
    'use strict';
    
    // Wait for the dashboard to be initialized
    document.addEventListener('DOMContentLoaded', function() {
        // Wait a bit more for the dashboard object to be created
        setTimeout(function() {
            if (window.dashboard && window.dashboard.apiCall) {
                console.log('Patching apiCall method to force HTTPS...');
                
                // Store the original method
                const originalApiCall = window.dashboard.apiCall.bind(window.dashboard);
                
                // Override with HTTPS-forced version
                window.dashboard.apiCall = async function(url, method = 'GET', data = null) {
                    // Force HTTPS for all URLs
                    let httpsUrl = url;
                    if (url.startsWith('http://')) {
                        httpsUrl = url.replace('http://', 'https://');
                        console.log(`Fixed Mixed Content: ${url} -> ${httpsUrl}`);
                    } else if (url.startsWith('/')) {
                        httpsUrl = `https://${window.location.host}${url}`;
                        console.log(`Added HTTPS base: ${url} -> ${httpsUrl}`);
                    }
                    
                    // Call the original method with the HTTPS URL
                    return originalApiCall(httpsUrl, method, data);
                };
                
                console.log('✅ Mixed Content fix applied successfully!');
                
                // Force reload of current section to apply the fix
                if (window.dashboard.currentSection) {
                    console.log(`Reloading section: ${window.dashboard.currentSection}`);
                    window.dashboard.loadCurrentSection();
                }
            } else {
                console.warn('Dashboard object not found, retrying...');
                // Retry after another delay
                setTimeout(arguments.callee, 500);
            }
        }, 1000);
    });
})();
