class DataPanel {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = { chartHeight: 80, ...options };
        this.charts = new Map();
        this.currentTimeRange = '1h';
        this.currentSpaceName = null;
        if (this.container) this.showPlaceholder();
    }

    displayMeasurementsForSpace(spaceName, measurementsData) {
        const spaceData = measurementsData.find(s => s.name === spaceName);
        if (!spaceData?.measurements?.length) {
            this.showNoData(spaceName);
            return;
        }

        this.clearCharts();
        this.currentSpaceName = spaceName;

        const sensorCount = spaceData.sensors?.length || 0;
        const measurementCount = spaceData.measurements.filter(m => m.values?.length).length;

        let html = `
            <div class="measurements-display">
                <div class="space-header">
                    <div class="space-info">
                        <div class="space-icon">
                            <svg viewBox="0 0 24 24" fill="none">
                                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" stroke="currentColor" stroke-width="1.5"/>
                                <path d="M9 22V12h6v10" stroke="currentColor" stroke-width="1.5"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="space-name">${spaceName}</h3>
                            <p class="space-meta">${measurementCount} measurements &middot; ${sensorCount} sensors</p>
                        </div>
                    </div>
                </div>
                <div class="time-range-selector">
                    <span class="time-range-label">Range</span>
                    <div class="time-range-buttons">
                        <button class="time-range-btn${this.currentTimeRange === '1h' ? ' active' : ''}" data-range="1h">1H</button>
                        <button class="time-range-btn${this.currentTimeRange === '12h' ? ' active' : ''}" data-range="12h">12H</button>
                        <button class="time-range-btn${this.currentTimeRange === '1d' ? ' active' : ''}" data-range="1d">1D</button>
                        <button class="time-range-btn${this.currentTimeRange === '7d' ? ' active' : ''}" data-range="7d">7D</button>
                        <button class="time-range-btn${this.currentTimeRange === '30d' ? ' active' : ''}" data-range="30d">30D</button>
                    </div>
                </div>
                <div class="measurements-grid">`;

        spaceData.measurements.forEach((measurement, index) => {
            if (!measurement.values?.length) return;
            const chartId = `chart-${index}`;
            const unit = this.getUnitForMeasurement(measurement.name);
            const sensor = spaceData.sensors?.find(s => s.id.toLowerCase().includes(measurement.name.toLowerCase()));
            const typeClass = this.getMeasurementTypeClass(measurement.name);
            const typeIcon = this.getMeasurementIcon(measurement.name);

            html += `
                <div class="measurement-card">
                    <div class="measurement-header">
                        <div class="measurement-title-group">
                            <div class="measurement-type-icon ${typeClass}">${typeIcon}</div>
                            <h5 class="measurement-title">${this.formatMeasurementName(measurement.name)}</h5>
                        </div>
                        <div class="measurement-meta">
                            ${unit ? `<span class="measurement-unit">${unit}</span>` : ''}
                            ${sensor ? `<span class="sensor-location">(${sensor.x}, ${sensor.y})</span>` : ''}
                        </div>
                    </div>
                    <div class="chart-wrapper">
                        <div id="${chartId}" class="chart-container"></div>
                    </div>
                    <div id="${chartId}-stats" class="measurement-stats"></div>
                </div>`;
        });

        html += '</div></div>';
        this.container.innerHTML = html;

        this.container.querySelectorAll('.time-range-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleTimeRangeChange(e.target.dataset.range));
        });

        setTimeout(() => {
            spaceData.measurements.forEach((measurement, index) => {
                if (!measurement.values?.length) return;
                const color = this.getChartColor(measurement.name);
                this.createChart(`chart-${index}`, measurement.values, measurement.name,
                    this.getUnitForMeasurement(measurement.name), color);
            });
        }, 100);
    }

    getMeasurementTypeClass(name) {
        const n = name.toLowerCase();
        if (n.includes('temp')) return 'temp';
        if (n.includes('humid')) return 'humidity';
        if (n === 'co2') return 'co2';
        if (n === 'tvoc') return 'tvoc';
        if (n.includes('pm')) return 'pm';
        if (n.includes('energy') || n.includes('power') || n.includes('current') || n.includes('voltage')) return 'energy';
        if (n.includes('pressure')) return 'pressure';
        return 'default';
    }

    getMeasurementIcon(name) {
        const n = name.toLowerCase();
        if (n.includes('temp')) return '<svg viewBox="0 0 16 16" fill="none"><path d="M8 2v8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="12" r="2.5" stroke="currentColor" stroke-width="1.3"/><path d="M5.5 4h5" stroke="currentColor" stroke-width="1" stroke-linecap="round"/></svg>';
        if (n.includes('humid')) return '<svg viewBox="0 0 16 16" fill="none"><path d="M8 2C8 2 3 7.5 3 10.5a5 5 0 0010 0C13 7.5 8 2 8 2z" stroke="currentColor" stroke-width="1.3"/></svg>';
        if (n === 'co2' || n === 'tvoc') return '<svg viewBox="0 0 16 16" fill="none"><circle cx="6" cy="8" r="3" stroke="currentColor" stroke-width="1.2"/><circle cx="11" cy="6" r="2" stroke="currentColor" stroke-width="1.2"/><circle cx="10" cy="11" r="1.5" stroke="currentColor" stroke-width="1.2"/></svg>';
        if (n.includes('pm')) return '<svg viewBox="0 0 16 16" fill="none"><circle cx="5" cy="5" r="1.5" fill="currentColor" opacity="0.6"/><circle cx="11" cy="4" r="1" fill="currentColor" opacity="0.4"/><circle cx="8" cy="9" r="2" fill="currentColor" opacity="0.5"/><circle cx="4" cy="12" r="1" fill="currentColor" opacity="0.3"/><circle cx="12" cy="11" r="1.5" fill="currentColor" opacity="0.5"/></svg>';
        if (n.includes('energy') || n.includes('power')) return '<svg viewBox="0 0 16 16" fill="none"><path d="M9 1L4 9h4l-1 6 5-8H8l1-6z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/></svg>';
        if (n.includes('pressure')) return '<svg viewBox="0 0 16 16" fill="none"><path d="M8 14V8M4 10l4-6 4 6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 14h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>';
        return '<svg viewBox="0 0 16 16" fill="none"><path d="M3 12l3-4 3 2 4-6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    }

    getChartColor(name) {
        const n = name.toLowerCase();
        if (n.includes('temp')) return '#ef4444';
        if (n.includes('humid')) return '#3b82f6';
        if (n === 'co2') return '#8b5cf6';
        if (n === 'tvoc') return '#f59e0b';
        if (n.includes('pm')) return '#64748b';
        if (n.includes('energy') || n.includes('power') || n.includes('current') || n.includes('voltage')) return '#22c55e';
        if (n.includes('pressure')) return '#06b6d4';
        return '#6366f1';
    }

    handleTimeRangeChange(newRange) {
        if (newRange === this.currentTimeRange || !this.currentSpaceName) return;

        this.container.querySelectorAll('.time-range-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.range === newRange);
        });
        this.currentTimeRange = newRange;

        const { startDate, endDate } = this.calculateDateRange(newRange);
        document.dispatchEvent(new CustomEvent('data-panel:time-range-changed', {
            detail: { spaceName: this.currentSpaceName, timeRange: newRange, startDate, endDate },
            bubbles: true
        }));
    }

    calculateDateRange(timeRange) {
        const now = new Date();
        const hoursMap = { '1h': 1, '12h': 12, '1d': 24, '7d': 168, '30d': 720 };
        const hoursBack = hoursMap[timeRange] || 1;
        return {
            startDate: new Date(now.getTime() - hoursBack * 3600000).toISOString(),
            endDate: now.toISOString()
        };
    }

    createChart(containerId, data, measurementName, unit = '', color = '#3b82f6') {
        const container = document.getElementById(containerId);
        if (!container) return;

        const timestamps = data.map(d => parseInt(d.timestamp) / 1000);
        const values = data.map(d => parseFloat(d.value));

        try {
            const opts = {
                width: container.offsetWidth || 400,
                height: this.options.chartHeight,
                series: [
                    {},
                    {
                        stroke: color,
                        width: 2,
                        fill: color + '18',
                    }
                ],
                scales: { x: { time: true }, y: { auto: true } },
                axes: [
                    {
                        stroke: '#94a3b8',
                        grid: { stroke: '#f1f5f9', width: 1 },
                        ticks: { stroke: '#e2e8f0', width: 1 },
                        font: '10px -apple-system, BlinkMacSystemFont, sans-serif',
                    },
                    {
                        stroke: '#94a3b8',
                        grid: { stroke: '#f1f5f9', width: 1 },
                        ticks: { stroke: '#e2e8f0', width: 1 },
                        font: '10px -apple-system, BlinkMacSystemFont, sans-serif',
                        size: 50,
                    }
                ],
                cursor: {
                    x: true,
                    y: false,
                    points: { size: 6, fill: color, stroke: '#fff', width: 2 }
                }
            };
            const chart = new uPlot(opts, [timestamps, values], container);
            this.charts.set(containerId, chart);
            this.addStatistics(containerId, values, unit);
        } catch (error) {
            console.error('Error creating chart:', error);
        }
    }

    addStatistics(containerId, values, unit) {
        const el = document.getElementById(containerId + '-stats');
        if (!el || values.length === 0) return;

        const min = Math.min(...values);
        const max = Math.max(...values);
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const latest = values[values.length - 1];

        el.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item"><span class="stat-label">Latest</span><span class="stat-value latest">${latest.toFixed(1)}${unit}</span></div>
                <div class="stat-item"><span class="stat-label">Min</span><span class="stat-value">${min.toFixed(1)}${unit}</span></div>
                <div class="stat-item"><span class="stat-label">Max</span><span class="stat-value">${max.toFixed(1)}${unit}</span></div>
                <div class="stat-item"><span class="stat-label">Avg</span><span class="stat-value">${avg.toFixed(1)}${unit}</span></div>
            </div>`;
    }

    getUnitForMeasurement(name) {
        const units = {
            temperature: '°C', humidity: '%', co2: ' ppm', tvoc: ' ppm',
            pm25: ' μg/m³', pm10: ' μg/m³', pressure: ' hPa',
            energyconsumption: ' Wh', current: ' mA', power: ' W', voltage: ' V'
        };
        return units[name.toLowerCase()] || '';
    }

    formatMeasurementName(name) {
        return name.charAt(0).toUpperCase() + name.slice(1).replace(/([A-Z])/g, ' $1');
    }

    clearCharts() {
        this.charts.forEach(chart => chart?.destroy?.());
        this.charts.clear();
    }

    showPlaceholder() {
        this.container.innerHTML = `
            <div class="chart-placeholder">
                <svg class="placeholder-icon" viewBox="0 0 48 48" fill="none">
                    <rect x="4" y="4" width="40" height="40" rx="4" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 32l8-10 6 6 10-14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="32" r="2" fill="currentColor"/>
                    <circle cx="20" cy="22" r="2" fill="currentColor"/>
                    <circle cx="26" cy="28" r="2" fill="currentColor"/>
                    <circle cx="36" cy="14" r="2" fill="currentColor"/>
                </svg>
                <span>Select an asset to view sensor data</span>
            </div>`;
    }

    showNoData(spaceName) {
        this.container.innerHTML = `
            <div class="chart-no-data">
                <svg class="placeholder-icon" viewBox="0 0 48 48" fill="none">
                    <rect x="4" y="4" width="40" height="40" rx="4" stroke="currentColor" stroke-width="2"/>
                    <path d="M16 24h16M24 16v16" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
                </svg>
                <span>No data available for "${spaceName}"</span>
            </div>`;
    }

    showLoading() {
        this.container.innerHTML = '<div class="chart-loading"><div class="loading-spinner"></div><div>Loading sensor data...</div></div>';
    }
}

window.DataPanel = DataPanel;
