/*
    Creates a div that represents an accordion list element for an accordion list.
    ARGS:
        String  id      - Unique suffix for all of an accordion element's relevant child elements
        String  label   - Text to appear on the accordion expand button
        div     content - Element(s) that will be .innerHTML()-ed into the accordion's body.
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

    header.setAttribute("id", "accordionHeader" + id);

    button.setAttribute("type", "button");
    button.setAttribute("data-bs-toggle", "collapse");
    button.setAttribute("data-bs-target", "#accordionCollapse" + id);
    button.setAttribute("aria-expanded", "false");
    button.setAttribute("aria-controls", "accordionCollapse"+ id);
    button.innerHTML = label;

    collapse.setAttribute("id", "accordionCollapse" + id);
    collapse.setAttribute("aria-labelledby", "accordionHeader" + id);
    collapse.setAttribute("data-bs-parent", "#leftOffcanvasAccordion"); // TODO: "#leftOffcanvasAccordion must be a param eventually

    // So apparently JS is case-sensitive and .innerHtml is not the same as .innerHTML
    // body.innerHTML = content;
    createBusStopInfoForOffcanvasAccordionBody( body, "Route 51" );

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
        div accordionDiv    - Element where the containers generated will be appended to.
        int routeId         - An id of a route whose info the accordion body will be composed of.
 */
function createBusStopInfoForOffcanvasAccordionBody( accordionDiv, routeId )
{
    // This for loop is simply to see if the generated container are formatted correctly.
    for( let i = 1; i < 10; i++ )
    {
        const busStopInfoContainer = generateStopInfoContainer(
            i,
            "Bus Stop #" + i,
            "Estimated Arrival Time: Never",
            "Scheduled Arrival Time: Nope"
        );

        accordionDiv.appendChild( busStopInfoContainer );
    }
    /*
    // Ripped from map_index.js
    jQuery.ajax({
        url: ROUTE_DETAILS,
        data: {'data': JSON.stringify(routeId)},
        type: "GET",
        dataType: 'json',
        success: (data) => {
            if (data) {
                data.all_stops.forEach((busStopJSONInfo) => {

                    const busStopInfoContainer = generateStopInfoContainer(
                        busStopJSONInfo.BusStopNumber,
                        busStopJSONInfo.BusStopName,
                        "???",          // TODO: Since this is dynamic, there has to be a way to update this.
                        "???"           // This too.
                    );

                    accordionDiv.appendChild( busStopInfoContainer );
                })
            } else
                console.log("No stops found for the given route.")
            resolve("Resolved")
        },
        error: (e) => {
            console.log(e.message)
            reject("rejected")
        }
    });*/
}

/*
    Creates a container for info on a singular bus stop.
 */
function generateStopInfoContainer( stopNumber, param_stopName, param_estTime, param_schTime )
{
    const container = document.createElement("div");
    const row       = document.createElement("div");
    const bPointDiv = document.createElement("div");    // A bullet point
    const bPointImg = document.createElement("i");
    const stopDiv   = document.createElement("div");    // Bus stop info container
    const stopName  = document.createElement("div");    // Bus stop name
    const estTime   = document.createElement("div");    // Estimated time
    const schTime   = document.createElement("div");    // Scheduled time

    container.className = "container bus-stop-container";
        container.setAttribute("id", stopNumber);
        row.className = "row";
            bPointDiv.className = "col-1 bus-stop-bullet-point";
                bPointImg.className = "fa fa-circle";   // Provided by FontAwesome 4.7.0
            stopDiv.className = "col-10";
                stopName.className = "row";
                    stopName.innerHTML = param_stopName;
                estTime.className  = "row";
                    estTime.innerHTML = param_estTime;
                schTime.className  = "row";
                    schTime.innerHTML = param_schTime;

    container.appendChild( row );
        row.appendChild( bPointDiv );
            bPointDiv.appendChild( bPointImg );
        row.appendChild( stopDiv );
            stopDiv.appendChild( stopName );
            stopDiv.appendChild( estTime );
            stopDiv.appendChild( schTime );

    return container;
}

// ALL_ACTIVE_ROUTES is from map_index.html, which provides an array of routes.
// The way it is obtained is out of scope for frontend.
for( let key in ALL_ACTIVE_ROUTES )
{
    document.getElementById("leftOffcanvasAccordion").appendChild(
        createAccordionElement(
            "route" + key,
            ALL_ACTIVE_ROUTES[key],
            "Route content goes here"
        )
    );
}

