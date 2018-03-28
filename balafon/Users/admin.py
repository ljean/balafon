# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib import admin
from balafon.Users import models
from balafon.Users.forms import UserPreferencesAdminForm


class UserPreferencesAdmin(admin.ModelAdmin):
    form = UserPreferencesAdminForm
    list_display = ['user', 'notify_due_actions', 'message_in_favorites']

admin.site.register(models.UserPreferences, UserPreferencesAdmin)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "content_type", "object_id"]
    list_filter = ["user", "content_type"]

admin.site.register(models.Favorite, FavoriteAdmin)


class UserHomepageAdmin(admin.ModelAdmin):
    list_display = ["user", "url"]

admin.site.register(models.UserHomepage, UserHomepageAdmin)


class CustomMenuItemInline(admin.TabularInline):
    model = models.CustomMenuItem


class CustomMenuAdmin(admin.ModelAdmin):
    inlines = [CustomMenuItemInline]

admin.site.register(models.CustomMenu, CustomMenuAdmin)