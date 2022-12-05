/*
    offcanvas.js is a javascript that handles the route offcanvas list used in map_index.js.
    Note that javascript files can share variables and functions (by default I think? Maybe
    because they are both used in map_index.html).
    - Emmer
 */

// ALL_ACTIVE_ROUTES is from 'map_index.html', which provides an array of routes.
for( let key in ALL_ACTIVE_ROUTES )
{
    let aRoutesAccordionInfo = createAccordionElement(
        "route" + key,
        ALL_ACTIVE_ROUTES[key],
        generateBusStopPlaceholder()
    )

    aRoutesAccordionInfo.onclick = () => {
        if (mapRouteMarkers[key]) {
            hideDisplayedMarkers()
            showRouteMarkers(key)
            getActiveBussesOnSelectedRoute()
        } else {
            initRouteMarkers(key).then((res) => {
                hideDisplayedMarkers()
                showRouteMarkers(key)
                getActiveBussesOnSelectedRoute()
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
    body.className     = "accordion-body";

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
function createBusStopInfoForOffcanvasAccordionBody( routeId )
{
    jQuery.ajax({
        url: ROUTE_DETAILS,
        data: {'data': JSON.stringify(routeId)},
        type: "GET",
        dataType: 'json',
        success: (data) => {
            if (data) {
                console.log(data)
                const returnDiv = document.createElement("div");
                console.log("beep");
                data.all_stops.forEach((busStop) => {
                    //mapRouteMarkers[route_id].push(new BusStop(busStop));
                    const busStopInfoContainer = generateStopInfoContainer(
                        busStop.BusStopIndex,
                        busStop.BusStopName,
                        "Estimated Arrival Time: " + defaultTimeString,
                        "Scheduled Arrival Time: " + defaultTimeString
                    );
                    returnDiv.appendChild( busStopInfoContainer );
                })

                return returnDiv;
            } else
                console.log("No stops found for the given route.")
            resolve("Resolved")
        },
        error: (e) => {
            console.log(e.message)
            reject("rejected")
        }
    });

}

/*
    Creates a container(div) of info on a singular bus stop.
 */
function generateStopInfoContainer( stopNumber, stopName, estTime, schTime )
{
    const container = document.createElement("div");
    const row       = document.createElement("div");
    const bPointDiv = document.createElement("div");    // A bullet point
    const bPointImg = document.createElement("i");
    const stopDiv   = document.createElement("div");    // Bus stop info container
    const stopNameDiv   = document.createElement("div");
    const stopNumberDiv = document.createElement("div");
    const estTimeDiv    = document.createElement("div");    // Estimated time
    const schTimeDiv    = document.createElement("div");    // Scheduled time

    container.className = "container bus-stop-container";
        container.setAttribute("id", stopNumber);
        row.className = "row";
            bPointDiv.className = "col-1 bus-stop-bullet-point";
                bPointImg.className = "fa fa-circle";   // Icon provided by FontAwesome 4.7.0
            stopDiv.className = "col-10";
                stopNameDiv.className = "row";
                    stopNameDiv.innerHTML = stopName;
                stopNumberDiv.className = "row";
                    stopNumberDiv.innerHTML = stopNumber;
                estTimeDiv.className  = "row";
                    estTimeDiv.innerHTML = estTime;
                schTimeDiv.className  = "row";
                    schTimeDiv.innerHTML = schTime;

    container.appendChild( row );
        row.appendChild( bPointDiv );
            bPointDiv.appendChild( bPointImg );
        row.appendChild( stopDiv );
            stopDiv.appendChild( stopNameDiv );
            stopDiv.appendChild( stopNumberDiv );
            stopDiv.appendChild( estTimeDiv );
            stopDiv.appendChild( schTimeDiv );

    return container;
}

function generateBusStopPlaceholder()
{
    const container = document.createElement("div");

    container.className = "container bus-stop-container";
    container.setAttribute("aria-hidden", "true");

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