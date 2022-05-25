
var map;
function initMap() {
    // marker_coords is defined in map_index.html using values passed in via django template engine

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: marker_coords
    });

    const marker = new google.maps.Marker({
        position: marker_coords,
        map: map,
    });
}

window.initMap = initMap;
