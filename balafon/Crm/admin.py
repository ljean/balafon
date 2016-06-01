# -*- coding: utf-8 -*-
"""admin"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from balafon.widgets import VerboseManyToManyRawIdWidget
from balafon.Crm import models


class HasParentFilter(admin.SimpleListFilter):
    """filter items to know if they have a parent"""
    title = _(u'Has parent')
    parameter_name = 'has_parent'

    def lookups(self, request, model_admin):
        return [
            (1, _(u'Yes')),
            (2, _(u'No')),
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
admin.site.register(models.ActionMenu)


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


class ActionTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'name', 'set', 'status_defined', 'subscribe_form', 'last_number', 'number_auto_generated',
        'default_template', 'is_editable', 'hide_contacts_buttons',
    ]
    list_filter = [
        'set', 'subscribe_form', 'number_auto_generated', 'default_template', 'action_template',
        'hide_contacts_buttons',
    ]
    list_editable = ['set', 'subscribe_form', 'last_number', 'number_auto_generated', 'hide_contacts_buttons',]

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
    list_display = ['__unicode__', 'parent']
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
    list_display = ['name', 'site']

admin.site.register(models.SubscriptionType, SubscriptionTypeAdmin)

class TeamMemberAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'user', 'active']
    list_filter = ['active']

admin.site.register(models.TeamMember, TeamMemberAdmin)

admin.site.register(models.StreetType)
