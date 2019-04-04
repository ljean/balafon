# -*- coding: utf-8 -*-
"""admin"""

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.messages import success, error
from django.utils.translation import ugettext_lazy as _

import floppyforms.__future__ as forms

from balafon.widgets import VerboseManyToManyRawIdWidget
from balafon.Crm import models
from balafon.Crm.forms.actions import ActionMenuAdminForm
from balafon.Crm.settings import get_language_choices


class HasParentFilter(admin.SimpleListFilter):
    """filter items to know if they have a parent"""
    title = _('Has parent')
    parameter_name = 'has_parent'

    def lookups(self, request, model_admin):
        return [
            (1, _('Yes')),
            (2, _('No')),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '1':
            return queryset.filter(parent__isnull=False)
        elif value == '2':
            return queryset.filter(parent__isnull=True)
        return queryset


@admin.register(models.Zone)
class ZoneAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'parent', 'type']
    ordering = ['type', 'name']
    list_filter = ['type', HasParentFilter, 'parent']
    search_fields = ['name']


@admin.register(models.EntityRole)
class EntityRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SameAs)
class SameAsAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['priority_contact', 'other_contacts', 'contacts_count']



@admin.register(models.OpportunityType)
class OpportunityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ActionMenu)
class ActionMenuAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['action_type', 'view_name', 'label', 'icon', 'a_attrs', 'order_index', 'only_for_status_str']
    list_filter = ['action_type', ]
    list_editable = ['order_index', ]
    search_fields = ['label', ]
    form = ActionMenuAdminForm


@admin.register(models.EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'name', 'gender', 'order', 'subscribe_form']
    list_editable = ['name', 'gender', 'order', 'subscribe_form']
    list_filter = ['subscribe_form']


@admin.register(models.ZoneType)
class ZoneTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'type']
    ordering = ['type', 'name']


def initialize_status2(modeladmin, request, queryset):
    for action_type in queryset:
        if action_type.default_status2:
            actions_queryset = action_type.action_set.filter(status2__isnull=True)
            actions_count = actions_queryset.count()
            actions_queryset.update(status2=action_type.default_status2)
            success(
                request,
                _("initialize {0} actions of type '{1}' with status2 '{2}'").format(
                    actions_count, action_type.name, action_type.default_status2.name
                )
            )
        else:
            error(
                request,
                _("No default status2 for actions type '{0}'").format(action_type.name)
            )
initialize_status2.short_description = _("Initialize status2 to default if Null")


def reset_status2(modeladmin, request, queryset):
    for action_type in queryset:
        if action_type.default_status2:
            actions_queryset = action_type.action_set.filter(status2=action_type.default_status2)
            actions_count = actions_queryset.count()
            actions_queryset.update(status2=None)
            success(
                request,
                _("reset {0} actions of type '{1}'").format(
                    actions_count, action_type.name
                )
            )
        else:
            error(
                request,
                _("No default status2 for actions type '{0}'").format(action_type.name)
            )
reset_status2.short_description = _("Reset status2 to Null")


def set_action_previous_status(modeladmin, request, queryset):
    for action_type in queryset:
        if not action_type.track_status:
            actions_queryset = action_type.action_set.all()
            actions_count = actions_queryset.count()
            for action in actions_queryset:
                action.previous_status = action.status
                action.save()
            success(
                request,
                _("set previous values for {0} actions").format(actions_count)
            )
        else:
            error(
                request,
                _("{0} : track status should be disabled when executing this action").format(action_type.name)
            )
set_action_previous_status.short_description = _("Track status : Set previous status")


def create_action_initial_track(modeladmin, request, queryset):
    for action_type in queryset:
        if action_type.track_status:
            actions_queryset = action_type.action_set.all()
            actions_count = actions_queryset.count()
            ignored_count = 0
            for action in actions_queryset:
                if action.status and action.status.is_final and action.done_date and action.done_date:
                    track_datetime = action.done_date
                else:
                    track_datetime = action.planned_date

                no_tracks_yet = models.ActionStatusTrack.objects.filter(action=action).count() == 0
                if action.status and track_datetime and no_tracks_yet:
                    models.ActionStatusTrack.objects.create(
                        status=action.status,
                        action=action,
                        datetime=track_datetime
                    )
                else:
                    ignored_count += 1

            success(
                request,
                _("create tracks for {0} actions / {1} ignored").format(actions_count - ignored_count, ignored_count)
            )
        else:
            error(
                request,
                _("{0} : track status should be enabled when executing this action").format(action_type.name)
            )
