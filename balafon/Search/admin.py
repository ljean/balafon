# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from balafon.Search import models

admin.site.register(models.Search)

class SearchGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'search']
    search_fields = ['name', 'search']
    raw_id_admin = ('search',)
admin.site.register(models.SearchGroup, SearchGroupAdmin)

class SearchFieldAdmin(admin.ModelAdmin):
    list_display = ['field', 'search_group', 'value']
    search_fields = ['field', 'field__group__search']
    raw_id_admin = ('search_group',)
admin.site.register(models.SearchField, SearchFieldAdmin)

