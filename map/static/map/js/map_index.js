// the following are variables accessible anywhere in the script (script vars)
let map;
let mapRouteMarkers = {};  // object to hold routes and their google.maps.Marker instances
let mapRoutePolylinePaths = {};  // object to hold routes and their DirectionsService polyline paths
let displayedRoute = ""  // ID of currently displayed route

let activeMarkerInfoWindow;   // marker info window
let activeMarkerObj = null;   // marker info window
const defaultTimeString = "TBD";

let poly, left;
let directionsService;


function RouteDropdown(map) {
    /* This function will Dynamically Add the available Route Options to the dropdown List.*/
    const routeDropdown = document.getElementById("routeDropdown")
    const button = document.getElementById("dropDownButton")

    const dropdownControls = document.getElementById("dropDownControls")
    for (let key in ALL_ACTIVE_ROUTES) {

        const li = document.createElement('li');     // create li element.

        const li_button = document.createElement("button")
        li_button.type = "button"
        li_button.setAttribute("class", 'dropdown-item')
        li_button.innerHTML = ALL_ACTIVE_ROUTES[key]

        // define the button's onclick behavior
        li_button.onclick = () => {
            var buttonText = ALL_ACTIVE_ROUTES[key];
            button.innerHTML = buttonText
            refreshBusRouteElements(key);
        }

        li.appendChild(li_button);
        dropdownControls.appendChild(li);     // append li to ul.
    }
    return routeDropdown;
}



/**
 * Hides bus route markers, polyline, gets (either from cache or server) and displays new bus route markers
 */
async function refreshBusRouteElements(route) {

    // Check whether the route is already cached
    if (!mapRouteMarkers[route]) {

        // Await data from server before continuing
        await jQuery.ajax({
            url: AJAX_URL_ROUTE_DETAILS,
            data: {'data': JSON.stringify(route)},
            type: "GET",
            dataType: 'json',
            success: (data) => {
                if (data) {
                    // console.log(data)
                    mapRouteMarkers[route] = []
                    data.all_stops.forEach((busStop) => {
                        mapRouteMarkers[route].push(new BusStop(busStop));
                    })
                } else
                    console.log("No stops found for the given route.")
            },
            error: (e) => {
                console.log(e.message)
            }
        });

    }

    // Hide currently displayed elements, show the new ones
    hideBusRoutePolyline()
    hideDisplayedMarkers()
    showRouteMarkers(route)
    getActiveBussesOnSelectedRoute()

}

/**
 * Displays the markers of the user-selected route by setting their map property to the map var used in this script.
 */
function showRouteMarkers(route /*string*/) {

    // bus_stop is a BusStop instance
    mapRouteMarkers[route].forEach(bus_stop => {
        // Display the marker
        bus_stop.marker.setMap(map);  // shows the marker

    })
    // Set the polyline stroke color to match the database value.
    poly.setOptions({strokeColor: mapRouteMarkers[route][0].location_pin_color});

    // set the script var to current route
    displayedRoute = route;

    // Draw Google's Directions Service polyline for the route
    DrawRoutePolyline(route);

}

/**
 * Hides polyline of entire bus route.
 */
function hideBusRoutePolyline() {
    // Polyline
    poly.setPath([]);
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
                updateBusMarkers(data);
            },
        });

    }
}


/**
 * Class to represent a bus stop. One of its properties is a google.maps.Marker instance.
 */
class BusStop {
    constructor(json_data) {

        this.name = json_data.BusStopName
        this.index = json_data.BusStopIndex
        this.number = json_data.BusStopNumber
        this.route = json_data.BusRouteName
        this.routeId = json_data.BusRouteId
        this.Lat = json_data.BusStopLatitude
        this.Lng = json_data.BusStopLongitude

        this.scheduled_arrival = defaultTimeString
        this.est_arrival = defaultTimeString
        this.location_pin_color = json_data.LocationPinColor
        // this.active = false;
        this.#initMapMarker();
        // this.intervalHandle = null;
    }

    showEATMessage() {
        let message = ""
        message += "Next Scheduled Arrival is at : " + this.scheduled_arrival + "<br />"
        if (this.est_arrival !== defaultTimeString)
            message += "Arrival in " + this.est_arrival
        return message
    }

