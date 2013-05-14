# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from sanza.Crm import models

admin.site.register(models.Zone)
admin.site.register(models.EntityRole)
admin.site.register(models.ActionType)
admin.site.register(models.SameAs)
admin.site.register(models.OpportunityType)

class EntityTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gender', 'order']
    list_editable = ['name', 'gender', 'order']
admin.site.register(models.EntityType, EntityTypeAdmin)

class ZoneTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
admin.site.register(models.ZoneType, ZoneTypeAdmin)

class OpportunityStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'ordering']
admin.site.register(models.OpportunityStatus, OpportunityStatusAdmin)

class ContactAdmin(admin.ModelAdmin):
    list_display = ['lastname', 'firstname', 'entity']
    search_fields = ['lastname']
    raw_id_admin = ('entity',)
admin.site.register(models.Contact, ContactAdmin)

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
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
    list_display = ['subject', 'entity']
    search_fields = ['subject', 'entity']
    raw_id_admin = ('entity',)
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