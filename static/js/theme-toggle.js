/**
 * RailServe Theme Toggle System
 * Handles switching between light and dark themes with smooth transitions
 */

class ThemeManager {
    constructor() {
        // Honor system preference if no stored theme
        const stored = localStorage.getItem('railserve-theme');
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        this.currentTheme = stored || systemTheme;
        this.themeToggle = null;
        this.themeIcon = null;
        this.themeText = null;
        this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        this.init();
    }
    
    init() {
        // Apply saved theme
        this.applyTheme(this.currentTheme);
        
        // Set up toggle button
        this.setupToggleButton();
        
        // Listen for system preference changes
        this.watchSystemPreference();
    }
    
    setupToggleButton() {
        this.themeToggle = document.getElementById('toggleTheme');
        this.themeIcon = document.getElementById('theme-icon');
        this.themeText = document.getElementById('theme-text');
        
        if (this.themeToggle) {
            this.themeToggle.addEventListener('click', () => {
                this.toggleTheme();
                this.addRippleEffect();
            });
            
            // Update button state
            this.updateToggleButton();
        }
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        this.saveTheme();
        this.updateToggleButton();
        
        // Add theme transition animation
        this.animateThemeTransition();
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', 
                theme === 'dark' ? '#0f172a' : '#1e40af'
            );
        }
        
        // Trigger custom event for other components
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
    }
    
    updateToggleButton() {
        if (!this.themeIcon || !this.themeText || !this.themeToggle) return;
        
        if (this.currentTheme === 'dark') {
            this.themeIcon.className = 'fas fa-sun';
            this.themeText.textContent = 'Light';
            this.themeToggle.setAttribute('aria-pressed', 'true');
            this.themeToggle.setAttribute('aria-label', 'Switch to light theme');
        } else {
            this.themeIcon.className = 'fas fa-moon';
            this.themeText.textContent = 'Dark';
            this.themeToggle.setAttribute('aria-pressed', 'false');
            this.themeToggle.setAttribute('aria-label', 'Switch to dark theme');
        }
    }
    
    saveTheme() {
        localStorage.setItem('railserve-theme', this.currentTheme);
    }
    
    watchSystemPreference() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        mediaQuery.addEventListener('change', (e) => {
            // Only auto-switch if user hasn't manually set a preference
            if (!localStorage.getItem('railserve-theme')) {
                this.currentTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.currentTheme);
                this.updateToggleButton();
            }
        });
    }
    
    animateThemeTransition() {
        // Skip animation if user prefers reduced motion
        if (this.prefersReducedMotion) return;
        
        // Create a smooth transition overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: ${this.currentTheme === 'dark' ? '#0f172a' : '#f8fafc'};
            opacity: 0;
            pointer-events: none;
            z-index: 9999;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(overlay);
        
        // Animate the overlay
        requestAnimationFrame(() => {
            overlay.style.opacity = '0.7';
        });
        
        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(overlay);
            }, 300);
        }, 150);
    }
    
    addRippleEffect() {
        if (!this.themeToggle || this.prefersReducedMotion) return;
        
        const ripple = document.createElement('span');
        const rect = this.themeToggle.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2;
        
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            width: ${size}px;
            height: ${size}px;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%) scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
            z-index: 1;
        `;
        
        this.themeToggle.style.position = 'relative';
        this.themeToggle.style.overflow = 'hidden';
        this.themeToggle.appendChild(ripple);
        
        // Add ripple animation
        if (!document.querySelector('#ripple-keyframes')) {
            const style = document.createElement('style');
            style.id = 'ripple-keyframes';
            style.textContent = `
                @keyframes ripple {
                    to {
                        transform: translate(-50%, -50%) scale(1);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    }
}

// Enhanced 3D Effects Manager
class EnhancedEffectsManager {
    constructor() {
        this.isEnabled = localStorage.getItem('railserve-3d-enabled') !== 'false';
        this.effects = [];
        
        if (this.isEnabled && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.init();
        }
    }
    
    init() {
        this.createFloatingElements();
        this.enhanceNavigation();
        this.addParticleEffects();
        this.setupMorphingShapes();
    }
    
