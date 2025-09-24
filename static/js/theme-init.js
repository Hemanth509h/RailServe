// Theme initialization - prevent FOUC by setting theme before CSS loads
(function() {
    const storedTheme = localStorage.getItem('railserve-theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const theme = storedTheme || systemTheme;
    document.documentElement.setAttribute('data-theme', theme);
    // Update theme color immediately
    const metaTheme = document.getElementById('meta-theme-color');
    if (metaTheme) {
        metaTheme.setAttribute('content', theme === 'dark' ? '#0f172a' : '#1e40af');
    }
})();