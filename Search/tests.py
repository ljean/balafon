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

class GroupSearchTest(BaseTestCase):
    def test_view_group(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD")
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ")
        
        group = mommy.make_one(models.Group, name=u"my group")
        
        group.entities.add(entity1)
        group.save()
        
        url = reverse('search_group', args=[group.id])
        
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_group(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD")
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ")
        
        group = mommy.make_one(models.Group, name=u"my group")
        group.entities.add(entity1)
        group.save()
        
        url = reverse('search')
        
        data = {"gr0#group#0": group.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_entity(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD")
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ")
                
        url = reverse('search')
        
        data = {"gr0#entity_name#0": 'tiny'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_contact(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD")
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ")
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC")
        
        url = reverse('search')
        
        data = {"gr0#contact_name#0": 'ABC'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
        
    def test_search_contact_of_group(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD")
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ")
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC")
        
        group = mommy.make_one(models.Group, name=u"my group")
        group.entities.add(entity1)
        group.save()
        
        url = reverse('search')
        
        data = {"gr0#contact_name#0": 'ABC', 'gr0#group#1': group.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
    def test_search_union_of_contacts(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD")
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ")
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC")
        
        url = reverse('search')
        
        data = {"gr0#contact_name#0": 'ABCD', 'gr1#contact_name#0': 'ABCA'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)