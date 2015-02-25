# -*- coding: utf-8 -*-
"""admin"""

from django.contrib import admin
from sanza.Emailing import models

class EmailingAdmin(admin.ModelAdmin):
    """emailing"""
    list_display = ['newsletter']
    raw_id_fields = ['send_to', 'sent_to']

admin.site.register(models.Emailing, EmailingAdmin)


class MagicLinkAdmin(admin.ModelAdmin):
    """magic links"""
    list_display = ['url', 'emailing']
    search_fields = ['url', 'emailing']
    raw_id_admin = ('emailing',)

admin.site.register(models.MagicLink, MagicLinkAdmin)

