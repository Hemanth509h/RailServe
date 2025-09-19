// Admin Analytics page specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeDateRangeSelector();
    initializeExportFunctionality();
    initializeMetricsRefresh();
});

let charts = {}; // Store chart instances for cleanup

function initializeCharts() {
    // Initialize all charts
    initializeRevenueChart();
    initializeBookingStatusChart();
    initializePopularTrainsChart();
    initializeBookingTrendsChart();
}

function initializeRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;
    
    // Get data from the template or API
    const revenueData = getRevenueData();
    
    charts.revenue = new Chart(ctx, {
        type: 'line',
        data: {
            labels: revenueData.labels,
            datasets: [{
                label: 'Revenue (₹)',
                data: revenueData.values,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: ₹' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function initializeBookingStatusChart() {
    const ctx = document.getElementById('bookingStatusChart');
    if (!ctx) return;
    
    const statusData = getBookingStatusData();
    
    charts.bookingStatus = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: statusData.labels,
            datasets: [{
                data: statusData.values,
                backgroundColor: [
                    '#10B981', // Confirmed - Green
                    '#F59E0B', // Waitlisted - Yellow
                    '#EF4444', // Cancelled - Red
                    '#6B7280'  // Pending - Gray
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

function initializePopularTrainsChart() {
    const ctx = document.getElementById('popularTrainsChart');
    if (!ctx) return;
    
    const trainsData = getPopularTrainsData();
    
    charts.popularTrains = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trainsData.labels,
            datasets: [{
                label: 'Bookings',
                data: trainsData.values,
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: 'rgb(59, 130, 246)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function initializeBookingTrendsChart() {
    const ctx = document.getElementById('bookingTrendsChart');
    if (!ctx) return;
    
    const trendsData = getBookingTrendsData();
    
    charts.bookingTrends = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendsData.labels,
            datasets: [{
                label: 'Daily Bookings',
                data: trendsData.values,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function initializeDateRangeSelector() {
    const dateButtons = document.querySelectorAll('.date-btn');
    const customDateInputs = document.querySelectorAll('.custom-date-range input');
    
    dateButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            dateButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const range = this.dataset.range;
            updateChartsForDateRange(range);
        });
    });
    
    // Custom date range
    customDateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            if (startDate && endDate) {
                // Deactivate preset buttons
                dateButtons.forEach(btn => btn.classList.remove('active'));
                updateChartsForCustomRange(startDate, endDate);
            }
        });
    });
}

function initializeExportFunctionality() {
    const exportButtons = document.querySelectorAll('.export-btn');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const format = this.dataset.format;
            const type = this.dataset.type || 'analytics';
            
            exportData(format, type);
        });
    });
}

function initializeMetricsRefresh() {
    const refreshButton = document.querySelector('.refresh-metrics');
    if (!refreshButton) return;
    
    refreshButton.addEventListener('click', function(e) {
        e.preventDefault();
        refreshAllMetrics();
    });
    
    // Auto-refresh every 5 minutes
    setInterval(refreshAllMetrics, 5 * 60 * 1000);
}

function updateChartsForDateRange(range) {
    showLoadingSpinner();
    
    fetch(`/admin/analytics_data?range=${range}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAllCharts(data);
                updateMetricsDisplay(data.metrics);
            } else {
                throw new Error(data.error || 'Failed to load data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Failed to update charts');
        })
        .finally(() => {
            hideLoadingSpinner();
        });
}

function updateChartsForCustomRange(startDate, endDate) {
    showLoadingSpinner();
    
    fetch(`/admin/analytics_data?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAllCharts(data);
                updateMetricsDisplay(data.metrics);
            } else {
                throw new Error(data.error || 'Failed to load data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Failed to update charts');
        })
        .finally(() => {
            hideLoadingSpinner();
        });
}

function updateAllCharts(data) {
    // Update revenue chart
    if (charts.revenue && data.revenue) {
        charts.revenue.data.labels = data.revenue.labels;
        charts.revenue.data.datasets[0].data = data.revenue.values;
        charts.revenue.update('active');
    }
    
    // Update booking status chart
    if (charts.bookingStatus && data.bookingStatus) {
        charts.bookingStatus.data.labels = data.bookingStatus.labels;
        charts.bookingStatus.data.datasets[0].data = data.bookingStatus.values;
        charts.bookingStatus.update('active');
    }
    
    // Update popular trains chart
    if (charts.popularTrains && data.popularTrains) {
        charts.popularTrains.data.labels = data.popularTrains.labels;
        charts.popularTrains.data.datasets[0].data = data.popularTrains.values;
        charts.popularTrains.update('active');
    }
    
    // Update booking trends chart
    if (charts.bookingTrends && data.bookingTrends) {
        charts.bookingTrends.data.labels = data.bookingTrends.labels;
        charts.bookingTrends.data.datasets[0].data = data.bookingTrends.values;
        charts.bookingTrends.update('active');
    }
}

