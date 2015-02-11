# -*- coding: utf-8 -*-
import sys

from django.conf import settings

if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.conf.urls import url, patterns, include

from django.contrib import admin
admin.autodiscover()

if getattr(settings, 'SANZA_NOTIFY_SUBSCRIPTIONS', ''):
    raise Exception(u"Invalid setting : SANZA_NOTIFY_SUBSCRIPTIONS has been replaced by SANZA_NOTIFICATION_EMAIL")

urlpatterns = patterns('',
    url(r'^crm/$', 'sanza.Users.views.user_homepage', name="sanza_homepage"),
    (r'^crm/', include('sanza.Crm.urls')),
    (r'^crm-search/', include('sanza.Search.urls')),
    (r'^emailing/', include('sanza.Emailing.urls')),
    #url(r'^accounts/profile/$', 'sanza.Crm.views.view_board_panel'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    #url(r'^export-database$', 'sanza.views.export_database_json', name="export_database_json"),
    url('^crm/go-to-home/', 'sanza.views.redirect_to_homepage', name="homepage"),
    url(r'^auto-save/(?P<model_type>\w+)/(?P<field_name>[\w-]+)/(?P<obj_id>\d+)/$', 'sanza.views.auto_save_data', name="auto_save_data"),
)

if 'djrill' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^mandrill/', include('djrill.urls')),
    )

if 'captcha' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^captcha/', include('captcha.urls')),
    )

if 'sanza.Apis' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'', include('sanza.Apis.urls')),
    )
    
if 'sanza.Profile' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^accounts/', include('sanza.Profile.urls')),
    )

urlpatterns += patterns('',
    (r'^accounts/', include('django.contrib.auth.urls')),
)

if 'sanza.Users' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^users/', include('sanza.Users.urls')),
    )
    
if 'jhouston' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^jhouston/', include('jhouston.urls')),
    )

if getattr(settings, 'SANZA_AS_HOMEPAGE', False):
    urlpatterns += patterns('',
        url(r'^$', 'sanza.Users.views.user_homepage', name='homepage'),
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

