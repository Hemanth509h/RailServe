// Payment Success Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Payment Success page loaded');
    
    // Auto-redirect after 10 seconds
    setTimeout(() => {
        const redirectUrl = document.querySelector('[data-redirect]')?.dataset.redirect;
        if (redirectUrl) {
            window.location.href = redirectUrl;
        }
    }, 10000);
});