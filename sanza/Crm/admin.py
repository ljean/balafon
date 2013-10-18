# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from sanza.Crm import models

admin.site.register(models.Zone)
admin.site.register(models.EntityRole)
admin.site.register(models.SameAs)
admin.site.register(models.OpportunityType)

class EntityTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gender', 'order']
    list_editable = ['name', 'gender', 'order']
admin.site.register(models.EntityType, EntityTypeAdmin)

class ZoneTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
admin.site.register(models.ZoneType, ZoneTypeAdmin)

class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'set', 'status_defined', 'subscribe_form', 'last_number', 'number_auto_generated', 'default_template', 'is_editable']
    list_filter = ['set', 'subscribe_form', 'number_auto_generated', 'default_template']
    list_editable = ['set', 'subscribe_form', 'last_number', 'number_auto_generated']
admin.site.register(models.ActionType, ActionTypeAdmin)

class OpportunityStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'ordering']
admin.site.register(models.OpportunityStatus, OpportunityStatusAdmin)

class ContactAdmin(admin.ModelAdmin):
    list_display = ['lastname', 'firstname', 'entity']
    search_fields = ['lastname']
    raw_id_admin = ('entity',)
admin.site.register(models.Contact, ContactAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description','subscribe_form']
    search_fields = ['name']
    list_filter=['subscribe_form']
    list_editable=['subscribe_form']
    
    filter_horizontal = ['entities', 'contacts']
admin.site.register(models.Group, GroupAdmin)

class GroupInline(admin.TabularInline):
    model = models.Group

class CityAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'parent']
    search_fields = ['name']
admin.site.register(models.City, CityAdmin)

class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    search_fields = ['name']
admin.site.register(models.Entity, EntityAdmin)

class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'entity', 'ended', 'display_on_board']
    search_fields = ['name', 'entity']
    raw_id_admin = ('entity',)
admin.site.register(models.Opportunity, OpportunityAdmin)

class ActionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'contact']
    search_fields = ['subject', 'contact']
    raw_id_admin = ('contact',)
admin.site.register(models.Action, ActionAdmin)

class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'label', 'widget', 'ordering', 'import_order', 'export_order']
    list_editable = ['ordering', 'import_order', 'export_order']
    list_filter = ('model', 'widget')
admin.site.register(models.CustomField, CustomFieldAdmin)

class EntityCustomFieldValueAdmin(admin.ModelAdmin):
    search_fields = ['entity']
admin.site.register(models.EntityCustomFieldValue, EntityCustomFieldValueAdmin)

class ContactCustomFieldValueAdmin(admin.ModelAdmin):
    search_fields = ['contact']
admin.site.register(models.ContactCustomFieldValue, ContactCustomFieldValueAdmin)

admin.site.register(models.ContactsImport)
admin.site.register(models.ActionSet)
admin.site.register(models.ActionStatus)
admin.site.register(models.ActionDocument)

class RelationshipTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'reverse']
    list_editable = ['name', 'reverse']
admin.site.register(models.RelationshipType, RelationshipTypeAdmin)

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ['id', 'contact1', 'relationship_type', 'contact2']
admin.site.register(models.Relationship, RelationshipAdmin)
