// Homepage specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize hero animations and search functionality
    initializeHeroAnimations();
    initializeSearchForm();
    initializeQuickBooking();
});

function initializeHeroAnimations() {
    // Add smooth scrolling for call-to-action buttons
    const ctaButtons = document.querySelectorAll('.cta-button, .btn-primary');
    ctaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            // Remove ripple after animation
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Animate stats on scroll
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
    
    // Observe stat cards and feature cards
    document.querySelectorAll('.stat-card, .feature-card').forEach(card => {
        observer.observe(card);
    });
}

function initializeSearchForm() {
    const searchForm = document.querySelector('.search-form');
    if (!searchForm) return;
    
    const fromInput = document.getElementById('from_station');
    const toInput = document.getElementById('to_station');
    const dateInput = document.getElementById('travel_date');
    const swapButton = document.querySelector('.swap-stations');
    
    // Station swap functionality
    if (swapButton && fromInput && toInput) {
        swapButton.addEventListener('click', function(e) {
            e.preventDefault();
            const fromValue = fromInput.value;
            const toValue = toInput.value;
            
            // Animate the swap
            fromInput.style.transform = 'translateX(10px)';
            toInput.style.transform = 'translateX(-10px)';
            
            setTimeout(() => {
                fromInput.value = toValue;
                toInput.value = fromValue;
                
                fromInput.style.transform = '';
                toInput.style.transform = '';
            }, 200);
            
            // Add rotation animation to swap icon
            this.style.transform = 'rotate(180deg)';
            setTimeout(() => {
                this.style.transform = '';
            }, 300);
        });
    }
    
    // Validate form before submission
    searchForm.addEventListener('submit', function(e) {
        const errors = [];
        
        if (!fromInput.value.trim()) {
            errors.push('Please select departure station');
        }
        
        if (!toInput.value.trim()) {
            errors.push('Please select destination station');
        }
        
        if (fromInput.value === toInput.value && fromInput.value) {
            errors.push('Departure and destination stations cannot be the same');
        }
        
        if (!dateInput.value) {
            errors.push('Please select travel date');
        } else {
            const selectedDate = new Date(dateInput.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                errors.push('Please select a future date');
            }
        }
        
        if (errors.length > 0) {
            e.preventDefault();
            showValidationErrors(errors);
        }
    });
    
    // Set minimum date to today
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
        
        // Set default date to today if empty
        if (!dateInput.value) {
            dateInput.value = today;
        }
    }
}

function initializeQuickBooking() {
    // Popular routes quick booking
    const popularRoutes = document.querySelectorAll('.popular-route');
    popularRoutes.forEach(route => {
        route.addEventListener('click', function() {
            const from = this.dataset.from;
            const to = this.dataset.to;
            
            if (from && to) {
                // Fill the search form
                const fromInput = document.getElementById('from_station');
                const toInput = document.getElementById('to_station');
                
                if (fromInput && toInput) {
                    fromInput.value = from;
                    toInput.value = to;
                    
                    // Scroll to search form
                    document.querySelector('.search-form').scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    
                    // Highlight the form briefly
                    const searchCard = document.querySelector('.search-card');
                    if (searchCard) {
                        searchCard.style.transform = 'scale(1.02)';
                        searchCard.style.boxShadow = '0 10px 30px rgba(59, 130, 246, 0.3)';
                        
                        setTimeout(() => {
                            searchCard.style.transform = '';
                            searchCard.style.boxShadow = '';
                        }, 1000);
                    }
                }
            }
        });
    });
}

function showValidationErrors(errors) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.validation-error');
    existingErrors.forEach(error => error.remove());
    
    // Create error container
    const errorContainer = document.createElement('div');
    errorContainer.className = 'validation-error alert alert-danger';
    errorContainer.innerHTML = `
        <strong>Please fix the following errors:</strong>
        <ul>
            ${errors.map(error => `<li>${error}</li>`).join('')}
        </ul>
    `;
    
    // Insert before search form
    const searchForm = document.querySelector('.search-form');
    searchForm.parentNode.insertBefore(errorContainer, searchForm);
    
    // Scroll to errors
    errorContainer.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorContainer.parentNode) {
            errorContainer.remove();
        }
    }, 5000);
}

// Add ripple effect CSS
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.4);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .animate-in {
        animation: slideInUp 0.6s ease-out;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);