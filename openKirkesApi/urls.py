
#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from django.conf.urls import url, include
from django.views.generic import TemplateView

from rest_framework import routers
from .views import loans, login

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url('', include(router.urls)),
    url(r'^loans/', loans),
    url(r'^login/', login)
]
