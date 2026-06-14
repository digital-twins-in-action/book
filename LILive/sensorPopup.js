const GRAPHQL_URL = 'http://localhost:5050/graphql';

const METRICS = [
  { key: 'temperature', label: 'Temp',      unit: '°C', color: '#ff6b6b' },
  { key: 'humidity',    label: 'Humidity',  unit: '%',  color: '#74b9ff' },
  { key: 'vib_count',  label: 'Vibration', unit: '',   color: '#a29bfe' },
];

const QUERY = `query getMeasures($space:String!,$start:String!,$end:String!){
  spaces(space:$space,startDate:$start,endDate:$end){
    name sensors{id name x y}
    measurements{name values{sensorId timestamp value}}
  }
}`;

function sparkline(values, color, w = 80, h = 28) {
  if (!values.length) return '';
  const min = Math.min(...values), max = Math.max(...values), range = max - min || 1;
  const pts = values.map((v, i) =>
    `${(i / (values.length - 1)) * w},${h - ((v - min) / range) * h}`
  ).join(' ');
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
  </svg>`;
}

function buildCard(sensor, measurements) {
  const rows = METRICS.map(({ key, label, unit, color }) => {
    const m = measurements.find(m => m.name === key);
    const vals = m ? m.values.filter(v => v.sensorId === sensor.id).map(v => v.value) : [];
    const latest = vals.length ? vals[vals.length - 1].toFixed(1) : '--';
    return `<div class="sp-row">
      <span class="sp-label">${label}</span>
      <span class="sp-val">${latest}${unit}</span>
      ${sparkline(vals, color)}
    </div>`;
  }).join('');
  return `<div class="sp-card popup-card">
    <div class="sp-title">${sensor.name}</div>${rows}
  </div>`;
}

function localToWorld(localCartesian, baseMatrix) {
  const worldPoint = Cesium.Matrix4.multiplyByPoint(baseMatrix, localCartesian, new Cesium.Cartesian3());
  const carto = Cesium.Cartographic.fromCartesian(worldPoint);
  return Cesium.Cartesian3.fromDegrees(
    Cesium.Math.toDegrees(carto.longitude),
    Cesium.Math.toDegrees(carto.latitude),
    carto.height
  );
}

// Build a pure ENU transform at the given lat/lon — no scale, no rotation.
// Sensor x/y are treated as metres east/north of the origin.
export function sensorBaseMatrix(lon, lat, height = 0) {
  return Cesium.Transforms.eastNorthUpToFixedFrame(
    Cesium.Cartesian3.fromDegrees(lon, lat, height)
  );
}

export async function initSensorPopups(viewer, {
  baseMatrix,
  space = 'Pump Station',
  startDate = new Date(Date.now() - 30 * 60000).toISOString(),
  endDate   = new Date().toISOString(),
}) {
  const res = await fetch(GRAPHQL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: QUERY, variables: { space, start: startDate, end: endDate } }),
  });
  const { data } = await res.json();
  const { sensors, measurements } = data.spaces[0];

  const popups = sensors.map(sensor => {
    const worldPos = localToWorld(new Cesium.Cartesian3(sensor.x, -sensor.y, 0), baseMatrix);
    const el = Object.assign(document.createElement('div'), { className: 'sp-popup' });
    el.innerHTML = buildCard(sensor, measurements);
    document.body.appendChild(el);
    return { el, worldPos };
  });

  viewer.scene.postRender.addEventListener(() => {
    const camPos = viewer.scene.camera.position;
    popups.forEach(({ el, worldPos }) => {
      const dist = Cesium.Cartesian3.distance(camPos, worldPos);
      const screen = dist < 500 && Cesium.SceneTransforms.wgs84ToWindowCoordinates(viewer.scene, worldPos);
      el.style.display = screen ? 'block' : 'none';
      if (screen) { el.style.left = `${screen.x}px`; el.style.top = `${screen.y}px`; }
    });
  });
}
