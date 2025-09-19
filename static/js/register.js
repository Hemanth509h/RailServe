// Registration page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeRegistrationForm();
    initializePasswordValidation();
    initializeUsernameValidation();
    initializeEmailValidation();
});

function initializeRegistrationForm() {
    const form = document.querySelector('.register-form');
    if (!form) return;
    
    // Focus on first input
    const firstInput = form.querySelector('input[type="text"], input[type="email"]');
    if (firstInput) firstInput.focus();
    
    // Add loading state to submit button
    form.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
            
            // Re-enable after 10 seconds if still on page (in case of error)
            setTimeout(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
                }
            }, 10000);
        }
    });
    
    // Real-time form validation
    const inputs = form.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
            updateSubmitButton();
        });
    });
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
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

function initializePasswordValidation() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (!passwordInput) return;
    
    // Create password strength indicator
    createPasswordStrengthIndicator(passwordInput);
    
    // Password input validation
    passwordInput.addEventListener('input', function() {
        updatePasswordStrength(this);
        
        // Validate confirm password if it has value
        if (confirmPasswordInput && confirmPasswordInput.value) {
            validatePasswordConfirmation();
        }
    });
    
    // Confirm password validation
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordConfirmation);
        confirmPasswordInput.addEventListener('blur', validatePasswordConfirmation);
    }
    
    // Add password toggle for both fields
    addPasswordToggle(passwordInput);
    if (confirmPasswordInput) {
        addPasswordToggle(confirmPasswordInput);
    }
}

function createPasswordStrengthIndicator(passwordInput) {
    const formGroup = passwordInput.closest('.form-group');
    if (!formGroup) return;
    
    const strengthContainer = document.createElement('div');
    strengthContainer.className = 'password-strength';
    strengthContainer.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill"></div>
        </div>
        <div class="strength-text">Password strength: <span class="strength-level">Weak</span></div>
        <div class="strength-requirements">
            <div class="requirement" data-requirement="length">
                <i class="fas fa-circle"></i> At least 8 characters
            </div>
            <div class="requirement" data-requirement="uppercase">
                <i class="fas fa-circle"></i> One uppercase letter
            </div>
            <div class="requirement" data-requirement="lowercase">
                <i class="fas fa-circle"></i> One lowercase letter
            </div>
            <div class="requirement" data-requirement="number">
                <i class="fas fa-circle"></i> One number
            </div>
            <div class="requirement" data-requirement="special">
                <i class="fas fa-circle"></i> One special character
            </div>
        </div>
    `;
    
    // Add CSS styles
    const style = document.createElement('style');
    style.textContent = `
        .password-strength {
            margin-top: 0.5rem;
            font-size: 0.85rem;
        }
        
        .strength-bar {
            height: 4px;
            background: var(--border-color);
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }
        
        .strength-fill {
            height: 100%;
            width: 0%;
            transition: all 0.3s ease;
            border-radius: 2px;
        }
        
        .strength-text {
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }
        
        .strength-level {
            font-weight: 600;
        }
        
        .strength-requirements {
            display: none;
        }
        
        .strength-requirements.show {
            display: block;
        }
        
        .requirement {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 0.25rem 0;
            color: var(--text-secondary);
        }
        
        .requirement.met {
            color: var(--success-color);
        }
        
        .requirement.met i {
            color: var(--success-color);
        }
        
        .requirement i {
            font-size: 0.6rem;
        }
    `;
    
    if (!document.querySelector('#password-strength-styles')) {
        style.id = 'password-strength-styles';
        document.head.appendChild(style);
    }
    
    formGroup.appendChild(strengthContainer);
}

function updatePasswordStrength(passwordInput) {
    const password = passwordInput.value;
    const strengthContainer = passwordInput.closest('.form-group').querySelector('.password-strength');
    if (!strengthContainer) return;
    
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
    
    // Update requirement indicators
    Object.keys(requirements).forEach(req => {
        const element = strengthContainer.querySelector(`[data-requirement="${req}"]`);
        if (element) {
            element.classList.toggle('met', requirements[req]);
        }
    });
    
    // Calculate strength
    const metRequirements = Object.values(requirements).filter(Boolean).length;
    const strengthPercentage = (metRequirements / 5) * 100;
    
    const strengthFill = strengthContainer.querySelector('.strength-fill');
    const strengthLevel = strengthContainer.querySelector('.strength-level');
    const requirementsDiv = strengthContainer.querySelector('.strength-requirements');
    
    // Update strength bar
    strengthFill.style.width = `${strengthPercentage}%`;
    
    // Update strength level and color
    let level, color;
    if (metRequirements <= 2) {
        level = 'Weak';
        color = 'var(--danger-color)';
    } else if (metRequirements <= 3) {
        level = 'Fair';
        color = 'var(--warning-color)';
    } else if (metRequirements <= 4) {
        level = 'Good';
        color = 'var(--info-color)';
    } else {
        level = 'Strong';
        color = 'var(--success-color)';
    }
    
    strengthLevel.textContent = level;
    strengthLevel.style.color = color;
    strengthFill.style.backgroundColor = color;
    
    // Show/hide requirements
    if (password.length > 0 && metRequirements < 5) {
        requirementsDiv.classList.add('show');
    } else {
        requirementsDiv.classList.remove('show');
    }
}

function validatePasswordConfirmation() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    
    if (!passwordInput || !confirmPasswordInput) return true;
    
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    if (!confirmPassword) {
        showFieldError(confirmPasswordInput, 'Please confirm your password');
        return false;
    }
    
    if (password !== confirmPassword) {
        showFieldError(confirmPasswordInput, 'Passwords do not match');
        return false;
    }
    
    clearFieldError(confirmPasswordInput);
    return true;
}

function initializeUsernameValidation() {
    const usernameInput = document.getElementById('username');
    if (!usernameInput) return;
    
    let checkTimeout;
    
    usernameInput.addEventListener('input', function() {
        clearTimeout(checkTimeout);
        clearFieldError(this);
        
        const username = this.value.trim();
        if (username.length >= 3) {
            // Debounce username availability check
            checkTimeout = setTimeout(() => {
                checkUsernameAvailability(username);
            }, 500);
        }
    });
}

function checkUsernameAvailability(username) {
    // This would typically make an AJAX call to check username availability
    // For now, we'll just validate format
    const usernameInput = document.getElementById('username');
    if (!usernameInput) return;
    
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        showFieldError(usernameInput, 'Username can only contain letters, numbers, and underscores');
        return;
    }
    
    if (username.length < 3 || username.length > 20) {
        showFieldError(usernameInput, 'Username must be 3-20 characters long');
        return;
    }
    
    // Show success indicator
    showFieldSuccess(usernameInput, 'Username is available');
}

function initializeEmailValidation() {
    const emailInput = document.getElementById('email');
    if (!emailInput) return;
    
    emailInput.addEventListener('blur', function() {
        validateEmail(this);
    });
}

function validateEmail(emailInput) {
    const email = emailInput.value.trim();
    
    if (!email) {
        showFieldError(emailInput, 'Email is required');
        return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showFieldError(emailInput, 'Please enter a valid email address');
        return false;
    }
    
    clearFieldError(emailInput);
    showFieldSuccess(emailInput, 'Valid email address');
    return true;
}

function addPasswordToggle(input) {
    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'password-toggle';
    toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    toggleButton.setAttribute('aria-label', 'Toggle password visibility');
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.style.position = 'relative';
        formGroup.appendChild(toggleButton);
        
        toggleButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 38px;
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 5px;
            border-radius: 3px;
            transition: color 0.3s ease;
        `;
        
        toggleButton.addEventListener('click', function() {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            
            const icon = this.querySelector('i');
            icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
            
            input.focus();
        });
    }
}

