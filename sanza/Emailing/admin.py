# -*- coding: utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse
from sanza.Emailing import models

class EmailingAdmin(admin.ModelAdmin):
    list_display = ['newsletter']
    raw_id_fields = ['send_to', 'sent_to']
admin.site.register(models.Emailing, EmailingAdmin)

class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ['url', 'emailing']
    search_fields = ['url', 'emailing']
    raw_id_admin = ('emailing',)
admin.site.register(models.MagicLink, MagicLinkAdmin)

