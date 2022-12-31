/*
    route_menu.js is a javascript that handles the route offcanvas list used in map_index.js.
    Note that javascript files can share variables and functions (by default I think? Maybe
    because they are both used in map_index.html).

    For convenience, here is the Bootstrap website:
    https://getbootstrap.com/docs/5.2/getting-started/introduction/
    - Emmer
 */

let selectedRoute = -1;     // This variable may be similar to 'displayedRoute' in map_index.js, but I did not realize at the time. -Emmer
let selectedBusStop = null
let selectedBusStopArrivalLabelParent = null

const ACCORDION_ITEM_ROUTE_PREFIX = "accordionItemOfRoute"
const ACCORDION_HEADER_ROUTE_PREFIX = "accordionHeaderForRoute"
const ACCORDION_COLLAPSE_ROUTE_PREFIX = "accordionCollapseForRoute"
const ACCORDION_BODY_ROUTE_PREFIX = "accordionBodyForRoute"
const LIST_GROUP_ROUTE_PREFIX = "listGroupForRoute"
const BUS_STOP_INFO_PLACEHOLDER_ROUTE_PREFIX = "busStopInfoPlaceholderForRoute"
const ARRIVAL_TIMES_ID_PREFIX = "arrivalTimesFor"
const RETRIEVING_ARRIVAL_TIMES_LABEL = "Retrieving arrival times..."
const SCHEDULED_ARRIVAL_TIME_LABEL = "Next scheduled arrival:"
const ESTIMATED_ARRIVAL_TIME_LABEL = "Next estimated arrival:"
const ESTIMATED_ARRIVAL_TIME_UPDATE_INTERVAL_MILLISECONDS = 30000
const NO_ROUTE_SELECTED_LABEL = "No route selected."
const NO_BUS_STOP_SELECTED_LABEL = "No bus stop selected."
const VIEWING_ROUTE_LABEL = "Viewing route "
const VIEWING_BUS_STOP_LABEL = "Viewing bus stop"

// ALL_ACTIVE_ROUTES is from 'map_index.html', which provides an array of routes.
for( let key in ALL_ACTIVE_ROUTES )
{
    // Generate placeholder bars while async things happen
    let aRoutesAccordionInfo = createAccordionElement(
        key,
        ALL_ACTIVE_ROUTES[key],
        generateBusStopPlaceholder( key )
    )

    document.getElementById("routeMenuAccordion").appendChild( aRoutesAccordionInfo );

    aRoutesAccordionInfo.querySelector("#" + ACCORDION_HEADER_ROUTE_PREFIX + key).onclick = () => {

        // This will prevent route info from being polled again
        // when closing the currently open accordion.
        if ( selectedRoute === key )    // User is closing the already opened route
        {
            console.log("Setting var selectedRoute to -1 and var selectedBusStop to null")
            selectedRoute = -1
            selectedBusStop = null

            updateSelectedRouteAndBusStopLabelsOnMap()

            return;
        }
        selectedRoute = key;

        updateSelectedRouteAndBusStopLabelsOnMap( ALL_ACTIVE_ROUTES[key] )

        refreshBusRouteElements(selectedRoute).then(()=>{
             const routeAccordion = document.getElementById(ACCORDION_BODY_ROUTE_PREFIX + key);
                routeAccordion.removeChild( document.getElementById(BUS_STOP_INFO_PLACEHOLDER_ROUTE_PREFIX + key) );
                routeAccordion.appendChild( createBusStopInfoOfRoute( key ) );
        })
    }

}

// Estimated arrival updater
setInterval(function()
{
    if( !selectedBusStop || !selectedBusStopArrivalLabelParent ) { console.log("No bus stop selected"); return }

    selectedBusStop.updateArrivalInfo().then( (res) => {

        updateArrivalLabels( selectedBusStop, selectedBusStopArrivalLabelParent )

    })

}, ESTIMATED_ARRIVAL_TIME_UPDATE_INTERVAL_MILLISECONDS)

/*
    Creates a div that represents an accordion list element for an accordion list.
    ARGS:
        String  id      - Unique developer setted suffix for all of an accordion element's relevant child elements
        String  label   - Text to appear on the accordion expand button
        div(?)  content - Element that will be .appendChild()-ed into the accordion's body.
    RETURN:
        A div element representing a new accordion element.
    NOTES:
        accordionId is not checked if the Id is already used. Hopefully nothing bad happens because of this.
        I eventually want accordionLabel to also accept a div as an arg someday, just in case.
 */
