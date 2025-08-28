// RailServe Analytics Charts - Chart.js Implementation

// Chart.js Configuration and Initialization
let charts = {};

// Initialize all analytics charts
function initializeAnalyticsCharts(revenueData, bookingStatusData, popularTrainsData, bookingTrendsData) {
    // Initialize Revenue Chart
    initializeRevenueChart(revenueData);
    
    // Initialize Booking Status Chart
    initializeBookingStatusChart(bookingStatusData);
    
    // Initialize Popular Trains Chart
    initializePopularTrainsChart(popularTrainsData);
    
    // Initialize Booking Trends Chart
    initializeBookingTrendsChart(bookingTrendsData);
}

// Revenue Chart (Line Chart)
function initializeRevenueChart(data) {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;
    
    charts.revenue = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Daily Revenue Trends',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Revenue: ₹' + context.parsed.y.toLocaleString('en-IN', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Revenue (₹)',
                        font: {
                            weight: 'bold'
                        }
                    },
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6,
                    backgroundColor: '#3b82f6',
                    borderColor: '#ffffff',
                    borderWidth: 2
                },
                line: {
                    tension: 0.4,
                    borderWidth: 3,
                    fill: true
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Booking Status Chart (Doughnut Chart)
function initializeBookingStatusChart(data) {
    const ctx = document.getElementById('bookingStatusChart');
    if (!ctx) return;
    
    charts.bookingStatus = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Booking Status Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed * 100) / total).toFixed(1);
                            return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                        }
                    }
                }
            },
            cutout: '50%',
            elements: {
                arc: {
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }
            }
        }
    });
}

// Popular Trains Chart (Horizontal Bar Chart)
function initializePopularTrainsChart(data) {
    const ctx = document.getElementById('popularTrainsChart');
    if (!ctx) return;
    
    charts.popularTrains = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                title: {
                    display: true,
                    text: 'Most Popular Trains',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#8b5cf6',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Bookings: ' + context.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Number of Bookings',
                        font: {
                            weight: 'bold'
                        }
                    },
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Train Name',
                        font: {
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            },
            elements: {
                bar: {
                    borderRadius: 4,
                    borderSkipped: false
                }
            }
        }
    });
}

// Booking Trends Chart (Area Chart)
function initializeBookingTrendsChart(data) {
    const ctx = document.getElementById('bookingTrendsChart');
    if (!ctx) return;
    
    charts.bookingTrends = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Booking Trends (Last 30 Days)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: '#059669',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Bookings: ' + context.parsed.y;
                        }
                    }
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Number of Bookings',
                        font: {
                            weight: 'bold'
                        }
                    },
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 5,
                    backgroundColor: '#059669',
                    borderColor: '#ffffff',
                    borderWidth: 2
                },
                line: {
                    tension: 0.4,
                    borderWidth: 3,
                    fill: true
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

// Utility function to update chart data
function updateChart(chartName, newData) {
    if (charts[chartName]) {
        charts[chartName].data = newData;
        charts[chartName].update('active');
    }
}

// Utility function to export chart as image
function exportChart(chartId) {
    const chart = charts[chartId.replace('Chart', '')];
    if (chart) {
        const canvas = chart.canvas;
        const link = document.createElement('a');
        link.download = chartId + '-export.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }
}

// Responsive chart resize handler
function handleChartResize() {
    Object.values(charts).forEach(chart => {
        chart.resize();
    });
}

// Initialize resize listener
window.addEventListener('resize', debounce(handleChartResize, 300));

// Chart color palettes
const colorPalettes = {
    primary: ['#3b82f6', '#1d4ed8', '#1e40af', '#1e3a8a'],
    success: ['#10b981', '#059669', '#047857', '#065f46'],
    warning: ['#f59e0b', '#d97706', '#b45309', '#92400e'],
    danger: ['#ef4444', '#dc2626', '#b91c1c', '#991b1b'],
    info: ['#06b6d4', '#0891b2', '#0e7490', '#155e75'],
    purple: ['#8b5cf6', '#7c3aed', '#6d28d9', '#5b21b6'],
    mixed: ['#10b981', '#f59e0b', '#ef4444', '#6b7280', '#3b82f6', '#8b5cf6']
};

// Function to get color palette
function getColorPalette(name = 'mixed', count = null) {
    const palette = colorPalettes[name] || colorPalettes.mixed;
    return count ? palette.slice(0, count) : palette;
}

// Chart animation configurations
const animationConfigs = {
    default: {
        duration: 2000,
        easing: 'easeInOutQuart'
    },
    fast: {
        duration: 1000,
        easing: 'easeOutQuart'
    },
    slow: {
        duration: 3000,
        easing: 'easeInOutQuint'
    }
};

// Function to create real-time chart updates
function createRealTimeChart(chartName, updateInterval = 30000) {
    setInterval(() => {
        // This would typically fetch new data from the server
        // For now, we'll just update the timestamp
        const chart = charts[chartName];
        if (chart && chart.data.labels) {
            const now = new Date();
            const timeLabel = now.toLocaleTimeString('en-IN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            
            // Add new data point (this would come from server in real implementation)
            chart.data.labels.push(timeLabel);
            
            // Remove old data if too many points
            if (chart.data.labels.length > 10) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => {
                    dataset.data.shift();
                });
            }
            
            chart.update('none');
        }
    }, updateInterval);
}

// Function to create chart with loading state
function createChartWithLoading(canvasId, chartConfig) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    
    const container = canvas.parentElement;
    
    // Show loading state
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chart-loading';
    loadingDiv.innerHTML = `
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 300px;
            color: #6b7280;
        ">
            <div style="
                width: 40px;
                height: 40px;
                border: 4px solid #e5e7eb;
                border-top: 4px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 1rem;
            "></div>
            <p>Loading chart data...</p>
        </div>
    `;
    
    container.appendChild(loadingDiv);
    canvas.style.display = 'none';
    
    // Simulate loading delay (in real app, this would be actual data loading)
    setTimeout(() => {
        loadingDiv.remove();
        canvas.style.display = 'block';
        
        // Create the actual chart
        return new Chart(canvas, chartConfig);
    }, 1000);
}

// Function to handle chart errors
function handleChartError(chartName, error) {
    console.error(`Error initializing ${chartName} chart:`, error);
    
    const canvas = document.getElementById(chartName + 'Chart');
    if (canvas) {
        const container = canvas.parentElement;
        container.innerHTML = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 300px;
                color: #ef4444;
                text-align: center;
                padding: 2rem;
            ">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                <h4>Chart Loading Error</h4>
                <p>Unable to load ${chartName} chart. Please refresh the page.</p>
                <button onclick="location.reload()" style="
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 0.375rem;
                    margin-top: 1rem;
                    cursor: pointer;
                ">Refresh Page</button>
            </div>
        `;
    }
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.ChartManager = {
    initializeAnalyticsCharts,
    updateChart,
    exportChart,
    handleChartResize,
    getColorPalette,
    createRealTimeChart,
    createChartWithLoading,
    handleChartError
};

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add Chart.js error handling
    Chart.defaults.plugins.tooltip.enabled = true;
    Chart.defaults.animation = animationConfigs.default;
    
    // Set global font family
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    
    console.log('Chart.js manager initialized');
});
