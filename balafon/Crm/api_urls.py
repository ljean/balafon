# -*- coding: utf-8 -*-
"""urls"""
# pylint: disable=C0330

from django.conf.urls import url, include

from rest_framework import routers

from balafon.Crm.api import (
    UpdateActionDateView, CreateActionView, DeleteActionView, UpdateActionView, ContactViewSet, ListActionsView,
    ListTeamMemberActionsView, AboutMeView, ContactsOrEntitiesView
)

router = routers.DefaultRouter()
router.register(r'contacts', ContactViewSet)

urlpatterns = [
    # api
    url(r'^api/', include(router.urls)),
    url(r'^api/update-action-date/(?P<pk>\d*)/$', UpdateActionDateView.as_view(), name="crm_api_update_action_date"),
    url(r'^api/update-action/(?P<pk>\d*)/$', UpdateActionView.as_view(), name="crm_api_update_action"),
    url(r'^api/create-action/$', CreateActionView.as_view(), name="crm_api_create_action"),
    url(r'^api/delete-action/(?P<pk>\d*)/$', DeleteActionView.as_view(), name="crm_api_delete_action"),
    url(r'^api/list-actions/$', ListActionsView.as_view(), name="crm_api_list_actions"),
    url(
        r'^api/list-team-member-actions/$', ListTeamMemberActionsView.as_view(), name="crm_api_list_team_member_actions"
    ),
    url(r'^api/about-me/$', AboutMeView.as_view(), name="crm_api_about_me"),
    url(r'^api/contacts-or-entities/$', ContactsOrEntitiesView.as_view(), name="crm_api_contacts_or_entities"),
]
