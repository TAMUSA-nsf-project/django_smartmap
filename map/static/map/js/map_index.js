
let map;

/**
 * The CenterControl adds a control to the map that recenters the map on marker_coords
 * This constructor takes the control DIV as an argument.
 * @constructor
 */
function CenterControl(controlDiv, map) {
  // Set CSS for the control border.
  const controlUI = document.createElement("div");

  controlUI.style.backgroundColor = "#fff";
  controlUI.style.border = "2px solid #fff";
  controlUI.style.borderRadius = "3px";
  controlUI.style.boxShadow = "0 2px 6px rgba(0,0,0,.3)";
  controlUI.style.cursor = "pointer";
  controlUI.style.marginTop = "8px";
  controlUI.style.marginBottom = "22px";
  controlUI.style.textAlign = "center";
  controlUI.title = "Click to recenter the map";
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior.
  const controlText = document.createElement("div");

  controlText.style.color = "rgb(25,25,25)";
  controlText.style.fontFamily = "Roboto,Arial,sans-serif";
  controlText.style.fontSize = "16px";
  controlText.style.lineHeight = "38px";
  controlText.style.paddingLeft = "5px";
  controlText.style.paddingRight = "5px";
  controlText.innerHTML = "Center Map";
  controlUI.appendChild(controlText);
  // Setup the click event listeners: simply set the map to marker_coords.
  controlUI.addEventListener("click", () => {
    map.setCenter(marker_coords);
  });
}



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

  // Create the DIV to hold the control and call the CenterControl()
  // constructor passing in this DIV.
    const centerControlDiv = document.createElement("div")
    CenterControl(centerControlDiv, map)
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv)
}

window.initMap = initMap;
