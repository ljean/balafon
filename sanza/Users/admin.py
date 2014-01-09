# -*- coding: utf-8 -*-
from django.contrib import admin
from sanza.Users import models
from sanza.Users.forms import UserPreferencesAdminForm

class UserPreferencesAdmin(admin.ModelAdmin):
    form = UserPreferencesAdminForm
    list_display = ['user', 'notify_due_actions']
    #list_editable = ['notify_due_actions']
    
admin.site.register(models.UserPreferences, UserPreferencesAdmin)