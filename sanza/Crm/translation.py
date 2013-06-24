# -*- coding: utf-8 -*-

from modeltranslation.translator import translator, TranslationOptions
from models import EntityType

class ArticleTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(EntityType, ArticleTranslationOptions)
