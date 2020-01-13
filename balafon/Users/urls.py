# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import url

from balafon.Users import views

urlpatterns = [
    url(r'^toggle/$', views.toggle_favorite, name='users_toggle_favorite'),
    url(r'^list/$', views.list_favorites, name='users_favorites_list'),
    url(r'^make-homepage/$', views.make_homepage, name='users_make_homepage'),
]