function validateField(input) {
    const fieldType = input.type;
    const fieldName = input.name || input.id;
    
    switch (fieldName) {
        case 'username':
            return validateUsername(input);
        case 'email':
            return validateEmail(input);
        case 'password':
            return validatePassword(input);
        case 'confirm_password':
            return validatePasswordConfirmation();
        default:
            return validateRequired(input);
    }
}

function validateUsername(input) {
    const value = input.value.trim();
    
    if (!value) {
        showFieldError(input, 'Username is required');
        return false;
    }
    
    if (value.length < 3) {
        showFieldError(input, 'Username must be at least 3 characters');
        return false;
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(value)) {
        showFieldError(input, 'Username can only contain letters, numbers, and underscores');
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
    
    if (value.length < 8) {
        showFieldError(input, 'Password must be at least 8 characters');
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function validateRequired(input) {
    if (!input.value.trim()) {
        showFieldError(input, `${getFieldLabel(input)} is required`);
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function getFieldLabel(input) {
    const label = input.closest('.form-group').querySelector('label');
    return label ? label.textContent.replace('*', '').trim() : 'This field';
}

function showFieldError(input, message) {
    clearFieldError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    errorDiv.style.cssText = `
        color: var(--danger-color);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    input.style.borderColor = 'var(--danger-color)';
    input.style.boxShadow = '0 0 0 2px rgba(239, 68, 68, 0.1)';
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(errorDiv);
    }
}

function showFieldSuccess(input, message) {
    clearFieldError(input);
    
    const successDiv = document.createElement('div');
    successDiv.className = 'form-success';
    successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
    successDiv.style.cssText = `
        color: var(--success-color);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    input.style.borderColor = 'var(--success-color)';
    input.style.boxShadow = '0 0 0 2px rgba(34, 197, 94, 0.1)';
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(successDiv);
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const existingError = formGroup.querySelector('.form-error');
        const existingSuccess = formGroup.querySelector('.form-success');
        
        if (existingError) existingError.remove();
        if (existingSuccess) existingSuccess.remove();
    }
    
    input.style.borderColor = '';
    input.style.boxShadow = '';
}

function updateSubmitButton() {
    const form = document.querySelector('.register-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!submitBtn) return;
    
    const requiredInputs = form.querySelectorAll('input[required]');
    const allValid = Array.from(requiredInputs).every(input => {
        return input.value.trim() && !input.closest('.form-group').querySelector('.form-error');
    });
    
    submitBtn.disabled = !allValid;
}