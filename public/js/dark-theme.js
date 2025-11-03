// Dark Theme Toggle Functionality for RailServe

(function() {
    'use strict';

    // Get theme elements
    const toggleButton = document.getElementById('toggleTheme');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    const metaThemeColor = document.getElementById('meta-theme-color');

    if (!toggleButton) return;

    // Get current theme
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    // Set theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('railserve-theme', theme);

        // Update button state
        toggleButton.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
        toggleButton.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');

        // Update icon and text
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
        if (themeText) {
            themeText.textContent = theme === 'dark' ? 'Light' : 'Dark';
        }

        // Update meta theme color
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#0f172a' : '#1e40af');
        }
    }

    // Toggle theme
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }

    // Initialize theme on page load
    function initializeTheme() {
        const currentTheme = getCurrentTheme();
        setTheme(currentTheme);
    }

    // Event listeners
    toggleButton.addEventListener('click', toggleTheme);

    // Listen for system theme changes
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    darkModeQuery.addEventListener('change', (e) => {
        // Only auto-switch if user hasn't set a preference
        if (!localStorage.getItem('railserve-theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });

    // Initialize on load
    initializeTheme();

    // Keyboard accessibility
    toggleButton.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            toggleTheme();
        }
    });
})();
