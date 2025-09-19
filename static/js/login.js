// Login page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeLoginForm();
    initializePasswordToggle();
    initializeFormValidation();
});

function initializeLoginForm() {
    const loginForm = document.querySelector('.login-form');
    if (!loginForm) return;
    
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const rememberCheckbox = document.getElementById('remember_me');
    
    // Focus on first empty input
    if (usernameInput && !usernameInput.value) {
        usernameInput.focus();
    } else if (passwordInput && !passwordInput.value) {
        passwordInput.focus();
    }
    
    // Add loading state to submit button
    loginForm.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
            
            // Re-enable after 10 seconds if still on page (in case of error)
            setTimeout(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
                }
            }, 10000);
        }
    });
    
    // Remember last username
    if (usernameInput && localStorage.getItem('lastUsername') && !usernameInput.value) {
        usernameInput.value = localStorage.getItem('lastUsername');
    }
    
    // Save username on form submit
    loginForm.addEventListener('submit', function() {
        if (usernameInput && usernameInput.value.trim()) {
            localStorage.setItem('lastUsername', usernameInput.value.trim());
        }
    });
}

function initializePasswordToggle() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;
    
    // Create toggle button
    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'password-toggle';
    toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    toggleButton.setAttribute('aria-label', 'Toggle password visibility');
    
    // Insert toggle button
    const passwordGroup = passwordInput.closest('.form-group');
    if (passwordGroup) {
        passwordGroup.style.position = 'relative';
        passwordGroup.appendChild(toggleButton);
        
        // Style the toggle button
        toggleButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 5px;
            border-radius: 3px;
            transition: color 0.3s ease;
        `;
        
        // Toggle functionality
        toggleButton.addEventListener('click', function() {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            
            const icon = this.querySelector('i');
            icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
            
            this.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
            
            // Refocus on input
            passwordInput.focus();
            // Move cursor to end
            passwordInput.setSelectionRange(passwordInput.value.length, passwordInput.value.length);
        });
        
        // Hover effect
        toggleButton.addEventListener('mouseenter', function() {
            this.style.color = 'var(--accent-color)';
        });
        
        toggleButton.addEventListener('mouseleave', function() {
            this.style.color = 'var(--text-secondary)';
        });
    }
}

function initializeFormValidation() {
    const form = document.querySelector('.login-form');
    if (!form) return;
    
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    // Real-time validation
    if (usernameInput) {
        usernameInput.addEventListener('blur', function() {
            validateUsername(this);
        });
        
        usernameInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('blur', function() {
            validatePassword(this);
        });
        
        passwordInput.addEventListener('input', function() {
            clearFieldError(this);
        });
    }
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        if (usernameInput && !validateUsername(usernameInput)) {
            isValid = false;
        }
        
        if (passwordInput && !validatePassword(passwordInput)) {
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            
            // Focus on first error field
            const firstError = form.querySelector('.form-error');
            if (firstError) {
                const input = firstError.closest('.form-group').querySelector('input');
                if (input) input.focus();
            }
        }
    });
}

function validateUsername(input) {
    const value = input.value.trim();
    const errors = [];
    
    if (!value) {
        errors.push('Username is required');
    } else if (value.length < 3) {
        errors.push('Username must be at least 3 characters');
    } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
        errors.push('Username can only contain letters, numbers, and underscores');
    }
    
    if (errors.length > 0) {
        showFieldError(input, errors[0]);
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function validatePassword(input) {
    const value = input.value;
    
    if (!value) {
        showFieldError(input, 'Password is required');
        return false;
    }
    
    if (value.length < 6) {
        showFieldError(input, 'Password must be at least 6 characters');
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function showFieldError(input, message) {
    clearFieldError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: var(--danger-color);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    // Add error icon
    const icon = document.createElement('i');
    icon.className = 'fas fa-exclamation-triangle';
    errorDiv.insertBefore(icon, errorDiv.firstChild);
    
    // Add error styling to input
    input.style.borderColor = 'var(--danger-color)';
    input.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.1)';
    
    // Insert error message
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(errorDiv);
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const existingError = formGroup.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    // Reset input styling
    input.style.borderColor = '';
    input.style.boxShadow = '';
}

// Handle caps lock detection
document.addEventListener('keydown', function(e) {
    const passwordInput = document.getElementById('password');
    if (!passwordInput || document.activeElement !== passwordInput) return;
    
    // Simple caps lock detection
    if (e.getModifierState && e.getModifierState('CapsLock')) {
        showCapsLockWarning(passwordInput);
    } else {
        hideCapsLockWarning(passwordInput);
    }
});

function showCapsLockWarning(input) {
    const existingWarning = input.closest('.form-group').querySelector('.caps-warning');
    if (existingWarning) return;
    
    const warning = document.createElement('div');
    warning.className = 'caps-warning';
    warning.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Caps Lock is on';
    warning.style.cssText = `
        color: var(--warning-color);
        font-size: 0.8rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(warning);
    }
}

function hideCapsLockWarning(input) {
    const warning = input.closest('.form-group').querySelector('.caps-warning');
    if (warning) {
        warning.remove();
    }
}