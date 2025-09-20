// Admin Emergency Quota Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Emergency Quota page loaded');
});

function releaseEmergencySeats(trainId, trainNumber, availableSeats) {
    // Emergency seat release functionality
    console.log('Releasing emergency seats for train:', trainNumber);
}

function closeEmergencyModal() {
    const modal = document.getElementById('emergencyModal');
    if (modal) {
        modal.style.display = 'none';
    }
}