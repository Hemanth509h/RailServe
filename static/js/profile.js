// Profile page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeProfileForm();
    initializePasswordChangeForm();
    initializeProfileImageUpload();
    initializeAccountSettings();
});

function initializeProfileForm() {
    const profileForm = document.querySelector('.profile-form');
    if (!profileForm) return;
    
    const editButton = document.querySelector('.edit-profile');
    const saveButton = document.querySelector('.save-profile');
    const cancelButton = document.querySelector('.cancel-edit');
    const inputs = profileForm.querySelectorAll('input, select, textarea');
    
    // Edit profile functionality
    if (editButton) {
        editButton.addEventListener('click', function(e) {
            e.preventDefault();
            enableFormEditing(true);
        });
    }
    
    // Cancel edit functionality
    if (cancelButton) {
        cancelButton.addEventListener('click', function(e) {
            e.preventDefault();
            enableFormEditing(false);
            resetFormValues();
        });
    }
    
    // Form submission
    profileForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveProfileChanges();
    });
    
    // Real-time validation
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateProfileField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
    
    function enableFormEditing(enable) {
        inputs.forEach(input => {
            if (input.name !== 'username') { // Username usually can't be changed
                input.disabled = !enable;
            }
        });
        
        if (editButton) editButton.style.display = enable ? 'none' : 'inline-flex';
        if (saveButton) saveButton.style.display = enable ? 'inline-flex' : 'none';
        if (cancelButton) cancelButton.style.display = enable ? 'inline-flex' : 'none';
        
        // Focus on first editable field
        if (enable) {
            const firstInput = profileForm.querySelector('input:not([disabled])');
            if (firstInput) firstInput.focus();
        }
    }
    
    function resetFormValues() {
        // Reset to original values (stored in data attributes)
        inputs.forEach(input => {
            const originalValue = input.dataset.originalValue;
            if (originalValue !== undefined) {
                input.value = originalValue;
            }
        });
        clearAllFieldErrors();
    }
    
    // Store original values
    inputs.forEach(input => {
        input.dataset.originalValue = input.value;
    });
}

function initializePasswordChangeForm() {
    const passwordForm = document.querySelector('.password-change-form');
    if (!passwordForm) return;
    
    const currentPasswordInput = document.getElementById('current_password');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_new_password');
    
    // Add password toggles
    if (currentPasswordInput) addPasswordToggle(currentPasswordInput);
    if (newPasswordInput) addPasswordToggle(newPasswordInput);
    if (confirmPasswordInput) addPasswordToggle(confirmPasswordInput);
    
    // Password strength indicator for new password
    if (newPasswordInput) {
        createPasswordStrengthIndicator(newPasswordInput);
    }
    
    // Form validation
    passwordForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validatePasswordForm()) {
            changePassword();
        }
    });
    
    // Real-time validation
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            updatePasswordStrength(this);
            if (confirmPasswordInput.value) {
                validatePasswordConfirmation();
            }
        });
    }
    
    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordConfirmation);
    }
}

function initializeProfileImageUpload() {
    const imageUpload = document.getElementById('profile_image');
    const imagePreview = document.querySelector('.profile-image-preview');
    const uploadButton = document.querySelector('.upload-image-btn');
    const removeButton = document.querySelector('.remove-image-btn');
    
    if (imageUpload && uploadButton) {
        uploadButton.addEventListener('click', function() {
            imageUpload.click();
        });
        
        imageUpload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                if (validateImageFile(file)) {
                    previewImage(file);
                } else {
                    this.value = ''; // Clear invalid file
                }
            }
        });
    }
    
    if (removeButton && imagePreview) {
        removeButton.addEventListener('click', function() {
            removeProfileImage();
        });
    }
    
    function validateImageFile(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        
        if (!allowedTypes.includes(file.type)) {
            showErrorMessage('Please select a valid image file (JPEG, PNG, or GIF)');
            return false;
        }
        
        if (file.size > maxSize) {
            showErrorMessage('Image file must be less than 5MB');
            return false;
        }
        
        return true;
    }
    
    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            if (imagePreview) {
                const img = imagePreview.querySelector('img') || document.createElement('img');
                img.src = e.target.result;
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
                img.style.borderRadius = '50%';
                
                if (!imagePreview.querySelector('img')) {
                    imagePreview.appendChild(img);
                }
                
                // Show remove button
                if (removeButton) {
                    removeButton.style.display = 'block';
                }
            }
        };
        reader.readAsDataURL(file);
    }
}

