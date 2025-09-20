// Admin Fare Management Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fare Management page loaded');
});

function editFare(trainId, trainNumber, farePerKm, tatkalFarePerKm) {
    console.log('Editing fare for train:', trainNumber);
}

function closeFareModal() {
    const modal = document.getElementById('fareModal');
    if (modal) {
        modal.style.display = 'none';
    }
}