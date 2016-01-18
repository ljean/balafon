# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

from coop_cms.settings import get_url_patterns

from sanza.urls import urlpatterns as sanza_urlpatterns


admin.autodiscover()

localized_patterns = get_url_patterns()

urlpatterns = localized_patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += sanza_urlpatterns
