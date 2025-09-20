// Common authentication validation functions
function showError(element, message) {
    element.textContent = message;
    element.style.display = 'block';
    element.style.color = '#e74c3c';
    element.style.fontSize = '0.875rem';
    element.style.marginTop = '0.25rem';
}

function hideError(element) {
    element.textContent = '';
    element.style.display = 'none';
}

// Login form validation
function initLoginValidation() {
    const form = document.getElementById('loginForm');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    
    if (!form || !username || !password) return;
    
    // Real-time validation
    username.addEventListener('input', function() {
        validateUsername();
    });
    
    password.addEventListener('input', function() {
        validatePassword();
    });
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        }
    });
    
    function validateUsername() {
        const value = username.value.trim();
        const errorElement = document.getElementById('username-error');
        
        if (value.length === 0) {
            showError(errorElement, 'Username is required');
            return false;
        } else if (value.length < 3) {
            showError(errorElement, 'Username must be at least 3 characters');
            return false;
        } else {
            hideError(errorElement);
            return true;
        }
    }
    
    function validatePassword() {
        const value = password.value;
        const errorElement = document.getElementById('password-error');
        
        if (value.length === 0) {
            showError(errorElement, 'Password is required');
            return false;
        } else if (value.length < 3) {
            showError(errorElement, 'Password must be at least 3 characters');
            return false;
        } else {
            hideError(errorElement);
            return true;
        }
    }
    
    function validateForm() {
        const isUsernameValid = validateUsername();
        const isPasswordValid = validatePassword();
        
        return isUsernameValid && isPasswordValid;
    }
}

// Register form validation
function initRegisterValidation() {
    const form = document.getElementById('registerForm');
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    
    if (!form || !username || !email || !password || !confirmPassword) return;
    
    // Real-time validation
    username.addEventListener('input', validateUsername);
    email.addEventListener('input', validateEmail);
    password.addEventListener('input', validatePassword);
    confirmPassword.addEventListener('input', validateConfirmPassword);
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
        }
    });
    
    function validateUsername() {
        const value = username.value.trim();
        const errorElement = document.getElementById('username-error');
        const usernamePattern = /^[a-zA-Z0-9_]+$/;
        
        if (value.length === 0) {
            showError(errorElement, 'Username is required');
            return false;
        } else if (value.length < 3) {
            showError(errorElement, 'Username must be at least 3 characters');
            return false;
        } else if (!usernamePattern.test(value)) {
            showError(errorElement, 'Username can only contain letters, numbers, and underscores');
            return false;
        } else {
            hideError(errorElement);
            return true;
        }
    }
    
    function validateEmail() {
        const value = email.value.trim();
        const errorElement = document.getElementById('email-error');
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (value.length === 0) {
            showError(errorElement, 'Email is required');
            return false;
        } else if (!emailPattern.test(value)) {
            showError(errorElement, 'Please enter a valid email address');
            return false;
        } else {
            hideError(errorElement);
            return true;
        }
    }
    
    function validatePassword() {
        const value = password.value;
        const errorElement = document.getElementById('password-error');
        const hasLetter = /[a-zA-Z]/.test(value);
        const hasNumber = /[0-9]/.test(value);
        
        if (value.length === 0) {
            showError(errorElement, 'Password is required');
            return false;
        } else if (value.length < 6) {
            showError(errorElement, 'Password must be at least 6 characters');
            return false;
        } else if (!hasLetter || !hasNumber) {
            showError(errorElement, 'Password must contain both letters and numbers');
            return false;
        } else {
            hideError(errorElement);
            // Re-validate confirm password when password changes
            if (confirmPassword.value) {
                validateConfirmPassword();
            }
            return true;
        }
    }
    
    function validateConfirmPassword() {
        const passwordValue = password.value;
        const confirmValue = confirmPassword.value;
        const errorElement = document.getElementById('confirm-password-error');
        
        if (confirmValue.length === 0) {
            showError(errorElement, 'Please confirm your password');
            return false;
        } else if (passwordValue !== confirmValue) {
            showError(errorElement, 'Passwords do not match');
            return false;
        } else {
            hideError(errorElement);
            return true;
        }
    }
    
    function validateForm() {
        const isUsernameValid = validateUsername();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        const isConfirmPasswordValid = validateConfirmPassword();
        
        return isUsernameValid && isEmailValid && isPasswordValid && isConfirmPasswordValid;
    }
}

// Initialize the appropriate validation based on the page
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('loginForm')) {
        initLoginValidation();
    }
    if (document.getElementById('registerForm')) {
        initRegisterValidation();
    }
});