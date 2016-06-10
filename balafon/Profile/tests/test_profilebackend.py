# -*- coding: utf-8 -*-

from unittest import skipIf

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from model_mommy import mommy
from registration.models import RegistrationProfile

from balafon.Crm import models
from balafon.Profile.utils import create_profile_contact, notify_registration


@skipIf(not ("balafon.Profile" in settings.INSTALLED_APPS), "registration not installed")
class ProfileBackendTest(TestCase):
    
    def setUp(self):
        settings.BALAFON_NOTIFICATION_EMAIL = "ljean@apidev.fr"
    
    def _create_user(self, **kwargs):
        data = {
            'username': "tutu",
            'email': "tutu@tutu.fr",
            'last_name': "Utu",
            'first_name': "Thierry"
        }
        data.update(kwargs)
        return User.objects.create(**data)
    
    def _create_profile_and_check(self, user):
        profile = create_profile_contact(user)
        contact = models.Contact.objects.get(email=user.email)
        self.assertEqual(contact.lastname, user.last_name)
        self.assertEqual(contact.firstname, user.first_name)
        return profile
    
    def test_create_balafon_contact(self):
        user = self._create_user()
        RegistrationProfile(user=user, activation_key=RegistrationProfile.ACTIVATED)
        self._create_profile_and_check(user)
        
    def test_create_balafon_contact_no_profile(self):
        user = self._create_user()
        self._create_profile_and_check(user)
    
    def test_create_balafon_contact_exists(self):
        user = self._create_user()
        self._create_profile_and_check(user)
        old_last_name = user.last_name
        old_first_name = user.first_name
        user.last_name = "John"
        user.first_name = "Doe"
        user.save()
        user.last_name = old_last_name
        user.first_name = old_first_name
        self._create_profile_and_check(user)
        self.assertEqual(models.Contact.objects.count(), 1)
    
    def test_create_balafon_contact_duplicate_email(self):
        user = self._create_user()
        contact = mommy.make(models.Contact, email=user.email)
        contact.entity.default_contact.delete()
        self._create_profile_and_check(user)
        self.assertEqual(models.Contact.objects.filter(email=user.email).count(), 1)
        self.assertEqual(models.Action.objects.count(), 1)

    def test_create_balafon_contact_multiple_email(self):
        user = self._create_user()
        contact1 = mommy.make(models.Contact, email=user.email)
        contact2 = mommy.make(models.Contact, email=user.email)
        # remove default contacts
        contact1.entity.contact_set.exclude(id=contact1.id).delete()
        contact2.entity.contact_set.exclude(id=contact2.id).delete()

        profile = create_profile_contact(user)
        contact = profile.contact
        self.assertEqual(contact.lastname, user.last_name)
        self.assertEqual(contact.firstname, user.first_name)

        self.assertEqual(models.Contact.objects.filter(email=user.email).count(), 3)
        # warn duplicates + account creation

        self.assertEqual(models.Action.objects.count(), 2)
        for action in models.Action.objects.all():
            self.assertEqual(list(action.contacts.all()), [contact])
    
    def test_notifiy_registration(self):
        user = self._create_user()
        profile = self._create_profile_and_check(user)
        
        notify_registration(profile)
        self.assertEqual(len(mail.outbox), 1)
        
        notif_email = mail.outbox[0]
        self.assertEqual(notif_email.to, [settings.BALAFON_NOTIFICATION_EMAIL])
        self.assertEqual(notif_email.cc, [])
        self.assertTrue(notif_email.body.find(user.email)>0)

