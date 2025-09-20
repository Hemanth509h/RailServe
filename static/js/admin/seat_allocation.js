// Admin Seat Allocation Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Seat Allocation page loaded');
    initializeDateFilters();
});

function initializeDateFilters() {
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        dateInput.min = new Date().toISOString().split('T')[0];
    }
}