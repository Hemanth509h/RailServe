/**
 * ===============================================
 * RAILSERVE ANIMATIONS JAVASCRIPT
 * Interactive animations and effects
 * ===============================================
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initScrollAnimations();
    initCardHoverEffects();
    initButtonRippleEffects();
    initParallaxEffects();
    initCounterAnimations();
});

/**
 * Scroll Reveal Animations
 * Reveals elements as they enter viewport
 */
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                // Optional: Stop observing after reveal
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all elements with scroll-reveal class
    document.querySelectorAll('.scroll-reveal').forEach(element => {
        observer.observe(element);
    });
}

/**
 * Card Hover 3D Tilt Effect
 * Adds interactive tilt effect to cards
 */
function initCardHoverEffects() {
    const cards = document.querySelectorAll('.train-card, .feature-card, .booking-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

/**
 * Button Ripple Effect
 * Creates material design ripple effect on buttons
 */
function initButtonRippleEffects() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple-effect');
            
            button.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * Parallax Scroll Effect
 * Creates depth effect on scroll
 */
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    if (parallaxElements.length > 0) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }
}

/**
 * Counter Animation
 * Animates numbers counting up
 */
function initCounterAnimations() {
    const counters = document.querySelectorAll('.counter');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.dataset.target);
        const duration = parseInt(counter.dataset.duration) || 2000;
        const increment = target / (duration / 16); // 60fps
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    };
    
    const counterObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                animateCounter(entry.target);
                entry.target.classList.add('counted');
                counterObserver.unobserve(entry.target);
            }
        });
    });
    
    counters.forEach(counter => counterObserver.observe(counter));
}

/**
 * Smooth Scroll to Element
 * Smooth scrolling for anchor links
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Add entrance animations to elements
 */
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('animate-fade-in-up');
        }, index * 100);
    });
}

/**
 * Floating Animation for Icons
 */
function initFloatingIcons() {
    const icons = document.querySelectorAll('.floating-icon');
    
    icons.forEach((icon, index) => {
        icon.style.animationDelay = `${index * 0.2}s`;
        icon.classList.add('animate-float');
    });
}

/**
 * Text Typing Animation
 */
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

/**
 * Progress Bar Animation
 */
function animateProgressBar(progressBar) {
    const targetWidth = progressBar.dataset.progress || '0%';
    progressBar.style.width = '0%';
    
    setTimeout(() => {
        progressBar.style.transition = 'width 1.5s ease-out';
        progressBar.style.width = targetWidth;
    }, 100);
}

/**
 * Stagger Animation for Lists
 */
function staggerAnimation(elements, animationClass, delay = 100) {
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add(animationClass);
        }, index * delay);
    });
}

/**
 * Add CSS ripple effect styles if not already present
 */
const animationStyle = document.createElement('style');
animationStyle.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .btn {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(animationStyle);

/**
 * Initialize all animations when page loads
 */
window.addEventListener('load', function() {
    // Add scroll-reveal class to elements that should animate on scroll
    const animateElements = document.querySelectorAll('.train-card, .feature-card, .booking-card');
    animateElements.forEach(el => el.classList.add('scroll-reveal'));
    
    // Initialize floating icons if present
    initFloatingIcons();
    
    // Log animations loaded
    console.log('RailServe animations loaded successfully');
});

/**
 * Export functions for use in other scripts
 */
window.RailServeAnimations = {
    smoothScrollTo,
    typeWriter,
    animateProgressBar,
    staggerAnimation
};
