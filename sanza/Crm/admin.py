# -*- coding: utf-8 -*-
"""admin"""

from django.contrib import admin
from sanza.Crm import models


class ZoneAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['name', 'parent', 'type']
    ordering = ['type', 'name']
    list_filter = ['type', 'parent']
    search_fields = ['name']
admin.site.register(models.Zone, ZoneAdmin)

admin.site.register(models.EntityRole)
admin.site.register(models.SameAs)
admin.site.register(models.OpportunityType)


class EntityTypeAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = ['id', 'name', 'gender', 'order']
    list_editable = ['name', 'gender', 'order']

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
        'default_template', 'is_editable'
    ]
    list_filter = ['set', 'subscribe_form', 'number_auto_generated', 'default_template']
    list_editable = ['set', 'subscribe_form', 'last_number', 'number_auto_generated']

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
    list_display = ['lastname', 'firstname', 'entity']
    search_fields = ['lastname']
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
    list_filer = ['parent',]
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
    list_display = ['subject']
    search_fields = ['subject']

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
admin.site.register(models.ActionSet)
admin.site.register(models.ActionStatus)
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

admin.site.register(models.SubscriptionType)
