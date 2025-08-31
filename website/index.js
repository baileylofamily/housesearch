// Initialize Google Maps
function initMap() {
  const vancouver = { lat: 49.25, lng: -123.139 };
  const map = new google.maps.Map(document.getElementById("map"), { zoom: 13, center: vancouver });

  // Add hard-coded blue markers
  const manualPos1 = { lat: 49.228, lng: -123.119 };
  const manualMarker1 = new google.maps.Marker({position: manualPos1, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_blue1.png"});
  const manualPos2 = { lat: 49.236260, lng: -123.123232 };
  const manualMarker2 = new google.maps.Marker({position: manualPos2, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_blue2.png"});

const pos7877867236_1 = { lat: 49.246022, lng: -123.115312 };
const marker7877867236_1 = new google.maps.Marker({position: pos7877867236_1, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_red1.png"});
const pos7876788719_2 = { lat: 49.243398, lng: -123.130041 };
const marker7876788719_2 = new google.maps.Marker({position: pos7876788719_2, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_red2.png"});
const pos7875529732_1 = { lat: 49.237357, lng: -123.116205 };
const marker7875529732_1 = new google.maps.Marker({position: pos7875529732_1, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_yellow1.png"});
const pos7877530487_2 = { lat: 49.239142, lng: -123.119044 };
const marker7877530487_2 = new google.maps.Marker({position: pos7877530487_2, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_yellow2.png"});
}

// Expose initMap globally for Google Maps API callback
window.initMap = initMap;
