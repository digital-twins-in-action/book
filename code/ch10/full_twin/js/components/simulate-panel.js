class SimulatePanel {
    constructor(containerId) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.currentSpaceName = null;
        this.currentMeasurements = null;
        this.simulationCharts = new Map();
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
                    <path d="M8 40V16l10 8 10-16 12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M8 40h32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M28 8l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-dasharray="2 3"/>
                </svg>
                <span>Select an asset to simulate outcomes</span>
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
                    <span>No data available to simulate for "${this.currentSpaceName}"</span>
                </div>`;
            return;
        }

        const measurements = spaceData.measurements.filter(m => m.values?.length);

        let html = `
            <div class="simulate-display">
                <div class="space-header">
                    <div class="space-info">
                        <div class="space-icon simulate-icon">
                            <svg viewBox="0 0 24 24" fill="none">
                                <path d="M12 3v3m0 12v3M3 12h3m12 0h3M5.6 5.6l2.15 2.15m8.5 8.5l2.15 2.15M5.6 18.4l2.15-2.15m8.5-8.5l2.15-2.15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="space-name">${this.currentSpaceName} &mdash; Simulation</h3>
                            <p class="space-meta">Adjust parameters to simulate what-if scenarios</p>
                        </div>
                    </div>
                </div>
                <div class="simulate-controls">
                    <div class="simulate-controls-row">`;

        measurements.forEach(m => {
            const values = m.values.map(v => parseFloat(v.value));
            const latest = values[values.length - 1];
            const unit = this.getUnit(m.name);
            html += `
                        <div class="simulate-param">
                            <label class="simulate-label">${this.formatName(m.name)} ${unit}</label>
                            <div class="simulate-slider-row">
                                <input type="range" class="simulate-slider" data-measurement="${m.name}"
                                    min="${(latest * 0.5).toFixed(1)}" max="${(latest * 1.5).toFixed(1)}"
                                    step="${(latest * 0.01).toFixed(2)}" value="${latest.toFixed(1)}">
                                <span class="simulate-value" id="sim-val-${m.name}">${latest.toFixed(1)}</span>
                            </div>
                        </div>`;
        });

        html += `
                    </div>
                    <button class="simulate-run-btn" id="simulate-run-btn">Run Simulation</button>
                </div>
                <div class="simulate-results" id="simulate-results"></div>
            </div>`;

        this.container.innerHTML = html;
        this.bindControls(spaceData);
    }

    bindControls(spaceData) {
        this.container.querySelectorAll('.simulate-slider').forEach(slider => {
            slider.addEventListener('input', (e) => {
                const name = e.target.dataset.measurement;
                const valEl = document.getElementById(`sim-val-${name}`);
                if (valEl) valEl.textContent = parseFloat(e.target.value).toFixed(1);
            });
        });

        const runBtn = document.getElementById('simulate-run-btn');
        if (runBtn) {
            runBtn.addEventListener('click', () => this.runSimulation(spaceData));
        }
    }

    runSimulation(spaceData) {
        const resultsEl = document.getElementById('simulate-results');
        if (!resultsEl) return;

        this.clearSimulationCharts();

        const adjustments = {};
        this.container.querySelectorAll('.simulate-slider').forEach(slider => {
            adjustments[slider.dataset.measurement] = parseFloat(slider.value);
        });

        const measurements = spaceData.measurements.filter(m => m.values?.length);
        let html = '<div class="simulate-results-grid">';

        measurements.forEach((m, index) => {
            const values = m.values.map(v => parseFloat(v.value));
            const latest = values[values.length - 1];
            const adjusted = adjustments[m.name] || latest;
            const delta = adjusted - latest;
            const pctChange = latest !== 0 ? ((delta / latest) * 100).toFixed(1) : '0.0';
            const unit = this.getUnit(m.name);
            const impact = this.estimateImpact(m.name, delta, latest);
            const chartId = `sim-chart-${index}`;

            html += `
                <div class="simulate-result-card">
                    <div class="simulate-result-header">
                        <h5 class="simulate-result-title">${this.formatName(m.name)}</h5>
                        <span class="simulate-delta ${delta >= 0 ? 'positive' : 'negative'}">
                            ${delta >= 0 ? '+' : ''}${pctChange}%
                        </span>
                    </div>
                    <div class="simulate-result-values">
                        <div class="simulate-result-val">
                            <span class="stat-label">Current</span>
                            <span class="stat-value">${latest.toFixed(1)}${unit}</span>
                        </div>
                        <div class="simulate-result-arrow">&#8594;</div>
                        <div class="simulate-result-val">
                            <span class="stat-label">Simulated</span>
                            <span class="stat-value latest">${adjusted.toFixed(1)}${unit}</span>
                        </div>
                    </div>
                    <div id="${chartId}" class="sim-chart-wrapper"></div>
                    <div class="simulate-impact ${impact.level}">${impact.text}</div>
                </div>`;
        });

        html += '</div>';
        resultsEl.innerHTML = html;

        setTimeout(() => {
            measurements.forEach((m, index) => {
                const values = m.values.map(v => parseFloat(v.value));
                const timestamps = m.values.map(v => parseInt(v.timestamp) / 1000);
                const latest = values[values.length - 1];
                const adjusted = adjustments[m.name] || latest;
                const delta = adjusted - latest;

                const simValues = values.map((v, i) => {
                    const weight = i / values.length;
                    return v + delta * weight;
                });

                this.createSimChart(`sim-chart-${index}`, timestamps, values, simValues, m.name);
            });
        }, 100);
    }

    createSimChart(containerId, timestamps, original, simulated, name) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const color = this.getColor(name);
        try {
            const opts = {
                width: container.offsetWidth || 300,
                height: 80,
                series: [
                    {},
                    { stroke: '#94a3b8', width: 1.5, dash: [4, 3], label: 'Original' },
                    { stroke: color, width: 2, fill: color + '18', label: 'Simulated' }
                ],
                scales: { x: { time: true }, y: { auto: true } },
                axes: [
                    { stroke: '#94a3b8', grid: { stroke: '#f1f5f9', width: 1 }, font: '10px sans-serif' },
                    { stroke: '#94a3b8', grid: { stroke: '#f1f5f9', width: 1 }, font: '10px sans-serif', size: 45 }
                ],
                cursor: { x: true, y: false, points: { size: 5, fill: color, stroke: '#fff', width: 2 } },
                legend: { show: false }
            };
            const chart = new uPlot(opts, [timestamps, original, simulated], container);
            this.simulationCharts.set(containerId, chart);
        } catch (e) {
            console.error('Error creating simulation chart:', e);
        }
    }

    estimateImpact(name, delta, baseline) {
        const n = name.toLowerCase();
        const absPct = baseline !== 0 ? Math.abs(delta / baseline) * 100 : 0;

        if (absPct < 5) return { level: 'low', text: 'Minimal impact expected' };

        if (n.includes('temp')) {
            if (delta > 0) return { level: absPct > 15 ? 'high' : 'medium', text: `Cooling load increases ~${(absPct * 1.5).toFixed(0)}%` };
            return { level: absPct > 15 ? 'high' : 'medium', text: `Heating demand increases ~${(absPct * 1.2).toFixed(0)}%` };
        }
        if (n.includes('humid')) {
            return { level: absPct > 20 ? 'high' : 'medium', text: `Comfort index shifts by ~${absPct.toFixed(0)}%` };
        }
        if (n === 'co2' || n === 'tvoc') {
            if (delta > 0) return { level: absPct > 15 ? 'high' : 'medium', text: 'Ventilation rate should increase' };
            return { level: 'low', text: 'Air quality improves' };
        }
        if (n.includes('energy') || n.includes('power')) {
            return { level: absPct > 20 ? 'high' : 'medium', text: `Energy cost change ~${(delta > 0 ? '+' : '')}${absPct.toFixed(0)}%` };
        }
        return { level: absPct > 20 ? 'high' : 'medium', text: `${absPct.toFixed(0)}% deviation from baseline` };
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

    clearSimulationCharts() {
        this.simulationCharts.forEach(chart => chart?.destroy?.());
        this.simulationCharts.clear();
    }
}

window.SimulatePanel = SimulatePanel;
