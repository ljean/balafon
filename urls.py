# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings
import sys
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^crm/$', 'sanza.Crm.views.view_board_panel', name="sanza_homepage"),
    (r'^crm/', include('sanza.Crm.urls')),
    (r'^search/', include('sanza.Search.urls')),
    (r'^emailing/', include('sanza.Emailing.urls')),
    #url(r'^accounts/profile/$', 'sanza.Crm.views.view_board_panel'),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^export-database$', 'sanza.views.export_database_json', name="export_database_json"),
)

if 'jhouston' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^jhouston/', include('jhouston.urls')),
    )

if getattr(settings, 'SANZA_AS_HOMEPAGE', False):
    urlpatterns += patterns('',
        url(r'^$', 'sanza.Crm.views.view_board_panel'),
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

