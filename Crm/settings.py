# -*- coding: utf-8 -*-

from django.conf import settings as project_settings

ENTITY_LOGO_DIR = getattr(project_settings, 'ENTITY_LOGO_DIR', 'entities/logos')
CONTACT_PHOTO_DIR = getattr(project_settings, 'CONTACT_PHOTO_DIR', 'contacts/photos')

def get_default_country():
    return getattr(project_settings, 'SANZA_DEFAULT_COUNTRY', 'France')
