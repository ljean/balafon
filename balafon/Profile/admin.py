# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _, ugettext

from . import models
from .utils import create_profile_contact


class ContactProfileCustomFieldInline(admin.TabularInline):
    model = models.ContactProfileCustomField


def finalize_user_profile(modeladmin, request, queryset):
    for profile in queryset:
        if profile.contact is None:
            create_profile_contact(profile.user)
            messages.success(request, ugettext('{0}: Contact created').format(profile.user))
        else:
            messages.warning(request, ugettext('{0}: Contact already existing').format(profile.user))


finalize_user_profile.short_description = _('Create contact')


@admin.register(models.ContactProfile)
class ContactProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'contact']
    raw_id_fields = ['user', 'contact', 'city']
    inlines = [ContactProfileCustomFieldInline]
    actions = [finalize_user_profile]


@admin.register(models.CategoryPermission)
class CategoryPermissionAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    filter_horizontal = ['can_view_groups', 'can_edit_groups']