    callBackMethod() {

        const toSend = {
            'route': this.routeId,
            'bus_stop_id': this.number,
            'calc_schedule': this.scheduled_arrival === defaultTimeString ? 1 : 0
        }
        jQuery.ajax({
            url: AJAX_URL_EST_ARRIVAL,
            data: {'data': JSON.stringify(toSend)},
            // ^the leftmost "data" is a keyword used by ajax and is not a key that is accessible
            // server-side, hence the object defined here
            type: "GET",
            //dataType: 'json', // dataType specifies the type of data expected back from the server,
            dataType: 'json',  // in this example HTML data is sent back via HttpResponse in views.py
            success: (data) => {
                if (data) {
                    // console.log(data)
                    if (data['est_arrival'] !== '') {
                        if (this.est_arrival === defaultTimeString) {
                            // Reset the scheduled arrival string. This scenario will happen if there were no buses available
                            // on the route when the info window was opened.
                            this.scheduled_arrival = defaultTimeString
                        }
                        this.est_arrival = data['est_arrival'];
                    } else
                        this.est_arrival = defaultTimeString;

                    if (data['scheduled_arrival'] !== '')
                        this.scheduled_arrival = data['scheduled_arrival']
                } else {
                    this.est_arrival = defaultTimeString
                    this.scheduled_arrival = defaultTimeString
                }


                // Refresh the info window
                this.refreshInfoWindow();
            },
        });

    }

    getInfoWindowContent() {
        return `<div class="container">
                    <div class="row">
                        <strong><b>${this.name}</b></strong>
                    </div>
                    <div class="row">
                        <div>Stop #: ${this.number}</div>
                    </div>
                    <div class="row">
                        <div>Route: ${this.route}</div>
                    </div>
                    <div class="row">
                        <div>${this.showEATMessage()}</div>
                    </div>
                </div>`
    }


    refreshInfoWindow() {
        activeMarkerInfoWindow.setContent(this.getInfoWindowContent())
    }

    // '#' prefix makes it a private method
    #initMapMarker() {
        // Google's recommended collection of icons: http://kml4earth.appspot.com/icons.html
        // Also see https://mapicons.mapsmarker.com/category/markers/transportation/?style=simple

        const svgMarker = {
            path: "M17.98,10.1c0,6.51-8.74,17.44-8.74,17.44,0,0-8.74-11.49-8.74-17.44C.5,4.8,4.41,.5,9.24,.5s8.74,4.3,8.74,9.6Z",
            fillColor: this.location_pin_color,
            fillOpacity: 1,
            scale: 1.5,
            labelOrigin: new google.maps.Point(10, 10),
            // Size of the SVG image
            size: new google.maps.Size(18.48, 28.35),
            // The origin for this image is (0, 0).
            origin: new google.maps.Point(0, 0),

            anchor: new google.maps.Point(10, 29),
        };

        let marker = new google.maps.Marker({
            position: {lat: this.Lat, lng: this.Lng},
            map: null,
            title: this.name,
            label: {
                text: `${this.index}`,
                color: "black",
                fontWeight: "bold"
            },
            icon: svgMarker,
        })

        // NOTE: PyCharm says addListener is deprecated, but it still works and the suggested method addEventListener doesn't work
        marker.addListener("click", () => {
            activeMarkerInfoWindow.close();  // closes any currently open info window
            activeMarkerInfoWindow.setContent(this.getInfoWindowContent())
            activeMarkerInfoWindow.open(marker.getMap(), marker)
            this.callBackMethod();

            // Set the current object as the active marker object
            activeMarkerObj = this

            //TODO Set the map view to the selected bus stop location
        })

        this.marker = marker;
    }

}

/**
 * Updates bus markers for currently selected route every X seconds.
 */
setInterval(function () {
    getActiveBussesOnSelectedRoute();
}, 3000)


setInterval(function () {

    if (activeMarkerInfoWindow.getMap() && activeMarkerObj) {
        console.log("Refreshing infowindow content.")
        activeMarkerObj.callBackMethod();
    } else {
        activeMarkerObj = null;
    }
}, 5000);

setInterval(function () {
    if (displayedRoute !== "" && busMarkers.length > 0) {
        console.log("Updating Polyline")
        reDrawPolyLineWithCurrentLocation(busMarkers[0].getPosition(), mapRoutePolylinePaths[displayedRoute]['polyline'])
    }
}, 10000);





/**
 * Initializes embedded google map. Passed to google maps API via script tag in map_index.html.
 */
