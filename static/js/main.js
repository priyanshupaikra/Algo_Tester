/**
 * Main JavaScript file for Algorithmic Trading Backtester
 * Handles form interactions, validation, and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize date inputs with default values
    initializeDateInputs();
    
    // Setup form validation
    setupFormValidation();
    
    // Setup symbol validation
    setupSymbolValidation();
    
    // Setup strategy parameter toggles
    setupStrategyToggle();
    
    // Setup loading states
    setupLoadingStates();
    
    // Setup tooltips and help text
    setupTooltips();
    
    // Setup chart responsiveness
    setupChartResponsiveness();
    
    console.log('Algorithmic Trading Backtester initialized');
}

/**
 * Initialize date inputs with sensible defaults
 */
function initializeDateInputs() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput) {
        const today = new Date();
        const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
        
        // Set default values if not already set
        if (!endDateInput.value) {
            endDateInput.value = today.toISOString().split('T')[0];
        }
        if (!startDateInput.value) {
            startDateInput.value = oneYearAgo.toISOString().split('T')[0];
        }
        
        // Set min/max constraints
        endDateInput.max = today.toISOString().split('T')[0];
        startDateInput.max = today.toISOString().split('T')[0];
        
        // Add change listeners for date validation
        startDateInput.addEventListener('change', validateDateRange);
        endDateInput.addEventListener('change', validateDateRange);
    }
}

/**
 * Validate date range to ensure start date is before end date
 */
function validateDateRange() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    if (startDateInput && endDateInput && startDateInput.value && endDateInput.value) {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        
        if (startDate >= endDate) {
            showError('Start date must be before end date');
            startDateInput.classList.add('form-invalid');
            endDateInput.classList.add('form-invalid');
            return false;
        } else {
            startDateInput.classList.remove('form-invalid');
            endDateInput.classList.remove('form-invalid');
            startDateInput.classList.add('form-valid');
            endDateInput.classList.add('form-valid');
            return true;
        }
    }
    return true;
}

/**
 * Setup comprehensive form validation
 */
function setupFormValidation() {
    const backtestForm = document.getElementById('backtestForm');
    
    if (backtestForm) {
        backtestForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            showFormLoading();
        });
        
        // Real-time validation for required fields
        const requiredFields = backtestForm.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            field.addEventListener('blur', validateField);
            field.addEventListener('input', clearFieldError);
        });
    }
}

/**
 * Validate the entire form before submission
 */
function validateForm() {
    let isValid = true;
    const errors = [];
    
    // Validate strategy selection
    const strategyType = document.getElementById('strategy_type');
    if (strategyType && !strategyType.value) {
        errors.push('Please select a trading strategy');
        strategyType.classList.add('form-invalid');
        isValid = false;
    }
    
    // Validate symbol
    const symbol = document.getElementById('symbol');
    if (symbol && (!symbol.value || symbol.value.trim().length === 0)) {
        errors.push('Please enter a valid stock symbol');
        symbol.classList.add('form-invalid');
        isValid = false;
    }
    
    // Validate date range
    if (!validateDateRange()) {
        errors.push('Please ensure start date is before end date');
        isValid = false;
    }
    
    // Validate initial capital
    const initialCapital = document.getElementById('initial_capital');
    if (initialCapital) {
        const capital = parseFloat(initialCapital.value);
        if (isNaN(capital) || capital < 1000) {
            errors.push('Initial capital must be at least $1,000');
            initialCapital.classList.add('form-invalid');
            isValid = false;
        }
    }
    
    // Validate strategy-specific parameters
    const strategyValue = strategyType ? strategyType.value : '';
    if (strategyValue === 'ma_crossover') {
        const shortWindow = document.getElementById('short_window');
        const longWindow = document.getElementById('long_window');
        
        if (shortWindow && longWindow) {
            const short = parseInt(shortWindow.value);
            const long = parseInt(longWindow.value);
            
            if (short >= long) {
                errors.push('Short window must be less than long window');
                shortWindow.classList.add('form-invalid');
                longWindow.classList.add('form-invalid');
                isValid = false;
            }
        }
    }
    
    // Display errors if any
    if (errors.length > 0) {
        showError(errors.join('<br>'));
    }
    
    return isValid;
}

/**
 * Validate individual form field
 */
