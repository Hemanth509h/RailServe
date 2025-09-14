// RailServe - Main JavaScript File

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize Application
function initializeApp() {
    setupFormValidation();
    setupFlashMessages();
    setupNavigation();
    setupAnimations();
    setupDateInputs();
    setupSearchFeatures();
}

// Form Validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

// Validate Form
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Validate Individual Field
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const required = field.hasAttribute('required');
    
    // Clear previous errors
    clearFieldError(field);
    
    // Required field validation
    if (required && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (value) {
        // Email validation
        if (type === 'email' && !isValidEmail(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
        
        // Password validation
        if (field.name === 'password' && value.length < 6) {
            showFieldError(field, 'Password must be at least 6 characters long');
            return false;
        }
        
        // Confirm password validation
        if (field.name === 'confirm_password') {
            const passwordField = document.querySelector('input[name="password"]');
            if (passwordField && value !== passwordField.value) {
                showFieldError(field, 'Passwords do not match');
                return false;
            }
        }
        
        // PNR validation
        if (field.name === 'pnr' && !/^\d{10}$/.test(value)) {
            showFieldError(field, 'PNR must be exactly 10 digits');
            return false;
        }
        
        // Date validation
        if (type === 'date' && new Date(value) < new Date().setHours(0,0,0,0)) {
            showFieldError(field, 'Date cannot be in the past');
            return false;
        }
    }
    
    return true;
}

// Show Field Error
function showFieldError(field, message) {
    field.classList.add('error');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.color = '#ef4444';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.parentNode.appendChild(errorDiv);
}

// Clear Field Error
function clearFieldError(field) {
    field.classList.remove('error');
    const errorMessage = field.parentNode.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

// Email Validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Flash Messages
function setupFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    
    flashMessages.forEach(message => {
        // Auto-hide success messages after 5 seconds
        if (message.classList.contains('alert-success')) {
            setTimeout(() => {
                fadeOut(message);
            }, 5000);
        }
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.className = 'flash-close';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            margin-left: auto;
            opacity: 0.7;
        `;
        
        closeBtn.addEventListener('click', () => {
            fadeOut(message);
        });
        
        message.appendChild(closeBtn);
    });
}

// Fade Out Animation
function fadeOut(element) {
    element.style.transition = 'opacity 0.3s ease-out';
    element.style.opacity = '0';
    
    setTimeout(() => {
        element.remove();
    }, 300);
}

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Highlight active page
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        }
    });
    
    // Mobile menu toggle (if needed)
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
}

// Animations
function setupAnimations() {
    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (!prefersReducedMotion) {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);
        
        // Observe elements
        const animateElements = document.querySelectorAll('.card, .train-card, .feature-card');
        animateElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
            observer.observe(el);
        });
        
        // Setup UI illusions
        setupCardTiltEffects();
        setupParallaxEffects();
    }
}

// Card Tilt Effects
function setupCardTiltEffects() {
    const cards = document.querySelectorAll('.train-card, .feature-card, .card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = card.style.transform || '';
            card.style.transition = 'transform 0.3s ease-out, box-shadow 0.3s ease-out';
        });
        
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / centerY * -10;
            const rotateY = (x - centerX) / centerX * 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
            card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.boxShadow = '';
        });
    });
}

// Parallax Effects
function setupParallaxEffects() {
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection) {
        // Create parallax layers for hero section
        const heroContent = heroSection.querySelector('.hero-content');
        
        window.addEventListener('scroll', throttle(() => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            
            if (heroContent) {
                heroContent.style.transform = `translateY(${parallax}px)`;
            }
        }, 16)); // ~60fps
    }
    
    // Background parallax for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        window.addEventListener('scroll', throttle(() => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.2 * (index % 2 === 0 ? 1 : -1);
            
            card.style.transform = `translateY(${rate}px)`;
        }, 16));
    });
}

// Add CSS for animations
const animationStyles = `
.animate-in {
    opacity: 1 !important;
    transform: translateY(0) !important;
}
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = animationStyles;
document.head.appendChild(styleSheet);

// Date Inputs
function setupDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
        
        // Set maximum date to 120 days from today (typical booking window)
        const maxDate = new Date();
        maxDate.setDate(maxDate.getDate() + 120);
        input.setAttribute('max', maxDate.toISOString().split('T')[0]);
    });
}

// Search Features
function setupSearchFeatures() {
    // Station search/filter
    const stationSelects = document.querySelectorAll('select[name*="station"]');
    
    stationSelects.forEach(select => {
        // Add search functionality if needed
        makeSelectSearchable(select);
    });
    
    // Auto-refresh search results
    const searchForm = document.querySelector('.search-form form');
    if (searchForm) {
        const inputs = searchForm.querySelectorAll('input, select');
        let searchTimeout;
        
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (isSearchFormComplete()) {
                        // Auto-search could be implemented here
                        // searchForm.submit();
                    }
                }, 1000);
            });
        });
    }
}