create_action_initial_track.short_description = _("Track status : create initial track")


@admin.register(models.ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'name', 'set', 'status_defined', 'subscribe_form', 'action_number',
        'default_template', 'is_editable', 'hide_contacts_buttons', 'track_status', 'is_default'
    ]
    list_filter = [
        'set', 'subscribe_form', 'number_auto_generated', 'number_generator', 'default_template', 'action_template',
        'hide_contacts_buttons', 'track_status',
    ]
    list_editable = ['set', 'subscribe_form', 'hide_contacts_buttons', ]
    actions = [initialize_status2, reset_status2, set_action_previous_status, create_action_initial_track]
    search_fields = ['name']


@admin.register(models.OpportunityStatus)
class OpportunityStatusAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'ordering']


class SubscriptionInline(admin.TabularInline):
    """custom inline"""
    model = models.Subscription


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['lastname', 'firstname', 'entity', 'email']
    search_fields = ['lastname', 'email']
    raw_id_admin = ('entity',)
    inlines = (SubscriptionInline,)

    def get_form(self, *args, **kwargs):
        form_class = super(ContactAdmin, self).get_form(*args, **kwargs)
        class custom_form_class(form_class):
            def __init__(self, *args, **kwargs):
                super(custom_form_class, self).__init__(*args, **kwargs)
                self.fields['favorite_language'].widget = forms.Select(choices=get_language_choices())
        return custom_form_class


@admin.register(models.Group)
class GroupAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'description', 'subscribe_form']
    search_fields = ['name']
    list_filter = ['subscribe_form']
    list_editable = ['subscribe_form']
    filter_horizontal = ['entities', 'contacts']


class GroupInline(admin.TabularInline):
    """custom inline"""
    model = models.Group


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'parent']
    search_fields = ['name']
    ordering = ['name']
    list_filter = [HasParentFilter, 'parent', ]
    raw_id_fields = ('groups',)


@admin.register(models.Entity)
class EntityAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ('name', 'type')
    search_fields = ['name']


@admin.register(models.Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', ]
    search_fields = ['name', ]
    raw_id_admin = ('entity',)


@admin.register(models.Action)
class ActionAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'id', 'planned_date', 'created', 'subject', 'type', 'status', 'done', 'opportunity', 'number', 'amount'
    ]
    search_fields = ['subject', 'number']
    list_filter = ['type', 'status', 'done', 'opportunity']
    readonly_fields = ['created', 'modified', 'created_by', 'last_modified_by']
    date_hierarchy = 'created'
    raw_id_fields = ['contacts', 'entities',]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, self.admin_site)
        else:
            return super(ActionAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        kwargs.pop('request')
        return db_field.formfield(**kwargs)


@admin.register(models.CustomFieldChoice)
class CustomFieldChoicedAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['value', 'label', 'order']


@admin.register(models.CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'model', 'label', 'widget', 'ordering', 'import_order', 'export_order']
    list_editable = ['ordering', 'import_order', 'export_order']
    list_filter = ('model', 'widget')
    filter_horizontal = ['choices']


@admin.register(models.EntityCustomFieldValue)
class EntityCustomFieldValueAdmin(admin.ModelAdmin):
    """custom admin view"""
    search_fields = ['entity']


@admin.register(models.ContactCustomFieldValue)
class ContactCustomFieldValueAdmin(admin.ModelAdmin):
    """custom admin view"""
    search_fields = ['contact']


@admin.register(models.ContactsImport)
class ContactsImportAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ActionSet)
class ActionSetAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'ordering']
    list_editable = ['ordering']
    search_fields = ['name']


@admin.register(models.ActionStatus)
class ActionStatusAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'ordering', 'is_final', 'background_color', 'fore_color']
    list_filter = ['is_final']
    list_editable = ['ordering', 'is_final', 'background_color', 'fore_color']
    search_fields = ['name']


@admin.register(models.ActionDocument)
class ActionDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RelationshipType)
class RelationshipTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'name', 'reverse']
    list_editable = ['name', 'reverse']


@admin.register(models.Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'contact1', 'relationship_type', 'contact2']


@admin.register(models.SubscriptionType)
class SubscriptionTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'site', 'order_index']
    list_editable = ['order_index']


@admin.register(models.TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'user', 'active']
    list_filter = ['active']


@admin.register(models.StreetType)
class StreetTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MailtoSettings)
class MailtoSettingsAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['action_type', 'subject', 'bcc']


@admin.register(models.ActionStatusTrack)
class ActionStatusTrackAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ActionNumberGenerator)
class ActionNumberGeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', )
