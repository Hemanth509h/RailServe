// Admin Dashboard specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboardWidgets();
    initializeStatsRefresh();
    initializeRecentActivity();
    initializeQuickActions();
});

function initializeDashboardWidgets() {
    // Animate stats cards on load
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100);
        }, index * 100);
    });
    
    // Add hover effects to admin cards
    const adminCards = document.querySelectorAll('.admin-card');
    adminCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = 'var(--card-hover-shadow)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'var(--card-shadow)';
        });
    });
}

function initializeStatsRefresh() {
    const refreshButton = document.querySelector('.refresh-stats');
    if (!refreshButton) return;
    
    refreshButton.addEventListener('click', function(e) {
        e.preventDefault();
        refreshDashboardStats();
    });
    
    // Auto-refresh stats every 5 minutes
    setInterval(refreshDashboardStats, 5 * 60 * 1000);
}

function refreshDashboardStats() {
    const refreshButton = document.querySelector('.refresh-stats');
    if (refreshButton) {
        refreshButton.disabled = true;
        refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    }
    
    fetch('/admin/dashboard_stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateStatsDisplay(data.stats);
                showSuccessMessage('Dashboard stats updated');
            } else {
                throw new Error(data.error || 'Failed to refresh stats');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Failed to refresh stats');
        })
        .finally(() => {
            if (refreshButton) {
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            }
        });
}

function updateStatsDisplay(stats) {
    // Update stat cards with animation
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        const statType = card.dataset.statType;
        const statNumber = card.querySelector('.stat-info h3');
        
        if (statNumber && stats[statType] !== undefined) {
            const currentValue = parseInt(statNumber.textContent.replace(/[^\d]/g, '')) || 0;
            const newValue = stats[statType];
            
            animateCounter(statNumber, currentValue, newValue);
        }
    });
}

function animateCounter(element, start, end) {
    const duration = 1000; // 1 second
    const increment = (end - start) / (duration / 16); // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        // Format the number based on the original format
        if (element.textContent.includes('₹')) {
            element.textContent = `₹${Math.round(current).toLocaleString()}`;
        } else {
            element.textContent = Math.round(current).toLocaleString();
        }
    }, 16);
}

function initializeRecentActivity() {
    // Load recent activity data
    loadRecentActivity();
    
    // Auto-refresh activity every 2 minutes
    setInterval(loadRecentActivity, 2 * 60 * 1000);
}

function loadRecentActivity() {
    const activityContainer = document.querySelector('.activity-list');
    if (!activityContainer) return;
    
    fetch('/admin/recent_activity')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateActivityDisplay(data.activities);
            }
        })
        .catch(error => {
            console.error('Error loading recent activity:', error);
        });
}