function initializeAccountSettings() {
    // Email notification preferences
    const notificationCheckboxes = document.querySelectorAll('.notification-setting');
    notificationCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateNotificationSetting(this.name, this.checked);
        });
    });
    
    // Privacy settings
    const privacySettings = document.querySelectorAll('.privacy-setting');
    privacySettings.forEach(setting => {
        setting.addEventListener('change', function() {
            updatePrivacySetting(this.name, this.value);
        });
    });
    
    // Account deactivation
    const deactivateButton = document.querySelector('.deactivate-account');
    if (deactivateButton) {
        deactivateButton.addEventListener('click', function(e) {
            e.preventDefault();
            confirmAccountDeactivation();
        });
    }
    
    // Export data
    const exportButton = document.querySelector('.export-data');
    if (exportButton) {
        exportButton.addEventListener('click', function(e) {
            e.preventDefault();
            exportUserData();
        });
    }
}

function saveProfileChanges() {
    const form = document.querySelector('.profile-form');
    const formData = new FormData(form);
    
    // Show loading state
    const saveButton = document.querySelector('.save-profile');
    if (saveButton) {
        saveButton.disabled = true;
        saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    }
    
    fetch('/update_profile', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Profile updated successfully');
            enableFormEditing(false);
            
            // Update stored original values
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.dataset.originalValue = input.value;
            });
        } else {
            showErrorMessage(data.error || 'Failed to update profile');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred. Please try again.');
    })
    .finally(() => {
        if (saveButton) {
            saveButton.disabled = false;
            saveButton.innerHTML = '<i class="fas fa-save"></i> Save Changes';
        }
    });
}

function changePassword() {
    const form = document.querySelector('.password-change-form');
    const formData = new FormData(form);
    
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Changing...';
    }
    
    fetch('/change_password', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Password changed successfully');
            form.reset();
            clearAllFieldErrors();
        } else {
            showErrorMessage(data.error || 'Failed to change password');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred. Please try again.');
    })
    .finally(() => {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-key"></i> Change Password';
        }
    });
}

function validatePasswordForm() {
    const currentPassword = document.getElementById('current_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_new_password').value;
    
    let isValid = true;
    
    if (!currentPassword) {
        showFieldError(document.getElementById('current_password'), 'Current password is required');
        isValid = false;
    }
    
    if (!newPassword) {
        showFieldError(document.getElementById('new_password'), 'New password is required');
        isValid = false;
    } else if (newPassword.length < 8) {
        showFieldError(document.getElementById('new_password'), 'New password must be at least 8 characters');
        isValid = false;
    }
    
    if (newPassword !== confirmPassword) {
        showFieldError(document.getElementById('confirm_new_password'), 'Passwords do not match');
        isValid = false;
    }
    
    if (currentPassword === newPassword) {
        showFieldError(document.getElementById('new_password'), 'New password must be different from current password');
        isValid = false;
    }
    
    return isValid;
}

function validatePasswordConfirmation() {
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_new_password').value;
    
    if (confirmPassword && newPassword !== confirmPassword) {
        showFieldError(document.getElementById('confirm_new_password'), 'Passwords do not match');
        return false;
    }
    
    clearFieldError(document.getElementById('confirm_new_password'));
    return true;
}

function validateProfileField(input) {
    const value = input.value.trim();
    const fieldName = input.name;
    
    if (input.hasAttribute('required') && !value) {
        showFieldError(input, 'This field is required');
        return false;
    }
    
    if (fieldName === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailRegex.test(value)) {
            showFieldError(input, 'Please enter a valid email address');
            return false;
        }
    }
    
    if (fieldName === 'phone') {
        const phoneRegex = /^[\d\s\-\+\(\)]+$/;
        if (value && !phoneRegex.test(value)) {
            showFieldError(input, 'Please enter a valid phone number');
            return false;
        }
    }
    
    clearFieldError(input);
    return true;
}

