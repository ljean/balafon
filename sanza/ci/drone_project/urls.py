# -*- coding: utf-8 -*-

from django.contrib import admin

from sanza.urls import urlpatterns as sanza_urlpatterns

admin.autodiscover()

urlpatterns = sanza_urlpatterns
