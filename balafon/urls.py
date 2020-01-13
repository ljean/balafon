# -*- coding: utf-8 -*-

import sys

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth import views as django_auth_views
from django.contrib.staticfiles.views import serve as serve_static
from django.views.static import serve as serve_media

from coop_cms.settings import get_url_patterns, get_media_root

from balafon.forms import BsAuthenticationForm, BsPasswordChangeForm, BsPasswordResetForm
from balafon.Users import views as users_views
from balafon.views import redirect_to_homepage, auto_save_data


if getattr(settings, 'BALAFON_NOTIFY_SUBSCRIPTIONS', ''):
    raise Exception("Invalid setting : BALAFON_NOTIFY_SUBSCRIPTIONS has been replaced by BALAFON_NOTIFICATION_EMAIL")


localized_patterns = get_url_patterns()


urlpatterns = [
    url(r'^crm/$', users_views.user_homepage, name="balafon_homepage"),
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
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            serve_media,
            {'document_root': get_media_root(), 'show_indexes': True}
        ),
    ]


urlpatterns += localized_patterns(
    url(r'^crm/', include('balafon.Crm.urls')),
    url(r'^crm/', include('balafon.Crm.api_urls')),
    url(r'^crm-search/', include('balafon.Search.urls')),
    url('^crm/go-to-home/', redirect_to_homepage, name="homepage"),
    url(
        r'^auto-save/(?P<model_type>\w+)/(?P<field_name>[\w-]+)/(?P<obj_id>\d+)/$',
        auto_save_data,
        name="auto_save_data"
    ),
    url(r'^emailing/', include('balafon.Emailing.urls')),
)

if 'coop_cms.apps.email_auth' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns(
        url(r'^accounts/', include('coop_cms.apps.email_auth.urls')),
    )
    if 'django_registration' in settings.INSTALLED_APPS and 'balafon.Profile' not in settings.INSTALLED_APPS:
        urlpatterns += localized_patterns(
            url(r'^accounts/', include('coop_cms.apps.email_auth.registration_backend.urls')),
        )
else:
    urlpatterns += localized_patterns(
        url(
            r'^accounts/login/$',
            django_auth_views.LoginView.as_view(authentication_form=BsAuthenticationForm),
            name='login'
        ),
        url(r'^accounts/password_change/$',
            django_auth_views.PasswordChangeView.as_view(form_class=BsPasswordChangeForm),
            name='password_change'
        ),
        url(
            r'^accounts/password_reset/$',
            django_auth_views.PasswordResetView.as_view(form_class=BsPasswordResetForm),
            name='password_reset'
        ),
    )


urlpatterns += localized_patterns(
    url(r'^accounts/', include('django.contrib.auth.urls'))
)


if 'balafon.Profile' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns(
        url(r'^accounts/', include('balafon.Profile.urls'))
    )


if 'balafon.Store' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns(
        url(r'^store/', include('balafon.Store.urls')),
        url(r'^store/', include('balafon.Store.api.urls'))
    )

if 'balafon.Users' in settings.INSTALLED_APPS:
    urlpatterns += localized_patterns(
        url(r'^users/', include('balafon.Users.urls')),
    )


if getattr(settings, 'BALAFON_AS_HOMEPAGE', False):
    urlpatterns += [
        url(r'^$', users_views.user_homepage, name='homepage'),
    ]


urlpatterns += localized_patterns(
    url(r'^', include('coop_cms.urls')),
)
