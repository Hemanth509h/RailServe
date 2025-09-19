// Payment page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializePaymentForm();
    initializePaymentMethods();
    initializeCardValidation();
    initializeUPIValidation();
    initializeNetBankingForm();
});

function initializePaymentForm() {
    const paymentForm = document.querySelector('.payment-form');
    if (!paymentForm) return;
    
    // Add loading state to submit button
    paymentForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validatePaymentForm()) {
            processPayment();
        }
    });
    
    // Auto-save form data to localStorage
    const inputs = paymentForm.querySelectorAll('input, select');
    inputs.forEach(input => {
        // Load saved data
        const savedValue = localStorage.getItem(`payment_${input.name}`);
        if (savedValue && input.type !== 'password') {
            input.value = savedValue;
        }
        
        // Save on change
        input.addEventListener('change', function() {
            if (this.type !== 'password') {
                localStorage.setItem(`payment_${this.name}`, this.value);
            }
        });
    });
}

function initializePaymentMethods() {
    const paymentMethodButtons = document.querySelectorAll('.payment-method-btn');
    const paymentForms = document.querySelectorAll('.payment-method-form');
    
    paymentMethodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const method = this.dataset.method;
            
            // Update active button
            paymentMethodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding form
            paymentForms.forEach(form => {
                if (form.dataset.method === method) {
                    form.style.display = 'block';
                    form.classList.add('active');
                    
                    // Focus on first input
                    const firstInput = form.querySelector('input');
                    if (firstInput) firstInput.focus();
                } else {
                    form.style.display = 'none';
                    form.classList.remove('active');
                }
            });
            
            // Update hidden payment method input
            const methodInput = document.getElementById('payment_method');
            if (methodInput) {
                methodInput.value = method;
            }
            
            // Update payment summary
            updatePaymentSummary(method);
        });
    });
    
    // Initialize with first method selected
    if (paymentMethodButtons.length > 0) {
        paymentMethodButtons[0].click();
    }
}

function initializeCardValidation() {
    const cardNumberInput = document.getElementById('card_number');
    const expiryInput = document.getElementById('card_expiry');
    const cvvInput = document.getElementById('card_cvv');
    const cardHolderInput = document.getElementById('card_holder_name');
    
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function() {
            formatCardNumber(this);
            detectCardType(this.value);
            validateCardNumber(this);
        });
        
        cardNumberInput.addEventListener('blur', function() {
            validateCardNumber(this);
        });
    }
    
    if (expiryInput) {
        expiryInput.addEventListener('input', function() {
            formatExpiryDate(this);
        });
        
        expiryInput.addEventListener('blur', function() {
            validateExpiryDate(this);
        });
    }
    
    if (cvvInput) {
        cvvInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').substring(0, 4);
        });
        
        cvvInput.addEventListener('blur', function() {
            validateCVV(this);
        });
    }
    
    if (cardHolderInput) {
        cardHolderInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^a-zA-Z\s]/g, '').toUpperCase();
        });
        
        cardHolderInput.addEventListener('blur', function() {
            validateCardHolderName(this);
        });
    }
}

function initializeUPIValidation() {
    const upiIdInput = document.getElementById('upi_id');
    
    if (upiIdInput) {
        upiIdInput.addEventListener('input', function() {
            this.value = this.value.toLowerCase();
            clearFieldError(this);
        });
        
        upiIdInput.addEventListener('blur', function() {
            validateUPIId(this);
        });
    }
}

function initializeNetBankingForm() {
    const bankSelect = document.getElementById('bank_name');
    const customerIdInput = document.getElementById('customer_id');
    
    if (bankSelect) {
        bankSelect.addEventListener('change', function() {
            updateBankingInfo(this.value);
        });
    }
    
    if (customerIdInput) {
        customerIdInput.addEventListener('blur', function() {
            validateCustomerId(this);
        });
    }
}

function formatCardNumber(input) {
    let value = input.value.replace(/\D/g, '');
    let formattedValue = value.replace(/(\d{4})(?=\d)/g, '$1 ');
    
    // Limit to 19 characters (16 digits + 3 spaces)
    if (formattedValue.length > 19) {
        formattedValue = formattedValue.substring(0, 19);
    }
    
    input.value = formattedValue;
}