    createFloatingElements() {
        // Create floating geometric shapes
        const shapes = ['circle', 'triangle', 'square', 'hexagon'];
        
        for (let i = 0; i < 8; i++) {
            const shape = document.createElement('div');
            shape.className = `floating-shape floating-${shapes[i % shapes.length]}`;
            
            shape.style.cssText = `
                position: fixed;
                width: ${20 + Math.random() * 40}px;
                height: ${20 + Math.random() * 40}px;
                background: linear-gradient(45deg, 
                    hsl(${Math.random() * 360}, 70%, 60%), 
                    hsl(${Math.random() * 360}, 70%, 80%));
                opacity: 0.1;
                border-radius: ${shape.className.includes('circle') ? '50%' : 
                    shape.className.includes('hexagon') ? '30%' : '0'};
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float-${i} ${15 + Math.random() * 10}s infinite linear;
                pointer-events: none;
                z-index: 1;
                transform-style: preserve-3d;
            `;
            
            document.body.appendChild(shape);
            this.effects.push(shape);
            
            // Create unique animation for each shape
            this.createFloatingAnimation(i);
        }
    }
    
    createFloatingAnimation(index) {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes float-${index} {
                0% {
                    transform: translate3d(0, 0, 0) rotate(0deg) scale(1);
                }
                25% {
                    transform: translate3d(${100 - Math.random() * 200}px, ${100 - Math.random() * 200}px, 50px) 
                               rotate(90deg) scale(1.2);
                }
                50% {
                    transform: translate3d(${200 - Math.random() * 400}px, ${50 - Math.random() * 100}px, -30px) 
                               rotate(180deg) scale(0.8);
                }
                75% {
                    transform: translate3d(${-100 + Math.random() * 200}px, ${-50 + Math.random() * 100}px, 40px) 
                               rotate(270deg) scale(1.1);
                }
                100% {
                    transform: translate3d(0, 0, 0) rotate(360deg) scale(1);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    enhanceNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach((link, index) => {
            link.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            
            link.addEventListener('mouseenter', () => {
                link.style.transform = 'translateY(-2px) scale(1.05)';
                link.style.textShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
                
                // Add glow effect
                link.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.5)';
            });
            
            link.addEventListener('mouseleave', () => {
                link.style.transform = 'translateY(0) scale(1)';
                link.style.textShadow = 'none';
                link.style.boxShadow = 'none';
            });
        });
    }
    
    addParticleEffects() {
        // Create particle system for hero section
        const heroSection = document.querySelector('.hero-section');
        if (!heroSection) return;
        
        const particleContainer = document.createElement('div');
        particleContainer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
            z-index: 1;
        `;
        
        heroSection.appendChild(particleContainer);
        
        // Create particles
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: absolute;
                width: 3px;
                height: 3px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: sparkle-${i} ${5 + Math.random() * 10}s infinite ease-in-out;
            `;
            
            particleContainer.appendChild(particle);
            this.createSparkleAnimation(i);
        }
    }
    
    createSparkleAnimation(index) {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes sparkle-${index} {
                0%, 100% {
                    opacity: 0;
                    transform: scale(0) rotate(0deg);
                }
                50% {
                    opacity: 1;
                    transform: scale(1) rotate(180deg);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    setupMorphingShapes() {
        // Add morphing background shapes
        const shapes = document.querySelectorAll('.train-card, .feature-card');
        
        shapes.forEach((shape, index) => {
            const morphBg = document.createElement('div');
            morphBg.style.cssText = `
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(45deg, 
                    hsl(${220 + index * 30}, 70%, 95%), 
                    hsl(${240 + index * 20}, 60%, 90%));
                opacity: 0;
                border-radius: 50%;
                z-index: -1;
                transition: all 0.6s ease;
                transform: scale(0);
            `;
            
            shape.style.position = 'relative';
            shape.style.overflow = 'hidden';
            shape.appendChild(morphBg);
            
            shape.addEventListener('mouseenter', () => {
                morphBg.style.opacity = '0.1';
                morphBg.style.transform = 'scale(1)';
            });
            
            shape.addEventListener('mouseleave', () => {
                morphBg.style.opacity = '0';
                morphBg.style.transform = 'scale(0)';
            });
        });
    }
    
    destroy() {
        this.effects.forEach(effect => {
            if (effect.parentNode) {
                effect.parentNode.removeChild(effect);
            }
        });
        this.effects = [];
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme manager
    window.themeManager = new ThemeManager();
    
    // Initialize enhanced effects
    window.enhancedEffects = new EnhancedEffectsManager();
    
    // Listen for 3D toggle changes
    document.addEventListener('3dToggleChanged', (e) => {
        if (e.detail.enabled) {
            if (!window.enhancedEffects) {
                window.enhancedEffects = new EnhancedEffectsManager();
            }
        } else if (window.enhancedEffects) {
            window.enhancedEffects.destroy();
            window.enhancedEffects = null;
        }
    });
});