function validateField(event) {
    const field = event.target;
    
    if (field.hasAttribute('required') && !field.value.trim()) {
        field.classList.add('form-invalid');
        return false;
    } else {
        field.classList.remove('form-invalid');
        field.classList.add('form-valid');
        return true;
    }
}

/**
 * Clear field error styling
 */
function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('form-invalid');
    
    if (field.value.trim()) {
        field.classList.add('form-valid');
    } else {
        field.classList.remove('form-valid');
    }
}

/**
 * Setup symbol validation with debouncing
 */
function setupSymbolValidation() {
    const symbolInput = document.getElementById('symbol');
    let validationTimeout;
    
    if (symbolInput) {
        symbolInput.addEventListener('input', function() {
            const symbol = this.value.trim().toUpperCase();
            this.value = symbol;
            
            // Clear previous timeout
            clearTimeout(validationTimeout);
            
            // Reset symbol status
            hideSymbolStatus();
            
            if (symbol.length >= 1) {
                // Show loading after short delay
                validationTimeout = setTimeout(() => {
                    validateSymbol(symbol);
                }, 500);
            }
        });
    }
}

/**
 * Validate symbol using API endpoint
 */
function validateSymbol(symbol) {
    if (!symbol || symbol.length === 0) {
        hideSymbolStatus();
        return;
    }
    
    showSymbolLoading();
    
    // Since we're avoiding fetch calls per guidelines, we'll use a simple approach
    // The actual validation will happen on form submission
    setTimeout(() => {
        // Simple client-side validation for common patterns
        if (/^[A-Z]{1,5}$/.test(symbol)) {
            showSymbolValid();
        } else {
            showSymbolInvalid();
        }
    }, 500);
}

/**
 * Show symbol loading state
 */
function showSymbolLoading() {
    const statusDiv = document.getElementById('symbolStatus');
    const loading = document.getElementById('symbolLoading');
    const valid = document.getElementById('symbolValid');
    const invalid = document.getElementById('symbolInvalid');
    
    if (statusDiv && loading) {
        statusDiv.classList.remove('hidden');
        loading.classList.remove('hidden');
        if (valid) valid.classList.add('hidden');
        if (invalid) invalid.classList.add('hidden');
    }
}

/**
 * Show symbol valid state
 */
function showSymbolValid() {
    const loading = document.getElementById('symbolLoading');
    const valid = document.getElementById('symbolValid');
    const invalid = document.getElementById('symbolInvalid');
    
    if (loading) loading.classList.add('hidden');
    if (valid) valid.classList.remove('hidden');
    if (invalid) invalid.classList.add('hidden');
}

/**
 * Show symbol invalid state
 */
function showSymbolInvalid() {
    const loading = document.getElementById('symbolLoading');
    const valid = document.getElementById('symbolValid');
    const invalid = document.getElementById('symbolInvalid');
    
    if (loading) loading.classList.add('hidden');
    if (valid) valid.classList.add('hidden');
    if (invalid) invalid.classList.remove('hidden');
}

/**
 * Hide symbol status
 */
function hideSymbolStatus() {
    const statusDiv = document.getElementById('symbolStatus');
    if (statusDiv) {
        statusDiv.classList.add('hidden');
    }
}

/**
 * Setup strategy parameter toggles
 */
function setupStrategyToggle() {
    const strategySelect = document.getElementById('strategy_type');
    
    if (strategySelect) {
        strategySelect.addEventListener('change', function() {
            toggleStrategyParameters(this.value);
        });
    }
}

/**
 * Toggle strategy parameters based on selection
 */
function toggleStrategyParameters(strategyType) {
    const strategyParams = document.getElementById('strategyParams');
    const maParams = document.getElementById('maParams');
    const mrParams = document.getElementById('mrParams');
    
    // Hide all parameter sections first
    if (maParams) maParams.classList.add('hidden');
    if (mrParams) mrParams.classList.add('hidden');
    
    if (strategyType && strategyParams) {
        strategyParams.classList.remove('hidden');
        
        // Show appropriate parameter section
        if (strategyType === 'ma_crossover' && maParams) {
            maParams.classList.remove('hidden');
            animateIn(maParams);
        } else if (strategyType === 'mean_reversion' && mrParams) {
            mrParams.classList.remove('hidden');
            animateIn(mrParams);
        }
    } else if (strategyParams) {
        strategyParams.classList.add('hidden');
    }
}