function createAccordionElement( id, label, content )
{
    const item     = document.createElement("div");    // A holder for all of an accordion elements
    const header   = document.createElement("h2");     // Frame for the accordion button
    const button   = document.createElement("button"); // Button to open the accordion body
    const collapse = document.createElement("div");    // Frames and contracts the accordion body
    const body     = document.createElement("div");    // Content of the accordion

    item.className     = "accordion-item";
    header.className   = "accordion-header";
    button.className   = "accordion-button collapsed";
    collapse.className = "accordion-collapse collapse";
    body.className     = "accordion-body accordion-body-route";

    item.setAttribute("id", ACCORDION_ITEM_ROUTE_PREFIX + id)
    header.setAttribute("id", ACCORDION_HEADER_ROUTE_PREFIX + id);

    button.setAttribute("type", "button");
    button.setAttribute("data-bs-toggle", "collapse");
    button.setAttribute("data-bs-target", "#" + ACCORDION_COLLAPSE_ROUTE_PREFIX + id);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", ACCORDION_COLLAPSE_ROUTE_PREFIX+ id);
    button.innerHTML = label;

    collapse.setAttribute("id", ACCORDION_COLLAPSE_ROUTE_PREFIX + id);
    collapse.setAttribute("aria-labelledby", ACCORDION_HEADER_ROUTE_PREFIX + id);
    collapse.setAttribute("data-bs-parent", "#routeMenuAccordion"); // "#routeMenuAccordion" must be a param eventually if this function is to be used for any other offcanvas

    body.setAttribute("id", ACCORDION_BODY_ROUTE_PREFIX + id);
    // So apparently JS is case-sensitive and .innerHtml is not the same as .innerHTML
    //body.innerHTML = content;
    //createBusStopInfoForOffcanvasAccordionBody( body, "Route 51" );

    body.appendChild( content );

    header.appendChild( button );
    collapse.appendChild( body );
    item.appendChild( header );
    item.appendChild( collapse );

    return item;
}

/*
    Generates material for the content section of accordion elements. The div returned
    should be placed inside a div of class "accordion-body".
    ARGS:
        string routeId  - An id of a route whose info the accordion body will be composed of.
    RETURNS:
        a div element
 */
function createBusStopInfoOfRoute( routeId )
{
    routeId = parseInt( routeId );

    const listGroup = document.createElement("div");
        listGroup.className = "list-group";
        listGroup.setAttribute("id", LIST_GROUP_ROUTE_PREFIX + routeId);

    // A aBusStop is a BusStop object instance. The class is located in map_index.js
    mapRouteMarkers[routeId].forEach( aBusStop =>
    {
        listGroup.appendChild(
            generateStopInfoContainer( aBusStop, listGroup.id )
        );
    });

    return listGroup;
}

/*
    Generates an "a" element that represents a singular bus stop on a route.
    ARGS:
        BusStop aBusStop        - The BusStop object whose information will be presented in the returned element.
        string forThisListGroup - Id of the element that the returned element will be parented to.
    RETURNS:
        a div element
 */
function generateStopInfoContainer( aBusStop, forThisListGroup )
{
    const listGroupItem     = document.createElement("a");

    const topRow            = document.createElement("div");
    const stopNameLabel     = document.createElement("strong");
    const stopNumberLabel   = document.createElement("small");

    const arrivalTimes = document.createElement("div");
    const estArrival = document.createElement("p");
    const schArrival = document.createElement("p");

    listGroupItem.className = "list-group-item list-group-item-action";
    listGroupItem.setAttribute("id", aBusStop.number);
    listGroupItem.setAttribute("data-bs-toggle", "collapse");
    listGroupItem.setAttribute("role", "button");
    listGroupItem.setAttribute("aria-expanded", "false");
    listGroupItem.setAttribute("href", "#" + ARRIVAL_TIMES_ID_PREFIX + aBusStop.number);
    listGroupItem.setAttribute("aria-controls", ARRIVAL_TIMES_ID_PREFIX + aBusStop.number);

    topRow.className = "d-flex w-100 justify-content-between";
    stopNameLabel.className = "mb-1";
    stopNumberLabel.className = "";

    stopNameLabel.innerHTML = "(" + aBusStop.index + ") " + aBusStop.name;
    stopNumberLabel.innerHTML = "#" + aBusStop.number;

    arrivalTimes.className = "collapse"
    arrivalTimes.setAttribute("id", ARRIVAL_TIMES_ID_PREFIX + aBusStop.number)
    arrivalTimes.setAttribute("data-bs-parent", "#" + forThisListGroup)     // This will make it so only one bus stop info can show at anytime.

    estArrival.setAttribute("id", "estArrival");

    schArrival.setAttribute("id", "schArrival");

    listGroupItem.appendChild( topRow );
        topRow.appendChild( stopNameLabel );
        topRow.appendChild( stopNumberLabel );

    listGroupItem.appendChild( arrivalTimes );
        arrivalTimes.appendChild( schArrival );
        arrivalTimes.appendChild( estArrival );

    listGroupItem.onclick = () =>
    {
        if( selectedBusStop === aBusStop )   // User clicked on the already viewed bus stop
        {
            console.log("Setting var selectedBusStop to null")
            selectedBusStop = null;
            selectedBusStopArrivalLabelParent = null

            updateSelectedRouteAndBusStopLabelsOnMap( ALL_ACTIVE_ROUTES[aBusStop.routeId] )

            return
        }

        selectedBusStop = aBusStop
        selectedBusStopArrivalLabelParent = listGroupItem

        updateSelectedRouteAndBusStopLabelsOnMap( ALL_ACTIVE_ROUTES[aBusStop.routeId], "(" + aBusStop.index + ") " + aBusStop.name )

        map.panTo( aBusStop.marker.getPosition() );

        // Apparently this bounce animation does not show on Chrome, which is weird since it is from the Google Maps API.
        if( aBusStop.marker.getAnimation() === null )
        {
            aBusStop.marker.setAnimation( google.maps.Animation.BOUNCE );
            setTimeout( function(){
                aBusStop.marker.setAnimation( null );
            }
            , 2000)
        }

        // This BusStop object has no scheduled time nor estimated time. The assumed reason is
        // that this information has not been requested yet from the server.
        if( aBusStop.scheduled_arrival === defaultTimeString && aBusStop.est_arrival === defaultTimeString )
        {
            // So, tell the user that the info is being retrieved.
            const arrivalPlaceholder = document.createElement("p");
                arrivalPlaceholder.setAttribute("id", "arrivalPlaceholder");
                arrivalPlaceholder.innerHTML = RETRIEVING_ARRIVAL_TIMES_LABEL;

            const spinnerGIF = document.createElement("div");
                spinnerGIF.className = "spinner-border spinner-border-sm";
                spinnerGIF.setAttribute("role", "status");

            const spinTextForScreenReaders = document.createElement("span");
                spinTextForScreenReaders.className = "visually-hidden";
                spinTextForScreenReaders.innerHTML = "Loading...";

            spinnerGIF.appendChild( spinTextForScreenReaders );
            arrivalPlaceholder.appendChild( spinnerGIF );

            listGroupItem.appendChild( arrivalPlaceholder );

            // Then begin the retrieval process
            aBusStop.updateArrivalInfo().then( (res) => {

                updateArrivalLabels( aBusStop, listGroupItem )

            }).then( (res) => {
                listGroupItem.querySelector("#arrivalPlaceholder").remove()
            })

        }

    }

    return listGroupItem;
}

