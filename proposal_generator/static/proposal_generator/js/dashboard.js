// Dashboard Common JavaScript

// API Base URL
const API_BASE = '/proposals/api';

// Current user (can be made dynamic later)
const CURRENT_USER = 'user123';

// Common utilities
const utils = {
    // Format date to readable string
    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },

    // Format datetime to readable string
    formatDateTime: (dateString) => {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Debounce function for search inputs
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Show toast notification
    showToast: (message, type = 'info') => {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        const toast = createToast(message, type);
        toastContainer.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove after hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Copy text to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            utils.showToast('Copied to clipboard!', 'success');
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            utils.showToast('Copied to clipboard!', 'success');
        }
    },

    // Download text as file
    downloadAsFile: (text, filename) => {
        const blob = new Blob([text], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        utils.showToast('File downloaded!', 'success');
    },

    // Show loading spinner
    showLoading: (element, text = 'Loading...') => {
        element.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary me-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <span>${text}</span>
            </div>
        `;
    },

    // Show error message
    showError: (element, message = 'An error occurred') => {
        element.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    },

    // Show empty state
    showEmpty: (element, message = 'No data available', icon = 'fas fa-inbox') => {
        element.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="${icon} fa-3x mb-3"></i>
                <h5>Nothing Here Yet</h5>
                <p>${message}</p>
            </div>
        `;
    }
};

// CSRF Token helper
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    
    if (csrfCookie) {
        return csrfCookie.split('=')[1];
    }
    
    // Fallback: try to get from meta tag
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta) {
        return csrfMeta.getAttribute('content');
    }
    
    // Fallback: try to get from hidden input
    const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    return null;
}

// API service
const api = {
    // Generic API call
    call: async (endpoint, options = {}) => {
        const url = `${API_BASE}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add CSRF token for non-GET requests
        if (options.method && options.method !== 'GET') {
            const csrfToken = getCSRFToken();
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
        }
        
        const config = {
            headers,
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                // If response isn't JSON, create error with status text
                throw new Error(`Server Error: ${response.status} ${response.statusText}`);
            }
            
            if (!response.ok) {
                // Provide detailed error message
                const errorMsg = data.error || data.message || `HTTP ${response.status}: ${response.statusText}`;
                console.error('API Error Details:', {
                    url,
                    status: response.status,
                    statusText: response.statusText,
                    error: data
                });
                throw new Error(errorMsg);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            console.error('Request details:', { url, config });
            throw error;
        }
    },

    // Portfolio endpoints
    portfolio: {
        create: (projectData) => api.call('/portfolio/create/', {
            method: 'POST',
            body: JSON.stringify(projectData)
        }),

        list: (userId = CURRENT_USER, params = {}) => {
            const query = new URLSearchParams(params).toString();
            return api.call(`/portfolio/user/${userId}/${query ? '?' + query : ''}`);
        },

        get: (projectId) => api.call(`/portfolio/detail/${projectId}/`),

        update: (projectId, projectData) => api.call(`/portfolio/detail/${projectId}/`, {
            method: 'PUT',
            body: JSON.stringify(projectData)
        }),

        delete: (projectId) => api.call(`/portfolio/detail/${projectId}/`, {
            method: 'DELETE'
        }),

        findSimilar: (jobDescription, userId = CURRENT_USER, topK = 3) => api.call('/portfolio/similar/', {
            method: 'POST',
            body: JSON.stringify({
                job_description: jobDescription,
                user_id: userId,
                top_k: topK
            })
        })
    },

    // Proposal endpoints
    proposal: {
        generate: (jobDescription, userId = CURRENT_USER) => api.call('/generate/', {
            method: 'POST',
            body: JSON.stringify({
                job_description: jobDescription,
                user_id: userId
            })
        }),

        generateCustom: (data, userId = CURRENT_USER) => api.call('/generate/custom/', {
            method: 'POST',
            body: JSON.stringify({
                ...data,
                user_id: userId
            })
        })
    }
};

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Create toast element
function createToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = 'toast fade';
    toast.setAttribute('role', 'alert');
    
    const iconMap = {
        success: 'fas fa-check-circle text-success',
        danger: 'fas fa-exclamation-circle text-danger',
        warning: 'fas fa-exclamation-triangle text-warning',
        info: 'fas fa-info-circle text-info'
    };
    
    toast.innerHTML = `
        <div class="toast-header">
            <i class="${iconMap[type] || iconMap.info} me-2"></i>
            <strong class="me-auto">Notification</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    return toast;
}

// Form validation helpers
const validation = {
    // Validate required fields
    required: (value, fieldName) => {
        if (!value || value.trim() === '') {
            throw new Error(`${fieldName} is required`);
        }
        return true;
    },

    // Validate email
    email: (value) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailRegex.test(value)) {
            throw new Error('Please enter a valid email address');
        }
        return true;
    },

    // Validate URL
    url: (value) => {
        if (!value) return true; // Optional field
        try {
            new URL(value);
            return true;
        } catch {
            throw new Error('Please enter a valid URL');
        }
    },

    // Validate minimum length
    minLength: (value, length, fieldName) => {
        if (value && value.length < length) {
            throw new Error(`${fieldName} must be at least ${length} characters long`);
        }
        return true;
    },

    // Validate form
    validateForm: (formData, rules) => {
        const errors = [];
        
        for (const [field, rule] of Object.entries(rules)) {
            const value = formData.get(field);
            
            try {
                if (rule.required) {
                    validation.required(value, rule.label || field);
                }
                
                if (rule.type === 'email') {
                    validation.email(value);
                }
                
                if (rule.type === 'url') {
                    validation.url(value);
                }
                
                if (rule.minLength) {
                    validation.minLength(value, rule.minLength, rule.label || field);
                }
            } catch (error) {
                errors.push(error.message);
            }
        }
        
        return errors;
    }
};

