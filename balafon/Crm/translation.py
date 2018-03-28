# -*- coding: utf-8 -*-
"""django-modeltranslation configuration"""

from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from .models import EntityType


class EntityTypeTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(EntityType, EntityTypeTranslationOptions)
