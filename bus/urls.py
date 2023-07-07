"""Defines URL patterns for map app."""
from django.urls import path
from . import views

app_name = "bus"
urlpatterns = [
    # Bus driver
    path('busdriver/', views.busdriver_view, name='busdriver-page'),
    path('busposition-ajax/', views.bus_position_ajax, name='busposition-ajax'),
    path('bushasendedbroadcast-ajax/', views.deleteBusHasEndedBroadcastAJAX, name='bushasendedbroadcast-ajax'),

    # User-requested bus data
    path('busestarrival-ajax/', views.getEstimatedArrivalAJAX, name='busestarrival-ajax'),
    path('activebussesonroute-ajax/', views.getActiveBussesOnRouteAJAX, name='activebussesonroute-ajax'),
    path('busroutepolyline-ajax/', views.getBusRouteGmapsPolylineEncodingAJAX, name='busroutepolyline-ajax'),
    path('buslaststop-ajax/', views.updateLastBusStopManualAJAX, name='buslaststop-ajax'),

    # Transit log
    path('transitlogs/', views.transit_logs_view, name='transitlogs'),
    path('transitlogs/<int:log_id>', views.transit_log_entries_view, name='transitlogentries'),
    path('downloadtransitlogcsv-ajax', views.downloadTransitLogCSV_AJAX, name='downloadtransitlogcsv-ajax'),

    # Seats
    path('seatavailability-ajax/', views.updateBusSeatAvailabilityAJAX, name='seatavailability-ajax'),

    # Bus route
    path('admin-view/', views.admin_view, name='admin-view'),
    path('all-active-buses-ajax/', views.getAllActiveBussesAJAX, name='all-active-buses-ajax'),
]
