# -*- coding: utf-8 -*-

from django.contrib import admin

from . import models


@admin.register(models.ContactProfile)
class ContactProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CategoryPermission)
class CategoryPermissionAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    filter_horizontal = ['can_view_groups', 'can_edit_groups']
