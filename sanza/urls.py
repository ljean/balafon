# -*- coding: utf-8 -*-

import sys

from django.conf import settings
from django.conf.urls import include, url, patterns
from django.contrib.auth import views as django_auth_views
from django.contrib.staticfiles.views import serve as serve_static
from django.views.static import serve as serve_media

from coop_cms.settings import get_url_patterns, get_media_root

from sanza.forms import BsAuthenticationForm, BsPasswordChangeForm, BsPasswordResetForm
from sanza.Users import views as users_views
from sanza.views import redirect_to_homepage, auto_save_data

if getattr(settings, 'SANZA_NOTIFY_SUBSCRIPTIONS', ''):
    raise Exception(u"Invalid setting : SANZA_NOTIFY_SUBSCRIPTIONS has been replaced by SANZA_NOTIFICATION_EMAIL")


localized_patterns = get_url_patterns()

urlpatterns = [
    url(r'^crm/$', users_views.user_homepage, name="sanza_homepage"),
]


if settings.DEBUG or ('test' in sys.argv) or getattr(settings, 'SERVE_STATIC', True):
    if settings.DEBUG:
        urlpatterns += [
            url(r'^static/(?P<path>.*)$', serve_static),
        ]
    else:
        urlpatterns += [
            url(r'^static/(?P<path>.*)$', serve_media, {'document_root': settings.STATIC_ROOT}),
        ]
    urlpatterns += patterns(
        '',
        url(
            r'^media/(?P<path>.*)$',
            serve_media,
            {'document_root': get_media_root(), 'show_indexes': True}
        ),
    )


urlpatterns += localized_patterns('',
    url(r'^crm/', include('sanza.Crm.urls')),
    url(r'^crm/', include('sanza.Crm.api_urls')),
    url(r'^crm-search/', include('sanza.Search.urls')),
    url('^crm/go-to-home/', redirect_to_homepage, name="homepage"),
    url(
        r'^auto-save/(?P<model_type>\w+)/(?P<field_name>[\w-]+)/(?P<obj_id>\d+)/$',
        auto_save_data,
        name="auto_save_data"
    ),
    url(r'^emailing/', include('sanza.Emailing.urls')),
    url(r'^accounts/', include('coop_cms.apps.email_auth.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
)


if 'djrill' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^mandrill/', include('djrill.urls')),
    ]


if 'captcha' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^captcha/', include('captcha.urls')),
    ]


if 'sanza.Apis' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'', include('sanza.Apis.urls')),
    ]


if 'coop_cms.apps.email_auth' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns('',
        url(r'^accounts/', include('coop_cms.apps.email_auth.urls'))
    )

else:
    urlpatterns += localized_patterns('',
        url(
            r'^accounts/login/$',
            django_auth_views.login,
            {'authentication_form': BsAuthenticationForm},
            name='login'
        ),
        url(r'^accounts/password_change/$',
            django_auth_views.password_change,
            {'password_change_form': BsPasswordChangeForm},
            name='password_change'
        ),
        url(
            r'^accounts/password_reset/$',
            django_auth_views.password_reset,
            {'password_reset_form': BsPasswordResetForm},
            name='password_reset'
        ),
        url(r'^accounts/', include('django.contrib.auth.urls'))
    )


if 'sanza.Profile' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns('',
        url(r'^accounts/', include('sanza.Profile.urls'))
    )


if 'sanza.Store' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns('',
        url(r'^store/', include('sanza.Store.urls')),
        url(r'^store/', include('sanza.Store.api_urls'))
    )


if 'sanza.Users' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns('',
        url(r'^users/', include('sanza.Users.urls')),
    )


if 'jhouston' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^jhouston/', include('jhouston.urls')),
    ]


if getattr(settings, 'SANZA_AS_HOMEPAGE', False):
    urlpatterns += [
        url(r'^$', users_views.user_homepage, name='homepage'),
    ]


urlpatterns += localized_patterns(
    '',
    url(r'^', include('coop_cms.urls')),
)
