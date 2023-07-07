/*
    offcanvas.js is a javascript that handles the route offcanvas list used in map_index.js.
    Note that javascript files can share variables and functions (by default I think? Maybe
    because they are both used in map_index.html).
    - Emmer
 */

let selectedRoute = -1;
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

    // ALL_ACTIVE_ROUTES is from 'map_index.html', which provides an array of routes.
for( let key in ALL_ACTIVE_ROUTES )
{
    // Generate placeholder bars while async
    let aRoutesAccordionInfo = createAccordionElement(
        key,
        ALL_ACTIVE_ROUTES[key],
        generateBusStopPlaceholder( key )
    )

    document.getElementById("routeMenuAccordion").appendChild( aRoutesAccordionInfo );

    aRoutesAccordionInfo.querySelector("#" + ACCORDION_HEADER_ROUTE_PREFIX + key).onclick = () => {
        // This will prevent route info from being polled again when closing
        // the currently open accordion.
        if ( selectedRoute === key )    // User is closing the already opened route
        {
            console.log("Setting var selectedRoute to -1 and var selectedBusStop to null")
            selectedRoute = -1
            selectedBusStop = null
            return;
        }
        selectedRoute = key;

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
    arrivalTimes.setAttribute("data-bs-parent", "#" + forThisListGroup)

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
            return
        }

        selectedBusStop = aBusStop
        selectedBusStopArrivalLabelParent = listGroupItem

        map.panTo( aBusStop.marker.getPosition() );

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

function updateArrivalLabels( aBusStop, busStopLabelParent )
{
    // NOTE: This function should only be used right after .updateArrivalInfo().
    // .updateArrivalInfo() in map_index.js has already updated the BusStop object's
    // .scheduled_arrival and .est_arrival data members by this point.
    // All that needs to be done is display the new data to the user.
    let estArrivalLabel = busStopLabelParent.querySelector("#estArrival")
    let schArrivalLabel = busStopLabelParent.querySelector("#schArrival")

    schArrivalLabel.innerHTML = "<small>" + SCHEDULED_ARRIVAL_TIME_LABEL + "</small><br />" + aBusStop.scheduled_arrival

    if( aBusStop.est_arrival !== "TBD" )
    {
        estArrivalLabel.innerHTML = "<small>" + ESTIMATED_ARRIVAL_TIME_LABEL + "</small><br />" + aBusStop.est_arrival
    }
    else
    {
        estArrivalLabel.innerHTML = ""
    }
}

/*
    Creates a container(div) of info on a singular bus stop.
 */
function generateStopInfoContainer_old( stopNumber, stopName, schTime, estTime )
{
    const container = document.createElement("div");
    const row       = document.createElement("div");
    const bPointDiv = document.createElement("div");    // A bullet point
    const bPointImg = document.createElement("i");
    const stopDiv   = document.createElement("div");    // Bus stop info container
    const stopNameDiv   = document.createElement("div");
    const stopNumberDiv = document.createElement("div");
    const schTimeDiv    = document.createElement("div");    // Scheduled time
    const estTimeDiv    = document.createElement("div");    // Estimated time

    container.className = "container";
        container.setAttribute("id", stopNumber);
        row.className = "row";
            bPointDiv.className = "col-1 bus-stop-bullet-point";
                bPointImg.className = "fa fa-circle";   // Icon provided by FontAwesome 4.7.0
            stopDiv.className = "col-10";
                stopNameDiv.className = "row";
                    stopNameDiv.innerHTML = "<strong>" + stopName + "</strong>";
                stopNumberDiv.className = "row";
                    stopNumberDiv.innerHTML = "Stop #: " + stopNumber;
                schTimeDiv.className  = "row";
                    schTimeDiv.innerHTML = "Scheduled Arrival: " + schTime;
                estTimeDiv.className  = "row";
                    estTimeDiv.innerHTML = "Estimated Arrival: " + estTime;

    container.appendChild( row );
        row.appendChild( bPointDiv );
            bPointDiv.appendChild( bPointImg );
        row.appendChild( stopDiv );
            stopDiv.appendChild( stopNameDiv );
            stopDiv.appendChild( stopNumberDiv );
            stopDiv.appendChild( schTimeDiv );
            stopDiv.appendChild( estTimeDiv );

    return container;
}

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