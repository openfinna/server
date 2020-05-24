#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from django.conf.urls import url, include
from rest_framework import routers

from .views import loans, login, holds, pickupLocations, changePickupLocation, lib_info, renew_loan, search, details, \
    details_raw, hold, changeDefaultPickupLocation, getDefaultLocation, fines, user_details, cancel_hold

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('', include(router.urls)),
    url(r'^loans/renew', renew_loan),
    url(r'^loans/', loans),
    url(r'^holds/cancel', cancel_hold),
    url(r'^holds/make', hold),
    url(r'^holds/', holds),
    url(r'^search/', search),
    url(r'^libraries/', lib_info),
    url(r'^pickup_locations/change/default', changeDefaultPickupLocation),
    url(r'^pickup_locations/change/', changePickupLocation),
    url(r'^pickup_locations/default', getDefaultLocation),
    url(r'^pickup_locations/', pickupLocations),
    url(r'^fines/', fines),
    url(r'^login/', login),
    url(r'^account/', user_details),
    url(r'^details/raw', details_raw),
    url(r'^details/', details)
]
