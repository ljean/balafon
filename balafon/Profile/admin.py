# -*- coding: utf-8 -*-
from django.contrib import admin
import models

admin.site.register(models.ContactProfile)

class CategoryPermissionAdmin(admin.ModelAdmin):
    list_display = ['__unicode__']
    filter_horizontal = ['can_view_groups', 'can_edit_groups']

admin.site.register(models.CategoryPermission, CategoryPermissionAdmin)
