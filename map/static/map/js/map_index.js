

// the following are variables accessible anywhere in the script (script vars)
let map;
let mapRouteMarkers = {};  // object to hold routes and their google.maps.Marker instances
let displayedRoute = ""  // ID of currently displayed route

let markerInfoWindow;   // marker info window

/**
 * The CenterControl adds a control to the map that recenters the map on marker_coords
 * This constructor takes the control DIV as an argument.
 *
 */
function CenterControl(map) {
    // Create the DIV to hold the control and call the CenterControl()
    // constructor passing in this DIV.
    const controlDiv = document.createElement("div")


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

    return controlDiv;
}

function RouteDropdown(map) {
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


/**
 * Displays the markers of the user-selected route by setting their map property to the map var used in this script.
 */
function showRouteMarkers(route /*string*/) {
    // bus_stop is a BusStop instance
    mapRouteMarkers[route].forEach(bus_stop => {
        bus_stop.marker.setMap(map);  // shows the marker
    })

    // set the script var to current route
    displayedRoute = route;
}


/**
 * Hides currently displayed markers by setting their map property to null.
 * Uses script variable displayedRoute, which contains the name of the currently displayed route. This could be
 * turned into an array to hold the IDs of several routes if we allow that.
 */
function hideDisplayedMarkers() {
    if (displayedRoute) {
        // bus_stop is a BusStop instance
        mapRouteMarkers[displayedRoute].forEach(bus_stop => {
            bus_stop.marker.setMap(null);
        })

        // reset script var
        displayedRoute = ""
    }
}


/**
 * Class to represent a bus stop. One of its properties is a google.maps.Marker instance.
 */
class BusStop {
    constructor(json_data) {
        this.name = json_data["Stop Name"]
        this.number = json_data["Stop Number"]
        this.route = json_data["route"]
        this.Lat = json_data.Lat
        this.Lng = json_data.Lng
        this.est_arrival = "TBD"
        this.#initMapMarker();
    }

    updateEstArrival(new_est_str) {
        this.est_arrival = new_est_str
    }


    getInfoWindowContent() {
        return `<div style='margin-bottom:-10px'><strong><b>${this.name}</b></strong></div><br>` +
        `Stop #: ${this.number}<br>` +
        `Route: ${this.route}<br>` +
        `Next Arrival in ${this.est_arrival}`;
    }

    // '#' prefix makes it a private method
    #initMapMarker() {
        let marker = new google.maps.Marker({
            position: {lat: this.Lat, lng: this.Lng},
            map: null,
            title: this.name
        })

        // NOTE: PyCharm says addListener is deprecated, but it still works and the suggested method addEventListener doesn't work
        marker.addListener("click", () => {
            markerInfoWindow.close();
            markerInfoWindow.setContent(this.getInfoWindowContent())
            markerInfoWindow.open(marker.getMap(), marker)
            // stopInfoWindow.open(map, marker)
        })

        this.marker = marker;
    }

}



/**
 * Replaced with BusStop class. Delete.
 */
function createRouteMarker(stop) {

    const stopName = stop["Stop Name"]

    marker = new google.maps.Marker({
        position: {lat: stop.Lat, lng: stop.Lng},
        map: null,
        title: stopName
    })

    return marker
}


/**
 * Initializes the mapRouteMarkers object that will contain google.maps.Marker instances.
 */
function initAllRouteMarkers() {
    for(var key in JSON_ROUTES) {
        mapRouteMarkers[key] = [];
        for (var key1 in JSON_ROUTES[key]){
            // console.log(JSON_ROUTES[key][key1])
            mapRouteMarkers[key][key1] = new BusStop(JSON_ROUTES[key][key1])
        }
    }
}


/**
 * Initializes embedded google map. Passed to google maps API via script tag in map_index.html.
 */
function initMap() {
    // marker_coords is defined in map_index.html using values passed in via django template engine

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: MAP_CENTER
    });

    // Initialize InfoWindow instance for the markers (all markers will use this instance)
    markerInfoWindow = new google.maps.InfoWindow();

    // Initialize BuStop instances that contain google.maps.Marker instances
    initAllRouteMarkers();

    // Create the DIV to hold the control by calling CenterControl()
    const centerControlDiv = CenterControl(map);

    // Create the DIV to hold the route-selection dropdown.
    const routeDropdownDiv = RouteDropdown(map);

    // Push the divs to the map.
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv)
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(routeDropdownDiv)

}

window.initMap = initMap;



/**
 * Socket.IO Stuff
 */

// setup socket var
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

// objects to track different busses which are identified by socket ID (sid) and organized by route or sid
var busMarkersByRoute = {}
var busMarkersBySid = {}


/**
 * Updates the google map markers in the busMarkersBySid object
 */
function updateBusMarkersBySid(data) {

    for (const sid in data) {
        const sidData = data[sid]

        var newLatLng = new google.maps.LatLng(sidData.bus_lat, sidData.bus_lng)

        var sidMarker;

        if (sid in busMarkersBySid) {
            sidMarker = busMarkersBySid[sid]
            if (sidMarker != undefined) {
                sidMarker.setPosition(newLatLng)
            } else {
                //todo, shouldn't happen
            }
        } else {
            // create a marker for sid
            sidMarker = new google.maps.Marker({
                position: newLatLng,
                map: map,
                title: sid,
                icon: "https://www.iconshock.com/image/SuperVista/Accounting/bus/",
            })
            busMarkersBySid[sid] = sidMarker
        }
    }
}


/**
 * Updates the google map markers in the busMarkersByRoute object by using the updated markers from busMarkersBySid
 */
function updateBusMarkersByRoute(data) {
    for (const sid in data) {

        const busRoute = data[sid].selected_route

        if (busRoute in busMarkersByRoute) {
            busMarkersByRoute[busRoute][sid] = busMarkersBySid[sid]
        } else {
            busMarkersByRoute[busRoute] = {[sid]: busMarkersBySid[sid]}  // must enclose first sid in brackets to force use of its string value
        }

    }
}

function updateBusStopArrivalTimes(data) {
    for(const route in data) {
        let updatedStopData = data[route]
        let routeBusStops = mapRouteMarkers[route]

        for (let i=0; i < routeBusStops.length; i++) {
            routeBusStops[i].updateEstArrival(updatedStopData[i].est_arrival)
        }

    }
}


// socket event listener for updated bus position
socket.on("display busses", data => {
    updateBusMarkersBySid(data);  // must be called first
    updateBusMarkersByRoute(data);  // dependent on busMarkersBySid object
});


// socket event listener for updated estimated arrival times
socket.on("update arrival times", data => {
    updateBusStopArrivalTimes(data)
});