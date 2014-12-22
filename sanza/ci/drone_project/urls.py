# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from sanza.urls import urlpatterns as sanza_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^localeurl/', include('localeurl.urls')),
    (r'^captcha/', include('captcha.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += sanza_urlpatterns