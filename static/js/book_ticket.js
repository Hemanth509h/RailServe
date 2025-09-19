// Book ticket page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeBookingForm();
    initializeSeatSelection();
    initializePassengerForms();
    initializeFareCalculation();
});

function initializeBookingForm() {
    const bookingForm = document.querySelector('.booking-form');
    if (!bookingForm) return;
    
    // Add loading state to submit button
    bookingForm.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing Booking...';
        }
    });
    
    // Passenger count validation
    const passengerCountInput = document.getElementById('passenger_count');
    if (passengerCountInput) {
        passengerCountInput.addEventListener('change', function() {
            updatePassengerForms(parseInt(this.value));
            calculateFare();
        });
    }
    
    // Travel date validation
    const travelDateInput = document.getElementById('travel_date');
    if (travelDateInput) {
        const today = new Date().toISOString().split('T')[0];
        travelDateInput.min = today;
        
        travelDateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const maxDate = new Date();
            maxDate.setDate(maxDate.getDate() + 120); // 120 days advance booking
            
            if (selectedDate > maxDate) {
                alert('Bookings are only allowed up to 120 days in advance');
                this.value = maxDate.toISOString().split('T')[0];
            }
            
            checkTatkalEligibility();
        });
    }
}

function initializeSeatSelection() {
    const seatMap = document.querySelector('.seat-map');
    if (!seatMap) return;
    
    const seats = seatMap.querySelectorAll('.seat');
    const selectedSeatsContainer = document.querySelector('.selected-seats');
    let selectedSeats = [];
    
    seats.forEach(seat => {
        if (!seat.classList.contains('occupied')) {
            seat.addEventListener('click', function() {
                const seatNumber = this.dataset.seatNumber;
                const passengerCount = parseInt(document.getElementById('passenger_count')?.value || 1);
                
                if (this.classList.contains('selected')) {
                    // Deselect seat
                    this.classList.remove('selected');
                    selectedSeats = selectedSeats.filter(s => s !== seatNumber);
                } else if (selectedSeats.length < passengerCount) {
                    // Select seat
                    this.classList.add('selected');
                    selectedSeats.push(seatNumber);
                } else {
                    alert(`You can only select ${passengerCount} seat(s)`);
                }
                
                updateSelectedSeatsDisplay();
                calculateFare();
            });
        }
    });
    
    function updateSelectedSeatsDisplay() {
        if (selectedSeatsContainer) {
            if (selectedSeats.length > 0) {
                selectedSeatsContainer.innerHTML = `
                    <h4>Selected Seats:</h4>
                    <div class="selected-seat-list">
                        ${selectedSeats.map(seat => `<span class="seat-tag">${seat}</span>`).join('')}
                    </div>
                `;
            } else {
                selectedSeatsContainer.innerHTML = '<p>No seats selected</p>';
            }
        }
        
        // Update hidden input for form submission
        const hiddenInput = document.getElementById('selected_seats');
        if (hiddenInput) {
            hiddenInput.value = selectedSeats.join(',');
        }
    }
}

function initializePassengerForms() {
    updatePassengerForms(1); // Initialize with 1 passenger
}

function updatePassengerForms(count) {
    const passengerFormsContainer = document.querySelector('.passenger-forms');
    if (!passengerFormsContainer) return;
    
    passengerFormsContainer.innerHTML = '';
    
    for (let i = 1; i <= count; i++) {
        const passengerForm = createPassengerForm(i);
        passengerFormsContainer.appendChild(passengerForm);
    }
}