// Make Select Searchable
function makeSelectSearchable(select) {
    // Simple search functionality for select elements
    select.addEventListener('keydown', function(e) {
        if (e.key.length === 1) {
            const searchTerm = e.key.toLowerCase();
            const options = Array.from(this.options);
            
            const matchingOption = options.find(option => 
                option.text.toLowerCase().startsWith(searchTerm)
            );
            
            if (matchingOption) {
                this.value = matchingOption.value;
            }
        }
    });
}

// Check if Search Form is Complete
function isSearchFormComplete() {
    const searchForm = document.querySelector('.search-form form');
    if (!searchForm) return false;
    
    const requiredFields = searchForm.querySelectorAll('[required]');
    return Array.from(requiredFields).every(field => field.value.trim());
}

// Utility Functions

// Format Currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

// Format Date
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    return new Intl.DateTimeFormat('en-IN', { ...defaultOptions, ...options }).format(new Date(date));
}

// Format Time
function formatTime(time) {
    return new Intl.DateTimeFormat('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    }).format(new Date(`2000-01-01T${time}`));
}

// Show Loading State
function showLoading(element, text = 'Loading...') {
    const loadingHTML = `
        <div class="loading-state" style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 1rem;
            color: #6b7280;
        ">
            <div class="spinner" style="
                width: 20px;
                height: 20px;
                border: 2px solid #e5e7eb;
                border-top: 2px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
            <span>${text}</span>
        </div>
    `;
    
    element.innerHTML = loadingHTML;
    
    // Add spinner animation if not already added
    if (!document.querySelector('#spinner-style')) {
        const spinnerStyle = document.createElement('style');
        spinnerStyle.id = 'spinner-style';
        spinnerStyle.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(spinnerStyle);
    }
}

// Hide Loading State
function hideLoading(element) {
    const loadingState = element.querySelector('.loading-state');
    if (loadingState) {
        loadingState.remove();
    }
}

// Debounce Function
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

// Throttle Function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Copy to Clipboard
function copyToClipboard(text, callback) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            if (callback) callback(true);
        }).catch(() => {
            fallbackCopyToClipboard(text, callback);
        });
    } else {
        fallbackCopyToClipboard(text, callback);
    }
}

// Fallback Copy to Clipboard
function fallbackCopyToClipboard(text, callback) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        if (callback) callback(true);
    } catch (err) {
        if (callback) callback(false);
    }
    
    document.body.removeChild(textArea);
}

// Show Toast Notification
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease-out;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    toast.style.backgroundColor = colors[type] || colors.info;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, duration);
}

// Local Storage Helpers
const storage = {
    set(key, value) {
        try {
            localStorage.setItem(`railserve_${key}`, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Error saving to localStorage:', error);
            return false;
        }
    },
    
    get(key) {
        try {
            const item = localStorage.getItem(`railserve_${key}`);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return null;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(`railserve_${key}`);
            return true;
        } catch (error) {
            console.error('Error removing from localStorage:', error);
            return false;
        }
    }
};

// Remember Form Data
function rememberFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        // Don't save sensitive data
        if (!key.includes('password') && !key.includes('cvv')) {
            data[key] = value;
        }
    });
    
    storage.set('form_data', data);
}

