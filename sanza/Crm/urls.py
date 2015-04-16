# -*- coding: utf-8 -*-
"""urls"""
# pylint: disable=C0330

from django.conf.urls import patterns, url

from sanza.Crm.views import planning as planning_views, documents as document_views


urlpatterns = patterns('sanza.Crm.views.entities',
    url(r'^entities$', 'view_entities_list', name='crm_view_entities_list'),
    url(r'^entity/(?P<entity_id>\d+)/$', 'view_entity', name='crm_view_entity'),
    url(r'^edit-entity/(?P<entity_id>\d+)/$', 'edit_entity', name='crm_edit_entity'),
    url(r'^create-entity/(?P<entity_type_id>\d+)/$', 'create_entity', name='crm_create_entity'),
    url(r'^delete-entity/(?P<entity_id>\d+)/$', 'delete_entity', name='crm_delete_entity'),
    url(r'^change-contact-entity/(?P<contact_id>\d+)/$', 'change_contact_entity', name='crm_change_contact_entity'),
    url(r'^entity-name/(?P<entity_id>.+)/$', 'get_entity_name', name='crm_get_entity_name'),
    url(r'^entities/list/$', 'get_entities', name='crm_get_entities'),
    url(r'^entity-id/$', 'get_entity_id', name='crm_get_entity_id'),

)


urlpatterns += patterns('sanza.Crm.views.contacts',
    url(r'^add-contact/(?P<entity_id>\d+)/$', 'add_contact', name='crm_add_contact'),
    url(r'^add-single-contact/$', 'add_single_contact', name='crm_add_single_contact'),
    url(r'^delete-contact/(?P<contact_id>\d+)/$', 'delete_contact', name='crm_delete_contact'),
    url(r'^edit-contact/(?P<contact_id>\d+)/$', 'edit_contact', name='crm_edit_contact'),
    url(
        r'^edit-contact-advanced/(?P<contact_id>\d+)/$',
        'edit_contact',
        kwargs={'mini': False},
        name='crm_edit_contact_advanced'
    ),
    url(
        r'^edit-contact-on-create-entity/(?P<contact_id>\d+)/$',
        'edit_contact',
        kwargs={'go_to_entity': True},
        name='crm_edit_contact_after_entity_created'
    ),
    url(r'^view-contact/(?P<contact_id>\d+)/$', 'view_contact', name='crm_view_contact'),
    url(r'^contact-name/(?P<contact_id>.+)/$', 'get_contact_name', name='crm_get_contact_name'),
    url(r'^contacts/list/$', 'get_contacts', name='crm_get_contacts'),
    url(r'^contact-id/$', 'get_contact_id', name='crm_get_contact_id'),

)


urlpatterns += patterns('sanza.Crm.views.actions',
    url(
        r'^view-contact-actions/(?P<contact_id>\d+)/(?P<action_set_id>\d+)/$',
        'view_all_contact_actions',
        name='crm_view_contact_actions'
    ),
    url(
        r'^view-entity-actions/(?P<entity_id>\d+)/(?P<action_set_id>\d+)/$',
        'view_all_entity_actions',
        name='crm_view_entity_actions'
    ),
    url(r'^add-action-for-entity/(?P<entity_id>\d+)/$', 'add_action_for_entity', name='crm_add_action_for_entity'),
    url(r'^add-action-for-contact/(?P<contact_id>\d+)/$', 'add_action_for_contact', name='crm_add_action_for_contact'),
    url(r'^edit-action/(?P<action_id>\d+)/$', 'edit_action', name='crm_edit_action'),
    url(r'^do-action/(?P<action_id>\d+)/$', 'do_action', name='crm_do_action'),
    url(r'^delete-action/(?P<action_id>\d+)/$', 'delete_action', name='crm_delete_action'),
    url(r'^entity-actions/(?P<entity_id>\d+)/(?P<set_id>\d+)/$', 'view_entity_actions', name='crm_entity_actions'),
    url(r'^contact-actions/(?P<contact_id>\d+)/(?P<set_id>\d+)/$', 'view_contact_actions', name='crm_contact_actions'),
    url(r'^add-action/$', 'add_action', name='crm_add_action'),
    url(r'^all-actions/$', 'view_all_actions', name='crm_all_actions'),
    url(r'^add-contact-to-action/(?P<action_id>\d+)/$', 'add_contact_to_action', name='crm_add_contact_to_action'),
    url(r'^add-entity-to-action/(?P<action_id>\d+)/$', 'add_entity_to_action', name='crm_add_entity_to_action'),
    url(
        r'^remove-contact-from-action/(?P<action_id>\d+)/(?P<contact_id>\d+)/$',
        'remove_contact_from_action',
        name='crm_remove_contact_from_action'
    ),
    url(
        r'^remove-entity-from-action/(?P<action_id>\d+)/(?P<entity_id>\d+)/$',
        'remove_entity_from_action',
        name='crm_remove_entity_from_action'
    ),
    url(r'^create-action/(?P<entity_id>\d+)/(?P<contact_id>\d+)/$', 'create_action', name='crm_create_action'),
    url(r'allowed-action-status/$', 'get_action_status', name="crm_get_action_status"),
)


