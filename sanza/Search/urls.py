# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('sanza.Search.views',
    url(r'^quick-search$', 'quick_search', name='quick_search'),
    url(r'^$', 'search', name='search'),
    url(r'^(?P<search_id>\d+)$', 'search', name='search'),
    url(r'^group/(?P<group_id>\d+)$', 'search', name='search_group'),
    url(r'^opportunity/(?P<opportunity_id>\d+)$', 'search', name='search_opportunity'),
    url(r'^get-field/(?P<name>\w+)$', 'get_field', name='search_get_field'),
    url(r'^mailto/(?P<bcc>\d+)$', 'mailto_contacts', name='search_mailto_contacts'),
    url(r'^save/(?P<search_id>\d*)$', 'save_search', name='search_save'),
    url(r'^list$', 'view_search_list', name='search_list'),
    url(r'^emailing$', 'create_emailing', name='search_emailing'),
    url(r'^as-excel$', 'export_contacts_as_excel', name='search_export_contacts_as_excel'),
    url(r'^create-actions$', 'create_action_for_contacts', name='search_create_action_for_contacts'),
    url(r'^add-contacts-to-group$', 'add_contacts_to_group', name='search_add_contacts_to_group'),
    url(r'^contacts-admin$', 'contacts_admin', name='search_contacts_admin'),
    url(r'^export_to_pdf$', 'export_to_pdf', name='search_export_to_pdf'),
)