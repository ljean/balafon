# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, AutoSlugField
from django.contrib.auth.models import User
from datetime import date
from django.contrib.contenttypes.generic import GenericRelation
from sanza.Users.models import Favorite

class Search(TimeStampedModel):
    name = models.CharField(_('name'), max_length=100)
    
    favorites = GenericRelation(Favorite)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'search')
        verbose_name_plural = _(u'searchs')

class SearchGroup(models.Model):
    search = models.ForeignKey(Search, verbose_name=_('search'))
    name = models.CharField(_('name'), max_length=100)
    
    def __unicode__(self):
        return u'{0} {1}'.format(self.search, self.name)

    class Meta:
        verbose_name = _(u'search group')
        verbose_name_plural = _(u'search groups')

class SearchField(models.Model):
    search_group = models.ForeignKey(SearchGroup, verbose_name=_('search group'))
    field = models.CharField(_('field'), max_length=100)
    value = models.CharField(_('value'), max_length=200)
    is_list = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u'{0} {1}'.format(self.search_group, self.field)

    class Meta:
        verbose_name = _(u'search field')
        verbose_name_plural = _(u'search fied')
