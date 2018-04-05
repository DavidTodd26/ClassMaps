function myFunction() {
  var map = L.map('map').setView([40.346, -74.653], 16);
  if (map.tap) map.tap.disable();
  L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
    maxZoom: 20,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
      '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
      'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.streets'
  }).addTo(map);
  //map._layersMinZoom=5;

// add a layer group, yet empty
var markersLayer = new L.LayerGroup();  
map.addLayer(markersLayer); 
 
// add the search bar to the map
  var controlSearch = new L.Control.Search({
    position:'topright',    // where do you want the search bar?
    layer: markersLayer,  // name of the layer
    initial: false,
    zoom: 11,        // set zoom to found location when searched
    marker: false,
    textPlaceholder: 'search...' // placeholder while nothing is searched
  });
 
  map.addControl(controlSearch); // add it to the map
// add var "code"
var code = '1ciPq3VfxUv3ucttkMPzNXNR1NLKA1JrOq1tGiLg2CsI'

// loop through spreadsheet with Tabletop
    Tabletop.init({ 
    key: code,
    callback: function(sheet, tabletop){ 
      
      for (var i in sheet){
        var data = sheet[i];

          var icon = L.icon({
              iconUrl: data.icon,
              iconSize:     [52, 60], // size of the icon
              iconAnchor:   [26, 60], // point of the icon which will correspond to marker's location
              popupAnchor: [0, -60]
          });
          if (data.iconori === "left") {
            icon = L.icon({
              iconUrl: data.icon,
              iconSize:     [60, 52], 
              iconAnchor:   [60, 26], 
              popupAnchor: [-35, -26]
              });
          };
          if (data.iconori === "right") {
            icon = L.icon({
              iconUrl: data.icon,
              iconSize:     [60, 52], 
              iconAnchor:   [0, 26], 
              popupAnchor: [35, -26]
              })
            };

          // L.marker([data.longitude, data.latitude], {icon: icon})
          // .addTo(map)
          // .bindPopup("<strong style='color: #84b819'>" + data.newsroom + "</strong><br>" + 
          //             data.company + " | " + data.city + "<br>Head: " + data.head).openPopup();
      }
    },
    simpleSheet: true 
  })
  
}