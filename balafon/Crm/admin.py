# -*- coding: utf-8 -*-
"""admin"""

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.messages import success, error
from django.utils.translation import ugettext_lazy as _

from balafon.widgets import VerboseManyToManyRawIdWidget
from balafon.Crm import models
from balafon.Crm.forms.actions import ActionMenuAdminForm


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


class ZoneAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'parent', 'type']
    ordering = ['type', 'name']
    list_filter = ['type', HasParentFilter, 'parent']
    search_fields = ['name']

admin.site.register(models.Zone, ZoneAdmin)


admin.site.register(models.EntityRole)


class SameAsAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['priority_contact', 'other_contacts', 'contacts_count']

admin.site.register(models.SameAs, SameAsAdmin)


admin.site.register(models.OpportunityType)


class ActionMenuAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['action_type', 'view_name', 'label', 'icon', 'a_attrs', 'order_index', 'only_for_status_str']
    list_filter = ['action_type', ]
    list_editable = ['order_index', ]
    search_fields = ['label', ]
    form = ActionMenuAdminForm

admin.site.register(models.ActionMenu, ActionMenuAdmin)


class EntityTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'name', 'gender', 'order', 'subscribe_form']
    list_editable = ['name', 'gender', 'order', 'subscribe_form']
    list_filter = ['subscribe_form']

admin.site.register(models.EntityType, EntityTypeAdmin)


class ZoneTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'type']
    ordering = ['type', 'name']

admin.site.register(models.ZoneType, ZoneTypeAdmin)


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


admin.site.register(models.ActionType, ActionTypeAdmin)


class OpportunityStatusAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'ordering']

admin.site.register(models.OpportunityStatus, OpportunityStatusAdmin)


class SubscriptionInline(admin.TabularInline):
    """custom inline"""
    model = models.Subscription


class ContactAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['lastname', 'firstname', 'entity', 'email']
    search_fields = ['lastname', 'email']
    raw_id_admin = ('entity',)
    inlines = (SubscriptionInline,)

admin.site.register(models.Contact, ContactAdmin)


class GroupAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'description', 'subscribe_form']
    search_fields = ['name']
    list_filter = ['subscribe_form']
    list_editable = ['subscribe_form']
    filter_horizontal = ['entities', 'contacts']

admin.site.register(models.Group, GroupAdmin)


class GroupInline(admin.TabularInline):
    """custom inline"""
    model = models.Group


class CityAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'parent']
    search_fields = ['name']
    ordering = ['name']
    list_filter = [HasParentFilter, 'parent', ]
    raw_id_fields = ('groups',)

admin.site.register(models.City, CityAdmin)


class EntityAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ('name', 'type')
    search_fields = ['name']

admin.site.register(models.Entity, EntityAdmin)


class OpportunityAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', ]
    search_fields = ['name', ]
    raw_id_admin = ('entity',)

admin.site.register(models.Opportunity, OpportunityAdmin)


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

admin.site.register(models.Action, ActionAdmin)


class CustomFieldAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'model', 'label', 'widget', 'ordering', 'import_order', 'export_order']
    list_editable = ['ordering', 'import_order', 'export_order']
    list_filter = ('model', 'widget')

admin.site.register(models.CustomField, CustomFieldAdmin)


class EntityCustomFieldValueAdmin(admin.ModelAdmin):
    """custom admin view"""
    search_fields = ['entity']

admin.site.register(models.EntityCustomFieldValue, EntityCustomFieldValueAdmin)


class ContactCustomFieldValueAdmin(admin.ModelAdmin):
    """custom admin view"""
    search_fields = ['contact']

admin.site.register(models.ContactCustomFieldValue, ContactCustomFieldValueAdmin)

admin.site.register(models.ContactsImport)


class ActionSetAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'ordering']
    list_editable = ['ordering']

admin.site.register(models.ActionSet, ActionSetAdmin)


class ActionStatusAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'ordering', 'is_final', 'background_color', 'fore_color']
    list_filter = ['is_final']
    list_editable = ['ordering', 'is_final', 'background_color', 'fore_color']

admin.site.register(models.ActionStatus, ActionStatusAdmin)

admin.site.register(models.ActionDocument)


class RelationshipTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'name', 'reverse']
    list_editable = ['name', 'reverse']

admin.site.register(models.RelationshipType, RelationshipTypeAdmin)


class RelationshipAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'contact1', 'relationship_type', 'contact2']

admin.site.register(models.Relationship, RelationshipAdmin)


class SubscriptionTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'site', 'order_index']
    list_editable = ['order_index']

admin.site.register(models.SubscriptionType, SubscriptionTypeAdmin)


class TeamMemberAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'user', 'active']
    list_filter = ['active']


admin.site.register(models.TeamMember, TeamMemberAdmin)


admin.site.register(models.StreetType)


class MailtoSettingsAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['action_type', 'subject', 'bcc']


admin.site.register(models.MailtoSettings, MailtoSettingsAdmin)

admin.site.register(models.ActionStatusTrack)


class ActionNumberGeneratorAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', )

admin.site.register(models.ActionNumberGenerator, ActionNumberGeneratorAdmin)

