// Train search and station management functions

function swapStations() {
    const fromSelect = document.getElementById('from_station');
    const toSelect = document.getElementById('to_station');

    if (fromSelect && toSelect) {
        const fromValue = fromSelect.value;
        const toValue = toSelect.value;

        fromSelect.value = toValue;
        toSelect.value = fromValue;
    }
}

// Initialize date restrictions and form functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set minimum date to today for journey date
    const journeyDate = document.getElementById('journey_date');
    if (journeyDate) {
        journeyDate.min = new Date().toISOString().split('T')[0];
    }
});