// Admin Route Management Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Route Management page loaded');
});

function closeAddStationModal() {
    const modal = document.getElementById('addStationModal');
    if (modal) {
        modal.style.display = 'none';
    }
}