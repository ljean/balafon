# -*- coding: utf-8 -*-
"""admin site"""

from __future__ import unicode_literals

from django.contrib import admin

import floppyforms.__future__ as forms

from balafon.Crm import settings as crm_settings
from balafon.Emailing import models


@admin.register(models.Emailing)
class EmailingAdmin(admin.ModelAdmin):
    """Emailing"""
    list_display = ['newsletter']
    raw_id_fields = [
        'send_to', 'sent_to', 'opened_emails', 'hard_bounce', 'soft_bounce', 'spam', 'unsub', 'rejected',
    ]

    def get_form(self, *args, **kwargs):
        form_class = super(EmailingAdmin, self).get_form(*args, **kwargs)
        class custom_form_class(form_class):
            def __init__(self, *args, **kwargs):
                super(custom_form_class, self).__init__(*args, **kwargs)
                self.fields['lang'].widget = forms.Select(choices=crm_settings.get_language_choices())
        return custom_form_class


@admin.register(models.MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    """Magic link"""
    list_display = ['url', 'emailing']
    search_fields = ['url', 'emailing']
    raw_id_admin = ('emailing',)
