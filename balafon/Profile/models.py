# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from coop_cms.models import ArticleCategory

from balafon.Crm.models import Contact, Group, City, EntityType


@python_2_unicode_compatible
class ContactProfile(models.Model):
    """Info creating a contact from registration"""

    class Meta:
        verbose_name = _('Contact profile')
        verbose_name_plural = _('Contact profiles')
    
    GENDER_CHOICE = (
        (Contact.GENDER_NOT_SET, ''),
        (Contact.GENDER_MALE, _('Mr')),
        (Contact.GENDER_FEMALE, _('Mrs')),
    )

    user = models.OneToOneField(User)

    contact = models.OneToOneField(Contact, blank=True, default=None, null=True)

    entity_name = models.CharField(_('Entity name'), max_length=200, blank=True, default="")
    entity_type = models.ForeignKey(EntityType, verbose_name=_('Entity type'), blank=True, null=True, default=None)

    zip_code = models.CharField(_('Zip code'), max_length=20, blank=True, default='')
    city = models.ForeignKey(City, verbose_name=_('City'), blank=True, default=None, null=True)
    gender = models.IntegerField(_('Gender'), choices=GENDER_CHOICE, blank=True, default=0)
    lastname = models.CharField(_('last name'), max_length=200, blank=True, default='')
    firstname = models.CharField(_('first name'), max_length=200, blank=True, default='')

    birth_date = models.DateField(_("birth date"), blank=True, default=None, null=True)

    phone = models.CharField(_('phone'), max_length=200, blank=True, default='')
    mobile = models.CharField(_('mobile'), max_length=200, blank=True, default='')

    address = models.CharField(_('address'), max_length=200, blank=True, default='')
    address2 = models.CharField(_('address 2'), max_length=200, blank=True, default='')
    address3 = models.CharField(_('address 3'), max_length=200, blank=True, default='')
    cedex = models.CharField(_('cedex'), max_length=200, blank=True, default='')

    subscriptions_ids = models.CharField(max_length=100, default="", blank=True)

    groups_ids = models.CharField(max_length=100, default="", blank=True)

    def __str__(self):
        return self.user.username
    
 
# signals
def create_profile(sender, instance, signal, created, **kwargs):
    if not created:
        created_profile = False
        try:
            ContactProfile.objects.get(user=instance)
        except ContactProfile.DoesNotExist:
            created_profile = True
    else:
        created_profile = True
        
    if created_profile:
        ContactProfile(user=instance).save()


if "balafon.Profile" in settings.INSTALLED_APPS:
    signals.post_save.connect(create_profile, sender=User)


@python_2_unicode_compatible
class CategoryPermission(models.Model):
    """Permissions on category"""

    class Meta:
        verbose_name = _('Category permission')
        verbose_name_plural = _('Category permissions')

    category = models.OneToOneField(ArticleCategory)
    can_view_groups = models.ManyToManyField(
        Group, blank=True, default=None, related_name="can_view_perm"
    )
    can_edit_groups = models.ManyToManyField(
        Group, blank=True, default=None, related_name="can_edit_perm"
    )
    
    def __str__(self):
        return '{0}'.format(self.category)
