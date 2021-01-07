# -*- coding: utf-8 -*-

from django.contrib import admin
from balafon.Users import models
from balafon.Users.forms import UserPreferencesAdminForm, UserPermissionsAdminForm


@admin.register(models.UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    form = UserPreferencesAdminForm
    list_display = ['user', 'notify_due_actions', 'message_in_favorites', ]


@admin.register(models.UserPermissions)
class UserPermissionsAdmin(admin.ModelAdmin):
    form = UserPermissionsAdminForm
    list_display = ['user', 'can_create_group', ]
    list_editable = ['can_create_group', ]


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["__str__", "user", "content_type", "object_id"]
    list_filter = ["user", "content_type"]


@admin.register(models.UserHomepage)
class UserHomepageAdmin(admin.ModelAdmin):
    list_display = ["user", "url"]


class CustomMenuItemInline(admin.StackedInline):
    model = models.CustomMenuItem
    fields = [
        'label', 'icon', 'url', 'reverse', 'reverse_kwargs', 'attributes',
        'query_string', 'order_index', 'only_for_users'
    ]
    raw_id_fields = ['only_for_users']
    extra = 0


@admin.register(models.CustomMenu)
class CustomMenuAdmin(admin.ModelAdmin):
    inlines = [CustomMenuItemInline]
