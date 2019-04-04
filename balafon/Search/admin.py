# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from balafon.Search import models


@admin.register(models.Search)
class SearchAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SearchGroup)
class SearchGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'search']
    search_fields = ['name', 'search']
    raw_id_admin = ('search',)


@admin.register(models.SearchField)
class SearchFieldAdmin(admin.ModelAdmin):
    list_display = ['field', 'search_group', 'value']
    search_fields = ['field', 'field__group__search']
    raw_id_admin = ('search_group',)
