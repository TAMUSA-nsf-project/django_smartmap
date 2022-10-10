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
    body.innerHTML = content;

    header.appendChild( button );
    collapse.appendChild( body );
    item.appendChild( header );
    item.appendChild( collapse );

    return item;
}

/*
    Generates material for the content section of accordion elements.
    ARGS:
        int routeId - The route info to compose.
    RETURN:
        A div displaying a route's information.
 */
function displayRouteInfoForOffcanvas( routeId )
{
    const item  = document.createElement("div");
    const dot   = document.createElement("i");

    dot.className = "fa-solid fa-circle-dot";
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

