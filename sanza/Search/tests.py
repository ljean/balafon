# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from datetime import datetime, date, timedelta
from model_mommy import mommy
from sanza.Crm import models
from sanza.Emailing.models import Emailing, MagicLink
from coop_cms.models import Newsletter
from django.core import management
from django.core import mail
from django.conf import settings
from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup as BeautifulSoup4
from django.utils.translation import ugettext as _

def get_form_errors(response):
    soup = BeautifulSoup(response.content)
    errors = soup.findAll('ul', {'class':'errorlist'})
    return len(errors)

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        self.client.login(username="toto", password="abc")

class GroupSearchTest(BaseTestCase):
    
    def test_view_search(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_search_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('search'))
        self.assertEqual(302, response.status_code)
        login_url = reverse('django.contrib.auth.views.login')[2:] #login url without lang prefix
        self.assertTrue(response['Location'].find(login_url)>0)
        
    def test_view_group(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make(models.Group, name=u"my group")
        
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
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1)
        group.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_contact_group(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make(models.Group, name=u"my group")
        group.contacts.add(contact1)
        group.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
    
    def test_search_two_group(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.entities.add(entity1)
        group2.entities.add(entity2)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group1.id, "gr0-_-group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_two_group_with_contacts(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.contacts.add(contact1)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.contacts.add(contact1)
        group2.contacts.add(contact2)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group1.id, "gr0-_-group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_two_group_mix_entity_contacts(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.contacts.add(contact1)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.contacts.add(contact1)
        group2.entities.add(entity2)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group1.id, "gr0-_-group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_two_group_not_in(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.entities.add(entity1)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-not_in_group-_-0": group1.id, "gr0-_-not_in_group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
    def test_search_two_group_in_and_not_in(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.entities.add(entity1)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group1.id, "gr0-_-not_in_group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
    def test_search_contacts_two_group_in_and_not_in(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.contacts.add(contact1)
        group1.contacts.add(contact2)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.contacts.add(contact1)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group1.id, "gr0-_-not_in_group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
    def test_search_contacts_entities_two_group_in_and_not_in(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()
        
        group2 = mommy.make(models.Group, name=u"oups")
        group2.contacts.add(contact1)
        group2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group1.id, "gr0-_-not_in_group-_-1": group2.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
    
        
    def test_search_entity(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
                
        url = reverse('search')
        
        data = {"gr0-_-entity_name-_-0": 'tiny'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_contact(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_name-_-0": 'ABC'}
        
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
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1)
        group.save()
        
        url = reverse('search')
        
        data = {"gr0-_-contact_name-_-0": 'ABC', 'gr0-_-group-_-1': group.id}
        
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
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_name-_-0": 'ABCD', 'gr1-_-contact_name-_-0': 'ABCA'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
        
    def test_search_has_email(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_has_email-_-0": 1}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
    
    def test_search_city(self):
        city = mommy.make(models.City)
        entity1 = mommy.make(models.Entity, name=u"My tiny corp", city=city)
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr")
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL")
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", city=city)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC")
        
        url = reverse('search')
        
        data = {"gr0-_-city-_-0": city.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
    
    def test_search_has_no_email(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_has_email-_-0": 0}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)

    def test_search_has_email_and_name(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_has_email-_-0": 1, "gr0-_-entity_name-_-1": entity1.name}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
    #def _create_opportunities_for_between_date(self):
    #    entity1 = mommy.make(models.Entity, name=u"Barthez")
    #    entity2 = mommy.make(models.Entity, name=u"Amoros")
    #    entity3 = mommy.make(models.Entity, name=u"Lizarazu")
    #    entity4 = mommy.make(models.Entity, name=u"Bossis")
    #    entity5 = mommy.make(models.Entity, name=u"Blanc")
    #    entity6 = mommy.make(models.Entity, name=u"Fernandez")
    #    entity7 = mommy.make(models.Entity, name=u"Cantona")
    #    entity8 = mommy.make(models.Entity, name=u"Tigana")
    #    entity9 = mommy.make(models.Entity, name=u"Papin")
    #    entity10 = mommy.make(models.Entity, name=u"Platini")
    #    entity11 = mommy.make(models.Entity, name=u"Zidane")
    #    entity12 = mommy.make(models.Entity, name=u"Deschamps")
    #    entity13 = mommy.make(models.Entity, name=u"Giresse")
    #    entity14 = mommy.make(models.Entity, name=u"Rocheteau")
    #    entity15 = mommy.make(models.Entity, name=u"Thuram")
    #    
    #    opp1 = mommy.make(models.Opportunity, entity=entity1,
    #        start_date=date(2011, 1, 1), end_date=date(2011, 12, 31))
    #    opp2 = mommy.make(models.Opportunity, entity=entity2,
    #        start_date=date(2011, 4, 10), end_date=date(2011, 4, 15))
    #    opp3 = mommy.make(models.Opportunity, entity=entity3,
    #        start_date=date(2011, 1, 1), end_date=date(2011, 4, 10))
    #    opp4 = mommy.make(models.Opportunity, entity=entity4,
    #        start_date=date(2011, 4, 15), end_date=date(2011, 12, 31))
    #    opp5 = mommy.make(models.Opportunity, entity=entity5,
    #        start_date=date(2011, 1, 1), end_date=date(2011, 2, 1))
    #    opp6 = mommy.make(models.Opportunity, entity=entity6,
    #        start_date=date(2011, 7, 1), end_date=date(2011, 8, 1))
    #    opp7 = mommy.make(models.Opportunity, entity=entity7,
    #        start_date=date(2011, 1, 1), ended=False)
    #    opp8 = mommy.make(models.Opportunity, entity=entity8,
    #        start_date=date(2011, 7, 1))
    #    opp9 = mommy.make(models.Opportunity, entity=entity9)
    #    opp10 = mommy.make(models.Opportunity, entity=entity10,
    #        end_date=date(2011, 12, 31))
    #    opp11 = mommy.make(models.Opportunity, entity=entity11,
    #        end_date=date(2011, 4, 15))
    #    opp12 = mommy.make(models.Opportunity, entity=entity12,
    #        end_date=date(2011, 4, 15), ended=True)
    #    opp13 = mommy.make(models.Opportunity, entity=entity13,
    #        end_date=date(2011, 4, 15), ended=False)
    #    opp14 = mommy.make(models.Opportunity, entity=entity14,
    #        start_date=date(2011, 1, 1), ended=True)
    #    
    #    class MyVars: pass
    #    vars = MyVars()
    #    for k, v in locals().items():
    #        setattr(vars, k, v)
    #    return vars
    #
    #    
    #def test_search_opportunity_between(self):
    #    vars = self._create_opportunities_for_between_date()
    #    
    #    url = reverse('search')
    #    
    #    data = {"gr0-_-opportunity_between-_-0": "01/04/2011 01/05/2011"}
    #    
    #    response = self.client.post(url, data=data)
    #    self.assertEqual(200, response.status_code)
    #    
    #    self.assertContains(response, vars.entity1.name)
    #    self.assertContains(response, vars.entity2.name)
    #    self.assertContains(response, vars.entity3.name)
    #    self.assertContains(response, vars.entity4.name)
    #    self.assertContains(response, vars.entity7.name)
    #    self.assertContains(response, vars.entity11.name)
    #    self.assertContains(response, vars.entity12.name)
    #    
    #    self.assertNotContains(response, vars.entity5.name)
    #    self.assertNotContains(response, vars.entity6.name)
    #    self.assertNotContains(response, vars.entity8.name)
    #    self.assertNotContains(response, vars.entity9.name)
    #    self.assertNotContains(response, vars.entity10.name)
    #    self.assertNotContains(response, vars.entity14.name)
    #    self.assertNotContains(response, vars.entity15.name)
    #    
    #def test_search_opportunity_not_between(self):
    #    vars = self._create_opportunities_for_between_date()
    #    
    #    url = reverse('search')
    #    
    #    data = {"gr0-_-no_opportunity_between-_-0": "01/04/2011 01/05/2011"}
    #    
    #    response = self.client.post(url, data=data)
    #    self.assertEqual(200, response.status_code)
    #    
    #    self.assertNotContains(response, vars.entity1.name)
    #    self.assertNotContains(response, vars.entity2.name)
    #    self.assertNotContains(response, vars.entity3.name)
    #    self.assertNotContains(response, vars.entity4.name)
    #    self.assertNotContains(response, vars.entity7.name)
    #    self.assertNotContains(response, vars.entity11.name)
    #    self.assertNotContains(response, vars.entity12.name)
    #    self.assertNotContains(response, vars.entity9.name)
    #    self.assertNotContains(response, vars.entity15.name)
    #    
    #    self.assertContains(response, vars.entity5.name)
    #    self.assertContains(response, vars.entity6.name)
    #    self.assertContains(response, vars.entity8.name)
    #    self.assertContains(response, vars.entity10.name)
    #    self.assertContains(response, vars.entity14.name)
        
class MainContactAndHasLeftSearchTest(BaseTestCase):
    
    def _make_contact(self, main_contact, has_left):
        entity = mommy.make(models.Entity, name=u"TinyTinyCorp")
        contact = entity.default_contact
        contact.lastname = 'TiniMax'
        contact.firstname = 'Boss'
        contact.main_contact = main_contact
        contact.has_left = has_left
        contact.save()
        return entity, contact
    
    def _make_another_contact(self, entity, main_contact, has_left):
        contact = mommy.make(models.Contact, entity=entity)
        contact.lastname = 'TinyMin'
        contact.firstname = 'Other'
        contact.main_contact = main_contact
        contact.has_left = has_left
        contact.save()
        return contact
    
    def test_main_contact(self):
        e, c = self._make_contact(True, False)
        
        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": e.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertContains(response, c.lastname)
        
    def test_main_contact_has_left(self):
        e, c = self._make_contact(True, True)
        
        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": e.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertNotContains(response, c.lastname)
        
    def test_only_one_main_contact(self):
        e, c = self._make_contact(False, False)
        
        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": e.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertNotContains(response, c.lastname)
        
        e.save()
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertContains(response, c.lastname)
        
        self.assertEqual(1, models.Contact.objects.count())
        c = models.Contact.objects.all()[0]
        self.assertEqual(c.main_contact, True)
        
        
    def test_two_main_contacts(self):
        e, c = self._make_contact(False, False)
        c2 = self._make_another_contact(e, True, False)
        
        url = reverse('search')
        data = {"gr0-_-entity_name-_-0": e.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertNotContains(response, c.lastname)
        self.assertContains(response, c2.lastname)
        
class MailtoContactsTest(BaseTestCase):
    
    def setUp(self):
        super(MailtoContactsTest, self).setUp()
        settings.SANZA_MAILTO_LIMIT = 50
        
        
    def _create_contact(self, email=''):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact.lastname = 'TiniMax'
        contact.firstname = 'Boss'
        contact.email = email
        contact.main_contact = True
        contact.has_left = False
        contact.save()
        return entity, contact
        
    def test_mailto_no_email(self):
        entity, contact = self._create_contact()
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, _(u'Mailto: Error, no emails defined'))
        
    def test_mailto_one_email(self):
        email = 'toto@mailinator.com'
        entity, contact = self._create_contact(email)
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('mailto:')==0)
        self.assertTrue(response['Location'].find(email)>0)
        self.assertTrue(response['Location'].find(contact.lastname)>0)
        self.assertTrue(response['Location'].find(contact.firstname)>0)
        
    def test_mailto_one_email_bcc(self):
        email = 'toto@mailinator.com'
        entity, contact = self._create_contact(email)
        url = reverse('search_mailto_contacts', args=[1])
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('mailto:')==0)
        self.assertTrue(response['Location'].find(email)>0)
        self.assertTrue(response['Location'].find(contact.lastname)>0)
        self.assertTrue(response['Location'].find(contact.firstname)>0)
        
    def test_mailto_several_emails(self):
        group = mommy.make(models.Group)
        contacts = []
        for i in xrange(50):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()
        
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('mailto:')==0)
        for contact in contacts:
            self.assertTrue(response['Location'].find(contact.email)>0)
            self.assertTrue(response['Location'].find(contact.lastname)>0)
            self.assertTrue(response['Location'].find(contact.firstname)>0)
        
    def test_mailto_several_emails_more_than_limit_text_mode(self):
        group = mommy.make(models.Group)
        settings.SANZA_MAILTO_LIMIT_AS_TEXT = True
        contacts = []
        for i in xrange(settings.SANZA_MAILTO_LIMIT + 1):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()
        
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        for contact in contacts:
            self.assertTrue(response.content.find(contact.email)>0)
            self.assertTrue(response.content.find(contact.lastname)>0)
            self.assertTrue(response.content.find(contact.firstname)>0)
            
    def test_mailto_several_emails_more_than_limit_clicks_mode(self):
        group = mommy.make(models.Group)
        settings.SANZA_MAILTO_LIMIT_AS_TEXT = False
        contacts = []
        for i in xrange(settings.SANZA_MAILTO_LIMIT * 2):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()
        
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.content.count('class="email-group"'))    
    
    def test_mailto_several_emails_more_than_limit_clicks_mode_not_exact(self):
        group = mommy.make(models.Group)
        settings.SANZA_MAILTO_LIMIT_AS_TEXT = False
        contacts = []
        for i in xrange(settings.SANZA_MAILTO_LIMIT + 1):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()
        
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.content.count('class="email-group"'))    
            
    def test_get_mailto(self):
        url = reverse('search_mailto_contacts', args=[0])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        

class AddToGroupActionTest(BaseTestCase):
    
    def test_add_contact_to_group(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(entity1)
        group.entities.add(entity2)
        group.save()
        
        group2 = mommy.make(models.Group, name="GROUP2")
        self.assertEqual(group2.entities.count(), 0)
        self.assertEqual(group2.contacts.count(), 0)
        
        contacts = [contact1, contact2, contact3]
        url = reverse('search_add_contacts_to_group')
        data = {
            "gr0-_-group-_-0": group.id, 'add_to_group': 'add_to_group',
            'groups': [group2.id], 'on_contact': True, 'contacts': ";".join([str(c.id) for c in contacts]) }
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(reverse('crm_board_panel')))
        
        group2 = models.Group.objects.get(id=group2.id)
        
        for c in contacts:
            self.assertTrue(c in group2.contacts.all())
        for e in [entity1, entity2]:
            self.assertFalse(e in group2.entities.all())
            
    def test_add_entity_to_group(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(entity1)
        group.entities.add(entity2)
        group.save()
        
        group2 = mommy.make(models.Group, name="GROUP2")
        self.assertEqual(group2.entities.count(), 0)
        self.assertEqual(group2.contacts.count(), 0)
        
        contacts = [contact1, contact2, contact3]
        url = reverse('search_add_contacts_to_group')
        data = {
            "gr0-_-group-_-0": group.id, 'add_to_group': 'add_to_group',
            'groups': [group2.id], 'on_contact': False, 'contacts': ";".join([str(c.id) for c in contacts]) }
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(reverse('crm_board_panel')))
        
        group2 = models.Group.objects.get(id=group2.id)
        
        for c in contacts:
            self.assertFalse(c in group2.contacts.all())
        for e in [entity1, entity2]:
            self.assertTrue(e in group2.entities.all())
        
class SameAsTest(BaseTestCase):
    
    def test_search_same_as_not_allowed1(self):
        
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False)
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()
        
        contact2 = mommy.make(models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False)
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.save()
        
        contact1.same_as = models.SameAs.objects.create(main_contact=contact1)
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact1.email)
        self.assertNotContains(response, contact2.email)
        
    def test_search_same_as_not_allowed2(self):
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False)
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()
        
        contact2 = mommy.make(models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False)
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.save()
        
        contact1.same_as = models.SameAs.objects.create(main_contact=contact2)
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        #print response
        self.assertNotContains(response, contact1.email)
        self.assertContains(response, contact2.email)
        
    def test_search_same_as_allowed(self):
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False)
        contact1.entity.name = u'Tiny Corp'
        contact1.entity.default_contact.delete()
        contact1.entity.save()
        
        contact2 = mommy.make(models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False)
        contact2.entity.name = u'Other Corp'
        contact2.entity.default_contact.delete()
        contact2.entity.save()
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(contact1.entity)
        group.entities.add(contact2.entity)
        group.save()
        
        contact1.same_as = models.SameAs.objects.create(main_contact=contact1)
        contact1.save()
        contact2.same_as = contact1.same_as
        contact2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '1'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.email)
        self.assertContains(response, contact2.email)
        
    #def test_search_same_as_not_allowed_no_prio(self):
    #    contact1 = mommy.make(models.Contact, lastname=u"ABCD", email="contact1@email1.fr", main_contact=True, has_left=False)
    #    contact1.entity.name = u'Tiny Corp'
    #    contact1.entity.default_contact.delete()
    #    contact1.entity.save()
    #    
    #    contact2 = mommy.make(models.Contact, lastname=u"ABCD", email="contact2@email2.fr", main_contact=True, has_left=False)
    #    contact2.entity.name = u'Other Corp'
    #    contact2.entity.default_contact.delete()
    #    contact2.entity.save()
    #    
    #    group = mommy.make(models.Group, name="GROUP1")
    #    group.entities.add(contact1.entity)
    #    group.entities.add(contact2.entity)
    #    group.save()
    #    
    #    contact1.same_as = models.SameAs.objects.create(main_contact=None)
    #    contact1.save()
    #    contact2.same_as = contact1.same_as
    #    contact2.save()
    #    
    #    url = reverse('search')
    #    
    #    data = {"gr0-_-group-_-0": group.id, "gr0-_-no_same_as-_-1": '0'}
    #    
    #    response = self.client.post(url, data=data)
    #    self.assertEqual(200, response.status_code)
    #    c1_found = response.content.find(contact1.email)>0
    #    c2_found = response.content.find(contact2.email)>0
    #    
    #    #To be investigated
    #    self.assertTrue(c1_found or c2_found)
    #    self.assertFalse(c1_found and c2_found)
        