// Local storage helpers
const storage = {
    // Save data to localStorage
    save: (key, data) => {
        try {
            localStorage.setItem(key, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    },

    // Load data from localStorage
    load: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            return defaultValue;
        }
    },

    // Remove data from localStorage
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Error removing from localStorage:', error);
        }
    }
};

// Dashboard stats updater
const dashboardStats = {
    // Update sidebar stats
    updateSidebar: async () => {
        try {
            const portfolioData = await api.portfolio.list();
            const totalProjects = portfolioData.count || 0;
            
            // Update sidebar counters
            const portfolioCountEl = document.getElementById('portfolio-count');
            const proposalsCountEl = document.getElementById('proposals-count');
            
            if (portfolioCountEl) portfolioCountEl.textContent = totalProjects;
            if (proposalsCountEl) proposalsCountEl.textContent = storage.load('proposalsGenerated', 0);
            
        } catch (error) {
            console.error('Error updating sidebar stats:', error);
        }
    },

    // Update main dashboard stats
    updateDashboard: async () => {
        try {
            const portfolioData = await api.portfolio.list();
            const projects = portfolioData.results || [];
            
            // Update all dashboard counters
            const updates = {
                'dashboard-portfolio-count': portfolioData.count || 0,
                'dashboard-featured-count': projects.filter(p => p.is_featured).length,
                'dashboard-analyzed-count': projects.filter(p => p.technologies && p.technologies.length > 0).length,
                'total-projects': portfolioData.count || 0,
                'featured-projects': projects.filter(p => p.is_featured).length,
                'analyzed-projects': projects.filter(p => p.technologies && p.technologies.length > 0).length
            };
            
            Object.entries(updates).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.textContent = value;
            });
            
        } catch (error) {
            console.error('Error updating dashboard stats:', error);
        }
    }
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Update stats on page load
    dashboardStats.updateSidebar();
    
    // Add global error handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        utils.showToast('An unexpected error occurred. Please try again.', 'danger');
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + K for quick search (if implemented)
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
});

// Export for use in other scripts
window.dashboardUtils = utils;
window.dashboardAPI = api;
window.dashboardValidation = validation;
window.dashboardStorage = storage;
window.dashboardStats = dashboardStats; 