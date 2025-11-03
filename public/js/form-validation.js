// Form Validation for RailServe

(function() {
    'use strict';

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFormValidation);
    } else {
        initFormValidation();
    }

    function initFormValidation() {
        setupDateInputs();
        setupFormSubmitValidation();
        setupRealTimeValidation();
    }

    // Setup date inputs with min/max constraints
    function setupDateInputs() {
        const dateInputs = document.querySelectorAll('input[type="date"]');

        dateInputs.forEach(input => {
            // Set minimum date to today
            const today = new Date().toISOString().split('T')[0];
            if (!input.hasAttribute('min')) {
                input.setAttribute('min', today);
            }

            // Set maximum date to 120 days from today (typical booking window)
            const maxDate = new Date();
            maxDate.setDate(maxDate.getDate() + 120);
            if (!input.hasAttribute('max')) {
                input.setAttribute('max', maxDate.toISOString().split('T')[0]);
            }
        });
    }

    // Setup form submit validation
    function setupFormSubmitValidation() {
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                    return false;
                }
            });
        });
    }

    // Validate form
    function validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                showFieldError(field, 'This field is required');
            } else {
                clearFieldError(field);
            }
        });

        // Additional validation for specific field types
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !isValidEmail(field.value)) {
                isValid = false;
                showFieldError(field, 'Please enter a valid email address');
            }
        });

        const phoneFields = form.querySelectorAll('input[type="tel"]');
        phoneFields.forEach(field => {
            if (field.value && !isValidPhone(field.value)) {
                isValid = false;
                showFieldError(field, 'Please enter a valid phone number');
            }
        });

        return isValid;
    }

    // Real-time validation
    function setupRealTimeValidation() {
        const inputs = document.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            // Validate on blur
            input.addEventListener('blur', function() {
                validateField(this);
            });

            // Clear error on focus
            input.addEventListener('focus', function() {
                clearFieldError(this);
            });
        });
    }

    // Validate individual field
    function validateField(field) {
        // Check required
        if (field.hasAttribute('required') && !field.value.trim()) {
            showFieldError(field, 'This field is required');
            return false;
        }

        // Check email
        if (field.type === 'email' && field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }

        // Check phone
        if (field.type === 'tel' && field.value && !isValidPhone(field.value)) {
            showFieldError(field, 'Please enter a valid phone number');
            return false;
        }

        // Check min/max for numbers
        if (field.type === 'number') {
            const min = field.getAttribute('min');
            const max = field.getAttribute('max');
            const value = parseFloat(field.value);

            if (min && value < parseFloat(min)) {
                showFieldError(field, `Value must be at least ${min}`);
                return false;
            }

            if (max && value > parseFloat(max)) {
                showFieldError(field, `Value must be at most ${max}`);
                return false;
            }
        }

        clearFieldError(field);
        return true;
    }

    // Show field error
    function showFieldError(field, message) {
        clearFieldError(field);

        field.classList.add('is-invalid');
        field.setAttribute('aria-invalid', 'true');

        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.color = '#ef4444';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';

        field.parentNode.insertBefore(errorDiv, field.nextSibling);
    }

    // Clear field error
    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        field.removeAttribute('aria-invalid');

        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Email validation
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Phone validation (Indian phone numbers)
    function isValidPhone(phone) {
        // Remove spaces, dashes, and parentheses
        const cleaned = phone.replace(/[\s\-\(\)]/g, '');
        // Indian phone number: 10 digits, optionally starting with +91 or 91
        const phoneRegex = /^(\+91|91)?[6-9]\d{9}$/;
        return phoneRegex.test(cleaned);
    }
})();
