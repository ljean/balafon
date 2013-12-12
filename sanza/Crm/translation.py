# -*- coding: utf-8 -*-

from modeltranslation.translator import translator, TranslationOptions
from models import EntityType

class EntityTypeTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(EntityType, EntityTypeTranslationOptions)
