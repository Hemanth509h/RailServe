// Booking history page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeBookingFilters();
    initializeBookingActions();
    initializePaginationControls();
    initializeSearchFunctionality();
});

function initializeBookingFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const bookingItems = document.querySelectorAll('.booking-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active filter button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const filterType = this.dataset.filter;
            
            // Filter booking items
            bookingItems.forEach(item => {
                const bookingStatus = item.dataset.status;
                
                if (filterType === 'all' || bookingStatus === filterType) {
                    item.style.display = 'block';
                    // Add fade-in animation
                    item.style.opacity = '0';
                    setTimeout(() => {
                        item.style.opacity = '1';
                    }, 100);
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Update results count
            updateResultsCount();
        });
    });
}

function initializeBookingActions() {
    // Cancel booking buttons
    const cancelButtons = document.querySelectorAll('.cancel-booking');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId;
            const bookingPnr = this.dataset.bookingPnr;
            
            if (confirm(`Are you sure you want to cancel booking ${bookingPnr}?`)) {
                cancelBooking(bookingId);
            }
        });
    });
    
    // Download ticket buttons
    const downloadButtons = document.querySelectorAll('.download-ticket');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId;
            const bookingPnr = this.dataset.bookingPnr;
            
            downloadTicket(bookingId, bookingPnr);
        });
    });
    
    // View details buttons
    const detailsButtons = document.querySelectorAll('.view-details');
    detailsButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId;
            showBookingDetails(bookingId);
        });
    });
    
    // Print ticket buttons
    const printButtons = document.querySelectorAll('.print-ticket');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId;
            printTicket(bookingId);
        });
    });
}

function initializePaginationControls() {
    const paginationButtons = document.querySelectorAll('.pagination .page-link');
    
    paginationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.classList.contains('disabled')) {
                e.preventDefault();
                return;
            }
            
            // Add loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // The form submission will handle the actual pagination
        });
    });
}

function initializeSearchFunctionality() {
    const searchInput = document.getElementById('search_query');
    const searchForm = document.querySelector('.search-form');
    
    if (searchInput) {
        let searchTimeout;
        
        // Real-time search with debouncing
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim().toLowerCase();
            
            searchTimeout = setTimeout(() => {
                filterBookingsBySearch(query);
            }, 300);
        });
        
        // Clear search button
        const clearButton = document.querySelector('.clear-search');
        if (clearButton) {
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                filterBookingsBySearch('');
            });
        }
    }
}

function filterBookingsBySearch(query) {
    const bookingItems = document.querySelectorAll('.booking-item');
    let visibleCount = 0;
    
    bookingItems.forEach(item => {
        const pnr = item.querySelector('.booking-pnr')?.textContent.toLowerCase() || '';
        const route = item.querySelector('.booking-route')?.textContent.toLowerCase() || '';
        const trainName = item.querySelector('.train-name')?.textContent.toLowerCase() || '';
        const date = item.querySelector('.booking-date')?.textContent.toLowerCase() || '';
        
        const isVisible = !query || 
                         pnr.includes(query) || 
                         route.includes(query) || 
                         trainName.includes(query) || 
                         date.includes(query);
        
        if (isVisible) {
            item.style.display = 'block';
            visibleCount++;
        } else {
            item.style.display = 'none';
        }
    });
    
    // Show "no results" message if needed
    showNoResultsMessage(visibleCount === 0 && query.length > 0);
}

function showNoResultsMessage(show) {
    let noResultsMsg = document.querySelector('.no-results-message');
    
    if (show && !noResultsMsg) {
        noResultsMsg = document.createElement('div');
        noResultsMsg.className = 'no-results-message alert alert-info';
        noResultsMsg.innerHTML = `
            <i class="fas fa-search"></i>
            <strong>No bookings found</strong><br>
            Try adjusting your search terms or filters.
        `;
        
        const bookingsList = document.querySelector('.bookings-list');
        if (bookingsList) {
            bookingsList.appendChild(noResultsMsg);
        }
    } else if (!show && noResultsMsg) {
        noResultsMsg.remove();
    }
}

function cancelBooking(bookingId) {
    const button = document.querySelector(`[data-booking-id="${bookingId}"].cancel-booking`);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cancelling...';
    }
    
    // Make AJAX request to cancel booking
    fetch(`/cancel_booking/${bookingId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update booking status in the UI
            updateBookingStatus(bookingId, 'cancelled');
            showSuccessMessage('Booking cancelled successfully');
        } else {
            showErrorMessage(data.error || 'Failed to cancel booking');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred. Please try again.');
    })
    .finally(() => {
        if (button) {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-times"></i> Cancel';
        }
    });
}

function downloadTicket(bookingId, pnr) {
    const button = document.querySelector(`[data-booking-id="${bookingId}"].download-ticket`);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
    }
    
    // Create temporary download link
    const link = document.createElement('a');
    link.href = `/download_ticket/${bookingId}`;
    link.download = `ticket_${pnr}.pdf`;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    if (button) {
        setTimeout(() => {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-download"></i> Download';
        }, 2000);
    }
    
    showSuccessMessage('Ticket download started');
}

function printTicket(bookingId) {
    // Open ticket in new window for printing
    const printWindow = window.open(`/print_ticket/${bookingId}`, '_blank', 'width=800,height=600');
    
    if (printWindow) {
        printWindow.onload = function() {
            printWindow.print();
        };
    } else {
        showErrorMessage('Please allow popups to print tickets');
    }
}

function showBookingDetails(bookingId) {
    // Create modal for booking details
    const modal = createBookingDetailsModal(bookingId);
    document.body.appendChild(modal);
    
    // Show modal
    modal.style.display = 'block';
    
    // Load booking details via AJAX
    loadBookingDetails(bookingId, modal);
}

function createBookingDetailsModal(bookingId) {
    const modal = document.createElement('div');
    modal.className = 'booking-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Booking Details</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loading booking details...
                </div>
            </div>
        </div>
    `;
    
    // Close modal functionality
    const closeBtn = modal.querySelector('.modal-close');
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    // Close on ESC key
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            modal.remove();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
    
    return modal;
}