function createPassengerForm(passengerNumber) {
    const formDiv = document.createElement('div');
    formDiv.className = 'passenger-form';
    formDiv.innerHTML = `
        <h4>Passenger ${passengerNumber}</h4>
        <div class="form-row">
            <div class="form-group">
                <label for="passenger_${passengerNumber}_name">Full Name *</label>
                <input type="text" id="passenger_${passengerNumber}_name" 
                       name="passengers[${passengerNumber}][name]" required>
            </div>
            <div class="form-group">
                <label for="passenger_${passengerNumber}_age">Age *</label>
                <input type="number" id="passenger_${passengerNumber}_age" 
                       name="passengers[${passengerNumber}][age]" min="1" max="120" required>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label for="passenger_${passengerNumber}_gender">Gender *</label>
                <select id="passenger_${passengerNumber}_gender" 
                        name="passengers[${passengerNumber}][gender]" required>
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label for="passenger_${passengerNumber}_berth">Berth Preference</label>
                <select id="passenger_${passengerNumber}_berth" 
                        name="passengers[${passengerNumber}][berth_preference]">
                    <option value="">No Preference</option>
                    <option value="Lower">Lower</option>
                    <option value="Middle">Middle</option>
                    <option value="Upper">Upper</option>
                    <option value="Side Lower">Side Lower</option>
                    <option value="Side Upper">Side Upper</option>
                </select>
            </div>
        </div>
    `;
    
    // Add validation to passenger inputs
    const inputs = formDiv.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validatePassengerField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
    
    return formDiv;
}

function initializeFareCalculation() {
    // Initialize fare calculation
    calculateFare();
    
    // Recalculate fare when relevant fields change
    const fareInputs = document.querySelectorAll('#passenger_count, #class_type, #booking_type');
    fareInputs.forEach(input => {
        input.addEventListener('change', calculateFare);
    });
}

function calculateFare() {
    const passengerCount = parseInt(document.getElementById('passenger_count')?.value || 1);
    const classType = document.getElementById('class_type')?.value || 'SL';
    const bookingType = document.getElementById('booking_type')?.value || 'general';
    const baseFare = parseFloat(document.querySelector('[data-base-fare]')?.dataset.baseFare || 100);
    
    // Class multipliers
    const classMultipliers = {
        'SL': 1.0,    // Sleeper
        '3A': 2.5,    // AC 3 Tier
        '2A': 3.5,    // AC 2 Tier
        '1A': 6.0     // AC First Class
    };
    
    // Booking type charges
    const bookingCharges = {
        'general': 0,
        'tatkal': 100,
        'premium_tatkal': 200
    };
    
    let totalFare = baseFare * classMultipliers[classType] * passengerCount;
    totalFare += bookingCharges[bookingType];
    
    // Service charges and taxes
    const serviceCharge = 15;
    const gst = totalFare * 0.05; // 5% GST
    
    const finalAmount = totalFare + serviceCharge + gst;
    
    // Update fare breakdown display
    updateFareDisplay({
        baseFare: baseFare * classMultipliers[classType] * passengerCount,
        bookingCharge: bookingCharges[bookingType],
        serviceCharge: serviceCharge,
        gst: gst,
        total: finalAmount
    });
}

function updateFareDisplay(fareBreakdown) {
    const fareContainer = document.querySelector('.fare-breakdown');
    if (!fareContainer) return;
    
    fareContainer.innerHTML = `
        <h4>Fare Breakdown</h4>
        <div class="fare-item">
            <span>Base Fare:</span>
            <span>₹${fareBreakdown.baseFare.toFixed(2)}</span>
        </div>
        ${fareBreakdown.bookingCharge > 0 ? `
            <div class="fare-item">
                <span>Booking Charges:</span>
                <span>₹${fareBreakdown.bookingCharge.toFixed(2)}</span>
            </div>
        ` : ''}
        <div class="fare-item">
            <span>Service Charge:</span>
            <span>₹${fareBreakdown.serviceCharge.toFixed(2)}</span>
        </div>
        <div class="fare-item">
            <span>GST (5%):</span>
            <span>₹${fareBreakdown.gst.toFixed(2)}</span>
        </div>
        <div class="fare-total">
            <span>Total Amount:</span>
            <span>₹${fareBreakdown.total.toFixed(2)}</span>
        </div>
    `;
    
    // Update hidden input for form submission
    const totalAmountInput = document.getElementById('total_amount');
    if (totalAmountInput) {
        totalAmountInput.value = fareBreakdown.total.toFixed(2);
    }
}

