# -*- coding: utf-8 -*-
"""admin site"""

from django.contrib import admin

from balafon.Emailing import models


class EmailingAdmin(admin.ModelAdmin):
    """Emailing"""
    list_display = ['newsletter']
    raw_id_fields = [
        'send_to', 'sent_to', 'opened_emails', 'hard_bounce', 'soft_bounce', 'spam', 'unsub', 'rejected',
    ]

admin.site.register(models.Emailing, EmailingAdmin)


class MagicLinkAdmin(admin.ModelAdmin):
    """Magic link"""
    list_display = ['url', 'emailing']
    search_fields = ['url', 'emailing']
    raw_id_admin = ('emailing',)

admin.site.register(models.MagicLink, MagicLinkAdmin)

