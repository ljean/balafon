# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('sanza.Users.views',
    url(r'^toggle/$', 'toggle_favorite', name='users_toggle_favorite'),
    url(r'^list/$', 'list_favorites', name='users_favorites_list'),
    url(r'^make-homepage/$', 'make_homepage', name='users_make_homepage'),
)