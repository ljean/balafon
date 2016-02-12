# -*- coding: utf-8 -*-
"""urls"""
# pylint: disable=C0330

from django.conf.urls import url

from balafon.Crm.views import planning as planning_views, documents as document_views
from balafon.Crm.views import (
    actions, bookmarks, contacts, custom_fields, cities, entities, groups, importers, opportunities, relationships
)


urlpatterns = [

    # entities
    url(r'^entities/$', entities.view_entities_list, name='crm_view_entities_list'),
    url(r'^entity/(?P<entity_id>\d+)/$', entities.view_entity, name='crm_view_entity'),
    url(r'^edit-entity/(?P<entity_id>\d+)/$', entities.edit_entity, name='crm_edit_entity'),
    url(r'^create-entity/(?P<entity_type_id>\d+)/$', entities.create_entity, name='crm_create_entity'),
    url(r'^delete-entity/(?P<entity_id>\d+)/$', entities.delete_entity, name='crm_delete_entity'),
    url(
        r'^change-contact-entity/(?P<contact_id>\d+)/$',
        entities.change_contact_entity,
        name='crm_change_contact_entity'
    ),
    url(r'^entity-name/(?P<entity_id>.+)/$', entities.get_entity_name, name='crm_get_entity_name'),
    url(r'^entities/list/$', entities.get_entities, name='crm_get_entities'),
    url(r'^entity-id/$', entities.get_entity_id, name='crm_get_entity_id'),

    # contacts
    url(r'^add-contact/(?P<entity_id>\d+)/$', contacts.add_contact, name='crm_add_contact'),
    url(r'^add-single-contact/$', contacts.add_single_contact, name='crm_add_single_contact'),
    url(r'^delete-contact/(?P<contact_id>\d+)/$', contacts.delete_contact, name='crm_delete_contact'),
    url(r'^edit-contact/(?P<contact_id>\d+)/$', contacts.edit_contact, name='crm_edit_contact'),
    url(
        r'^edit-contact-advanced/(?P<contact_id>\d+)/$',
        contacts.edit_contact,
        kwargs={'mini': False},
        name='crm_edit_contact_advanced'
    ),
    url(
        r'^edit-contact-on-create-entity/(?P<contact_id>\d+)/$',
        contacts.edit_contact,
        kwargs={'go_to_entity': True},
        name='crm_edit_contact_after_entity_created'
    ),
    url(
        r'^edit-contact-on-entity/(?P<contact_id>\d+)/$',
        contacts.edit_contact,
        kwargs={'go_to_entity': True},
        name='crm_edit_contact_on_entity'
    ),
    url(r'^view-contact/(?P<contact_id>\d+)/$', contacts.view_contact, name='crm_view_contact'),
    url(r'^contact-name/(?P<contact_id>.+)/$', contacts.get_contact_name, name='crm_get_contact_name'),
    url(r'^contacts/list/$', contacts.get_contacts, name='crm_get_contacts'),
    url(r'^contact-id/$', contacts.get_contact_id, name='crm_get_contact_id'),

    # actions
    url(
        r'^view-contact-actions/(?P<contact_id>\d+)/(?P<action_set_id>\d+)/$',
        actions.view_all_contact_actions,
        name='crm_view_contact_actions'
    ),
    url(
        r'^view-entity-actions/(?P<entity_id>\d+)/(?P<action_set_id>\d+)/$',
        actions.view_all_entity_actions,
        name='crm_view_entity_actions'
    ),
    url(r'^add-action-for-entity/(?P<entity_id>\d+)/$', actions.add_action_for_entity, name='crm_add_action_for_entity'),
    url(r'^add-action-for-contact/(?P<contact_id>\d+)/$', actions.add_action_for_contact, name='crm_add_action_for_contact'),
    url(r'^edit-action/(?P<action_id>\d+)/$', actions.edit_action, name='crm_edit_action'),
    url(r'^do-action/(?P<action_id>\d+)/$', actions.do_action, name='crm_do_action'),
    url(r'^delete-action/(?P<action_id>\d+)/$', actions.delete_action, name='crm_delete_action'),
    url(r'^entity-actions/(?P<entity_id>\d+)/(?P<set_id>\d+)/$', actions.view_entity_actions, name='crm_entity_actions'),
    url(r'^contact-actions/(?P<contact_id>\d+)/(?P<set_id>\d+)/$', actions.view_contact_actions, name='crm_contact_actions'),
    url(r'^add-action/$', actions.add_action, name='crm_add_action'),
    url(r'^all-actions/$', actions.view_all_actions, name='crm_all_actions'),
    url(r'^add-contact-to-action/(?P<action_id>\d+)/$', actions.add_contact_to_action, name='crm_add_contact_to_action'),
    url(r'^add-entity-to-action/(?P<action_id>\d+)/$', actions.add_entity_to_action, name='crm_add_entity_to_action'),
    url(
        r'^remove-contact-from-action/(?P<action_id>\d+)/(?P<contact_id>\d+)/$',
        actions.remove_contact_from_action,
        name='crm_remove_contact_from_action'
    ),
    url(
        r'^remove-entity-from-action/(?P<action_id>\d+)/(?P<entity_id>\d+)/$',
        actions.remove_entity_from_action,
        name='crm_remove_entity_from_action'
    ),
    url(r'^create-action/(?P<entity_id>\d+)/(?P<contact_id>\d+)/$', actions.create_action, name='crm_create_action'),
    url(r'allowed-action-status/$', actions.get_action_status, name="crm_get_action_status"),
    url(r'^clone-action/(?P<action_id>\d+)/$', actions.clone_action, name='crm_clone_action'),
    url(r'^update-action-status/(?P<action_id>\d+)/$', actions.update_action_status, name='crm_update_action_status'),
    url(r'^reassign-action/(?P<action_id>\d+)/$', actions.reassign_action, name='crm_reassign_action'),

    # relationships
    url(r'^same-as/(?P<contact_id>\d+)/$', relationships.same_as, name='crm_same_as'),
    url('^same-as-suggestions/$', relationships.get_same_as_suggestions, name='crm_same_as_suggestions'),
    url(
        r'^remove-same-as/(?P<current_contact_id>\d+)/(?P<contact_id>\d+)/$',
        relationships.remove_same_as,
        name='crm_remove_same_as'
    ),
    url(r'^add-relationship/(?P<contact_id>\d+)/$', relationships.add_relationship, name='crm_add_relationship'),
    url(
        r'^delete-relationship/(?P<contact_id>\d+)/(?P<relationship_id>\d+)/$',
        relationships.delete_relationship,
        name='crm_delete_relationship'
    ),
    url(
        r'^make-main-contact/(?P<current_contact_id>\d+)/(?P<contact_id>\d+)/$',
        relationships.make_main_contact,
        name='crm_make_main_contact'
    ),

    # groups
    url(r'^add-entity-to-group/(?P<entity_id>\d+)/$', groups.add_entity_to_group, name='crm_add_entity_to_group'),
    url(r'^add-contact-to-group/(?P<contact_id>\d+)/$', groups.add_contact_to_group, name='crm_add_contact_to_group'),
    url(r'^get-group-suggest-list/$', groups.get_group_suggest_list, name='crm_get_group_suggest_list'),
    url(
        r'^remove-from-group/(?P<group_id>\d+)/(?P<entity_id>\d+)/$',
        groups.remove_entity_from_group,
        name='crm_remove_entity_from_group'
    ),
    url(
        r'^remove-contact-from-group/(?P<group_id>\d+)/(?P<contact_id>\d+)/$',
        groups.remove_contact_from_group,
        name='crm_remove_contact_from_group'
    ),
    url(r'^edit-group/(?P<group_id>\d+)/$', groups.edit_group, name='crm_edit_group'),
    url(r'^delete-group/(?P<group_id>\d+)/$', groups.delete_group, name='crm_delete_group'),
    url(r'^add-group/$', groups.add_group, name='crm_add_group'),
    url(r'^my-groups/$', groups.see_my_groups, name='crm_see_my_groups'),
    url(r'^group-name/(?P<gr_id>\d+)/$', groups.get_group_name, name='crm_get_group_name'),
    url(r'^groups/list/$', groups.get_groups, name='crm_get_groups'),
    url(r'^group-id/$', groups.get_group_id, name='crm_get_group_id'),
    url(r'^select-contact-or-entity/$', groups.select_contact_or_entity, name='crm_select_contact_or_entity'),
    url(r'^get-contact-or-entity/$', groups.get_contact_or_entity, name='crm_get_contact_or_entity'),

    # cities
    url(r'^city-name/(?P<city>.*)/$', cities.get_city_name, name='crm_get_city_name'),
    url(r'^cities/list/$', cities.get_cities, name='crm_get_cities'),
    url(r'^city-id/$', cities.get_city_id, name='crm_get_city_id'),

    # bookmarks
    url(r'^board/$', bookmarks.view_board_panel, name='crm_board_panel'),
    url(r'^toggle-action-bookmark/(?P<action_id>\d+)/$', bookmarks.toggle_action_bookmark, name='crm_toggle_action_bookmark'),
    url(
        r'^toggle-opportunity-bookmark/(?P<opportunity_id>\d+)/$',
        bookmarks.toggle_opportunity_bookmark,
        name='crm_toggle_opportunity_bookmark'
    ),

    # opportunities
    url(r'^edit-opportunity/(?P<opportunity_id>\d+)/$', opportunities.edit_opportunity, name='crm_edit_opportunity'),
    url(r'^view-opportunity/(?P<opportunity_id>\d+)/$', opportunities.view_opportunity, name='crm_view_opportunity'),
    url(
        r'^delete-opportunity/(?P<opportunity_id>\d+)/$',
        opportunities.delete_opportunity,
        name='crm_delete_opportunity'
    ),
    url(
        r'^opportunities/(?P<entity_id>\d+)/$',
        opportunities.view_entity_opportunities,
        name='crm_entity_opportunities'
    ),
    url(r'^opportunities/$', opportunities.view_all_opportunities, name='crm_all_opportunities'),
    url(r'^opportunities-by/(?P<ordering>.+)/$', opportunities.view_all_opportunities, name='crm_all_opportunities_by'),
    url(r'^add-opportunity/$', opportunities.add_opportunity, name='crm_add_opportunity'),
    url(r'^opportunity-name/(?P<opp_id>.+)/$', opportunities.get_opportunity_name, name='crm_get_opportunity_name'),
    url(r'^opportunities/list/$', opportunities.get_opportunities, name='crm_get_opportunities'),
    url(r'^opportunity-id/$', opportunities.get_opportunity_id, name='crm_get_opportunity_id'),
    url(
        r'add-action-to-opportunity/(?P<action_id>\d+)/$',
        opportunities.add_action_to_opportunity,
        name='crm_add_action_to_opportunity'
    ),
    url(
        r'remove-action-from-opportunity/(?P<action_id>\d+)/(?P<opportunity_id>\d+)/$',
        opportunities.remove_action_from_opportunity,
        name='crm_remove_action_from_opportunity'
    ),

    # custom_fields
    url(
        r'^edit-custom-fields/(?P<model_name>\w+)/(?P<instance_id>\d+)/$',
        custom_fields.edit_custom_fields,
        name='crm_edit_custom_fields'
    ),

    # importers
    url(r'^contacts-import/new/$', importers.new_contacts_import, name='crm_new_contacts_import'),
    url(
        r'^contacts-import/(?P<import_id>\d+)/$',
        importers.confirm_contacts_import,
        name='crm_confirm_contacts_import'
    ),
    url(r'^contacts-import/template.csv$', importers.contacts_import_template, name='crm_contacts_import_template'),
    url('^contacts-import/unsubscribe/', importers.unsubscribe_contacts_import, name="crm_unsubscribe_contacts_import"),

    # planning
    url(r'^actions-of-month/$', planning_views.ThisMonthActionsView.as_view(), name="crm_this_month_actions"),
    url(r'^actions-of-week/$', planning_views.ThisWeekActionsView.as_view(), name="crm_this_week_actions"),
    url(r'^actions-of-day/$', planning_views.TodayActionsView.as_view(), name="crm_today_actions"),
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
    url(r'^go-to-planning-date/$', planning_views.go_to_planning_date, name='crm_go_to_planning_date'),

    # documents
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
]
