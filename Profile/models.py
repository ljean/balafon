# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from sanza.Crm.models import Contact, Group
from coop_cms.models import ArticleCategory

class ContactProfile(models.Model):
    user = models.OneToOneField(User)
    contact = models.OneToOneField(Contact, blank=True, default=None, null=True)
    accept_newsletter = models.BooleanField()
    accept_3rdparty = models.BooleanField()

    #User.profile = property(lambda u: ContactProfile.objects.get_or_create(user=u)[0])

    def __unicode__(self):
        return self.user.username
    
 
#signals
def create_profile(sender, instance, signal, created, **kwargs):
    if not created:
        create_profile = False
        try:
            profile = ContactProfile.objects.get(user=instance)
        except ContactProfile.DoesNotExist:
            create_profile = True
    else:
        create_profile = True
        
    if create_profile:
        ContactProfile(user=instance).save()

signals.post_save.connect(create_profile, sender=User)


class CategoryPermission(models.Model):
    category = models.OneToOneField(ArticleCategory)
    can_view_groups = models.ManyToManyField(Group, blank=True, default=None, null=True,
        related_name="can_view_perm")
    can_edit_groups = models.ManyToManyField(Group, blank=True, default=None, null=True,
        related_name="can_edit_perm")
    
    def __unicode__(self):
        return unicode(self.category)
