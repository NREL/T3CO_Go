/**
 * T3CO Charts - Enhanced Chart.js Integration for T3CO Analysis
 * Provides comprehensive visualization for Total Cost of Ownership data
 */

class T3COCharts {
    constructor() {
        this.charts = {};
        this.defaultOptions = this.getDefaultOptions();
        this.colorPalette = {
            primary: '#1976d2',
            secondary: '#424242',
            success: '#4caf50',
            warning: '#ff9800',
            error: '#f44336',
            info: '#2196f3',
            accent: '#ff5722',
            gradient: ['#1976d2', '#2196f3', '#03dac6', '#4caf50', '#8bc34a', '#cddc39', '#ffeb3b', '#ff9800', '#ff5722', '#f44336']
        };
        this.animations = {
            duration: 1500,
            easing: 'easeInOutQuart'
        };
    }

    /**
     * Get default Chart.js options with T3CO styling
     */
    getDefaultOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            family: 'Roboto, sans-serif'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#1976d2',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                },
                datalabels: {
                    display: false // Disable by default, enable per chart as needed
                }
            },
            animation: this.animations,
            interaction: {
                intersect: false,
                mode: 'index'
            }
        };
    }

    /**
     * Initialize all charts with provided data
     */
    initializeCharts(chartData) {
        console.log('T3COCharts: Initializing charts with data:', Object.keys(chartData));
        
        try {
            // Map data to chart methods with proper canvas IDs
            const chartMappings = [
                { data: chartData.tco_stacked_breakdown, method: 'initTCOStackedBreakdown', canvasId: 'tcoSummaryChart' },
                { data: chartData.cost_category_summary, method: 'initCostCategorySummary', canvasId: 'costBreakdownChart' },
                { data: chartData.key_metrics, method: 'initKeyMetrics', canvasId: 'keyMetricsChart' },
                { data: chartData.cost_timeline, method: 'initCostTimeline', canvasId: 'costTimelineChart' },
                { data: chartData.performance_radar, method: 'initPerformanceRadar', canvasId: 'performanceRadarChart' }
            ];

            let chartsCreated = 0;
            
            chartMappings.forEach(({ data, method, canvasId }) => {
                if (data && this[method]) {
                    const canvas = document.getElementById(canvasId);
                    if (canvas) {
                        console.log(`Creating chart: ${method} on canvas ${canvasId}`);
                        this[method](data, canvasId);
                        chartsCreated++;
                    } else {
                        console.warn(`Canvas not found: ${canvasId}`);
                    }
                } else if (!data) {
                    console.log(`No data for ${method}`);
                } else {
                    console.warn(`Method not found: ${method}`);
                }
            });

            if (chartsCreated === 0) {
                console.warn('No charts were created. Showing no data message.');
                this.showNoDataMessage();
            } else {
                console.log(`Successfully created ${chartsCreated} charts`);
            }

        } catch (error) {
            console.error('Error initializing charts:', error);
            this.showErrorMessage();
        }
    }

    /**
     * Create T3CO Stacked Breakdown Chart (Bar Chart)
     */
    initTCOStackedBreakdown(chartData, canvasId = 'tcoSummaryChart') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found for TCO breakdown chart`);
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const options = {
            ...this.defaultOptions,
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: 'USD',
                                minimumFractionDigits: 0
                            }).format(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Total Cost of Ownership - Component Breakdown',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                },
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                }
            }
        };

        console.log('Creating TCO Stacked Breakdown chart with data:', chartData);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: chartData.type || 'bar',
            data: chartData.data,
            options: options
        });

        return this.charts[canvasId];
    }

    /**
     * Create Cost Category Summary Chart (Doughnut Chart)
     */
    initCostCategorySummary(chartData, canvasId = 'costBreakdownChart') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found for cost category chart`);
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const options = {
            ...this.defaultOptions,
            cutout: '60%',
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Cost Distribution by Category',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            }
        };

        console.log('Creating Cost Category Summary chart with data:', chartData);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: chartData.type || 'doughnut',
            data: chartData.data,
            options: options
        });

        return this.charts[canvasId];
    }

    /**
     * Create Key Metrics Chart (Bar Chart)
     */
    initKeyMetrics(chartData, canvasId = 'keyMetricsChart') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found for key metrics chart`);
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const options = {
            ...this.defaultOptions,
            indexAxis: 'y', // Horizontal bar chart
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Key Performance Metrics',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                },
                legend: {
                    display: false
                }
            }
        };

        console.log('Creating Key Metrics chart with data:', chartData);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: chartData.type || 'bar',
            data: chartData.data,
            options: options
        });

        return this.charts[canvasId];
    }

    /**
     * Create Cost Timeline Chart (Line Chart)
     */
    initCostTimeline(chartData, canvasId = 'costTimelineChart') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found for cost timeline chart`);
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const options = {
            ...this.defaultOptions,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    beginAtZero: true,
                    position: 'left',
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: 'USD',
                                minimumFractionDigits: 0
                            }).format(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: {
                        callback: function(value) {
                            return new Intl.NumberFormat('en-US', {
                                style: 'currency',
                                currency: 'USD',
                                minimumFractionDigits: 0
                            }).format(value);
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Cost Timeline Analysis',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                }
            }
        };

        console.log('Creating Cost Timeline chart with data:', chartData);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: chartData.type || 'line',
            data: chartData.data,
            options: options
        });

        return this.charts[canvasId];
    }

    /**
     * Create Performance Radar Chart
     */
    initPerformanceRadar(chartData, canvasId = 'performanceRadarChart') {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas ${canvasId} not found for performance radar chart`);
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const options = {
            ...this.defaultOptions,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                ...this.defaultOptions.plugins,
                title: {
                    display: true,
                    text: 'Vehicle Performance Profile',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    padding: 20
                }
            }
        };

        console.log('Creating Performance Radar chart with data:', chartData);
        
        this.charts[canvasId] = new Chart(ctx, {
            type: chartData.type || 'radar',
            data: chartData.data,
            options: options
        });

        return this.charts[canvasId];
    }

    /**
     * Show message when no data is available
     */
    showNoDataMessage() {
        console.log('Showing no data message');
        const chartContainers = document.querySelectorAll('.chart-card');
        chartContainers.forEach(container => {
            const canvas = container.querySelector('canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.font = '16px Roboto, sans-serif';
                ctx.fillStyle = '#666';
                ctx.textAlign = 'center';
                ctx.fillText('No chart data available', canvas.width / 2, canvas.height / 2);
                ctx.font = '12px Roboto, sans-serif';
                ctx.fillText('Run an analysis to see visualizations', canvas.width / 2, canvas.height / 2 + 25);
            }
        });
    }

    /**
     * Show error message
     */
    showErrorMessage() {
        console.log('Showing error message');
        const chartContainers = document.querySelectorAll('.chart-card');
        chartContainers.forEach(container => {
            const canvas = container.querySelector('canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.font = '16px Roboto, sans-serif';
                ctx.fillStyle = '#f44336';
                ctx.textAlign = 'center';
                ctx.fillText('Error loading charts', canvas.width / 2, canvas.height / 2);
                ctx.font = '12px Roboto, sans-serif';
                ctx.fillText('Please try refreshing the page', canvas.width / 2, canvas.height / 2 + 25);
            }
        });
    }

    /**
     * Refresh charts with new data
     */
    refresh(newData) {
        console.log('Refreshing charts with new data');
        
        // Destroy all existing charts
        Object.keys(this.charts).forEach(chartId => {
            if (this.charts[chartId]) {
                this.charts[chartId].destroy();
                delete this.charts[chartId];
            }
        });

        // Reinitialize with new data
        this.initializeCharts(newData);
    }

    /**
     * Destroy all charts
     */
    destroy() {
        Object.keys(this.charts).forEach(chartId => {
            if (this.charts[chartId]) {
                this.charts[chartId].destroy();
                delete this.charts[chartId];
            }
        });
        this.charts = {};
    }

    /**
     * Get chart instance by ID
     */
    getChart(chartId) {
        return this.charts[chartId];
    }

    /**
     * Export chart as image
     */
    exportChart(chartId, format = 'png') {
        const chart = this.charts[chartId];
        if (chart) {
            const canvas = chart.canvas;
            const link = document.createElement('a');
            link.download = `t3co_${chartId}.${format}`;
            link.href = canvas.toDataURL(`image/${format}`);
            link.click();
        }
    }
}

// Export for global use
window.T3COCharts = T3COCharts;

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('T3COCharts module loaded and ready');
    
    // Auto-initialize if chart data is available
    if (typeof window.chartDataConfig !== 'undefined' && window.chartDataConfig) {
        const chartsInstance = new T3COCharts();
        chartsInstance.initializeCharts(window.chartDataConfig);
        
        // Make globally available
        window.t3coChartsInstance = chartsInstance;
    }
});
