// Animation JavaScript for RailServe

(function() {
    'use strict';

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Initialize animations when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAnimations);
    } else {
        initAnimations();
    }

    function initAnimations() {
        if (!prefersReducedMotion) {
            setupScrollAnimations();
            setupCardTiltEffects();
            setupParallaxEffects();
        }
    }

    // Intersection Observer for fade-in animations
    function setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target); // Only animate once
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
    }

    // Card Tilt Effects on hover
    function setupCardTiltEffects() {
        const cards = document.querySelectorAll('.train-card, .feature-card, .card');

        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transition = 'transform 0.3s ease-out, box-shadow 0.3s ease-out';
            });

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = (y - centerY) / centerY * -5; // Reduced rotation
                const rotateY = (x - centerX) / centerX * 5;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
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
            const heroContent = heroSection.querySelector('.hero-content');

            window.addEventListener('scroll', throttle(() => {
                const scrolled = window.pageYOffset;
                const parallax = scrolled * 0.3; // Reduced parallax effect

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
                const rate = scrolled * -0.1 * (index % 2 === 0 ? 1 : -1);

                card.style.transform = `translateY(${rate}px)`;
            }, 16));
        });
    }

    // Throttle function to limit execution rate
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
        };
    }
})();