function updateMetricsDisplay(metrics) {
    if (!metrics) return;
    
    Object.keys(metrics).forEach(key => {
        const metricElement = document.querySelector(`[data-metric="${key}"]`);
        if (metricElement) {
            const valueElement = metricElement.querySelector('.metric-value');
            const changeElement = metricElement.querySelector('.metric-change');
            
            if (valueElement) {
                animateMetricValue(valueElement, metrics[key].value);
            }
            
            if (changeElement && metrics[key].change !== undefined) {
                updateMetricChange(changeElement, metrics[key].change);
            }
        }
    });
}

function animateMetricValue(element, newValue) {
    const currentValue = parseFloat(element.textContent.replace(/[^\d.-]/g, '')) || 0;
    
    if (element.textContent.includes('₹')) {
        animateCounter(element, currentValue, newValue, (val) => `₹${val.toLocaleString()}`);
    } else if (element.textContent.includes('%')) {
        animateCounter(element, currentValue, newValue, (val) => `${val.toFixed(1)}%`);
    } else {
        animateCounter(element, currentValue, newValue, (val) => Math.round(val).toLocaleString());
    }
}

function animateCounter(element, start, end, formatter) {
    const duration = 1000;
    const increment = (end - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        element.textContent = formatter(current);
    }, 16);
}

function updateMetricChange(element, change) {
    element.className = 'metric-change';
    
    if (change > 0) {
        element.classList.add('positive');
        element.innerHTML = `<i class="fas fa-arrow-up"></i> +${change.toFixed(1)}%`;
    } else if (change < 0) {
        element.classList.add('negative');
        element.innerHTML = `<i class="fas fa-arrow-down"></i> ${change.toFixed(1)}%`;
    } else {
        element.classList.add('neutral');
        element.innerHTML = `<i class="fas fa-minus"></i> 0%`;
    }
}

function exportData(format, type) {
    const exportButton = document.querySelector(`[data-format="${format}"][data-type="${type}"]`);
    
    if (exportButton) {
        exportButton.disabled = true;
        exportButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
    }
    
    // Get current date range
    const activeButton = document.querySelector('.date-btn.active');
    const range = activeButton ? activeButton.dataset.range : '30';
    
    // Create download link
    const link = document.createElement('a');
    link.href = `/admin/export_analytics?format=${format}&type=${type}&range=${range}`;
    link.download = `analytics_${type}_${new Date().toISOString().split('T')[0]}.${format}`;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    if (exportButton) {
        setTimeout(() => {
            exportButton.disabled = false;
            exportButton.innerHTML = `<i class="fas fa-download"></i> Export ${format.toUpperCase()}`;
        }, 2000);
    }
    
    showSuccessMessage(`${format.toUpperCase()} export started`);
}

function refreshAllMetrics() {
    const refreshButton = document.querySelector('.refresh-metrics');
    
    if (refreshButton) {
        refreshButton.disabled = true;
        refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    }
    
    // Get current date range
    const activeButton = document.querySelector('.date-btn.active');
    const range = activeButton ? activeButton.dataset.range : '30';
    
    fetch(`/admin/analytics_data?range=${range}&refresh=true`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateAllCharts(data);
                updateMetricsDisplay(data.metrics);
                showSuccessMessage('Analytics refreshed successfully');
            } else {
                throw new Error(data.error || 'Failed to refresh data');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorMessage('Failed to refresh analytics');
        })
        .finally(() => {
            if (refreshButton) {
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            }
        });
}

// Data getter functions (these would typically get data from the template or API)
function getRevenueData() {
    // This would typically come from the template or an API call
    const labels = [];
    const values = [];
    
    // Generate sample data for the last 30 days
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        values.push(Math.floor(Math.random() * 50000) + 10000);
    }
    
    return { labels, values };
}

function getBookingStatusData() {
    return {
        labels: ['Confirmed', 'Waitlisted', 'Cancelled', 'Pending'],
        values: [150, 45, 25, 10]
    };
}

function getPopularTrainsData() {
    return {
        labels: ['12345 - Express', '54321 - Superfast', '98765 - Mail', '13579 - Local', '24680 - Passenger'],
        values: [85, 72, 58, 45, 32]
    };
}

function getBookingTrendsData() {
    const labels = [];
    const values = [];
    
    // Generate sample data for the last 7 days
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        values.push(Math.floor(Math.random() * 50) + 20);
    }
    
    return { labels, values };
}

function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'analytics-loading';
    spinner.innerHTML = `
        <div class="loading-overlay">
            <div class="spinner">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Updating analytics...</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(spinner);
}

function hideLoadingSpinner() {
    const spinner = document.querySelector('.analytics-loading');
    if (spinner) {
        spinner.remove();
    }
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

// Cleanup function
window.addEventListener('beforeunload', function() {
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
});

// Add CSS for loading spinner
const style = document.createElement('style');
style.textContent = `
    .analytics-loading {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .loading-overlay {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        box-shadow: var(--card-shadow);
    }
    
    .spinner i {
        font-size: 2rem;
        color: var(--accent-color);
        margin-bottom: 1rem;
    }
    
    .spinner p {
        color: var(--text-primary);
        margin: 0;
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
`;

if (!document.querySelector('#admin-analytics-styles')) {
    style.id = 'admin-analytics-styles';
    document.head.appendChild(style);
}