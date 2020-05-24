"""openKirkes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from django.conf.urls import url, include
from django.contrib import admin

from openKirkesApi.views import api_guide, error_404

urlpatterns = [
    url(r'^openkirkes-admin/', admin.site.urls),
    url('api/', include('openKirkesApi.urls')),
    url(r'^$', api_guide),
    url(r'^', error_404)

]
