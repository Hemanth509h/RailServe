/**
 * ===============================================
 * RAILSERVE DARK THEME TOGGLE
 * Dedicated JavaScript for dark/light theme switching
 * ===============================================
 */

class ThemeManager {
    constructor() {
        this.currentTheme = this.getStoredTheme() || this.getSystemTheme();
        this.themeToggle = null;
        this.themeIcon = null;
        this.themeText = null;
        
        this.init();
    }
    
    init() {
        // Apply theme on page load
        this.applyTheme(this.currentTheme);
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupToggleButton());
        } else {
            this.setupToggleButton();
        }
        
        // Listen for system theme changes
        this.watchSystemTheme();
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
            
            // Update UI to match current theme
            this.updateToggleUI();
        }
    }
    
    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.currentTheme);
        this.saveTheme();
        this.updateToggleUI();
        
        // Dispatch custom event for other scripts to listen to
        this.dispatchThemeChangeEvent();
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#0f172a' : '#1e40af');
        }
        
        // Update ARIA attributes for accessibility
        if (this.themeToggle) {
            this.themeToggle.setAttribute('aria-pressed', theme === 'dark');
            this.themeToggle.setAttribute('aria-label', 
                theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'
            );
        }
    }
    
    updateToggleUI() {
        if (!this.themeIcon || !this.themeText) return;
        
        if (this.currentTheme === 'dark') {
            this.themeIcon.classList.remove('fa-moon');
            this.themeIcon.classList.add('fa-sun');
            this.themeText.textContent = 'Light';
        } else {
            this.themeIcon.classList.remove('fa-sun');
            this.themeIcon.classList.add('fa-moon');
            this.themeText.textContent = 'Dark';
        }
    }
    
    getStoredTheme() {
        return localStorage.getItem('railserve-theme');
    }
    
    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    saveTheme() {
        localStorage.setItem('railserve-theme', this.currentTheme);
    }
    
    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Only listen to system theme if user hasn't set preference
        mediaQuery.addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                this.currentTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.currentTheme);
                this.updateToggleUI();
            }
        });
    }
    
    addRippleEffect() {
        if (!this.themeToggle) return;
        
        const ripple = document.createElement('span');
        ripple.classList.add('theme-ripple');
        
        this.themeToggle.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    dispatchThemeChangeEvent() {
        const event = new CustomEvent('themechange', {
            detail: { theme: this.currentTheme }
        });
        window.dispatchEvent(event);
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .theme-ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        width: 100px;
        height: 100px;
        margin-top: -50px;
        margin-left: -50px;
        top: 50%;
        left: 50%;
        animation: theme-ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes theme-ripple-animation {
        from {
            transform: scale(0);
            opacity: 1;
        }
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .toggle-theme {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
window.ThemeManager = themeManager;

// Log successful load
console.log('RailServe Dark Theme Manager loaded successfully');
console.log('Current theme:', themeManager.currentTheme);