class HasZipTest(BaseTestCase):
    
    def test_has_zip(self):
        
        contact1 = mommy.make(models.Contact, zip_code="42424", lastname="AAAAAA")
        contact2 = mommy.make(models.Contact, zip_code="", lastname="BBBBBBB")
        
        contact3 = mommy.make(models.Contact, zip_code="", lastname="CCCCCCCC")
        contact3.entity.zip_code = u'45454'
        contact3.entity.save()
        
        contact4 = mommy.make(models.Contact, zip_code="56565", lastname="DDDDDDDD")
        contact4.entity.zip_code = u'45454'
        contact4.entity.save()
        
        
        url = reverse('search')
        
        data = {"gr0-_-has_zip-_-0": 1}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact4.lastname)
        
    def test_has_no_zip(self):
        
        contact1 = mommy.make(models.Contact, zip_code="42424", lastname="AAAAAA")
        contact2 = mommy.make(models.Contact, zip_code="", lastname="BBBBBBB")
        
        contact3 = mommy.make(models.Contact, zip_code="", lastname="CCCCCCCC")
        contact3.entity.zip_code = u'45454'
        contact3.entity.save()
        
        contact4 = mommy.make(models.Contact, zip_code="56565", lastname="DDDDDDDD")
        contact4.entity.zip_code = u'45454'
        contact4.entity.save()
        
        
        url = reverse('search')
        
        data = {"gr0-_-has_zip-_-0": 0}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)

