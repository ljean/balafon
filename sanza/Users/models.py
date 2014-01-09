# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class UserPreferences(models.Model):
    user = models.OneToOneField(User)
    notify_due_actions = models.BooleanField(default=None, verbose_name=_(u"Notify due actions"))
    
    def __unicode__(self):
        return self.user.username