// Restore Form Data
function restoreFormData(form) {
    const savedData = storage.get('form_data');
    if (!savedData) return;
    
    Object.entries(savedData).forEach(([key, value]) => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field && field.type !== 'password') {
            field.value = value;
        }
    });
}

// Export functions for use in other scripts
window.RailServe = {
    formatCurrency,
    formatDate,
    formatTime,
    showLoading,
    hideLoading,
    showToast,
    copyToClipboard,
    storage,
    debounce,
    throttle
};

// Enhanced Mobile Navigation
document.addEventListener('DOMContentLoaded', () => {
    setupMobileNavigation();
    setupViewportOptimization();
});

function setupMobileNavigation() {
    const navToggle = document.getElementById('nav-toggle-icon');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (navToggle && navMenu) {
        // Toggle mobile menu
        navToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleMobileMenu();
        });
        
        // Close menu when clicking on nav links
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    closeMobileMenu();
                }
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                closeMobileMenu();
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeMobileMenu();
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                closeMobileMenu();
            }
        });
    }
}

function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    const navToggle = document.getElementById('nav-toggle-icon');
    
    if (navMenu && navToggle) {
        navMenu.classList.toggle('active');
        
        // Animate hamburger icon
        if (navMenu.classList.contains('active')) {
            navToggle.classList.remove('fa-bars');
            navToggle.classList.add('fa-times');
        } else {
            navToggle.classList.remove('fa-times');
            navToggle.classList.add('fa-bars');
        }
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
    }
}

function closeMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    const navToggle = document.getElementById('nav-toggle-icon');
    
    if (navMenu && navToggle) {
        navMenu.classList.remove('active');
        navToggle.classList.remove('fa-times');
        navToggle.classList.add('fa-bars');
        document.body.style.overflow = '';
    }
}

// Viewport optimization for mobile devices
function setupViewportOptimization() {
    // Disable zoom on input focus for iOS
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            if (window.innerWidth <= 768) {
                const viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) {
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
                }
            }
        });
        
        input.addEventListener('blur', () => {
            if (window.innerWidth <= 768) {
                const viewport = document.querySelector('meta[name="viewport"]');
                if (viewport) {
                    viewport.setAttribute('content', 'width=device-width, initial-scale=1.0');
                }
            }
        });
    });
    
    // Add touch-friendly styles for mobile
    if ('ontouchstart' in window) {
        document.body.classList.add('touch-device');
    }
}

// Add mobile-specific utility functions
const MobileUtils = {
    // Check if device is mobile
    isMobile() {
        return window.innerWidth <= 768;
    },
    
    // Check if device is tablet
    isTablet() {
        return window.innerWidth > 768 && window.innerWidth <= 1024;
    },
    
    // Check if device is touch-enabled
    isTouchDevice() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    },
    
    // Prevent default touch behavior for certain elements
    preventTouchDefaults(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                e.preventDefault();
            }, { passive: false });
        });
    },
    
    // Add ripple effect for touch interactions
    addRippleEffect(element) {
        element.addEventListener('touchstart', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.touches[0].clientX - rect.left - size / 2;
            const y = e.touches[0].clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            }, 600);
        });
    }
};

// Add CSS for ripple effect and touch styles
const mobileStyles = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .touch-device .btn:active,
    .touch-device .nav-link:active,
    .touch-device .train-card:active {
        transform: translateY(1px);
    }
    
    .touch-device .btn {
        -webkit-tap-highlight-color: transparent;
    }
    
    /* Improve touch targets */
    @media (max-width: 768px) {
        .btn, .nav-link, .tab-button {
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Better spacing for touch */
        .nav-menu .nav-link {
            margin-bottom: 0.5rem;
            padding: 1rem;
        }
        
        /* Prevent text selection on touch */
        .btn, .nav-link, .train-card {
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
    }
`;

// Add mobile styles to document
const mobileStyleSheet = document.createElement('style');
mobileStyleSheet.textContent = mobileStyles;
document.head.appendChild(mobileStyleSheet);

// Export mobile utilities
window.RailServe.Mobile = MobileUtils;