urlpatterns += patterns('sanza.Crm.views.relationships',
    url(r'^same-as/(?P<contact_id>\d+)/$', 'same_as', name='crm_same_as'),
    url(
        r'^remove-same-as/(?P<current_contact_id>\d+)/(?P<contact_id>\d+)/$',
        'remove_same_as',
        name='crm_remove_same_as'
    ),
    url(r'^add-relationship/(?P<contact_id>\d+)/$', 'add_relationship', name='crm_add_relationship'),
    url(
        r'^delete-relationship/(?P<contact_id>\d+)/(?P<relationship_id>\d+)/$',
        'delete_relationship',
        name='crm_delete_relationship'
    ),
    url(
        r'^make-main-contact/(?P<current_contact_id>\d+)/(?P<contact_id>\d+)/$',
        'make_main_contact',
        name='crm_make_main_contact'
    ),
)


urlpatterns += patterns('sanza.Crm.views.groups',
    url(r'^add-entity-to-group/(?P<entity_id>\d+)/$', 'add_entity_to_group', name='crm_add_entity_to_group'),
    url(r'^add-contact-to-group/(?P<contact_id>\d+)/$', 'add_contact_to_group', name='crm_add_contact_to_group'),
    url(r'^get-group-suggest-list/$', 'get_group_suggest_list', name='crm_get_group_suggest_list'),
    url(
        r'^remove-from-group/(?P<group_id>\d+)/(?P<entity_id>\d+)/$',
        'remove_entity_from_group',
        name='crm_remove_entity_from_group'
    ),
    url(
        r'^remove-contact-from-group/(?P<group_id>\d+)/(?P<contact_id>\d+)/$',
        'remove_contact_from_group',
        name='crm_remove_contact_from_group'
    ),
    url(r'^edit-group/(?P<group_id>\d+)/$', 'edit_group', name='crm_edit_group'),
    url(r'^delete-group/(?P<group_id>\d+)/$', 'delete_group', name='crm_delete_group'),
    url(r'^add-group/$', 'add_group', name='crm_add_group'),
    url(r'^my-groups/$', 'see_my_groups', name='crm_see_my_groups'),
    url(r'^group-name/(?P<gr_id>\d+)/$', 'get_group_name', name='crm_get_group_name'),
    url(r'^groups/list/$', 'get_groups', name='crm_get_groups'),
    url(r'^group-id/$', 'get_group_id', name='crm_get_group_id'),

)


urlpatterns += patterns('sanza.Crm.views.cities',
    url(r'^city-name/(?P<city>.*)/$', 'get_city_name', name='crm_get_city_name'),
    url(r'^cities/list/$', 'get_cities', name='crm_get_cities'),
    url(r'^city-id/$', 'get_city_id', name='crm_get_city_id'),
)


urlpatterns += patterns('sanza.Crm.views.bookmarks',
    url(r'^board/$', 'view_board_panel', name='crm_board_panel'),
    url(r'^toggle-action-bookmark/(?P<action_id>\d+)/$', 'toggle_action_bookmark', name='crm_toggle_action_bookmark'),
    url(
        r'^toggle-opportunity-bookmark/(?P<opportunity_id>\d+)/$',
        'toggle_opportunity_bookmark',
        name='crm_toggle_opportunity_bookmark'
    ),

)


