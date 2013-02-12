# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('sanza.Profile.views',
    url(r'edit/$', 'edit_profile', name='profile_edit'),
)