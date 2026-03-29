class SceneViewer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = { enableLighting: true, enableFog: true, ...options };
        this.viewer = null;
        this.currentAssetId = null;
        this.eventListeners = {};
        this.isInitialized = false;
        this.sensorMarkers = new Map();
        this.originCoords = [-31.961505, 115.868492, -31];
        //this.originCoords = [-31.961505, 115.868492, -30];
        this.init();
    }

    async init() {
        if (!this.container) return;
        try {
            await this.initializeCesium();
            this.setupEventListeners();
            this.isInitialized = true;
            this.emit('scene-viewer-ready');
        } catch (error) {
            console.error('Failed to initialize scene viewer:', error);
            this.showError('Failed to initialize 3D viewer.');
        }
    }

    async initializeCesium() {
        Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiYzlkYWY1NC1lY2MyLTQwMTItOTZmOS1iMGZjZDhiYWVlNmMiLCJpZCI6OTA1NDMsImlhdCI6MTc1ODk2NzE3NH0.gbIKYC6HhxEjslsowGakuUorIEnkMjKYBvo49oyd7r0';

        this.container.innerHTML = '';
        const cesiumContainer = document.createElement('div');
        cesiumContainer.id = 'cesium-viewer';
        cesiumContainer.style.width = '100%';
        cesiumContainer.style.height = '100%';
        this.container.appendChild(cesiumContainer);

        this.viewer = new Cesium.Viewer(cesiumContainer, {
            terrain: Cesium.Terrain.fromWorldTerrain(),
            geocoder: false, homeButton: false, sceneModePicker: false,
            navigationHelpButton: false, animation: false, timeline: false,
            fullscreenButton: false, vrButton: false, infoBox: false,
            selectionIndicator: false
        });

        const scene = this.viewer.scene;
        scene.globe.enableLighting = this.options.enableLighting;
        scene.fog.enabled = this.options.enableFog;
        scene.fog.density = 0.0002;

        this.viewer.useBrowserRecommendedResolution = false;
        this.viewer.resolutionScale = window.devicePixelRatio;

        await this.loadDefault3DContent();
        this.setDefaultCameraPosition();
    }

    async loadDefault3DContent() {
        try {
            const [lat, lon, height] = this.originCoords;
            const matrix = Cesium.Matrix4.multiply(
                Cesium.Transforms.eastNorthUpToFixedFrame(
                    Cesium.Cartesian3.fromDegrees(lon, lat, height)
                ),
                Cesium.Matrix4.multiply(
                    Cesium.Matrix4.fromScale(new Cesium.Cartesian3(0.01, 0.01, 0.01)),
                    Cesium.Matrix4.fromRotation(
                        Cesium.Matrix3.fromRotationZ(-20 * Math.PI / 180)
                    ),
                    new Cesium.Matrix4()
                ),
                new Cesium.Matrix4()
            );

            // Hide the entire globe surface.
            //this.viewer.scene.globe.show = false;

            // Manually force the Sky Atmosphere to render.
            // This gives you the blue sky effect without the ground ball.
            //this.viewer.scene.skyAtmosphere.show = true;


            // const [googleTileset, customTileset] = await Promise.all([
            //     Cesium.createGooglePhotorealistic3DTileset(),
            //     Cesium.Cesium3DTileset.fromUrl("https://3d.dtia.site/tiles/tileset.json")
            // ]);

            const [osmBuildings, customTileset] = await Promise.all([
                Cesium.createOsmBuildingsAsync(),
                Cesium.Cesium3DTileset.fromUrl("https://3d.dtia.site/tiles/tileset.json")
            ]);

            customTileset.modelMatrix = matrix;
            this.viewer.scene.primitives.add(osmBuildings);
            // this.viewer.scene.primitives.add(googleTileset);
            this.viewer.scene.primitives.add(customTileset);
        } catch (error) {
            console.error('Failed to load 3D content:', error);
        }
    }

    setDefaultCameraPosition() {
        const [lat, lon] = this.originCoords;
        this.viewer.scene.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(lon, lat, 200)
        });
    }

    setupEventListeners() {
        this.viewer.cesiumWidget.creditContainer.style.display = 'none';
        this.viewer.scene.renderError.addEventListener((scene, error) => {
            console.error('Cesium rendering error:', error);
            this.emit('render-error', { error });
        });
    }

    createModelMatrix(lon, lat, height, scaleFactor, rotationZDeg = 0) {
        const translation = Cesium.Transforms.eastNorthUpToFixedFrame(
            Cesium.Cartesian3.fromDegrees(lon, lat, height)
        );
        const scaleAndRotation = Cesium.Matrix4.multiply(
            Cesium.Matrix4.fromRotation(
                Cesium.Matrix3.fromRotationZ(rotationZDeg * Cesium.Math.RADIANS_PER_DEGREE)
            ),
            Cesium.Matrix4.fromScale(new Cesium.Cartesian3(scaleFactor, scaleFactor, scaleFactor)),
            new Cesium.Matrix4()
        );
        return Cesium.Matrix4.multiply(translation, scaleAndRotation, new Cesium.Matrix4());
    }

    localToGeographic(localCartesian, baseTransformMatrix) {
        const worldPoint = Cesium.Matrix4.multiplyByPoint(baseTransformMatrix, localCartesian, new Cesium.Cartesian3());
        const cartographic = Cesium.Cartographic.fromCartesian(worldPoint);
        return {
            longitude: Cesium.Math.toDegrees(cartographic.longitude),
            latitude: Cesium.Math.toDegrees(cartographic.latitude),
            height: cartographic.height
        };
    }

    getUnitForMeasurement(name) {
        const units = {
            temperature: '°C', humidity: '%', co2: ' ppm', tvoc: ' ppm',
            pm25: ' μg/m³', pm10: ' μg/m³', pressure: ' hPa',
            energyconsumption: ' Wh', current: ' mA', power: ' W', voltage: ' V'
        };
        return units[name.toLowerCase()] || '';
    }

    getLatestSensorValues(sensorId, spaceData) {
        if (!spaceData?.measurements) return [];
        return spaceData.measurements
            .filter(m => m.values?.length > 0)
            .map(m => {
                const latest = m.values[m.values.length - 1];
                return {
                    name: m.name,
                    value: parseFloat(latest.value).toFixed(1),
                    unit: this.getUnitForMeasurement(m.name)
                };
            });
    }

    createSensorTooltipMarker(position, sensor, sensorValues, spaceName) {
        const sensorIdText = `📡 ${sensor.id.substring(0, 12)}${sensor.id.length > 12 ? '...' : ''}`;
        let maxTextWidth = sensorIdText.length * 8;
        if (sensorValues.length > 0) {
            sensorValues.forEach(sv => {
                maxTextWidth = Math.max(maxTextWidth, `${sv.name}: ${sv.value}${sv.unit}`.length * 7);
            });
        }

        const width = Math.max(160, maxTextWidth + 20);
        const headerHeight = 24;
        const lineHeight = 16;
        const contentHeight = Math.max(sensorValues.length, 1) * lineHeight;
        const height = headerHeight + contentHeight + 28;
        const arrowSize = 8;

        const valueText = sensorValues.length > 0
            ? sensorValues.map((sv, i) =>
                `<tspan x="10" dy="${i === 0 ? 16 : 16}" font-size="11" fill="#333">${sv.name}: ${sv.value}${sv.unit}</tspan>`
            ).join('')
            : '<tspan x="10" dy="16" font-size="11" fill="#666">No data available</tspan>';

        const svg = `
            <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
                <rect x="5" y="5" width="${width - 10}" height="${height - arrowSize - 10}"
                      rx="8" ry="8" fill="white" stroke="#007bff" stroke-width="2"/>
                <path d="M ${width / 2 - arrowSize} ${height - arrowSize - 5}
                         L ${width / 2} ${height - 5}
                         L ${width / 2 + arrowSize} ${height - arrowSize - 5} Z"
                      fill="white" stroke="#007bff" stroke-width="2"/>
                <rect x="5" y="5" width="${width - 10}" height="${headerHeight}" rx="8" ry="8" fill="#007bff"/>
                <rect x="5" y="${5 + 8}" width="${width - 10}" height="${headerHeight - 8}" fill="#007bff"/>
                <text x="10" y="21" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="white">
                    ${sensorIdText}
                </text>
                <text x="0" y="${headerHeight + 5}" font-family="Arial, sans-serif">${valueText}</text>
            </svg>`;

        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);

        return this.viewer.entities.add({
            id: `sensor-${sensor.id}-${spaceName}`,
            name: `Sensor ${sensor.id}`,
            position: position,
            billboard: {
                image: url,
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND,
                scale: 1.0,
                scaleByDistance: new Cesium.NearFarScalar(1.0, 1.0, 1000.0, 0.6)
            }
        });
    }

    addSensorMarkers(sensors, spaceName, measurementsData = null) {
        if (!this.viewer || !sensors?.length) return;

        const [originLat, originLon] = this.originCoords;
        const baseMatrix = this.createModelMatrix(originLon, originLat, -39, 1, -20);

        sensors.forEach(sensor => {
            try {
                const existingId = `sensor-${sensor.id}-${spaceName}`;
                if (this.viewer.entities.getById(existingId)) return;

                const localCartesian = new Cesium.Cartesian3(sensor.x, -sensor.y, 10);
                const globalCoords = this.localToGeographic(localCartesian, baseMatrix);
                const worldPosition = Cesium.Cartesian3.fromDegrees(
                    globalCoords.longitude, globalCoords.latitude, globalCoords.height
                );

                const spaceData = measurementsData?.find(s => s.name === spaceName);
                const sensorValues = this.getLatestSensorValues(sensor.id, spaceData);
                const entity = this.createSensorTooltipMarker(worldPosition, sensor, sensorValues, spaceName);

                if (!this.sensorMarkers.has(spaceName)) this.sensorMarkers.set(spaceName, []);
                this.sensorMarkers.get(spaceName).push(entity);
            } catch (error) {
                console.error(`Error adding sensor marker for ${sensor.id}:`, error);
            }
        });

        if (sensors.length > 0) {
            setTimeout(() => this.flyToSensors(spaceName), 500);
        }
    }

    clearSensorMarkers() {
        // Sensor markers persist across selections (additive mode)
    }

    flyToSensors(spaceName) {
        if (!this.viewer || !this.sensorMarkers.has(spaceName)) return;
        const sensors = this.sensorMarkers.get(spaceName);
        if (sensors.length === 0) return;

        if (sensors.length === 1) {
            this.viewer.flyTo(sensors[0], { duration: 2.0, offset: new Cesium.HeadingPitchRange(0, -0.5, 100) });
        } else {
            this.viewer.flyTo(sensors, { duration: 2.0 });
        }
    }

    isReady() { return this.isInitialized && this.viewer !== null; }

    showError(message) {
        const div = document.createElement('div');
        div.className = 'scene-error';
        div.innerHTML = `<div class="error-icon">&#9888;&#65039;</div><div class="error-message">${message}</div>`;
        this.container.appendChild(div);
    }

    on(event, callback) {
        if (!this.eventListeners[event]) this.eventListeners[event] = [];
        this.eventListeners[event].push(callback);
    }

    emit(event, data) {
        (this.eventListeners[event] || []).forEach(cb => { try { cb(data); } catch (e) { console.error(e); } });
    }
}

window.SceneViewer = SceneViewer;