urlpatterns += patterns('sanza.Crm.views.opportunities',
    url(r'^edit-opportunity/(?P<opportunity_id>\d+)/$', 'edit_opportunity', name='crm_edit_opportunity'),
    url(r'^view-opportunity/(?P<opportunity_id>\d+)/$', 'view_opportunity', name='crm_view_opportunity'),
    url(r'^delete-opportunity/(?P<opportunity_id>\d+)/$', 'delete_opportunity', name='crm_delete_opportunity'),
    url(r'^opportunities/(?P<entity_id>\d+)/$', 'view_entity_opportunities', name='crm_entity_opportunities'),
    url(r'^opportunities/$', 'view_all_opportunities', name='crm_all_opportunities'),
    url(r'^opportunities-by/(?P<ordering>.+)/$', 'view_all_opportunities', name='crm_all_opportunities_by'),
    url(r'^add-opportunity/$', 'add_opportunity', name='crm_add_opportunity'),
    url(r'^opportunity-name/(?P<opp_id>.+)/$', 'get_opportunity_name', name='crm_get_opportunity_name'),
    url(r'^opportunities/list/$', 'get_opportunities', name='crm_get_opportunities'),
    url(r'^opportunity-id/$', 'get_opportunity_id', name='crm_get_opportunity_id'),
    url(
        r'add-action-to-opportunity/(?P<action_id>\d+)/$',
        'add_action_to_opportunity',
        name='crm_add_action_to_opportunity'
    ),
    url(
        r'remove-action-from-opportunity/(?P<action_id>\d+)/(?P<opportunity_id>\d+)/$',
        'remove_action_from_opportunity',
        name='crm_remove_action_from_opportunity'
    ),
)


urlpatterns += patterns('sanza.Crm.views.custom_fields',
    url(
        r'^edit-custom-fields/(?P<model_name>\w+)/(?P<instance_id>\d+)/$',
        'edit_custom_fields',
        name='crm_edit_custom_fields'
    ),
)


urlpatterns += patterns('sanza.Crm.views.importers',
    url(r'^contacts-import/new/$', 'new_contacts_import', name='crm_new_contacts_import'),
    url(r'^contacts-import/(?P<import_id>\d+)/$', 'confirm_contacts_import', name='crm_confirm_contacts_import'),
    url(r'^contacts-import/template.csv$', 'contacts_import_template', name='crm_contacts_import_template'),
    url('^contacts-import/unsubscribe/', 'unsubscribe_contacts_import', name="crm_unsubscribe_contacts_import")
)


urlpatterns += patterns('',
    url(
        r'^actions-of-month/(?P<year>\d{4})/(?P<month>\d+)/$',
        planning_views.ActionMonthArchiveView.as_view(),
        name="crm_actions_of_month"
    ),
    url(
        r'^actions-of-week/(?P<year>\d{4})/(?P<week>\d+)/$',
        planning_views.ActionWeekArchiveView.as_view(),
        name="crm_actions_of_week"
    ),
    url(
        r'^actions-of-day/(?P<year>\d{4})/(?P<month>[-\w]+)/(?P<day>\d+)/$',
        planning_views.ActionDayArchiveView.as_view(),
        name="crm_actions_of_day"
    ),
    url(
        r'^actions-not-planned/$',
        planning_views.NotPlannedActionArchiveView.as_view(),
        name="crm_actions_not_planned"
    ),
)


urlpatterns += patterns('',
    url(
        r'^action-document/(?P<pk>\d+)/edit/$',
        document_views.ActionDocumentEditView.as_view(),
        name='crm_edit_action_document'
    ),
    url(
        r'^action-document/(?P<pk>\d+)/pdf/$',
        document_views.ActionDocumentPdfView.as_view(),
        name='crm_pdf_action_document'
    ),
    url(
        r'^action-document/(?P<pk>\d+)/$',
        document_views.ActionDocumentDetailView.as_view(),
        name='crm_view_action_document'
    ),
)
