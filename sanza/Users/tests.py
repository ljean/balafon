# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from datetime import datetime
from model_mommy import mommy
from sanza.Crm import models
from django.core import management
from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from bs4 import BeautifulSoup as BS4
from datetime import datetime, timedelta
from StringIO import StringIO
import sys
from sanza.Users.models import UserPreferences

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        return self.client.login(username="toto", password="abc")


class NotifyDueActionsTestCase(BaseTestCase):
    
    def now(self):
        if settings.USE_TZ:
            return datetime.now().replace(tzinfo=timezone.utc)
        else:
            return datetime.now()
    
    def _notify_due_actions(self, verbosity=0):
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('notify_due_actions', verbosity=verbosity, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        return buf.readlines()
    
    def test_notify_due_actions(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
        for a in actions:
            self.assertTrue(email.body.find(a.subject)>0)
            self.assertTrue(email.body.find(a.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
        
    
    def test_notify_due_actions_not_in_staff(self):
        u = mommy.make(User, is_active=True, is_staff=False, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
    
    def test_notify_due_actions_disabled(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=False)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
    
    def test_notify_due_actions_no_preferences(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        #up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
        
    def test_notify_due_actions_some_in_future(self):
        tomorrow = datetime.today() + timedelta(1)
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=tomorrow, done=False, in_charge=u)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
            self.assertTrue(email.body.find(a.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
    
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            self.assertFalse(email.body.find(a.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
    
    
    def test_notify_due_actions_some_not_in_charge(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            
    def test_notify_due_actions_some_done(self):
        tomorrow = datetime.today() + timedelta(1)
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=True, in_charge=u)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            
    def test_notify_due_actions_some_not_planned(self):
        tomorrow = datetime.today() + timedelta(1)
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", done=False, in_charge=u)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            
    
    def test_notify_due_actions_some_planned_date(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=datetime.today(), done=False, in_charge=u)
        notified_actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)

        
    