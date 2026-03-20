class DigitalTwinViewer {
    constructor() {
        this.splitPanes = null;
        this.treeBrowser = null;
        this.sceneViewer = null;
        this.dataPanel = null;
        this.simulatePanel = null;
        this.predictPanel = null;
        this.graphqlClient = null;
        this.selectedAssetId = null;
    }

    init() {
        try {
            this.graphqlClient = new GraphQLClient('https://j8qwc5uxog.execute-api.us-east-1.amazonaws.com/Prod/graphql', {
                headers: { 'Content-Type': 'application/json' },
                maxRetries: 3, retryDelay: 1000, timeout: 10000
            });
            window.graphqlClient = this.graphqlClient;

            this.splitPanes = new SplitPanes();
            this.splitPanes.init();

            this.sceneViewer = new SceneViewer('cesium-container', {
                enableLighting: true, enableFog: true
            });

            this.dataPanel = new DataPanel('chart-container', { chartHeight: 120 });
            this.simulatePanel = new SimulatePanel('simulate-container');
            this.predictPanel = new PredictPanel('predict-container');

            this.initTabs();

            this.treeBrowser = new TreeBrowser('tree-container', { expandOnSelect: true, showIcons: true });
            this.treeBrowser.on('asset-selected', (data) => this.handleAssetSelection(data));
            this.treeBrowser.on('tree-loaded', () => this.setHeaderStatus(true));
            this.treeBrowser.on('tree-error', () => this.setHeaderStatus(false));
            this.treeBrowser.loadAssetHierarchy();

            document.addEventListener('data-panel:time-range-changed', (e) => this.handleTimeRangeChange(e.detail));

            console.log('Digital Twin Viewer initialized');
        } catch (error) {
            console.error('Failed to initialize:', error);
            this.showGlobalMessage('Failed to initialize application.', 'error');
        }
    }

    async handleAssetSelection({ assetId, assetData }) {
        this.selectedAssetId = assetId;
        const spaceName = assetData?.name || assetId;
        await this.fetchAndDisplayMeasurements(spaceName);
    }

    async handleTimeRangeChange({ spaceName, startDate, endDate }) {
        await this.fetchAndDisplayMeasurements(spaceName, startDate, endDate);
    }

    initTabs() {
        document.querySelectorAll('.panel-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabId = tab.dataset.tab;
                document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.panel-tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(`tab-${tabId}`)?.classList.add('active');

                if (tabId === 'simulate') this.simulatePanel.render();
                if (tabId === 'predict') this.predictPanel.render();
            });
        });
    }

    async fetchAndDisplayMeasurements(spaceName, startDate, endDate) {
        try {
            this.dataPanel.showLoading();
            const data = await this.graphqlClient.getMeasures(spaceName, startDate, endDate);

            if (this.dataPanel && data) {
                this.dataPanel.displayMeasurementsForSpace(spaceName, data);
            }

            if (this.simulatePanel && data) {
                this.simulatePanel.setData(spaceName, data);
            }
            if (this.predictPanel && data) {
                this.predictPanel.setData(spaceName, data);
            }

            if (this.sceneViewer?.isReady() && data) {
                this.sceneViewer.clearSensorMarkers();
                const spaceData = data.find(s => s.name === spaceName);
                if (spaceData?.sensors?.length && this.sceneViewer.addSensorMarkers) {
                    this.sceneViewer.addSensorMarkers(spaceData.sensors, spaceName, data);
                }
            }
        } catch (error) {
            console.error(`Failed to fetch measurements for ${spaceName}:`, error);
            this.dataPanel?.showNoData(spaceName);
            this.sceneViewer?.clearSensorMarkers?.();
        }
    }

    setHeaderStatus(connected) {
        const statusEl = document.getElementById('header-status');
        if (!statusEl) return;
        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('.status-text');
        if (connected) {
            dot.classList.add('connected');
            text.textContent = 'Connected';
        } else {
            dot.classList.remove('connected');
            text.textContent = 'Disconnected';
        }
    }

    showGlobalMessage(message, type = 'info') {
        let el = document.getElementById('global-message');
        if (!el) {
            el = document.createElement('div');
            el.id = 'global-message';
            el.className = 'global-message';
            document.body.appendChild(el);
        }
        el.className = `global-message ${type}`;
        el.textContent = message;
        el.style.display = 'block';
        if (type === 'success' || type === 'info') {
            setTimeout(() => { el.style.display = 'none'; }, 3000);
        }
    }
}

let digitalTwinViewer = null;
document.addEventListener('DOMContentLoaded', () => {
    digitalTwinViewer = new DigitalTwinViewer();
    digitalTwinViewer.init();
});

window.DigitalTwinViewer = DigitalTwinViewer;