function loadBookingDetails(bookingId, modal) {
    fetch(`/booking_details/${bookingId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const modalBody = modal.querySelector('.modal-body');
                modalBody.innerHTML = generateBookingDetailsHTML(data.booking);
            } else {
                throw new Error(data.error || 'Failed to load booking details');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const modalBody = modal.querySelector('.modal-body');
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to load booking details. Please try again.
                </div>
            `;
        });
}

function generateBookingDetailsHTML(booking) {
    return `
        <div class="booking-details">
            <div class="detail-section">
                <h4>Journey Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>PNR:</label>
                        <span class="pnr-number">${booking.pnr}</span>
                    </div>
                    <div class="detail-item">
                        <label>Train:</label>
                        <span>${booking.train_number} - ${booking.train_name}</span>
                    </div>
                    <div class="detail-item">
                        <label>Route:</label>
                        <span>${booking.from_station} → ${booking.to_station}</span>
                    </div>
                    <div class="detail-item">
                        <label>Date:</label>
                        <span>${booking.travel_date}</span>
                    </div>
                    <div class="detail-item">
                        <label>Class:</label>
                        <span>${booking.class_type}</span>
                    </div>
                    <div class="detail-item">
                        <label>Status:</label>
                        <span class="status-badge ${booking.status}">${booking.status.toUpperCase()}</span>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Passenger Information</h4>
                <div class="passengers-list">
                    ${booking.passengers.map((passenger, index) => `
                        <div class="passenger-item">
                            <span class="passenger-number">${index + 1}.</span>
                            <span class="passenger-name">${passenger.name}</span>
                            <span class="passenger-age">${passenger.age}Y</span>
                            <span class="passenger-gender">${passenger.gender}</span>
                            ${passenger.seat_number ? `<span class="seat-number">Seat: ${passenger.seat_number}</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="detail-section">
                <h4>Payment Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Total Amount:</label>
                        <span class="amount">₹${booking.total_amount}</span>
                    </div>
                    <div class="detail-item">
                        <label>Payment Status:</label>
                        <span class="payment-status ${booking.payment_status}">${booking.payment_status}</span>
                    </div>
                    <div class="detail-item">
                        <label>Booking Date:</label>
                        <span>${booking.booking_date}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function updateBookingStatus(bookingId, newStatus) {
    const bookingItem = document.querySelector(`[data-booking-id="${bookingId}"]`).closest('.booking-item');
    if (bookingItem) {
        // Update status badge
        const statusBadge = bookingItem.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.className = `status-badge ${newStatus}`;
            statusBadge.textContent = newStatus.toUpperCase();
        }
        
        // Update data attribute
        bookingItem.dataset.status = newStatus;
        
        // Hide cancel button if cancelled
        if (newStatus === 'cancelled') {
            const cancelBtn = bookingItem.querySelector('.cancel-booking');
            if (cancelBtn) {
                cancelBtn.style.display = 'none';
            }
        }
    }
}

function updateResultsCount() {
    const visibleBookings = document.querySelectorAll('.booking-item[style*="block"], .booking-item:not([style*="none"])').length;
    const totalBookings = document.querySelectorAll('.booking-item').length;
    
    const resultsCount = document.querySelector('.results-count');
    if (resultsCount) {
        resultsCount.textContent = `Showing ${visibleBookings} of ${totalBookings} bookings`;
    }
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `temp-message alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
    `;
    
    // Insert at top of page
    const container = document.querySelector('.booking-history-container');
    if (container) {
        container.insertBefore(messageDiv, container.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
    
    // Scroll to message
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}

// Add CSS for modal and animations
const style = document.createElement('style');
style.textContent = `
    .booking-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: none;
    }
    
    .booking-modal .modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-secondary);
        border-radius: 12px;
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    .booking-modal .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .booking-modal .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-secondary);
    }
    
    .booking-modal .modal-body {
        padding: 1.5rem;
    }
    
    .detail-section {
        margin-bottom: 2rem;
    }
    
    .detail-section h4 {
        color: var(--accent-color);
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 0.5rem;
    }
    
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .detail-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .detail-item label {
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    .passenger-item {
        display: flex;
        gap: 1rem;
        padding: 0.75rem;
        background: var(--bg-primary);
        border-radius: 6px;
        margin-bottom: 0.5rem;
        align-items: center;
    }
    
    .passenger-number {
        font-weight: bold;
        color: var(--accent-color);
        min-width: 20px;
    }
    
    .temp-message {
        position: sticky;
        top: 0;
        z-index: 100;
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;

if (!document.querySelector('#booking-history-styles')) {
    style.id = 'booking-history-styles';
    document.head.appendChild(style);
}