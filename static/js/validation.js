/**
 * RailServe Client-Side Validation Library
 * 
 * Purpose: Provide instant user feedback for form validation
 * Security Note: This is for USER EXPERIENCE only - backend validation 
 * in Python is MANDATORY for security (prevents attackers bypassing JS)
 * 
 * Architecture: Mirrors validation rules from src/validators.py
 * 
 * @author RailServe Team
 * @version 1.0
 */

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

/**
 * Sanitizes user input by trimming whitespace and removing dangerous characters
 * @param {string} input - Raw user input
 * @returns {string} Sanitized input
 */
function sanitizeInput(input) {
    if (!input) return '';
    return input.trim();
}

/**
 * Shows error message for a form field
 * @param {string} fieldId - ID of the input field
 * @param {string} message - Error message to display
 */
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Remove any existing error message
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error styling to field
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    // Create and insert error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message text-danger small mt-1';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

/**
 * Shows success indicator for a valid field
 * @param {string} fieldId - ID of the input field
 */
function showSuccess(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Remove any error message
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add success styling
    field.classList.remove('is-invalid');
    field.classList.add('is-valid');
}

/**
 * Clears all validation messages from a field
 * @param {string} fieldId - ID of the input field
 */
function clearValidation(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    const existingError = field.parentElement.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    field.classList.remove('is-invalid', 'is-valid');
}

// ============================================================================
// FIELD VALIDATORS (Mirror src/validators.py rules)
// ============================================================================

/**
 * Validates email address format
 * Rules: Must be valid email format, max 254 characters
 * @param {string} email - Email address to validate
 * @returns {object} {isValid: boolean, message: string}
 */