function updateActivityDisplay(activities) {
    const activityContainer = document.querySelector('.activity-list');
    if (!activityContainer) return;
    
    activityContainer.innerHTML = '';
    
    activities.forEach(activity => {
        const activityItem = document.createElement('li');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon">
                <i class="fas ${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-time">${formatTimeAgo(activity.timestamp)}</div>
            </div>
        `;
        
        activityContainer.appendChild(activityItem);
    });
}

function getActivityIcon(activityType) {
    const icons = {
        'booking': 'fa-ticket-alt',
        'user_registration': 'fa-user-plus',
        'payment': 'fa-credit-card',
        'cancellation': 'fa-times-circle',
        'system': 'fa-cog',
        'error': 'fa-exclamation-triangle'
    };
    
    return icons[activityType] || 'fa-circle';
}

function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);
    
    if (diffInSeconds < 60) {
        return 'Just now';
    } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
}

function initializeQuickActions() {
    // Quick add train functionality
    const quickAddTrain = document.querySelector('.quick-add-train');
    if (quickAddTrain) {
        quickAddTrain.addEventListener('click', function(e) {
            e.preventDefault();
            showQuickAddTrainModal();
        });
    }
    
    // Quick add station functionality
    const quickAddStation = document.querySelector('.quick-add-station');
    if (quickAddStation) {
        quickAddStation.addEventListener('click', function(e) {
            e.preventDefault();
            showQuickAddStationModal();
        });
    }
    
    // System status checks
    const systemStatusItems = document.querySelectorAll('.status-item');
    systemStatusItems.forEach(item => {
        item.addEventListener('click', function() {
            const service = this.dataset.service;
            checkServiceStatus(service);
        });
    });
}

function showQuickAddTrainModal() {
    const modal = document.createElement('div');
    modal.className = 'quick-action-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Quick Add Train</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <form class="quick-train-form">
                    <div class="form-group">
                        <label for="quick_train_number">Train Number</label>
                        <input type="text" id="quick_train_number" name="number" required>
                    </div>
                    <div class="form-group">
                        <label for="quick_train_name">Train Name</label>
                        <input type="text" id="quick_train_name" name="name" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="quick_total_seats">Total Seats</label>
                            <input type="number" id="quick_total_seats" name="total_seats" min="1" required>
                        </div>
                        <div class="form-group">
                            <label for="quick_fare_per_km">Fare per KM (₹)</label>
                            <input type="number" id="quick_fare_per_km" name="fare_per_km" step="0.01" min="0" required>
                        </div>
                    </div>
                    <div class="modal-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i> Add Train
                        </button>
                        <button type="button" class="btn btn-secondary modal-cancel">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'block';
    
    // Form submission
    const form = modal.querySelector('.quick-train-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitQuickTrain(this, modal);
    });
    
    // Close modal functionality
    setupModalCloseHandlers(modal);
    
    // Focus on first input
    modal.querySelector('#quick_train_number').focus();
}

function showQuickAddStationModal() {
    const modal = document.createElement('div');
    modal.className = 'quick-action-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Quick Add Station</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <form class="quick-station-form">
                    <div class="form-group">
                        <label for="quick_station_name">Station Name</label>
                        <input type="text" id="quick_station_name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="quick_station_code">Station Code</label>
                        <input type="text" id="quick_station_code" name="code" maxlength="10" style="text-transform: uppercase;" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="quick_station_city">City</label>
                            <input type="text" id="quick_station_city" name="city" required>
                        </div>
                        <div class="form-group">
                            <label for="quick_station_state">State</label>
                            <input type="text" id="quick_station_state" name="state" required>
                        </div>
                    </div>
                    <div class="modal-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-plus"></i> Add Station
                        </button>
                        <button type="button" class="btn btn-secondary modal-cancel">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'block';
    
    // Form submission
    const form = modal.querySelector('.quick-station-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitQuickStation(this, modal);
    });
    
    // Close modal functionality
    setupModalCloseHandlers(modal);
    
    // Focus on first input
    modal.querySelector('#quick_station_name').focus();
}

function submitQuickTrain(form, modal) {
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    
    const formData = new FormData(form);
    
    fetch('/admin/quick_add_train', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Train added successfully');
            modal.remove();
            refreshDashboardStats();
        } else {
            showErrorMessage(data.error || 'Failed to add train');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus"></i> Add Train';
    });
}

function submitQuickStation(form, modal) {
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    
    const formData = new FormData(form);
    
    fetch('/admin/quick_add_station', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Station added successfully');
            modal.remove();
            refreshDashboardStats();
        } else {
            showErrorMessage(data.error || 'Failed to add station');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-plus"></i> Add Station';
    });
}

function checkServiceStatus(service) {
    fetch(`/admin/service_status/${service}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateServiceStatusDisplay(service, data.status);
            }
        })
        .catch(error => {
            console.error('Error checking service status:', error);
        });
}

function updateServiceStatusDisplay(service, status) {
    const statusItem = document.querySelector(`[data-service="${service}"]`);
    if (!statusItem) return;
    
    const statusIcon = statusItem.querySelector('.status-icon');
    const statusText = statusItem.querySelector('.status-text');
    
    statusIcon.className = 'status-icon';
    
    switch (status) {
        case 'online':
            statusIcon.classList.add('online');
            statusText.textContent = `${service} Service - Online`;
            break;
        case 'warning':
            statusIcon.classList.add('warning');
            statusText.textContent = `${service} Service - Warning`;
            break;
        case 'offline':
            statusIcon.classList.add('offline');
            statusText.textContent = `${service} Service - Offline`;
            break;
    }
}

function setupModalCloseHandlers(modal) {
    const closeBtn = modal.querySelector('.modal-close');
    const cancelBtn = modal.querySelector('.modal-cancel');
    
    const closeModal = () => modal.remove();
    
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    const existingMessages = document.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `temp-message alert alert-${type === 'success' ? 'success' : 'danger'}`;
    messageDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
    `;
    
    const container = document.querySelector('.admin-container');
    if (container) {
        container.insertBefore(messageDiv, container.firstChild);
    }
    
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}

// Add CSS for modals and animations
const style = document.createElement('style');
style.textContent = `
    .quick-action-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: none;
    }
    
    .quick-action-modal .modal-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--bg-secondary);
        border-radius: 12px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
    }
    
    .quick-action-modal .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .quick-action-modal .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--text-secondary);
    }
    
    .quick-action-modal .modal-body {
        padding: 1.5rem;
    }
    
    .quick-action-modal .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    .quick-action-modal .form-group {
        margin-bottom: 1rem;
    }
    
    .quick-action-modal label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .quick-action-modal input,
    .quick-action-modal select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .modal-actions {
        display: flex;
        gap: 1rem;
        justify-content: flex-end;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-color);
    }
    
    .temp-message {
        position: sticky;
        top: 0;
        z-index: 100;
        animation: slideDown 0.3s ease-out;
        margin-bottom: 1rem;
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
    
    .status-item {
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .status-item:hover {
        background: var(--bg-secondary);
    }
`;

if (!document.querySelector('#admin-dashboard-styles')) {
    style.id = 'admin-dashboard-styles';
    document.head.appendChild(style);
}