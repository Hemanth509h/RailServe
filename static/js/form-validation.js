// RailServe Form Validation Utility
// Comprehensive client-side validation for all forms

class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        if (!this.form) {
            console.error(`Form with id '${formId}' not found`);
            return;
        }
        this.errors = {};
        this.init();
    }

    init() {
        // Prevent form submission if validation fails
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                this.showErrors();
            }
        });

        // Real-time validation for inputs
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
            input.addEventListener('input', () => {
                this.clearFieldError(input);
            });
        });
    }

    validateForm() {
        this.errors = {};
        const inputs = this.form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            this.validateField(input);
        });

        return Object.keys(this.errors).length === 0;
    }

    validateField(field) {
        const name = field.name || field.id;
        const value = field.value.trim();
        const type = field.type;

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            this.addError(name, `${this.getFieldLabel(field)} is required`);
            this.markFieldInvalid(field);
            return false;
        }

        // Skip further validation if field is empty and not required
        if (!value && !field.hasAttribute('required')) {
            this.markFieldValid(field);
            return true;
        }

        // Email validation
        if (type === 'email' || field.name === 'email') {
            if (!this.isValidEmail(value)) {
                this.addError(name, 'Please enter a valid email address');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Phone validation (Indian format)
        if (field.name === 'phone' || field.name === 'mobile') {
            if (!this.isValidPhone(value)) {
                this.addError(name, 'Please enter a valid 10-digit phone number');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Password validation
        if (type === 'password' && field.name === 'password') {
            if (value.length < 6) {
                this.addError(name, 'Password must be at least 6 characters long');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Confirm password validation
        if (field.name === 'confirm_password') {
            const passwordField = this.form.querySelector('[name="password"]');
            if (passwordField && value !== passwordField.value) {
                this.addError(name, 'Passwords do not match');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Username validation
        if (field.name === 'username') {
            if (value.length < 3) {
                this.addError(name, 'Username must be at least 3 characters long');
                this.markFieldInvalid(field);
                return false;
            }
            if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                this.addError(name, 'Username can only contain letters, numbers, and underscores');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Name validation (letters and spaces only)
        if (field.name === 'name' || field.name.includes('_name')) {
            if (!/^[a-zA-Z\s]+$/.test(value)) {
                this.addError(name, 'Name can only contain letters and spaces');
                this.markFieldInvalid(field);
                return false;
            }
            if (value.length < 2) {
                this.addError(name, 'Name must be at least 2 characters long');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Age validation
        if (field.name === 'age' || field.name.includes('_age')) {
            const age = parseInt(value);
            if (isNaN(age) || age < 1 || age > 120) {
                this.addError(name, 'Please enter a valid age (1-120)');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // PNR validation (10 digits)
        if (field.name === 'pnr') {
            if (!/^\d{10}$/.test(value)) {
                this.addError(name, 'PNR must be exactly 10 digits');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Date validation (no past dates for journey)
        if (type === 'date' && (field.name === 'journey_date' || field.name === 'date')) {
            const selectedDate = new Date(value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                this.addError(name, 'Journey date cannot be in the past');
                this.markFieldInvalid(field);
                return false;
            }

            // Max 120 days in advance
            const maxDate = new Date();
            maxDate.setDate(maxDate.getDate() + 120);
            if (selectedDate > maxDate) {
                this.addError(name, 'Bookings can only be made up to 120 days in advance');
                this.markFieldInvalid(field);
                return false;
            }
        }

        // Number validation
        if (type === 'number') {
            const num = parseFloat(value);
            if (isNaN(num)) {
                this.addError(name, 'Please enter a valid number');
                this.markFieldInvalid(field);
                return false;
            }
            if (field.hasAttribute('min') && num < parseFloat(field.getAttribute('min'))) {
                this.addError(name, `Minimum value is ${field.getAttribute('min')}`);
                this.markFieldInvalid(field);
                return false;
            }
            if (field.hasAttribute('max') && num > parseFloat(field.getAttribute('max'))) {
                this.addError(name, `Maximum value is ${field.getAttribute('max')}`);
                this.markFieldInvalid(field);
                return false;
            }
        }

        this.markFieldValid(field);
        return true;
    }

    isValidEmail(email) {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(email);
    }

    isValidPhone(phone) {
        // Indian phone number: 10 digits
        const re = /^[6-9]\d{9}$/;
        return re.test(phone.replace(/[\s-]/g, ''));
    }

    addError(fieldName, message) {
        this.errors[fieldName] = message;
    }

    clearFieldError(field) {
        const name = field.name || field.id;
        delete this.errors[name];
        this.markFieldValid(field);
    }

    markFieldInvalid(field) {
        field.style.borderColor = '#e74c3c';
        field.style.backgroundColor = '#fee';
        
        // Show error message if error container exists
        const errorContainer = field.parentElement.querySelector('.error-message');
        if (errorContainer) {
            const name = field.name || field.id;
            errorContainer.textContent = this.errors[name] || '';
            errorContainer.style.display = 'block';
            errorContainer.style.color = '#e74c3c';
        }
    }

    markFieldValid(field) {
        field.style.borderColor = '';
        field.style.backgroundColor = '';
        
        // Hide error message
        const errorContainer = field.parentElement.querySelector('.error-message');
        if (errorContainer) {
            errorContainer.textContent = '';
            errorContainer.style.display = 'none';
        }
    }

    showErrors() {
        // Scroll to first error
        const firstErrorField = this.form.querySelector('[style*="border-color: rgb(231, 76, 60)"]');
        if (firstErrorField) {
            firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstErrorField.focus();
        }

        // Show general error message if exists
        const generalError = this.form.querySelector('.general-error');
        if (generalError) {
            generalError.textContent = 'Please correct the errors in the form';
            generalError.style.display = 'block';
        }
    }

    getFieldLabel(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`);
        if (label) {
            return label.textContent.trim().replace(/\*/g, '');
        }
        return field.name || field.id || 'This field';
    }
}

// Station selection validation
function validateStationSelection(fromStationId, toStationId, fromStationName, toStationName) {
    if (fromStationId === toStationId) {
        alert('From and To stations cannot be the same');
        return false;
    }
    return true;
}

// Passenger count validation
function validatePassengerCount(count) {
    const maxPassengers = 6;
    if (count < 1) {
        alert('Please select at least 1 passenger');
        return false;
    }
    if (count > maxPassengers) {
        alert(`Maximum ${maxPassengers} passengers allowed per booking`);
        return false;
    }
    return true;
}

console.log('RailServe Form Validation utility loaded');
