# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.conf import settings
import sys

if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.contrib import admin
admin.autodiscover()

if getattr(settings, 'SANZA_NOTIFY_SUBSCRIPTIONS', ''):
    raise Exception(u"Invalid setting : SANZA_NOTIFY_SUBSCRIPTIONS has been replaced by SANZA_NOTIFICATION_EMAIL")

urlpatterns = patterns('',
    url(r'^crm/$', 'sanza.Crm.views.view_board_panel', name="sanza_homepage"),
    (r'^crm/', include('sanza.Crm.urls')),
    (r'^crm-search/', include('sanza.Search.urls')),
    (r'^emailing/', include('sanza.Emailing.urls')),
    #url(r'^accounts/profile/$', 'sanza.Crm.views.view_board_panel'),
    (r'^accounts/', include('django.contrib.auth.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^export-database$', 'sanza.views.export_database_json', name="export_database_json"),
    url('^crm/go-to-home/', 'sanza.views.redirect_to_homepage', name="homepage")
)

if 'jhouston' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^jhouston/', include('jhouston.urls')),
    )

if getattr(settings, 'SANZA_AS_HOMEPAGE', False):
    urlpatterns += patterns('',
        url(r'^$', 'sanza.Crm.views.view_board_panel', name='homepage'),
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

