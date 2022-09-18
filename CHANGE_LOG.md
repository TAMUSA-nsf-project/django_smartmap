[comment]: <> (Always add the latest change on top of this file so that it appears in the reverse chronological order.)

## Aug 31, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/ed9e1e4f-e7cf-45ad-a8e9-647ece875cd5?authuser=0&project=nsf-2131193-18902)
1. Adding a collapsable legend box to google maps. These shows bus color meaning according to bus occupancy status.

Security Testing details - TBD

## Aug 30, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/7caa8be6-80dc-4e38-a14d-773b0d9c289d?authuser=0&project=nsf-2131193-18902)
1. Adjusting the route line Width Adding '*' to the ALLOWED_HOSTS in development.py
2. Adding UI fixes for bus driver page. Big buttons for occupancy status.
3. Fix bug with buttons in busdriver_2.html, restylized seat-availability buttons

Security Testing details - TBD

## Aug 23, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/39f8938a-5894-4b74-919b-7d1e656e8557?authuser=0&project=nsf-2131193-18902)
1. Adding separation of variables to the settings file. Now there will be separate files to hold default, development and production settings.
2. Adding remaining bus schedule details except Route 93

Security Testing details - TBD

## Aug 15, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/39f8938a-5894-4b74-919b-7d1e656e8557?authuser=0&project=nsf-2131193-18902)
1. Modified 'map/static/map/js/map_index.js' to introduce logic to draw the route polyline based on bus position.
2. Added interface to indicate the occupancy status to the Bus Driver page.

Security Testing details - TBD

## Aug 13, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/5fc2c14d-38ed-416e-9456-034cdc37bb6d?authuser=0&project=nsf-2131193-18902)
1. Introduced BusSchedule database model in 'bus/models.py'
2. Modified 'bus/views.py' use the newly added 'BusSchedule' table value to calculate the ETA for a bus stop.
3. Added schedule details predata to 'route_data/bus_schedules.json'

Security Testing details - TBD

## Aug 9, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/078314d3-0f89-4d28-b5d5-d2e53920b346?authuser=0&project=nsf-2131193-18902)
1. Using CDT time zone value for Estimated time of arrival.

Security Testing details - TBD

## Aug 4, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/efe936a8-5e7c-47e0-9bb0-55158d28d69c?authuser=0&project=nsf-2131193-18902)
1. Migration file dependency bug fix.
2. Fixing Google Maps mobile appearance changes in 'main/templates/main/nsf_footer.html' and 'map/static/map/js/map_index.js'
3. TODO: Discuss with Ali

Security Testing details - TBD

## Aug 3, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/0ea1d3d9-7f92-4e30-8b6e-b4bb8a9c1539?authuser=0&project=nsf-2131193-18902)
1. Modified 'bus/apps.py' and 'users/apps.py' to move the predata population logic to use post migrate signal. Now pre data check will be performed after each database migration.
2. Restricting the access to transit log view page only to admins.
3. Refactoring the message shown on the info window.

Security Testing details - TBD

## Aug 3, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/0ac1b9b3-bd22-424e-ad04-b05ad0939278?authuser=0&project=nsf-2131193-18902)
1. Modified 'bus/apps.py' and 'users/apps.py' to move the predata population logic to use post migrate signal. Now pre data check will be performed after each database migration.

Security Testing details - TBD


## Aug 2, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/0ac1b9b3-bd22-424e-ad04-b05ad0939278?authuser=0&project=nsf-2131193-18902)
1. Modifying the Bus start and End time field to use UTC.
2. Modified 'map/static/map/js/map_index.js' to add ETA for a given bus stop.
3. Modified 'bus/views.py' to add logic to calculate estimated arrival time.

Security Testing details - TBD

## Aug 1, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/13ae8fd9-4821-41cf-9204-5f433a51c80e?authuser=0&project=nsf-2131193-18902)
1. Introduced new page to view transit log details. 'bus/templates/bus/transit_log_entries.html'
2. Added option to download transit log as an excel file.

Security Testing details - TBD

## Jul 27, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/30cda7a4-bb9c-4f83-92c8-b846f2748ab4?authuser=0&project=nsf-2131193-18902)
1. Warn driver with popup if they try to leave the page while toggle-switch is activated

Security Testing details - TBD

## Jul 22, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/744c6a31-e134-4a73-82fb-8d35934348e6?authuser=0&project=nsf-2131193-18902)
1. Modified 'map/static/map/js/map_index.js' to pan the google maps to proper view bounds based on a route selection.
2. Added bus model migration file for meta data changes

Security Testing details - TBD

## Jul 20, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/bc317670-db22-4d56-9e28-434df893adeb?authuser=0&project=nsf-2131193-18902)
1. Modified 'bsuroute' model to add 'color_code' field.
2. Modified 'getRouteDetails' under 'commons/helper.py' to return the new color_code field.
3. Updated front end code in 'map/static/map/js/map_index.js' to set the location pin color based on the database value.
4. Modified 'map/static/map/js/map_index.js' to adjust the anchor point for bus icon.

Security Testing details - TBD


## Jul 19, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/e39af40a-8b4c-4b75-91d0-aac29013f196?authuser=0&project=nsf-2131193-18902)
1. Modified 'bus/templates/bus/busdriver_2.html' to add start and stop driving toggle switch.
2. Modified 'bus/views.py' to add method to remove the bus object from 'buses' table when bus driver clicks stop driving.

Security Testing details - TBD

## Jul 18, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/53bef708-f6b3-4a6e-9ae6-e6a51d091bad?authuser=0&project=nsf-2131193-18902)
1. Introduced a new app named 'commons' to add common functionalities reused across other apps.
2. Added methods 'getAllActiveRoutesDropDown' and 'getRoutesDetails(route_id)' in commons app under unit 'helper'. These methods will return all the existing Routes and route details respectively.
3. Front end code now load and cache the route details based on user selection instead of loading all routes during start up.
4. Removed socket IO related un used code from views.py file of 'maps' app.
5. Added 'getRouteDetailsAJAX' method to views of 'maps' app.
6. Added 'route' Foreign key to Bus model.

Security Testing details - TBD

## Jul 14, 2022
[Build Details](https://console.cloud.google.com/cloud-build/builds;region=global/51b37fe8-063d-4c94-a8da-3c08975cee1d?authuser=0&project=nsf-2131193-18902)
1. Automated code build and deployment using Google cloud build.
2. Started using docker for deployment and packaging.
3. Updated interval for bus position broadcast.
4. Added instructions to emulate bus on a particular route using android emulator.

Security Testing details - TBD
