# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from balafon.Users.models import Favorite


class Search(TimeStampedModel):
    """A search"""
    name = models.CharField(_('name'), max_length=100)
    
    favorites = GenericRelation(Favorite)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('search')
        verbose_name_plural = _('searchs')


class SearchGroup(models.Model):
    """blocks"""
    search = models.ForeignKey(Search, verbose_name=_('search'), on_delete=models.CASCADE)
    name = models.CharField(_('name'), max_length=100)
    
    def __str__(self):
        return '{0} {1}'.format(self.search, self.name)

    class Meta:
        verbose_name = _('search group')
        verbose_name_plural = _('search groups')


class SearchField(models.Model):
    """fields"""
    search_group = models.ForeignKey(SearchGroup, verbose_name=_('search group'), on_delete=models.CASCADE)
    field = models.CharField(_('field'), max_length=100)
    value = models.CharField(_('value'), max_length=200)
    is_list = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    
    def __str__(self):
        return '{0} {1}'.format(self.search_group, self.field)

    class Meta:
        verbose_name = _('search field')
        verbose_name_plural = _('search fied')