function updateNotificationSetting(settingName, value) {
    fetch('/update_notification_setting', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            setting: settingName,
            value: value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Notification setting updated');
        } else {
            showErrorMessage('Failed to update setting');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

function updatePrivacySetting(settingName, value) {
    fetch('/update_privacy_setting', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            setting: settingName,
            value: value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Privacy setting updated');
        } else {
            showErrorMessage('Failed to update setting');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

function confirmAccountDeactivation() {
    const confirmed = confirm(
        'Are you sure you want to deactivate your account? This action cannot be undone. ' +
        'All your bookings and data will be permanently deleted.'
    );
    
    if (confirmed) {
        const secondConfirm = prompt(
            'Type "DEACTIVATE" to confirm account deactivation:'
        );
        
        if (secondConfirm === 'DEACTIVATE') {
            deactivateAccount();
        }
    }
}

function deactivateAccount() {
    fetch('/deactivate_account', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Account deactivated successfully. You will be redirected to the homepage.');
            window.location.href = '/';
        } else {
            showErrorMessage('Failed to deactivate account');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

function exportUserData() {
    const button = document.querySelector('.export-data');
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
    }
    
    // Create download link
    const link = document.createElement('a');
    link.href = '/export_user_data';
    link.download = 'my_railserve_data.json';
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    if (button) {
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-download"></i> Export My Data';
        }, 2000);
    }
    
    showSuccessMessage('Data export started');
}

// Utility functions
function addPasswordToggle(input) {
    const toggleButton = document.createElement('button');
    toggleButton.type = 'button';
    toggleButton.className = 'password-toggle';
    toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.style.position = 'relative';
        formGroup.appendChild(toggleButton);
        
        toggleButton.style.cssText = `
            position: absolute;
            right: 10px;
            top: 70%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 5px;
        `;
        
        toggleButton.addEventListener('click', function() {
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            
            const icon = this.querySelector('i');
            icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
        });
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
    `;
    
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
    
    const metRequirements = Object.values(requirements).filter(Boolean).length;
    const strengthPercentage = (metRequirements / 5) * 100;
    
    const strengthFill = strengthContainer.querySelector('.strength-fill');
    const strengthLevel = strengthContainer.querySelector('.strength-level');
    
    strengthFill.style.width = `${strengthPercentage}%`;
    
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
    
    input.style.borderColor = '';
}

function clearAllFieldErrors() {
    const errors = document.querySelectorAll('.form-error');
    errors.forEach(error => error.remove());
    
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.style.borderColor = '';
    });
}

function enableFormEditing(enable) {
    const inputs = document.querySelectorAll('.profile-form input, .profile-form select, .profile-form textarea');
    inputs.forEach(input => {
        if (input.name !== 'username') {
            input.disabled = !enable;
        }
    });
    
    const editButton = document.querySelector('.edit-profile');
    const saveButton = document.querySelector('.save-profile');
    const cancelButton = document.querySelector('.cancel-edit');
    
    if (editButton) editButton.style.display = enable ? 'none' : 'inline-flex';
    if (saveButton) saveButton.style.display = enable ? 'inline-flex' : 'none';
    if (cancelButton) cancelButton.style.display = enable ? 'inline-flex' : 'none';
}

function removeProfileImage() {
    if (confirm('Are you sure you want to remove your profile image?')) {
        fetch('/remove_profile_image', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const imagePreview = document.querySelector('.profile-image-preview');
                if (imagePreview) {
                    imagePreview.innerHTML = '<i class="fas fa-user"></i>';
                }
                
                const removeButton = document.querySelector('.remove-image-btn');
                if (removeButton) {
                    removeButton.style.display = 'none';
                }
                
                showSuccessMessage('Profile image removed successfully');
            } else {
                showErrorMessage('Failed to remove profile image');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Network error occurred');
        });
    }
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    const existingMessages = document.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `temp-message alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
    `;
    
    const container = document.querySelector('.profile-container');
    if (container) {
        container.insertBefore(messageDiv, container.firstChild);
    }
    
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}

// Add CSS for password strength and other elements
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
    }
    
    .strength-level {
        font-weight: 600;
    }
    
    .temp-message {
        position: sticky;
        top: 0;
        z-index: 100;
        animation: slideDown 0.3s ease-out;
        margin-bottom: 1rem;
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;

if (!document.querySelector('#profile-styles')) {
    style.id = 'profile-styles';
    document.head.appendChild(style);
}