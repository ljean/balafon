# -*- coding: utf-8 -*-

from django.conf.urls import url

from balafon.Search import views


urlpatterns = [
    url(r'^quick-search/$', views.quick_search, name='quick_search'),
    url(r'^$', views.search, name='search'),
    url(r'^(?P<search_id>\d+)/$', views.search, name='search'),
    url(r'^group/(?P<group_id>\d+)/$', views.search, name='search_group'),
    url(r'^opportunity/(?P<opportunity_id>\d+)/$', views.search, name='search_opportunity'),
    url(r'^city/(?P<city_id>\d+)/$', views.search, name='search_cities'),
    url(r'^get-field/(?P<name>\w+)/$', views.get_field, name='search_get_field'),
    url(r'^mailto/(?P<bcc>\d+)/$', views.mailto_contacts, name='search_mailto_contacts'),
    url(r'^save-search/(?P<search_id>\d+)/$', views.save_search, name='search_save'),
    url(r'^list/$', views.view_search_list, name='search_list'),
    url(r'^emailing/$', views.create_emailing, name='search_emailing'),
    url(r'^as-excel/$', views.export_contacts_as_excel, name='search_export_contacts_as_excel'),
    url(r'^create-actions/$', views.create_action_for_contacts, name='search_create_action_for_contacts'),
    url(r'^add-contacts-to-group/$', views.add_contacts_to_group, name='search_add_contacts_to_group'),
    url(r'^contacts-admin/$', views.contacts_admin, name='search_contacts_admin'),
    url(r'^export_to_pdf/$', views.export_to_pdf, name='search_export_to_pdf'),
]