/*
    Updates the arrival text labels of the specified bus stop parent using the specified BusStop object.
    ARGS:
        BusStop aBusStop            - The BusStop object whose information will be presented in the labels.
        Element busStopLabelParent  - The element which parents the arrival labels
    RETURNS:
        null
 */
function updateArrivalLabels( aBusStop, busStopLabelParent )
{
    /*  NOTE: This function should only be used in a .then() after .updateArrivalInfo().
        An example can be found near the end of generateStopInfoContainer().
        .updateArrivalInfo() in map_index.js would have already updated the BusStop
        object's .scheduled_arrival and .est_arrival data members by this function is
        called. All that needs to be done is display the new data to the user.
    */
    let estArrivalLabel = busStopLabelParent.querySelector("#estArrival")
    let schArrivalLabel = busStopLabelParent.querySelector("#schArrival")

    schArrivalLabel.innerHTML = "<small>" + SCHEDULED_ARRIVAL_TIME_LABEL + "</small><br />" + aBusStop.scheduled_arrival

    if( aBusStop.est_arrival !== defaultTimeString )    // defaultTimeString is from map_index.js
    {
        estArrivalLabel.innerHTML = "<small>" + ESTIMATED_ARRIVAL_TIME_LABEL + "</small><br />" + aBusStop.est_arrival
    }
    else
    {
        estArrivalLabel.innerHTML = ""
    }
}

/*
    Replaces the text of the information located on the top right section of the map.
    ARGS:
        String routeText    - The text that will appear in the upper section
        String stopText     - The text that will appear in the bottom section
    RETURNS:
        null
 */
function updateSelectedRouteAndBusStopLabelsOnMap( routeText, stopText )
{
    routeText = routeText != null ? routeText : NO_ROUTE_SELECTED_LABEL
    stopText = stopText != null ? stopText : NO_BUS_STOP_SELECTED_LABEL
    const selectedRouteAndBusStopLabels = document.getElementById("selectedRouteAndBusStopLabels")

    let updatedString = "";
    if( routeText !== NO_ROUTE_SELECTED_LABEL )
    {
        updatedString += "<p><strong>" + routeText + "</strong></p>"
        + "<p><strong>" + stopText + "</strong></p>"
    }

    selectedRouteAndBusStopLabels.innerHTML = updatedString
}

/*
    Creates three softly glowing bars that act as placeholders.
    ARGS:
        key - Route Id that the placeholders will be parented to.
    RETURNS:
        null
 */
function generateBusStopPlaceholder( key )
{
    const container = document.createElement("div");
        container.className = "container bus-stop-container";
        container.setAttribute("aria-hidden", "true");
        container.setAttribute("id", BUS_STOP_INFO_PLACEHOLDER_ROUTE_PREFIX + key)

    const placeholder       = document.createElement("p");
    placeholder.className = "placeholder-glow";

    for( let i = 0; i < 4; i++ )
    {
        const placeholderLine   = document.createElement("span");
        placeholderLine.className = "placeholder col-12";
        placeholder.appendChild( placeholderLine );
    }

    container.appendChild( placeholder );
    return container;
}