function formatExpiryDate(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length >= 2) {
        value = value.substring(0, 2) + '/' + value.substring(2, 4);
    }
    
    input.value = value;
}

function detectCardType(cardNumber) {
    const cardTypeIcon = document.querySelector('.card-type-icon');
    const cardTypeText = document.querySelector('.card-type-text');
    
    if (!cardTypeIcon || !cardTypeText) return;
    
    const cleanNumber = cardNumber.replace(/\D/g, '');
    let cardType = 'unknown';
    let cardName = 'Unknown';
    
    if (/^4/.test(cleanNumber)) {
        cardType = 'visa';
        cardName = 'Visa';
    } else if (/^5[1-5]/.test(cleanNumber)) {
        cardType = 'mastercard';
        cardName = 'Mastercard';
    } else if (/^3[47]/.test(cleanNumber)) {
        cardType = 'amex';
        cardName = 'American Express';
    } else if (/^6(?:011|5)/.test(cleanNumber)) {
        cardType = 'discover';
        cardName = 'Discover';
    }
    
    cardTypeIcon.className = `card-type-icon ${cardType}`;
    cardTypeText.textContent = cardName;
}

function validateCardNumber(input) {
    const cardNumber = input.value.replace(/\D/g, '');
    
    if (!cardNumber) {
        showFieldError(input, 'Card number is required');
        return false;
    }
    
    if (cardNumber.length < 13 || cardNumber.length > 16) {
        showFieldError(input, 'Card number must be 13-16 digits');
        return false;
    }
    
    // Luhn algorithm validation
    if (!isValidCardNumber(cardNumber)) {
        showFieldError(input, 'Invalid card number');
        return false;
    }
    
    clearFieldError(input);
    showFieldSuccess(input, 'Valid card number');
    return true;
}