function checkTatkalEligibility() {
    const travelDateInput = document.getElementById('travel_date');
    const bookingTypeSelect = document.getElementById('booking_type');
    
    if (!travelDateInput || !bookingTypeSelect) return;
    
    const travelDate = new Date(travelDateInput.value);
    const today = new Date();
    const daysDifference = Math.ceil((travelDate - today) / (1000 * 60 * 60 * 24));
    
    const tatkalOptions = bookingTypeSelect.querySelectorAll('option[value="tatkal"], option[value="premium_tatkal"]');
    
    // Tatkal booking is available 1 day before travel for AC classes and same day for non-AC
    if (daysDifference <= 1) {
        tatkalOptions.forEach(option => option.disabled = false);
        
        // Show tatkal info
        showTatkalInfo();
    } else {
        tatkalOptions.forEach(option => {
            option.disabled = true;
            if (option.selected) {
                bookingTypeSelect.value = 'general';
                calculateFare();
            }
        });
        
        hideTatkalInfo();
    }
}

function showTatkalInfo() {
    let tatkalInfo = document.querySelector('.tatkal-info');
    if (!tatkalInfo) {
        tatkalInfo = document.createElement('div');
        tatkalInfo.className = 'tatkal-info alert alert-info';
        tatkalInfo.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <strong>Tatkal Booking Available:</strong> 
            You can now book Tatkal tickets for this travel date. 
            Additional charges apply.
        `;
        
        const bookingTypeGroup = document.getElementById('booking_type').closest('.form-group');
        bookingTypeGroup.appendChild(tatkalInfo);
    }
}

function hideTatkalInfo() {
    const tatkalInfo = document.querySelector('.tatkal-info');
    if (tatkalInfo) {
        tatkalInfo.remove();
    }
}

function validatePassengerField(input) {
    const value = input.value.trim();
    const fieldName = input.name;
    
    if (input.hasAttribute('required') && !value) {
        showFieldError(input, 'This field is required');
        return false;
    }
    
    if (fieldName.includes('name')) {
        if (value.length < 2) {
            showFieldError(input, 'Name must be at least 2 characters');
            return false;
        }
        
        if (!/^[a-zA-Z\s]+$/.test(value)) {
            showFieldError(input, 'Name can only contain letters and spaces');
            return false;
        }
    }
    
    if (fieldName.includes('age')) {
        const age = parseInt(value);
        if (age < 1 || age > 120) {
            showFieldError(input, 'Please enter a valid age (1-120)');
            return false;
        }
        
        // Show senior citizen discount info
        if (age >= 60) {
            showFieldInfo(input, 'Senior citizen discount applicable');
        }
    }
    
    clearFieldError(input);
    return true;
}

function showFieldError(input, message) {
    clearFieldError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    errorDiv.style.cssText = `
        color: var(--danger-color);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    input.style.borderColor = 'var(--danger-color)';
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(errorDiv);
    }
}

function showFieldInfo(input, message) {
    const existingInfo = input.closest('.form-group').querySelector('.form-info');
    if (existingInfo) return;
    
    const infoDiv = document.createElement('div');
    infoDiv.className = 'form-info';
    infoDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    infoDiv.style.cssText = `
        color: var(--info-color);
        font-size: 0.85rem;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.appendChild(infoDiv);
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const existingError = formGroup.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
    }
    
    input.style.borderColor = '';
}

// Add CSS for seat selection and fare breakdown
const style = document.createElement('style');
style.textContent = `
    .seat {
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .seat.selected {
        background: var(--accent-color) !important;
        color: white;
        transform: scale(1.1);
    }
    
    .seat.occupied {
        background: var(--danger-color) !important;
        color: white;
        cursor: not-allowed;
    }
    
    .seat-tag {
        background: var(--accent-color);
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
    }
    
    .fare-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .fare-total {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        font-weight: bold;
        font-size: 1.1rem;
        border-top: 2px solid var(--accent-color);
        margin-top: 0.5rem;
    }
    
    .passenger-form {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .passenger-form h4 {
        margin-bottom: 1rem;
        color: var(--accent-color);
    }
`;

if (!document.querySelector('#booking-styles')) {
    style.id = 'booking-styles';
    document.head.appendChild(style);
}