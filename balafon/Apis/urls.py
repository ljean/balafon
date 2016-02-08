# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

#from rest_framework import routers
#from balafon.Apis import views

#router = routers.DefaultRouter()
#router.register(r'crm-groups', views.GroupViewSet)
#
#print router.urls
#
#urlpatterns = patterns('',
#    url(r'^apis/', include(router.urls)),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
#)

from tastypie.api import Api
from balafon.Apis.resources import GroupResource, ContactResource

v1_api = Api(api_name='v1')
v1_api.register(GroupResource())
v1_api.register(ContactResource())

# Standard bits...
urlpatterns = patterns('',
    (r'^apis/', include(v1_api.urls)),
)