function validateExpiryDate(input) {
    const expiry = input.value;
    
    if (!expiry) {
        showFieldError(input, 'Expiry date is required');
        return false;
    }
    
    const [month, year] = expiry.split('/');
    
    if (!month || !year || month.length !== 2 || year.length !== 2) {
        showFieldError(input, 'Please enter date in MM/YY format');
        return false;
    }
    
    const monthNum = parseInt(month);
    const yearNum = parseInt('20' + year);
    
    if (monthNum < 1 || monthNum > 12) {
        showFieldError(input, 'Invalid month');
        return false;
    }
    
    const currentDate = new Date();
    const expiryDate = new Date(yearNum, monthNum - 1);
    
    if (expiryDate <= currentDate) {
        showFieldError(input, 'Card has expired');
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function validateCVV(input) {
    const cvv = input.value;
    
    if (!cvv) {
        showFieldError(input, 'CVV is required');
        return false;
    }
    
    if (cvv.length < 3 || cvv.length > 4) {
        showFieldError(input, 'CVV must be 3-4 digits');
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function validateCardHolderName(input) {
    const name = input.value.trim();
    
    if (!name) {
        showFieldError(input, 'Cardholder name is required');
        return false;
    }
    
    if (name.length < 2) {
        showFieldError(input, 'Name must be at least 2 characters');
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function validateUPIId(input) {
    const upiId = input.value.trim();
    
    if (!upiId) {
        showFieldError(input, 'UPI ID is required');
        return false;
    }
    
    // UPI ID format: username@provider
    const upiRegex = /^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$/;
    
    if (!upiRegex.test(upiId)) {
        showFieldError(input, 'Please enter a valid UPI ID (e.g., user@paytm)');
        return false;
    }
    
    clearFieldError(input);
    showFieldSuccess(input, 'Valid UPI ID');
    return true;
}

function validateCustomerId(input) {
    const customerId = input.value.trim();
    
    if (!customerId) {
        showFieldError(input, 'Customer ID is required');
        return false;
    }
    
    if (customerId.length < 3) {
        showFieldError(input, 'Customer ID must be at least 3 characters');
        return false;
    }
    
    clearFieldError(input);
    return true;
}

function isValidCardNumber(cardNumber) {
    // Luhn algorithm
    let sum = 0;
    let isEven = false;
    
    for (let i = cardNumber.length - 1; i >= 0; i--) {
        let digit = parseInt(cardNumber.charAt(i));
        
        if (isEven) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        
        sum += digit;
        isEven = !isEven;
    }
    
    return sum % 10 === 0;
}

function validatePaymentForm() {
    const activeForm = document.querySelector('.payment-method-form.active');
    if (!activeForm) return false;
    
    const method = activeForm.dataset.method;
    let isValid = true;
    
    switch (method) {
        case 'card':
            isValid = validateCardForm();
            break;
        case 'upi':
            isValid = validateUPIForm();
            break;
        case 'netbanking':
            isValid = validateNetBankingForm();
            break;
        case 'wallet':
            isValid = validateWalletForm();
            break;
    }
    
    return isValid;
}

function validateCardForm() {
    const cardNumber = document.getElementById('card_number');
    const expiry = document.getElementById('card_expiry');
    const cvv = document.getElementById('card_cvv');
    const holderName = document.getElementById('card_holder_name');
    
    let isValid = true;
    
    if (!validateCardNumber(cardNumber)) isValid = false;
    if (!validateExpiryDate(expiry)) isValid = false;
    if (!validateCVV(cvv)) isValid = false;
    if (!validateCardHolderName(holderName)) isValid = false;
    
    return isValid;
}

function validateUPIForm() {
    const upiId = document.getElementById('upi_id');
    return validateUPIId(upiId);
}

function validateNetBankingForm() {
    const bankName = document.getElementById('bank_name');
    const customerId = document.getElementById('customer_id');
    
    let isValid = true;
    
    if (!bankName.value) {
        showFieldError(bankName, 'Please select a bank');
        isValid = false;
    }
    
    if (!validateCustomerId(customerId)) isValid = false;
    
    return isValid;
}

function validateWalletForm() {
    const walletType = document.getElementById('wallet_type');
    const mobileNumber = document.getElementById('wallet_mobile');
    
    let isValid = true;
    
    if (!walletType.value) {
        showFieldError(walletType, 'Please select a wallet');
        isValid = false;
    }
    
    if (!mobileNumber.value) {
        showFieldError(mobileNumber, 'Mobile number is required');
        isValid = false;
    } else if (!/^[6-9]\d{9}$/.test(mobileNumber.value)) {
        showFieldError(mobileNumber, 'Please enter a valid mobile number');
        isValid = false;
    }
    
    return isValid;
}

function processPayment() {
    const submitButton = document.querySelector('.payment-submit');
    const originalText = submitButton.innerHTML;
    
    // Show processing state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing Payment...';
    
    // Collect form data
    const formData = new FormData(document.querySelector('.payment-form'));
    
    // Simulate payment processing
    fetch('/process_payment', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showPaymentSuccess(data);
        } else {
            showPaymentError(data.error || 'Payment failed. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showPaymentError('Network error occurred. Please check your connection and try again.');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    });
}

function showPaymentSuccess(data) {
    // Clear form data from localStorage
    clearSavedFormData();
    
    // Show success modal
    const modal = createPaymentResultModal('success', data);
    document.body.appendChild(modal);
    modal.style.display = 'block';
    
    // Redirect after delay
    setTimeout(() => {
        window.location.href = data.redirect_url || '/booking_history';
    }, 3000);
}

function showPaymentError(message) {
    // Show error modal
    const modal = createPaymentResultModal('error', { message });
    document.body.appendChild(modal);
    modal.style.display = 'block';
}

function createPaymentResultModal(type, data) {
    const modal = document.createElement('div');
    modal.className = 'payment-result-modal';
    
    if (type === 'success') {
        modal.innerHTML = `
            <div class="modal-content success">
                <div class="success-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h3>Payment Successful!</h3>
                <p>Your booking has been confirmed.</p>
                <div class="transaction-details">
                    <div class="detail-item">
                        <span>Transaction ID:</span>
                        <span class="transaction-id">${data.transaction_id}</span>
                    </div>
                    <div class="detail-item">
                        <span>PNR Number:</span>
                        <span class="pnr-number">${data.pnr}</span>
                    </div>
                    <div class="detail-item">
                        <span>Amount Paid:</span>
                        <span class="amount">₹${data.amount}</span>
                    </div>
                </div>
                <p class="redirect-message">Redirecting to booking history...</p>
                <div class="modal-actions">
                    <a href="/booking_history" class="btn btn-primary">View Booking</a>
                    <a href="/download_ticket/${data.booking_id}" class="btn btn-secondary">Download Ticket</a>
                </div>
            </div>
        `;
    } else {
        modal.innerHTML = `
            <div class="modal-content error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h3>Payment Failed</h3>
                <p>${data.message}</p>
                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="this.closest('.payment-result-modal').remove()">
                        Try Again
                    </button>
                    <a href="/booking_history" class="btn btn-secondary">Go to History</a>
                </div>
            </div>
        `;
    }
    
    return modal;
}

function updatePaymentSummary(method) {
    const summaryContainer = document.querySelector('.payment-summary');
    if (!summaryContainer) return;
    
    // Update method-specific charges
    const methodCharges = {
        'card': 0,
        'upi': 0,
        'netbanking': 5,
        'wallet': 2
    };
    
    const charge = methodCharges[method] || 0;
    const baseAmount = parseFloat(document.querySelector('[data-base-amount]')?.dataset.baseAmount || 0);
    const totalAmount = baseAmount + charge;
    
    // Update summary display
    const chargeElement = summaryContainer.querySelector('.method-charge');
    const totalElement = summaryContainer.querySelector('.total-amount');
    
    if (chargeElement) {
        chargeElement.textContent = charge > 0 ? `₹${charge}` : 'Free';
    }
    
    if (totalElement) {
        totalElement.textContent = `₹${totalAmount.toFixed(2)}`;
    }
}

function updateBankingInfo(bankName) {
    const infoContainer = document.querySelector('.banking-info');
    if (!infoContainer || !bankName) return;
    
    // Show bank-specific information
    const bankInfo = {
        'sbi': 'State Bank of India - Use your internet banking credentials',
        'hdfc': 'HDFC Bank - NetBanking login required',
        'icici': 'ICICI Bank - Use your customer ID and password',
        'axis': 'Axis Bank - Internet banking authentication required'
    };
    
    const info = bankInfo[bankName] || 'Please have your internet banking credentials ready';
    infoContainer.innerHTML = `<i class="fas fa-info-circle"></i> ${info}`;
}

function clearSavedFormData() {
    // Remove all payment-related data from localStorage
    Object.keys(localStorage).forEach(key => {
        if (key.startsWith('payment_')) {
            localStorage.removeItem(key);
        }
    });
}

// Utility functions
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
}

function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}

// Add CSS for payment-specific elements
const style = document.createElement('style');
style.textContent = `
    .payment-method-btn {
        transition: all 0.3s ease;
    }
    
    .payment-method-btn.active {
        background: var(--accent-color);
        color: white;
        border-color: var(--accent-color);
    }
    
    .payment-method-form {
        display: none;
        animation: fadeIn 0.3s ease-out;
    }
    
    .payment-method-form.active {
        display: block;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .card-type-icon {
        width: 32px;
        height: 20px;
        background-size: contain;
        background-repeat: no-repeat;
        display: inline-block;
    }
    
    .card-type-icon.visa {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 32"><rect fill="%231A1F71" width="48" height="32" rx="4"/><text x="24" y="20" text-anchor="middle" fill="white" font-size="10" font-weight="bold">VISA</text></svg>');
    }
    
    .card-type-icon.mastercard {
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 32"><rect fill="%23EB001B" width="48" height="32" rx="4"/><text x="24" y="20" text-anchor="middle" fill="white" font-size="8" font-weight="bold">MC</text></svg>');
    }
    
    .payment-result-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 1000;
        display: none;
    }
    
    .payment-result-modal .modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 2rem;
        max-width: 500px;
        width: 90%;
        text-align: center;
    }
    
    .success-icon, .error-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .success-icon {
        color: var(--success-color);
    }
    
    .error-icon {
        color: var(--danger-color);
    }
    
    .transaction-details {
        background: var(--bg-primary);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .detail-item {
        display: flex;
        justify-content: space-between;
        margin: 0.5rem 0;
    }
    
    .redirect-message {
        color: var(--text-secondary);
        font-style: italic;
        margin: 1rem 0;
    }
    
    .modal-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-top: 1.5rem;
    }
`;

if (!document.querySelector('#payment-styles')) {
    style.id = 'payment-styles';
    document.head.appendChild(style);
}