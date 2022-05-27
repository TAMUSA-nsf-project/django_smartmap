

// the following are variables accessible anywhere in the script (script vars)
let map;
let mapRouteMarkers = {};  // object to hold routes and their google.maps.Marker instances
let displayedRoute = ""  // ID of currently displayed route

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
    map.setCenter(MAP_CENTER);

  });
}

function RouteDropdown() {
    /**
     * This function creates and returns a div that contains a route-selection dropdown.
     */

    /*
        The following html was copied from https://getbootstrap.com/docs/5.2/components/dropdowns/.
        This was converted to javascript using the document.createElement method.
     */
    // <div id="route-dropdown" className="dropdown">
    //     <button className="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton1"
    //             data-bs-toggle="dropdown" aria-expanded="false">
    //         Dropdown button
    //     </button>
    //     <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
    //         <li><a className="dropdown-item" href="#">Action</a></li>
    //         <li><a className="dropdown-item" href="#">Another action</a></li>
    //         <li><a className="dropdown-item" href="#">Something else here</a></li>
    //     </ul>
    // </div>

    const routeDropdown = document.createElement("div")
    routeDropdown.id = "route-dropdown"
    routeDropdown.className = "dropdown"
    routeDropdown.style.marginTop = "10px";

    const button = document.createElement("button")
    button.className="btn btn-secondary dropdown-toggle"
    button.type="button"
    button.id = "dropdownMenuButton1"
    button.setAttribute("data-bs-toggle", "dropdown")
    button.setAttribute("aria-expanded", "false")
    button.innerHTML = "Select Route"
    routeDropdown.appendChild(button)

    const listItems = document.createElement("ul")
    listItems.className="dropdown-menu"
    listItems.setAttribute("aria-labelledby", "dropdownMenuButton1")
    // listItems.innerHTML = '<li><a className="dropdown-item" href="#">Action</a></li>'

    const arr = ['alpha', 'bravo', 'charlie', 'delta', 'echo'];

    for (let key in JSON_ROUTES) {

        const li = document.createElement('li');     // create li element.

        const li_button = document.createElement("button")
        li_button.type = "button"
        li_button.setAttribute("class", 'dropdown-item')
        li_button.innerHTML = key

        // define the button's onclick behavior
        li_button.onclick = () => {
            hideDisplayedMarkers()
            showRouteMarkers(key);
        }

        li.appendChild(li_button);
        listItems.appendChild(li);     // append li to ul.
    }
    routeDropdown.appendChild(listItems)
    return routeDropdown;
}


function showRouteMarkers(route /*string*/) {
    /**
     * Displays the markers of the user-selected route by setting their map property to the map var used in this script.
     */
    mapRouteMarkers[route].forEach(marker => {
        marker.setMap(map);  // shows the marker
    })

    // set the script var to current route
    displayedRoute = route;
}

function hideDisplayedMarkers() {
    /**
     * Hides currently displayed markers by setting their map property to null.
     * Uses script variable displayedRoute, which contains the name of the currently displayed route. This could be
     * turned into an array to hold the IDs of several routes if we allow that.
     */
    if (displayedRoute) {
        mapRouteMarkers[displayedRoute].forEach((marker) => {
            marker.setMap(null);
        })

        // reset script var
        displayedRoute = ""
    }
}




function createRouteMarker(stop) {
    return new google.maps.Marker({
        position: {lat: stop.Lat, lng: stop.Lng},
        map: null,
        title: stop["Stop Name"]
    })
}

function initAllRouteMarkers() {
    /**
     * Initializes the mapRouteMarkers object that will contain google.maps.Marker instances.
     */
    for(var key in JSON_ROUTES) {
        mapRouteMarkers[key] = [];
        for (var key1 in JSON_ROUTES[key]){
            // console.log(JSON_ROUTES[key][key1])
            mapRouteMarkers[key][key1] = createRouteMarker(JSON_ROUTES[key][key1])
        }
    }
}

function initMap() {
    // marker_coords is defined in map_index.html using values passed in via django template engine

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: MAP_CENTER
    });

    // Initialize object of route markers
    initAllRouteMarkers();

    // Create the DIV to hold the control and call the CenterControl()
    // constructor passing in this DIV.
    const centerControlDiv = document.createElement("div")
    CenterControl(centerControlDiv, map)

    // Create the DIV to hold the route-selection dropdown.
    const routeDropdownDiv = RouteDropdown();

    // Push the divs to the map.
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv)
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(routeDropdownDiv)

}

window.initMap = initMap;
