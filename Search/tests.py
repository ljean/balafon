# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from datetime import datetime
from model_mommy import mommy
from sanza.Crm import models
from sanza.Emailing.models import Emailing, MagicLink
from coop_cms.models import Newsletter
from django.core import management
from django.core import mail
from django.conf import settings
from BeautifulSoup import BeautifulSoup

def get_form_errors(response):
    soup = BeautifulSoup(response.content)
    errors = soup.findAll('ul', {'class':'errorlist'})
    return len(errors)

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def _login(self):
        self.client.login(username="toto", password="abc")

class CreateEmailingTest(BaseTestCase):
    def test_create_mailing(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        newsletter = mommy.make_one(Newsletter)
        
        url = reverse('search_emailing')
        
        response = self.client.post(url, data={
            'create_emailing': True, 
            'newsletter': newsletter.id, 'contacts': ';'.join([unicode(c.id) for c in contacts])
        })
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(Emailing.objects.count(), 1)
        emailing = Emailing.objects.all()[0]
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        self.assertEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 3)
        self.assertEqual(emailing.sent_to.count(), 0)
        
    def test_create_mailing_new_newsletter(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        url = reverse('search_emailing')
        
        response = self.client.post(url, data={
            'create_emailing': True, 'subject': 'Hello',
            'newsletter': 0, 'contacts': ';'.join([unicode(c.id) for c in contacts])
        })
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(Newsletter.objects.count(), 1)
        self.assertEqual(Emailing.objects.count(), 1)
        emailing = Emailing.objects.all()[0]
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        self.assertEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 3)
        self.assertEqual(emailing.sent_to.count(), 0)
        
    def test_create_mailing_new_newsletter_no_subject(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        url = reverse('search_emailing')
        
        response = self.client.post(url, data={
            'create_emailing': True,
            'newsletter': 0, 'contacts': ';'.join([unicode(c.id) for c in contacts])
        })
        self.assertEqual(200, response.status_code)
        self.assertEqual(get_form_errors(response), 1)
        self.assertEqual(Newsletter.objects.count(), 0)
        self.assertEqual(Emailing.objects.count(), 0)
        
        