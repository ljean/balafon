# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import patterns, include, url
from django.conf import settings
import sys

if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('coop_cms.apps.email_auth.urls')),
    (r'^accounts/', include('django.contrib.auth.urls')),
)

if settings.DEBUG or ('test' in sys.argv) or getattr(settings, 'SERVE_STATIC', True):
    if settings.DEBUG:
        urlpatterns += patterns('django.contrib.staticfiles.views',
            url(r'^static/(?P<path>.*)$', 'serve'),
        )
    else:
        urlpatterns += patterns('',
            (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        )
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )
    
urlpatterns += patterns('',
    (r'^djaloha/', include('djaloha.urls')),
    (r'^', include('coop_cms.urls')),
    (r'^coop_bar/', include('coop_bar.urls')),
)