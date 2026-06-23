export function initImagePopup(viewer, {
  imagePath,
  lat,
  lon,
  height = 0,
  label = '',
  distThreshold = 2000,
}) {
  const worldPos = Cesium.Cartesian3.fromDegrees(lon, lat, height);

  const el = document.createElement('div');
  el.className = 'img-popup';
  el.innerHTML = `
    <div class="img-card popup-card">
      ${label ? `<div class="img-label">${label}</div>` : ''}
      <img src="${imagePath}" alt="${label}" onclick="window.open('${imagePath}', '_blank')" />
    </div>`;
  document.body.appendChild(el);

  let visible = false;

  viewer.scene.postRender.addEventListener(() => {
    if (!visible) { el.style.display = 'none'; return; }
    const dist = Cesium.Cartesian3.distance(viewer.scene.camera.position, worldPos);
    const screen = dist < distThreshold &&
      Cesium.SceneTransforms.wgs84ToWindowCoordinates(viewer.scene, worldPos);
    el.style.display = screen ? 'block' : 'none';
    if (screen) {
      el.style.left = `${screen.x}px`;
      el.style.top  = `${screen.y}px`;
    }
  });

  return () => (visible = !visible);
}
