// Food Cart Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Food Cart page loaded');
    initializeCartForm();
});

function initializeCartForm() {
    const cartForm = document.querySelector('form[action*="place_food_order"]');
    if (cartForm) {
        console.log('Cart form initialized');
    }
}