// the following are variables accessible anywhere in the script (script vars)
let map;
let mapRouteMarkers = {};  // object to hold routes and their google.maps.Marker instances
let displayedRoute = ""  // ID of currently displayed route

let activeMarkerInfoWindow;   // marker info window
let activeMarkerObj = null;   // marker info window

var busIcon;  // icon for bus

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
    button.className = "btn btn-secondary dropdown-toggle"
    button.type = "button"
    button.id = "dropdownMenuButton1"
    button.setAttribute("data-bs-toggle", "dropdown")
    button.setAttribute("aria-expanded", "false")
    button.innerHTML = "Select Route"
    routeDropdown.appendChild(button)

    const listItems = document.createElement("ul")
    listItems.className = "dropdown-menu"
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
            button.innerHTML = key;
            hideDisplayedMarkers()
            showRouteMarkers(key);
            getActiveBussesOnSelectedRoute();
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


function getActiveBussesOnSelectedRoute() {
    if (displayedRoute) {
        const toSend = {'route': displayedRoute}
        jQuery.ajax({
            url: AJAX_URL_ACTIVE_BUSSES_ON_ROUTE,
            data: {'data': JSON.stringify(toSend)},
            // ^the leftmost "data" is a keyword used by ajax and is not a key that is accessible
            // server-side, hence the object defined here
            type: "GET",
            dataType: 'json',  // data returned by server is json in this case
            success: (data) => {
                updateBusMarkersBySid(data);
            },
        });

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
        // this.active = false;
        this.#initMapMarker();
        // this.intervalHandle = null;
    }

    callBackMethod() {

        const toSend = {'route': this.route, 'bus_stop_id': this.number}
        jQuery.ajax({
            url: AJAX_EST_ARRIVAL_URL, //TODO setup url
            data: {'data': JSON.stringify(toSend)},
            // ^the leftmost "data" is a keyword used by ajax and is not a key that is accessible
            // server-side, hence the object defined here
            type: "GET",
            //dataType: 'json', // dataType specifies the type of data expected back from the server,
            dataType: 'html',  // in this example HTML data is sent back via HttpResponse in views.py
            success: (data) => {
                if (data) {
                    console.log(data)
                    this.est_arrival = data;
                } else
                    this.est_arrival = "TBD"

                // Refresh the info window
                this.refreshInfoWindow();
            },
        });

    }

    getInfoWindowContent() {
        return `<div style='margin-bottom:-10px'><strong><b>${this.name}</b></strong></div><br>` +
            `Stop #: ${this.number}<br>` +
            `Route: ${this.route}<br>` +
            `Next Arrival in ${this.est_arrival}`;
    }


    refreshInfoWindow() {
        activeMarkerInfoWindow.setContent(this.getInfoWindowContent())
    }

    // '#' prefix makes it a private method
    #initMapMarker() {
        // Google's recommended collection of icons: http://kml4earth.appspot.com/icons.html
        // Also see https://mapicons.mapsmarker.com/category/markers/transportation/?style=simple

        const icon_size = 30;  // dimension in pixels

        const busStopIcon = {
            url: "https://maps.google.com/mapfiles/kml/pal5/icon57.png",
            scaledSize: new google.maps.Size(icon_size, icon_size),  // resize to X by X pixels
        };

        let marker = new google.maps.Marker({
            position: {lat: this.Lat, lng: this.Lng},
            map: null,
            title: this.name,
            icon: busStopIcon,
        })

        // NOTE: PyCharm says addListener is deprecated, but it still works and the suggested method addEventListener doesn't work
        marker.addListener("click", () => {
            activeMarkerInfoWindow.close();  // closes any currently open info window
            activeMarkerInfoWindow.setContent(this.getInfoWindowContent())
            activeMarkerInfoWindow.open(marker.getMap(), marker)
            this.callBackMethod();

            // Set the current object as the active marker object
            activeMarkerObj = this
        })

        this.marker = marker;
    }

}


setInterval(function () {
    console.log("infoWindow is bound to map: " + (activeMarkerInfoWindow.getMap() ? true : false));
    if (activeMarkerInfoWindow.getMap() && activeMarkerObj) {
        activeMarkerObj.callBackMethod();
    } else {
        activeMarkerObj = null;
    }


}, 5000);


/**
 * Initializes the mapRouteMarkers object that will contain google.maps.Marker instances.
 */
function initAllRouteMarkers() {
    for (const route in JSON_ROUTES) {
        mapRouteMarkers[route] = [];
        for (const busStop in JSON_ROUTES[route]) {
            mapRouteMarkers[route][busStop] = new BusStop(JSON_ROUTES[route][busStop])
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
    activeMarkerInfoWindow = new google.maps.InfoWindow();

    // Initialize bus icon using google.maps.Size method to resize image at specified url
    busIcon = {
        url: "https://www.iconshock.com/image/SuperVista/Accounting/bus/",
        scaledSize: new google.maps.Size(50, 50),  // resize to 50x50 pixels
        // rotationAngle: 0
    };

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
 * Updates from server
 */
let busMarkers = [];


/**
 * Updates the google map markers in the busMarkersBySid object
 */
function updateBusMarkersBySid(data) {

    for (let i = 0; i < busMarkers.length; i++) {
        busMarkers[i].setMap(null);
    }

    busMarkers = [];

    for (const sid in data) {
        const sidData = data[sid]

        var newLatLng = new google.maps.LatLng(sidData.bus_lat, sidData.bus_lng)

        let sidMarker = new google.maps.Marker({
            position: newLatLng,
            map: map,
            title: sid,
            icon: busIcon,
        })

        busMarkers.push(sidMarker);

    }
}


