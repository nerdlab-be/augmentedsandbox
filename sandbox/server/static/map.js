const map = L.map('map').setView([51.505, -0.09], 8);

const osmTiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
const esriTiles = L.tileLayer('http://localhost/tiles/{z}/{y}/{x}')
osmTiles.addTo(map);
esriTiles.addTo(map);

const updateView = async () => {
  const response = await fetch('/location');
  const coordinates = await response.json();
  map.flyTo(coordinates, 8);
};

setInterval(updateView, 10000);