/**
 * Setup loading states for forms
 */
function setupLoadingStates() {
    // This will be called when forms are submitted
}

/**
 * Show form loading state
 */
function showFormLoading() {
    const submitBtn = document.getElementById('runBacktestBtn');
    
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span class="ml-2">Running Backtest...</span>';
        
        // Add loading overlay
        showLoadingOverlay('Running backtest, please wait...');
    }
}

/**
 * Show loading overlay
 */
function showLoadingOverlay(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="bg-white rounded-lg shadow-lg p-8 text-center">
            <div class="loading-spinner mx-auto mb-4"></div>
            <p class="text-gray-700 font-medium">${message}</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

/**
 * Setup tooltips and help text
 */
function setupTooltips() {
    // Add hover effects for info icons
    const infoIcons = document.querySelectorAll('.fa-info-circle');
    infoIcons.forEach(icon => {
        icon.addEventListener('mouseenter', function() {
            this.style.color = '#3b82f6';
        });
        
        icon.addEventListener('mouseleave', function() {
            this.style.color = '';
        });
    });
}

/**
 * Setup chart responsiveness
 */
function setupChartResponsiveness() {
    // Handle window resize for Plotly charts
    window.addEventListener('resize', debounce(function() {
        const charts = document.querySelectorAll('[id$="Chart"]');
        charts.forEach(chart => {
            if (typeof Plotly !== 'undefined' && chart.data) {
                Plotly.Plots.resize(chart);
            }
        });
    }, 250));
}

/**
 * Set symbol value (used by popular symbol buttons)
 */
function setSymbol(symbol) {
    const symbolInput = document.getElementById('symbol');
    if (symbolInput) {
        symbolInput.value = symbol.toUpperCase();
        symbolInput.dispatchEvent(new Event('input'));
        
        // Add visual feedback
        symbolInput.classList.add('form-valid');
        
        // Scroll to symbol input
        symbolInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Utility functions
 */

/**
 * Show error message
 */
function showError(message) {
    // Create alert if it doesn't exist
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container container mx-auto px-4 mt-4';
        
        const nav = document.querySelector('nav');
        if (nav && nav.nextSibling) {
            nav.parentNode.insertBefore(alertContainer, nav.nextSibling);
        }
    }
    
    // Clear existing alerts
    alertContainer.innerHTML = '';
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()" aria-label="Close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Show success message
 */
function showSuccess(message) {
    // Similar to showError but with success styling
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container container mx-auto px-4 mt-4';
        
        const nav = document.querySelector('nav');
        if (nav && nav.nextSibling) {
            nav.parentNode.insertBefore(alertContainer, nav.nextSibling);
        }
    }
    
    alertContainer.innerHTML = '';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()" aria-label="Close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Animate element in
 */
function animateIn(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        element.style.transition = 'all 0.3s ease-out';
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 10);
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format currency values
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

/**
 * Format percentage values
 */
function formatPercentage(value, decimals = 2) {
    return `${value.toFixed(decimals)}%`;
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccess('Copied to clipboard!');
        }).catch(() => {
            showError('Failed to copy to clipboard');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            showSuccess('Copied to clipboard!');
        } catch (err) {
            showError('Failed to copy to clipboard');
        }
        
        document.body.removeChild(textArea);
    }
}

/**
 * Export functionality for results
 */
function exportResults(format = 'csv') {
    const table = document.querySelector('table');
    if (!table) {
        showError('No data to export');
        return;
    }
    
    let content = '';
    const rows = table.querySelectorAll('tr');
    
    if (format === 'csv') {
        rows.forEach((row, index) => {
            const cells = row.querySelectorAll('th, td');
            const rowData = Array.from(cells).map(cell => {
                const text = cell.textContent.trim();
                return text.includes(',') ? `"${text}"` : text;
            }).join(',');
            
            content += rowData + '\n';
        });
        
        downloadFile(content, 'backtest-results.csv', 'text/csv');
    }
}

/**
 * Download file helper
 */
function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
}

// Make functions available globally for onclick handlers
window.setSymbol = setSymbol;
window.showError = showError;
window.showSuccess = showSuccess;
window.copyToClipboard = copyToClipboard;
window.exportResults = exportResults;
