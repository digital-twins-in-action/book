class PredictPanel {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentSpaceName = null;
        this.currentMeasurements = null;
        this.predictionCharts = new Map();
        this.horizonHours = 6;
        if (this.container) this.showPlaceholder();
    }

    setData(spaceName, measurementsData) {
        this.currentSpaceName = spaceName;
        this.currentMeasurements = measurementsData;
    }

    showPlaceholder() {
        this.container.innerHTML = `
            <div class="chart-placeholder">
                <svg class="placeholder-icon" viewBox="0 0 48 48" fill="none">
                    <path d="M6 36l10-8 8 4 10-14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M34 18l8-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="3 3"/>
                    <circle cx="42" cy="12" r="3" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M6 42h36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <span>Select an asset to predict future trends</span>
            </div>`;
    }

    render() {
        if (!this.currentSpaceName || !this.currentMeasurements) {
            this.showPlaceholder();
            return;
        }

        const spaceData = this.currentMeasurements.find(s => s.name === this.currentSpaceName);
        if (!spaceData?.measurements?.length) {
            this.container.innerHTML = `
                <div class="chart-no-data">
                    <svg class="placeholder-icon" viewBox="0 0 48 48" fill="none">
                        <rect x="4" y="4" width="40" height="40" rx="4" stroke="currentColor" stroke-width="2"/>
                        <path d="M16 24h16M24 16v16" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.4"/>
                    </svg>
                    <span>No data available to predict for "${this.currentSpaceName}"</span>
                </div>`;
            return;
        }

        this.clearPredictionCharts();
        const measurements = spaceData.measurements.filter(m => m.values?.length);

        let html = `
            <div class="predict-display">
                <div class="space-header">
                    <div class="space-info">
                        <div class="space-icon predict-icon">
                            <svg viewBox="0 0 24 24" fill="none">
                                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/>
                                <path d="M12 7v5l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="space-name">${this.currentSpaceName} &mdash; Predictions</h3>
                            <p class="space-meta">Trend-based forecast using linear regression</p>
                        </div>
                    </div>
                </div>
                <div class="predict-horizon-selector">
                    <span class="time-range-label">Forecast Horizon</span>
                    <div class="time-range-buttons">
                        <button class="time-range-btn predict-horizon-btn${this.horizonHours === 1 ? ' active' : ''}" data-hours="1">1H</button>
                        <button class="time-range-btn predict-horizon-btn${this.horizonHours === 6 ? ' active' : ''}" data-hours="6">6H</button>
                        <button class="time-range-btn predict-horizon-btn${this.horizonHours === 12 ? ' active' : ''}" data-hours="12">12H</button>
                        <button class="time-range-btn predict-horizon-btn${this.horizonHours === 24 ? ' active' : ''}" data-hours="24">1D</button>
                        <button class="time-range-btn predict-horizon-btn${this.horizonHours === 168 ? ' active' : ''}" data-hours="168">7D</button>
                    </div>
                </div>
                <div class="predict-results-grid">`;

        measurements.forEach((m, index) => {
            const values = m.values.map(v => parseFloat(v.value));
            const timestamps = m.values.map(v => parseInt(v.timestamp) / 1000);
            const unit = this.getUnit(m.name);
            const prediction = this.linearPredict(timestamps, values, this.horizonHours);
            const trend = prediction.slope > 0 ? 'rising' : prediction.slope < 0 ? 'falling' : 'stable';
            const latest = values[values.length - 1];
            const predicted = prediction.futureValues[prediction.futureValues.length - 1];
            const delta = predicted - latest;
            const chartId = `predict-chart-${index}`;

            html += `
                    <div class="predict-card">
                        <div class="predict-card-header">
                            <h5 class="predict-card-title">${this.formatName(m.name)}</h5>
                            <span class="predict-trend ${trend}">
                                ${trend === 'rising' ? '&#9650;' : trend === 'falling' ? '&#9660;' : '&#9654;'}
                                ${trend.charAt(0).toUpperCase() + trend.slice(1)}
                            </span>
                        </div>
                        <div id="${chartId}" class="predict-chart-wrapper"></div>
                        <div class="predict-summary">
                            <div class="stat-item">
                                <span class="stat-label">Current</span>
                                <span class="stat-value">${latest.toFixed(1)}${unit}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Predicted</span>
                                <span class="stat-value latest">${predicted.toFixed(1)}${unit}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Change</span>
                                <span class="stat-value ${delta >= 0 ? 'positive' : 'negative'}">${delta >= 0 ? '+' : ''}${delta.toFixed(1)}${unit}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Confidence</span>
                                <span class="stat-value">${(prediction.r2 * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>`;
        });

        html += '</div></div>';
        this.container.innerHTML = html;

        this.container.querySelectorAll('.predict-horizon-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.horizonHours = parseInt(e.target.dataset.hours);
                this.container.querySelectorAll('.predict-horizon-btn').forEach(b =>
                    b.classList.toggle('active', b.dataset.hours === String(this.horizonHours)));
                this.render();
            });
        });

        setTimeout(() => {
            measurements.forEach((m, index) => {
                const values = m.values.map(v => parseFloat(v.value));
                const timestamps = m.values.map(v => parseInt(v.timestamp) / 1000);
                const prediction = this.linearPredict(timestamps, values, this.horizonHours);
                this.createPredictChart(`predict-chart-${index}`, timestamps, values,
                    prediction.futureTimestamps, prediction.futureValues,
                    prediction.upperBound, prediction.lowerBound, m.name);
            });
        }, 100);
    }

    linearPredict(timestamps, values, horizonHours) {
        const n = values.length;
        if (n < 2) {
            const last = values[n - 1] || 0;
            const lastTs = timestamps[n - 1] || Date.now() / 1000;
            return {
                slope: 0, r2: 0,
                futureTimestamps: [lastTs + horizonHours * 3600],
                futureValues: [last],
                upperBound: [last], lowerBound: [last]
            };
        }

        let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0;
        for (let i = 0; i < n; i++) {
            sumX += timestamps[i];
            sumY += values[i];
            sumXY += timestamps[i] * values[i];
            sumX2 += timestamps[i] * timestamps[i];
            sumY2 += values[i] * values[i];
        }
        const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        const ssTot = sumY2 - (sumY * sumY) / n;
        let ssRes = 0;
        for (let i = 0; i < n; i++) {
            const predicted = slope * timestamps[i] + intercept;
            ssRes += (values[i] - predicted) ** 2;
        }
        const r2 = ssTot > 0 ? Math.max(0, 1 - ssRes / ssTot) : 0;

        const stdErr = Math.sqrt(ssRes / Math.max(1, n - 2));
        const lastTs = timestamps[n - 1];
        const steps = Math.max(10, Math.min(50, horizonHours));
        const stepSize = (horizonHours * 3600) / steps;

        const futureTimestamps = [];
        const futureValues = [];
        const upperBound = [];
        const lowerBound = [];

        for (let i = 1; i <= steps; i++) {
            const t = lastTs + stepSize * i;
            const v = slope * t + intercept;
            const spread = stdErr * 1.96 * Math.sqrt(1 + (i / steps));
            futureTimestamps.push(t);
            futureValues.push(v);
            upperBound.push(v + spread);
            lowerBound.push(v - spread);
        }

        return { slope, intercept, r2, futureTimestamps, futureValues, upperBound, lowerBound };
    }

    createPredictChart(containerId, histTimestamps, histValues, futTimestamps, futValues, upper, lower, name) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const color = this.getColor(name);

        const allTs = [...histTimestamps, ...futTimestamps];
        const histSeries = [...histValues, ...new Array(futTimestamps.length).fill(null)];
        const futSeries = [...new Array(histTimestamps.length - 1).fill(null), histValues[histValues.length - 1], ...futValues];
        const upperSeries = [...new Array(histTimestamps.length - 1).fill(null), histValues[histValues.length - 1], ...upper];
        const lowerSeries = [...new Array(histTimestamps.length - 1).fill(null), histValues[histValues.length - 1], ...lower];

        try {
            const opts = {
                width: container.offsetWidth || 300,
                height: 90,
                series: [
                    {},
                    { stroke: color, width: 2, label: 'Historical' },
                    { stroke: color, width: 2, dash: [5, 3], label: 'Predicted' },
                    { stroke: color + '30', width: 1, fill: color + '10', label: 'Upper' },
                    { stroke: color + '30', width: 1, fill: color + '10', label: 'Lower' }
                ],
                scales: { x: { time: true }, y: { auto: true } },
                axes: [
                    { stroke: '#94a3b8', grid: { stroke: '#f1f5f9', width: 1 }, font: '10px sans-serif' },
                    { stroke: '#94a3b8', grid: { stroke: '#f1f5f9', width: 1 }, font: '10px sans-serif', size: 45 }
                ],
                cursor: { x: true, y: false, points: { size: 5, fill: color, stroke: '#fff', width: 2 } },
                legend: { show: false }
            };
            const chart = new uPlot(opts, [allTs, histSeries, futSeries, upperSeries, lowerSeries], container);
            this.predictionCharts.set(containerId, chart);
        } catch (e) {
            console.error('Error creating prediction chart:', e);
        }
    }

    getUnit(name) {
        const units = {
            temperature: '°C', humidity: '%', co2: 'ppm', tvoc: 'ppm',
            pm25: 'μg/m³', pm10: 'μg/m³', pressure: 'hPa',
            energyconsumption: 'Wh', current: 'mA', power: 'W', voltage: 'V'
        };
        return units[name.toLowerCase()] || '';
    }

    formatName(name) {
        return name.charAt(0).toUpperCase() + name.slice(1).replace(/([A-Z])/g, ' $1');
    }

    getColor(name) {
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

    clearPredictionCharts() {
        this.predictionCharts.forEach(chart => chart?.destroy?.());
        this.predictionCharts.clear();
    }
}

window.PredictPanel = PredictPanel;
