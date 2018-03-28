# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin

from . import models


admin.site.register(models.ContactProfile)


class CategoryPermissionAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    filter_horizontal = ['can_view_groups', 'can_edit_groups']

admin.site.register(models.CategoryPermission, CategoryPermissionAdmin)
