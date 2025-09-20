// Admin Quota Management Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Quota Management page loaded');
    initializeFilters();
});

function initializeFilters() {
    const trainFilter = document.getElementById('trainFilter');
    const quotaFilter = document.getElementById('quotaFilter');
    
    if (trainFilter) {
        trainFilter.addEventListener('input', filterTrains);
    }
    if (quotaFilter) {
        quotaFilter.addEventListener('change', filterTrains);
    }
}

function filterTrains() {
    const searchTerm = document.getElementById('trainFilter')?.value.toLowerCase() || '';
    const quotaFilter = document.getElementById('quotaFilter')?.value || '';
    const cards = document.querySelectorAll('.quota-card');
    
    cards.forEach(card => {
        // Add filtering logic here
        console.log('Filtering trains');
    });
}