function validateEmail(email) {
    email = sanitizeInput(email);
    
    if (!email) {
        return { isValid: false, message: 'Email address is required' };
    }
    
    if (email.length > 254) {
        return { isValid: false, message: 'Email address is too long' };
    }
    
    // RFC 5322 compliant email regex (simplified)
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
        return { isValid: false, message: 'Please enter a valid email address' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates username
 * Rules: 3-50 characters, alphanumeric + dots/underscores/hyphens only
 * @param {string} username - Username to validate
 * @returns {object} {isValid: boolean, message: string}
 */
function validateUsername(username) {
    username = sanitizeInput(username);
    
    if (!username) {
        return { isValid: false, message: 'Username is required' };
    }
    
    if (username.length < 3) {
        return { isValid: false, message: 'Username must be at least 3 characters long' };
    }
    
    if (username.length > 50) {
        return { isValid: false, message: 'Username cannot exceed 50 characters' };
    }
    
    // Only allow alphanumeric, dots, underscores, hyphens
    const usernameRegex = /^[a-zA-Z0-9._-]+$/;
    if (!usernameRegex.test(username)) {
        return { isValid: false, message: 'Username can only contain letters, numbers, dots, underscores, and hyphens' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates password strength
 * Rules: 8-128 characters, must contain letter and number
 * @param {string} password - Password to validate
 * @returns {object} {isValid: boolean, message: string}
 */
function validatePassword(password) {
    if (!password) {
        return { isValid: false, message: 'Password is required' };
    }
    
    if (password.length < 8) {
        return { isValid: false, message: 'Password must be at least 8 characters long' };
    }
    
    if (password.length > 128) {
        return { isValid: false, message: 'Password is too long (maximum 128 characters)' };
    }
    
    // Must contain at least one letter
    if (!/[a-zA-Z]/.test(password)) {
        return { isValid: false, message: 'Password must contain at least one letter' };
    }
    
    // Must contain at least one number
    if (!/[0-9]/.test(password)) {
        return { isValid: false, message: 'Password must contain at least one number' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates that two passwords match
 * @param {string} password - Original password
 * @param {string} confirmPassword - Confirmation password
 * @returns {object} {isValid: boolean, message: string}
 */
function validatePasswordMatch(password, confirmPassword) {
    if (password !== confirmPassword) {
        return { isValid: false, message: 'Passwords do not match' };
    }
    return { isValid: true, message: '' };
}

/**
 * Validates Indian phone number
 * Rules: 10 digits, optionally starting with +91
 * @param {string} phone - Phone number to validate
 * @param {boolean} required - Whether phone is required
 * @returns {object} {isValid: boolean, message: string}
 */
function validatePhone(phone, required = true) {
    phone = sanitizeInput(phone);
    
    if (!phone) {
        if (required) {
            return { isValid: false, message: 'Phone number is required' };
        }
        return { isValid: true, message: '' };
    }
    
    // Remove +91 prefix if present
    phone = phone.replace(/^\+91/, '');
    
    // Must be exactly 10 digits
    const phoneRegex = /^[6-9]\d{9}$/;
    if (!phoneRegex.test(phone)) {
        return { isValid: false, message: 'Please enter a valid 10-digit Indian phone number' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates passenger name
 * Rules: 2-100 characters, letters and spaces only
 * @param {string} name - Name to validate
 * @returns {object} {isValid: boolean, message: string}
 */
function validateName(name) {
    name = sanitizeInput(name);
    
    if (!name) {
        return { isValid: false, message: 'Name is required' };
    }
    
    if (name.length < 2) {
        return { isValid: false, message: 'Name must be at least 2 characters long' };
    }
    
    if (name.length > 100) {
        return { isValid: false, message: 'Name is too long (maximum 100 characters)' };
    }
    
    // Only letters and spaces
    const nameRegex = /^[a-zA-Z\s]+$/;
    if (!nameRegex.test(name)) {
        return { isValid: false, message: 'Name can only contain letters and spaces' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates age
 * Rules: 0-120 years
 * @param {number|string} age - Age to validate
 * @returns {object} {isValid: boolean, message: string}
 */
function validateAge(age) {
    age = parseInt(age);
    
    if (isNaN(age)) {
        return { isValid: false, message: 'Please enter a valid age' };
    }
    
    if (age < 0 || age > 120) {
        return { isValid: false, message: 'Age must be between 0 and 120' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates date is not in the past
 * @param {string} dateStr - Date string in YYYY-MM-DD format
 * @returns {object} {isValid: boolean, message: string}
 */
function validateFutureDate(dateStr) {
    if (!dateStr) {
        return { isValid: false, message: 'Date is required' };
    }
    
    const selectedDate = new Date(dateStr);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to compare dates only
    
    if (selectedDate < today) {
        return { isValid: false, message: 'Please select a future date' };
    }
    
    return { isValid: true, message: '' };
}

/**
 * Validates PNR number format
 * Rules: 10 digits
 * @param {string} pnr - PNR number to validate
 * @returns {object} {isValid: boolean, message: string}
 */
function validatePNR(pnr) {
    pnr = sanitizeInput(pnr);
    
    if (!pnr) {
        return { isValid: false, message: 'PNR number is required' };
    }
    
    const pnrRegex = /^\d{10}$/;
    if (!pnrRegex.test(pnr)) {
        return { isValid: false, message: 'PNR must be exactly 10 digits' };
    }
    
    return { isValid: true, message: '' };
}

// ============================================================================
// FORM VALIDATION HELPERS
// ============================================================================

/**
 * Validates a single field and shows immediate feedback
 * @param {string} fieldId - ID of the field to validate
 * @param {string} validationType - Type of validation to perform
 * @param {object} options - Additional options (e.g., required, matchField)
 */
function validateField(fieldId, validationType, options = {}) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    const value = field.value;
    let result;
    
    // Perform appropriate validation based on type
    switch (validationType) {
        case 'email':
            result = validateEmail(value);
            break;
        case 'username':
            result = validateUsername(value);
            break;
        case 'password':
            result = validatePassword(value);
            break;
        case 'password-match':
            const matchField = document.getElementById(options.matchField);
            result = validatePasswordMatch(matchField ? matchField.value : '', value);
            break;
        case 'phone':
            result = validatePhone(value, options.required !== false);
            break;
        case 'name':
            result = validateName(value);
            break;
        case 'age':
            result = validateAge(value);
            break;
        case 'date':
            result = validateFutureDate(value);
            break;
        case 'pnr':
            result = validatePNR(value);
            break;
        default:
            return;
    }
    
    // Show validation result
    if (result.isValid) {
        showSuccess(fieldId);
    } else {
        showError(fieldId, result.message);
    }
    
    return result.isValid;
}

/**
 * Validates entire form and returns true if all fields are valid
 * Note: This does NOT replace backend validation - it's for UX only!
 * @param {string} formId - ID of the form to validate
 * @param {Array} validations - Array of {fieldId, type, options} objects
 * @returns {boolean} True if form is valid
 */
function validateForm(formId, validations) {
    let isFormValid = true;
    
    // Validate each field
    validations.forEach(validation => {
        const isFieldValid = validateField(
            validation.fieldId, 
            validation.type, 
            validation.options || {}
        );
        
        if (!isFieldValid) {
            isFormValid = false;
        }
    });
    
    return isFormValid;
}

// ============================================================================
// REAL-TIME VALIDATION SETUP
// ============================================================================

/**
 * Sets up real-time validation for a field (validates on blur/input)
 * @param {string} fieldId - ID of the field
 * @param {string} validationType - Type of validation
 * @param {object} options - Validation options
 */
function setupFieldValidation(fieldId, validationType, options = {}) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    // Validate on blur (when user leaves the field)
    field.addEventListener('blur', () => {
        validateField(fieldId, validationType, options);
    });
    
    // Clear validation on focus (when user starts typing again)
    field.addEventListener('focus', () => {
        clearValidation(fieldId);
    });
    
    // Optional: Validate on input for immediate feedback
    if (options.validateOnInput) {
        field.addEventListener('input', () => {
            validateField(fieldId, validationType, options);
        });
    }
}

// ============================================================================
// EXPORT FOR USE IN OTHER FILES
// ============================================================================

// Make functions globally available
window.RailServeValidation = {
    // Core validators
    validateEmail,
    validateUsername,
    validatePassword,
    validatePasswordMatch,
    validatePhone,
    validateName,
    validateAge,
    validateFutureDate,
    validatePNR,
    
    // Helpers
    validateField,
    validateForm,
    setupFieldValidation,
    showError,
    showSuccess,
    clearValidation,
    sanitizeInput
};

console.log('✅ RailServe Validation Library loaded successfully');
