# -*- coding: utf-8 -*-

from sanza.urls import urlpatterns as sanza_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = sanza_urlpatterns
