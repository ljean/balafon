# -*- coding: utf-8 -*-
"""user customization"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


class UserPreferences(models.Model):
    """user preferences"""

    user = models.OneToOneField(User)
    notify_due_actions = models.BooleanField(default=False, verbose_name=_(u"Notify due actions"))
    message_in_favorites = models.BooleanField(
        default=False,
        verbose_name=_(u"Create automatically a favorite for message posted from the public form")
    )
    
    def __unicode__(self):
        return self.user.username


class Favorite(models.Model):
    """user favorite items"""

    user = models.ForeignKey(User, verbose_name=_("user"), related_name="user_favorite_set")
    content_type = models.ForeignKey(ContentType, verbose_name=_("content_type"), related_name="user_favorite_set")
    object_id = models.PositiveIntegerField(verbose_name=_("object id"))
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name = _(u'Favorite')
        verbose_name_plural = _(u'Favorites')
        unique_together = (('user', 'content_type', 'object_id'),)
        
    def __unicode__(self):
        return u"{0} - {1}".format(self.user, self.content_object)


class UserHomepage(models.Model):
    """User homepage"""

    user = models.OneToOneField(User, verbose_name=_("user"))
    url = models.URLField(verbose_name=_("URL"))
    
    class Meta:
        verbose_name = _(u'User homepage')
        verbose_name_plural = _(u'User homepages')
        
    def __unicode__(self):
        return u"{0} - {1}".format(self.user, self.url)