class HasEntitySearchTest(BaseTestCase):
    
    def test_contact_has_entity(self):
        
        entity1 = mommy.make(models.Entity, is_single_contact=False)
        entity2 = mommy.make(models.Entity, is_single_contact=True)
        
        contact1 = entity1.default_contact
        contact1.lastname = "AZERTYUIOP"
        contact1.save()
        
        contact2 = entity2.default_contact
        contact2.lastname = "QWERTYUIOP"
        contact2.save()
        
        
        url = reverse('search')
        
        data = {"gr0-_-has_entity-_-0": 1}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        
    def test_contact_doesnt_have_entity(self):
        
        entity1 = mommy.make(models.Entity, is_single_contact=False)
        entity2 = mommy.make(models.Entity, is_single_contact=True)
        
        contact1 = entity1.default_contact
        contact1.lastname = "AZERTYUIOP"
        contact1.save()
        
        contact2 = entity2.default_contact
        contact2.lastname = "QWERTYUIOP"
        contact2.save()
        
        
        url = reverse('search')
        
        data = {"gr0-_-has_entity-_-0": 0}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)

        
class ModifiedSearchTest(BaseTestCase):
    
    def test_contact_modified_today(self):
        
        contact1 = mommy.make(models.Contact, lastname="Azertuiop")
        
        url = reverse('search')
        
        data = {"gr0-_-contact_by_modified_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact1.lastname)
        
    def test_contact_modified_tomorrow(self):
        
        contact1 = mommy.make(models.Contact, lastname="Azertuiop")
        
        url = reverse('search')
        
        dt = date.today() + timedelta(1)
        data = {"gr0-_-contact_by_modified_date-_-0": '{0} {0}'.format(dt.strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, contact1.lastname)
        
    def test_entity_modified_today(self):
        
        contact1 = mommy.make(models.Contact, lastname="Azertuiop")
        
        url = reverse('search')
        
        data = {"gr0-_-entity_by_modified_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact1.lastname)
        
    def test_entity_modified_today_no_single_contact(self):
        
        contact1 = mommy.make(models.Contact, lastname="Azertuiop")
        entity2 = mommy.make(models.Entity, is_single_contact=True)
        contact2 = entity2.default_contact
        contact2.lastname = "QWERTYUIOP"
        contact2.save()
        
        url = reverse('search')
        
        data = {"gr0-_-entity_by_modified_date-_-0": '{0} {0}'.format(date.today().strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        
    def test_entity_modified_tomorrow(self):
        
        contact1 = mommy.make(models.Contact, lastname="Azertuiop")
        
        url = reverse('search')
        
        dt = date.today() + timedelta(1)
        data = {"gr0-_-entity_by_modified_date-_-0": '{0} {0}'.format(dt.strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, contact1.lastname)
        
class RelationshipSearchTest(BaseTestCase):
    
    def test_contact_by_relationship_type_with_reverse(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        
        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        
        url = reverse('search')
        
        data = {"gr0-_-contacts_by_relationship_type-_-0": master.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, obi.lastname)
        self.assertNotContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)
        
    def test_contact_by_relationship_type_reverse(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        
        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        
        url = reverse('search')
        
        data = {"gr0-_-contacts_by_relationship_type-_-0": -master.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, obi.lastname)
        self.assertContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)
        
    def test_contact_by_relationship_type(self):    
        john = mommy.make(models.Contact, firstname="Hohn", lastname="Lennon")
        ringo = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        friends = mommy.make(models.RelationshipType, name="Fiends")
        
        r = models.Relationship.objects.create(contact1=john, contact2=ringo, relationship_type=friends)
        
        url = reverse('search')
        
        data = {"gr0-_-contacts_by_relationship_type-_-0": friends.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, john.lastname)
        self.assertContains(response, ringo.lastname)
        self.assertNotContains(response, doe.lastname)
        
    def test_contact_by_relationship_date(self):    
        john = mommy.make(models.Contact, firstname="Hohn", lastname="Lennon")
        ringo = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        friends = mommy.make(models.RelationshipType, name="Fiends")
        
        r = models.Relationship.objects.create(contact1=john, contact2=ringo, relationship_type=friends)
        
        url = reverse('search')
        
        dt = date.today()
        data = {"gr0-_-contacts_by_relationship_dates-_-0": '{0} {0}'.format(dt.strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, john.lastname)
        self.assertContains(response, ringo.lastname)
        self.assertNotContains(response, doe.lastname)
        
    def test_contact_by_relationship_not_in_date(self):    
        john = mommy.make(models.Contact, firstname="Hohn", lastname="Lennon")
        ringo = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        friends = mommy.make(models.RelationshipType, name="Fiends")
        
        r = models.Relationship.objects.create(contact1=john, contact2=ringo, relationship_type=friends)
        
        url = reverse('search')
        
        dt = date.today() + timedelta(1)
        data = {"gr0-_-contacts_by_relationship_dates-_-0": '{0} {0}'.format(dt.strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, john.lastname)
        self.assertNotContains(response, ringo.lastname)
        self.assertNotContains(response, doe.lastname)
        
        