function initMap() {
    // marker_coords is defined in map_index.html using values passed in via django template engine

    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: MAP_CENTER,
        gestureHandling: "greedy",
        disableDefaultUI: true,
    });

    // Initialize InfoWindow instance for the markers (all markers will use this instance)
    activeMarkerInfoWindow = new google.maps.InfoWindow();


    // Initialize DirectionsService object
    directionsService = new google.maps.DirectionsService();

    // Initialize polyline object
    poly = new google.maps.Polyline({
        strokeColor: "#000000",
        strokeOpacity: 1,
        strokeWeight: 5,
    });
    left = new google.maps.Polyline({
        strokeColor: "#000000",
        strokeOpacity: 1,
        strokeWeight: 5,
    });

    // Create the div to hold the route-selection dropdown.
    const routeDropdownDiv = RouteDropdown(map);

    // Push control divs to the map.
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(routeDropdownDiv)

    jQuery.ajax({
        url: AJAX_URL_BUS_OCCUPANCY_STATUS,
        type: "GET",
        dataType: 'json',  // in this example HTML data is sent back via HttpResponse in views.py
        success: (data) => {
            console.log(data)

            var legend = document.getElementById('legendContent');
            data.forEach((item) => {
                var div = document.createElement('div');
                div.innerHTML = '<img src="' + item.icon + '"> ' + item.description;
                legend.appendChild(div);
            })
            map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push
            (document.getElementById('legend'));
        },
    });
}

window.initMap = initMap;


/**
 * Updates from server
 */
let busMarkers = [];
let startIndex = 0;


const LOCATION_PROXIMITY = 50;

function reDrawPolyLineWithCurrentLocation(busLocation, mapRoutePolylinePath) {

    let arrayLen = mapRoutePolylinePath.length;
    let newIndex = -1;
    for (let i = startIndex; i < arrayLen; i++) {
        let distanceBetween = google.maps.geometry.spherical.computeDistanceBetween(busLocation, mapRoutePolylinePath[i])
        // console.log("Distance ----", val)
        if (distanceBetween < LOCATION_PROXIMITY) {
            // console.log("Found at index ---: ", i)
            newIndex = i + 1
            break
        }
    }

    if (newIndex !== -1 && newIndex > startIndex) {
        startIndex = newIndex

        poly.setMap(null)
        left.setMap(null)

        left.setPath(mapRoutePolylinePath.slice(0, startIndex))
        left.setOptions({strokeColor: mapRouteMarkers[displayedRoute][0].location_pin_color});
        left.setMap(map)

    }
}

/**
 * Updates the google map markers representing buses.
 */
function updateBusMarkers(data) {

    for (let i = 0; i < busMarkers.length; i++) {
        busMarkers[i].setMap(null);
    }

    busMarkers = [];

    for (const busID in data) {
        const busData = data[busID]

        const busLatLng = new google.maps.LatLng(busData.bus_lat, busData.bus_lng);

        const iconWidth = 100  // pixels

        const busIcon = {
            url: busData.bus_color,
            scaledSize: new google.maps.Size(iconWidth, iconWidth),
            // rotationAngle: 0
        };

        let sidMarker = new google.maps.Marker({
            position: busLatLng,
            map: map,
            title: busID,
            icon: busIcon,
            optimized: false,
            zIndex: 99999999
        })

        busMarkers.push(sidMarker);
    }
}

/**
 * Draws Google's Directions Service polyline path for the user-selected route.
 * @param route: user-selected bus route
 * @constructor
 */
async function DrawRoutePolyline(route) {

    // Check whether the route is already cached
    if (!mapRoutePolylinePaths[route]) {

        const toSend = {'route': route}

        // Ensure "await" is in front of ajax call, data must be received back from server before continuing
        await jQuery.ajax({
            url: AJAX_URL_ROUTE_POLYLINE_ENCODING,
            data: {'data': JSON.stringify(toSend)},
            // ^the leftmost "data" is a keyword used by ajax and is not a key that is accessible
            // server-side, hence the object defined here
            type: "GET",
            dataType: 'json',  // data returned by server is json in this case
            success: (data) => {
                // Cache the path
                mapRoutePolylinePaths[route] = {}

                mapRoutePolylinePaths[route]['polyline'] = {}
                mapRoutePolylinePaths[route]['polyline'] = google.maps.geometry.encoding.decodePath(data.polyline_encoding);

                mapRoutePolylinePaths[route]['bounds'] = {}
                mapRoutePolylinePaths[route]['bounds'] = data.polyline_bounds

            },
        });

    }
    // Clear the polylines from the previous route
    left.setMap(null)

    // Draw the line, todo make sure this part is always asynchronous
    poly.setPath(mapRoutePolylinePaths[route].polyline);

    // Create a bounds variable used to update the viewport to fully display the current route
    const polyline_bounds = mapRoutePolylinePaths[route].bounds
    let bounds = new google.maps.LatLngBounds()
    bounds.extend(new google.maps.LatLng(polyline_bounds.northeast))
    bounds.extend(new google.maps.LatLng(polyline_bounds.southwest))

    // Sets the viewport to contain the given bounds
    map.fitBounds(bounds)  // todo bound padding optional arg

    // Display everything
    poly.setMap(map);

}
