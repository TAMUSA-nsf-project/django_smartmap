/*
    offcanvas.js is a javascript that handles the route offcanvas list used in map_index.js.
    Note that javascript files can share variables and functions (by default I think? Maybe
    because they are both used in map_index.html).
    - Emmer
 */

let currentlyViewedRoute = -1;

// ALL_ACTIVE_ROUTES is from 'map_index.html', which provides an array of routes.
for( let key in ALL_ACTIVE_ROUTES )
{
    // Generate placeholder bars while async
    let aRoutesAccordionInfo = createAccordionElement(
        "route" + key,
        ALL_ACTIVE_ROUTES[key],
        generateBusStopPlaceholder( key )
    )

    aRoutesAccordionInfo.querySelector("#accordionHeader_route" + key).onclick = () => {
        console.log("curr: " + currentlyViewedRoute + "\n key: " + key )
        // This will prevent route info from being polled again when closing
        // the currently open accordion.
        if ( currentlyViewedRoute == key )
        {
            return;
        }
        currentlyViewedRoute = key;

        if (mapRouteMarkers[key]) {     // mapRouteMarkers is from map_index.js
            hideDisplayedMarkers()      // Same with these three functions
            showRouteMarkers(key)
            getActiveBussesOnSelectedRoute()

        } else {
            initRouteMarkers(key).then((res) => {
                hideDisplayedMarkers()
                showRouteMarkers(key)
                getActiveBussesOnSelectedRoute()

                // Route bus stop info generated at initRouteMarkers().
                // Remove placeholders and display bus stops.
                const routeAccordion = document.getElementById("accordionBody_route" + key);
                routeAccordion.removeChild( document.getElementById("busStopInfoPlaceholder_route" + key) );
                routeAccordion.appendChild( createBusStopInfoOfRoute( key ) );
            });
        }
    }

    document.getElementById("leftOffcanvasAccordion").appendChild( aRoutesAccordionInfo );
}

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

    item.setAttribute("id", "accordionItem_" + id)
    header.setAttribute("id", "accordionHeader_" + id);

    button.setAttribute("type", "button");
    button.setAttribute("data-bs-toggle", "collapse");
    button.setAttribute("data-bs-target", "#accordionCollapse_" + id);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", "accordionCollapse_"+ id);
    button.innerHTML = label;

    collapse.setAttribute("id", "accordionCollapse_" + id);
    collapse.setAttribute("aria-labelledby", "accordionHeader_" + id);
    collapse.setAttribute("data-bs-parent", "#leftOffcanvasAccordion"); // TODO: "#leftOffcanvasAccordion must be a param eventually

    body.setAttribute("id", "accordionBody_" + id);
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
        //listGroup.setAttribute("aria-current", "true");

    // A aBusStop is a BusStop object instance. The class is located in map_index.js
    mapRouteMarkers[routeId].forEach( aBusStop =>
    {
        listGroup.appendChild(
            generateStopInfoContainer( aBusStop )
        );
    });

    return listGroup;
}

function generateStopInfoContainer( aBusStop )
{
    const listGroupItem = document.createElement("a");
    const topRow        = document.createElement("div");
    const stopNameLabel     = document.createElement("strong");
    const stopNumberLabel   = document.createElement("small");

    listGroupItem.className = "list-group-item list-group-item-action";
    listGroupItem.setAttribute("id", aBusStop.number);
    //listGroupItem.setAttribute("aria-current", "true");

    topRow.className = "d-flex w-100 justify-content-between";
    stopNameLabel.className = "mb-1";
    stopNumberLabel.className = "";

    stopNameLabel.innerHTML = "(" + aBusStop.index + ") " + aBusStop.name;
    stopNumberLabel.innerHTML = "#" + aBusStop.number;

    listGroupItem.appendChild( topRow );
        topRow.appendChild( stopNameLabel );
        topRow.appendChild( stopNumberLabel );

    listGroupItem.onclick = () =>
    {
        map.panTo( aBusStop.marker.getPosition() );
        aBusStop.marker.setAnimation( google.maps.Animation.BOUNCE );

        // This BusStop object has no scheduled time nor estimated time. The assumed reason is
        // that this information has not been requested yet from the server.
        if( aBusStop.scheduled_arrival === defaultTimeString || aBusStop.est_arrival === defaultTimeString )
        {
            // So, tell the user that the info is being retrieved.
            const arrivalPlaceholder = document.createElement("p");
                arrivalPlaceholder.setAttribute("id", "arrivalPlaceholder");
                arrivalPlaceholder.innerHTML = "Retrieving arrival times... ";

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

                // Check if this is the first time the arrivals are requested for this bus stop.
                // If so, generate <p> elements that will contain that info.
                if( listGroupItem.querySelector("#arrivalTimes") === null )
                {
                    const arrivalTimes = document.createElement("p");
                        arrivalTimes.setAttribute("id", "arrivalTimes");
                    const estArrival = document.createElement("p");
                        estArrival.setAttribute("id", "estArrival");
                    const schArrival = document.createElement("p");
                        schArrival.setAttribute("id", "schArrival");

                    arrivalTimes.appendChild( schArrival );
                    arrivalTimes.appendChild( estArrival );
                    listGroupItem.appendChild( arrivalTimes );
                }

                // .callbackMethod() has already updated the BusStop object's
                // .scheduled_arrival and .est_arrival data members by this point.
                // All that needs to be done is display them.
                listGroupItem.querySelector("#estArrival").innerHTML = "<small>Estimated Arrival Time</small><br />" + aBusStop.est_arrival;
                listGroupItem.querySelector("#schArrival").innerHTML = "<small>Scheduled Arrival Time</small><br />" + aBusStop.scheduled_arrival;

                listGroupItem.querySelector("#arrivalPlaceholder").remove();

            });


        }


    }

    return listGroupItem;
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
        container.setAttribute("id", "busStopInfoPlaceholder_route" + key)

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