# -*- coding: utf-8 -*-

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()
    
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
from django.utils.unittest.case import SkipTest
from sanza.Crm import settings as crm_settings
from unittest import skipIf

def get_form_errors(response):
    soup = BeautifulSoup4(response.content)
    #errors = soup.findAll('ul', {'class':'errorlist'})
    errors = soup.select('.field-error .label')
    return errors

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def _login(self):
        rc = self.client.login(username="toto", password="abc")

class CitySearchTest(BaseTestCase):
    
    def test_view_search(self):
        city1 = mommy.make(models.City)
        city2 = mommy.make(models.City)
        
        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()
        
        entity2 = mommy.make(models.Entity)
        contact2 = entity2.default_contact
        contact2.lastname = "EFGH"
        contact2.main_contact = True
        contact2.has_left = False
        contact2.city = city1
        contact2.save()
        
        entity3 = mommy.make(models.Entity)
        contact3 = entity3.default_contact
        contact3.lastname = "IJKL"
        contact3.main_contact = True
        contact3.has_left = False
        contact3.city = city2
        contact3.save()
        
        entity4 = mommy.make(models.Entity)
        contact4 = entity3.default_contact
        contact4.lastname = "MNOP"
        contact4.main_contact = True
        contact4.has_left = False
        contact4.save()
        
        url = reverse("search_cities", args=[city1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)
        
    def test_quick_search_city1(self):
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")
        
        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()
        
        url = reverse("quick_search")
        data = {"text": "Zoo"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, city1.name)
        self.assertNotContains(response, city2.name)
        
    def test_quick_search_city2(self):
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")
        
        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()
        
        url = reverse("quick_search")
        data = {"text": "oo"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, city1.name)
        self.assertNotContains(response, city2.name)
        
    def test_quick_search_city3(self):
        city1 = mommy.make(models.City, name="ZooPark")
        city2 = mommy.make(models.City, name="VodooPark")
        
        entity1 = mommy.make(models.Entity, city=city1)
        contact1 = entity1.default_contact
        contact1.lastname = "ABCD"
        contact1.main_contact = True
        contact1.has_left = False
        contact1.save()
        
        entity3 = mommy.make(models.Entity)
        contact3 = entity3.default_contact
        contact3.lastname = "IJKL"
        contact3.main_contact = True
        contact3.has_left = False
        contact3.city = city2
        contact3.save()
        
        url = reverse("quick_search")
        data = {"text": "oo"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, city1.name)
        self.assertContains(response, city2.name)


class EmailSearchTest(BaseTestCase):
    
    def test_search_email(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, email="abcd@mailinator.com", entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_entity_email-_-0": "mailinator"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
    def test_search_email_empty(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, email="abcd@mailinator.com", entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_entity_email-_-0": ""}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual(1, len(soup.select('.field-error')))
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
    def test_search_email_entity(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, entity=entity2, lastname=u"RTYU", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_entity_email-_-0": "mailinator"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, contact4.lastname)
        
    def test_search_email_full(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, email="abcd@mailinator.com", entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, entity=entity2, lastname=u"RTYU", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_entity_email-_-0": "contact@mailinator.com"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, contact4.lastname)
        
    def test_search_email_none(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, email="abcd@mailinator.com", entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", email="contact@mailinator.com")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        contact4 = mommy.make(models.Contact, entity=entity2, lastname=u"RTYU", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_entity_email-_-0": "toto@toto.com"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual(0, len(soup.select('.field-error')))
        
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact4.lastname)


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
        
    def test_search_contact_notes(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False, notes="NOTE: 20/20")
        
        entity3 = mommy.make(models.Entity, name=u"The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        for c in [contact1, contact4]:
            c.notes = "{0} - Hello Dolly - {0}".format(c.lastname)
            c.save()
        
        url = reverse('search')
        
        data = {"gr0-_-contact_notes-_-0": 'Dolly'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
        
    def test_search_contact_firstname(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, firstname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, firstname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_firstname-_-0": 'ABC'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.firstname)
        self.assertNotContains(response, contact3.firstname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.firstname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.firstname)
    
    def test_search_entity_notes(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp", notes="This one should be found.")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", notes="Not this one")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org", notes="Found")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-entity_notes-_-0": 'found'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
        
    def test_search_entity_description(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp", description="This one should be found.")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp", description="Not this one")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org", description="Found")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-entity_description-_-0": 'found'}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        
        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name)
        self.assertContains(response, contact4.lastname)
        
    def test_search_contact_notes(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", notes="This one should be found.", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", notes="Not this one", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"ABCABC", notes="Found", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-contact_notes-_-0": 'found'}
        
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
        
    def test_search_has_left_exclude(self):
        e, c1 = self._make_contact(True, True)
        c2 = self._make_another_contact(e, True, False)
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(e)
        group.save()
        
        url = reverse('search')
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertNotContains(response, c1.lastname)
        self.assertContains(response, c2.lastname)
        
    def test_search_has_left_include(self):
        e, c1 = self._make_contact(True, True)
        c2 = self._make_another_contact(e, True, False)
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(e)
        group.save()
        
        url = reverse('search')
        data = {"gr0-_-group-_-0": group.id, "gr0-_-contact_has_left-_-1": 1, }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertContains(response, c1.lastname)
        self.assertContains(response, c2.lastname)
        
    def test_search_has_left_only(self):
        e, c1 = self._make_contact(True, True)
        c2 = self._make_another_contact(e, True, False)
        
        group = mommy.make(models.Group, name="GROUP1")
        group.entities.add(e)
        group.save()
        
        url = reverse('search')
        data = {"gr0-_-group-_-0": group.id, "gr0-_-contact_has_left-_-1": 0, }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e.name)
        self.assertContains(response, c1.lastname)
        self.assertNotContains(response, c2.lastname)
        
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
    
    @skipIf(not crm_settings.ALLOW_SINGLE_CONTACT, "ALLOW_SINGLE_CONTACT disabled")
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
        
    @skipIf(not crm_settings.ALLOW_SINGLE_CONTACT, "ALLOW_SINGLE_CONTACT disabled")
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
        
class EmailingSearchTest(BaseTestCase):
    
    def test_contact_by_emailing_sent(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        emailing = mommy.make(Emailing)
        emailing.sent_to.add(obi)
        emailing.save()
        
        url = reverse('search')
        
        data = {"gr0-_-emailing_sent-_-0": emailing.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, obi.lastname)
        self.assertNotContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)
        
    def test_contact_by_emailing_opened(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        emailing = mommy.make(Emailing)
        emailing.sent_to.add(obi)
        emailing.sent_to.add(anakin)
        emailing.opened_emails.add(obi)
        
        emailing.save()
        
        url = reverse('search')
        
        data = {"gr0-_-emailing_opened-_-0": emailing.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, obi.lastname)
        self.assertNotContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)
        
    def test_contact_by_emailing_error(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        
        url = reverse('search')
        
        data = {"gr0-_-emailing_opened-_-0": 333}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, obi.lastname)
        self.assertNotContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)
        
        self.assertEqual(1, len(get_form_errors(response)))

class QuickSearchTest(BaseTestCase):
    
    def test_contact_by_name(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        sw = mommy.make(models.Entity)
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
            
        url = reverse('quick_search')
        
        data = {"text": u"Skywalker"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.firstname)
        self.assertNotContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        
    def test_has_left_contact_by_name(self):    
        sw = mommy.make(models.Entity)
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", entity=sw, has_left=True)
            
        url = reverse('quick_search')
        
        data = {"text": u"Skywalker"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.firstname)
        self.assertContains(response, luke.firstname)
        
    def test_has_left_contact_by_entity_name(self):    
        sw = mommy.make(models.Entity, name="Star-Wars", is_single_contact=False)
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", entity=sw, has_left=True)
        leia = mommy.make(models.Contact, firstname="Leia", lastname="Skywalker", entity=sw)
        shmi = mommy.make(models.Contact, firstname="Shmi", lastname="Skywalker", entity=sw, main_contact=False)
            
        url = reverse('quick_search')
        
        data = {"text": u"Star-Wars"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, anakin.firstname)
        self.assertNotContains(response, shmi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertContains(response, leia.firstname)
        
    def test_contact_by_entity_name(self):    
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")
        sw = mommy.make(models.Entity, name="Starwars")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
        st = mommy.make(models.Entity, name="StarTrek")
        pic = mommy.make(models.Contact, firstname="Jean-Luc", lastname="Piccard", entity=st)
        ds = mommy.make(models.Entity, name="DarkSide")
        palpatine = mommy.make(models.Contact, firstname="Senateur", lastname="Palpatine", entity=ds)
            
        url = reverse('quick_search')
        
        data = {"text": u"Star"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, pic.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, palpatine.firstname)
        
    def test_contact_by_phone(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", phone="04.99.99.99.99")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", mobile="04.99.00.00.00")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", phone="03.33.33.33.33")
        sw = mommy.make(models.Entity, phone="04.99.11.22.33")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
            
        url = reverse('quick_search')
        
        data = {"text": u"04.99"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.phone)
        self.assertContains(response, obi.mobile)
        self.assertContains(response, sw.phone)
        self.assertNotContains(response, doe.phone)
        
        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, sw.name)
        self.assertNotContains(response, doe.firstname)
        
    def test_contact_by_phone_has_left(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", phone="04.99.99.99.99", has_left=True)
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", mobile="04.99.00.00.00", has_left=True)
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", phone="03.33.33.33.33")
        sw = mommy.make(models.Entity, phone="04.99.11.22.33")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw, has_left=True)
            
        url = reverse('quick_search')
        
        data = {"text": u"04.99"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.phone)
        self.assertContains(response, obi.mobile)
        self.assertContains(response, sw.phone)
        self.assertNotContains(response, doe.phone)
        
        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, sw.name)
        self.assertNotContains(response, doe.firstname)

        
    def test_contact_by_email(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", email="anakin@starwars.com")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", email="obiwan@starwars.com")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", email="john.doe@toto.fr")
        sw = mommy.make(models.Entity, email="contact@starwars.com")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
        sidious = mommy.make(models.Contact, firstname="Dark", lastname="Sidious", entity=sw, email="sidious@darkside.com")
            
        url = reverse('quick_search')
        
        data = {"text": u"@starwars.com"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.email)
        self.assertContains(response, obi.email)
        self.assertContains(response, sw.email)
        self.assertNotContains(response, doe.email)
        self.assertNotContains(response, sidious.email)
        
        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, sidious.firstname)
        
    def test_contact_by_email_has_left(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", email="anakin@starwars.com", has_left=True)
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", email="obiwan@starwars.com", has_left=True)
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", email="john.doe@toto.fr")
        sw = mommy.make(models.Entity, email="contact@starwars.com")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw, has_left=True)
        sidious = mommy.make(models.Contact, firstname="Dark", lastname="Sidious", entity=sw, email="sidious@darkside.com")
            
        url = reverse('quick_search')
        
        data = {"text": u"@starwars.com"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.email)
        self.assertContains(response, obi.email)
        self.assertContains(response, sw.email)
        self.assertNotContains(response, doe.email)
        self.assertNotContains(response, sidious.email)
        
        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, sidious.firstname)
        
    def test_contact_by_email_no_at(self):    
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker", email="anakin@starwars.com")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi", email="obiwan@starwars.com")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John", email="john.doe@toto.fr")
        sw = mommy.make(models.Entity, email="contact@starwars.com")
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker", entity=sw)
        sidious = mommy.make(models.Contact, firstname="Dark", lastname="Sidious", entity=sw, email="sidious@darkside.com")
            
        url = reverse('quick_search')
        
        data = {"text": u"starwars.com"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, anakin.email)
        self.assertContains(response, obi.email)
        self.assertContains(response, sw.email)
        self.assertNotContains(response, doe.email)
        self.assertNotContains(response, sidious.email)
        
        self.assertContains(response, anakin.firstname)
        self.assertContains(response, obi.firstname)
        self.assertContains(response, luke.firstname)
        self.assertNotContains(response, doe.firstname)
        self.assertNotContains(response, sidious.firstname)
        
class ActionSearchTest(BaseTestCase):
        
    def test_search_action_type_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        at = mommy.make(models.ActionType, name=u"my action type")
        action = mommy.make(models.Action, type=at)
        action.entities.add(entity1)
        action.entities.add(entity2)
        action.save()
        
        _at = mommy.make(models.ActionType, name=u"another action type")
        action = mommy.make(models.Action, type=_at)
        action.entities.add(entity3)
        action.save()
        
        url = reverse('search')
        
        data = {"gr0-_-action_type-_-0": at.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        
        
    def test_search_action_type_contacts(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        at = mommy.make(models.ActionType, name=u"my action type")
        action = mommy.make(models.Action, type=at)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, type=at)
        action.contacts.add(contact2)
        action.save()
        
        _at = mommy.make(models.ActionType, name=u"another action type")
        action = mommy.make(models.Action, type=_at)
        action.contacts.add(contact5)
        action.save()
        
        url = reverse('search')
        
        data = {"gr0-_-action_type-_-0": at.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
    def test_search_action_type_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        at = mommy.make(models.ActionType, name=u"my action type")
        action = mommy.make(models.Action, type=at)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, type=at)
        action.entities.add(entity2)
        action.save()
        
        _at = mommy.make(models.ActionType, name=u"another action type")
        action = mommy.make(models.Action, type=_at)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()
        
        url = reverse('search')
        
        data = {"gr0-_-action_type-_-0": at.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
    def test_search_action_subject_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        action = mommy.make(models.Action, subject="Hello world")
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, subject="Hello world")
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, subject="Bye-bye")
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()
        
        url = reverse('search')
        
        data = {"gr0-_-action_name-_-0": "Hello world"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
    def test_search_action_in_progress_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        action = mommy.make(models.Action, done=False)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, done=False)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-action-_-0": 1}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    def test_search_no_action_in_progress_contacts_and_entities(self):
        contact1 = mommy.make(models.Contact, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=contact1.entity, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=contact1.entity, lastname=u"EFGH", main_contact=True, has_left=False)
        
        contact2 = mommy.make(models.Contact, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        contact4 = mommy.make(models.Contact, lastname=u"MNOP", main_contact=True, has_left=False)
        
        contact5 = mommy.make(models.Contact, lastname=u"RSTU", main_contact=True, has_left=False)
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        contact1.entity.default_contact.delete()
        contact2.entity.default_contact.delete()
        contact4.entity.default_contact.delete()
        contact5.entity.default_contact.delete()
        contact7.entity.default_contact.delete()
        
        action = mommy.make(models.Action, done=False)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, done=False)
        action.entities.add(contact2.entity)
        action.save()
        
        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(contact4.entity)
        action.save()
        
        url = reverse('search')
        
        data = {"gr0-_-action-_-0": 0}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertNotContains(response, contact2.lastname)
        
        self.assertContains(response, contact4.lastname)
        
        self.assertContains(response, contact5.lastname)
        
        self.assertContains(response, contact7.lastname)
        
    def test_search_action_by_done_date_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, done=True)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, done=True)
        action.contacts.add(contact5)
        action.entities.add(entity3)
        action.done_date = datetime.now() - timedelta(10)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)
        
        data = {"gr0-_-action_by_done_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    def test_search_action_by_planned_date_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        action = mommy.make(models.Action, planned_date=datetime.now())
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, planned_date=datetime.now())
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, planned_date=datetime.now()- timedelta(10))
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        dt1 = datetime.now() - timedelta(1)
        dt2 = datetime.now() + timedelta(1)
        
        data = {"gr0-_-action_by_planned_date-_-0": u"{0} {1}".format(dt1.strftime("%d/%m/%Y"), dt2.strftime("%d/%m/%Y"))}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    def test_search_action_by_in_charge_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        user1 = mommy.make(User)
        user2 = mommy.make(User)
        
        action = mommy.make(models.Action, in_charge=user1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, in_charge=user1)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, in_charge=user2)
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-action_by_user-_-0": user1.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
        
    def test_search_action_by_amount_gte_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        action = mommy.make(models.Action, amount=20)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, amount=30)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, amount=10)
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-action_gte_amount-_-0": 15}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    def test_search_action_by_amout_lt_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        action = mommy.make(models.Action, amount=10)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, amount=5)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, amount=20)
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-action_lt_amount-_-0": 15}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertContains(response, entity3.name) #amount default value is 0 
        self.assertContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    def test_search_action_status_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        s1 = mommy.make(models.ActionStatus)
        s2 = mommy.make(models.ActionStatus)
        
        action = mommy.make(models.Action, status=s1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, status=s1)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, status=s2)
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-action_status-_-0": s1.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    def test_search_action_opportunity_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        s1 = mommy.make(models.Opportunity)
        s2 = mommy.make(models.Opportunity)
        
        action = mommy.make(models.Action, opportunity=s1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, opportunity=s1)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, opportunity=s2)
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-opportunity-_-0": s1.id}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        
    #def test_search_action_not_opportunity_contacts_and_entities(self):
    #    entity1 = mommy.make(models.Entity, name=u"My tiny corp")
    #    contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
    #    contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
    #    contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
    #    
    #    entity2 = mommy.make(models.Entity, name=u"Other corp")
    #    contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
    #    
    #    entity3 = mommy.make(models.Entity, name=u"A big big corp")
    #    contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
    #    
    #    entity4 = mommy.make(models.Entity, name=u"A huge corp")
    #    contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
    #    
    #    s1 = mommy.make(models.Opportunity)
    #    s2 = mommy.make(models.Opportunity)
    #    
    #    action = mommy.make(models.Action, opportunity=s2)
    #    action.contacts.add(contact1)
    #    action.contacts.add(contact3)
    #    action.save()
    #    
    #    action = mommy.make(models.Action, opportunity=s2)
    #    action.entities.add(entity2)
    #    action.save()
    #    
    #    action = mommy.make(models.Action, opportunity=s1)
    #    action.contacts.add(contact5)
    #    action.save()
    #    
    #    action = mommy.make(models.Action)
    #    action.entities.add(entity3)
    #    action.save()
    #    
    #    contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
    #    
    #    url = reverse('search')
    #    
    #    data = {"gr0-_-not_opportunity-_-0": s1.id}
    #    
    #    response = self.client.post(url, data=data)
    #    self.assertEqual(200, response.status_code)
    #    
    #    soup = BeautifulSoup4(response.content)
    #    self.assertEqual([], list(soup.select(".field-error")))
    #    
    #    self.assertContains(response, entity1.name)
    #    self.assertContains(response, contact1.lastname)
    #    self.assertContains(response, contact3.lastname)
    #    self.assertNotContains(response, contact6.lastname)
    #    
    #    self.assertContains(response, entity2.name)
    #    self.assertContains(response, contact2.lastname)
    #    
    #    self.assertNotContains(response, entity3.name)
    #    self.assertNotContains(response, contact4.lastname)
    #    
    #    self.assertNotContains(response, entity4.name)
    #    self.assertNotContains(response, contact5.lastname)
    #    
    #    self.assertNotContains(response, contact7.lastname)
    
    def test_search_action_opportunity_name_contacts_and_entities(self):
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        contact6 = mommy.make(models.Contact, entity=entity1, lastname=u"EFGH", main_contact=True, has_left=False)
        
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make(models.Entity, name=u"A big big corp")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname=u"MNOP", main_contact=True, has_left=False)
        
        entity4 = mommy.make(models.Entity, name=u"A huge corp")
        contact5 = mommy.make(models.Contact, entity=entity4, lastname=u"RSTU", main_contact=True, has_left=False)
        
        s1 = mommy.make(models.Opportunity, name="ABCD")
        s2 = mommy.make(models.Opportunity, name="BCDA")
        s3 = mommy.make(models.Opportunity, name="ZZZZ")
        
        
        action = mommy.make(models.Action, opportunity=s1)
        action.contacts.add(contact1)
        action.contacts.add(contact3)
        action.save()
        
        action = mommy.make(models.Action, opportunity=s2)
        action.entities.add(entity2)
        action.save()
        
        action = mommy.make(models.Action, opportunity=s3)
        action.contacts.add(contact5)
        action.save()
        
        action = mommy.make(models.Action)
        action.entities.add(entity3)
        action.save()
        
        contact7 = mommy.make(models.Contact, lastname=u"@!+=", main_contact=True, has_left=False)
        
        url = reverse('search')
        
        data = {"gr0-_-opportunity_name-_-0": "BCD"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        soup = BeautifulSoup4(response.content)
        self.assertEqual([], list(soup.select(".field-error")))
        
        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertNotContains(response, contact6.lastname)
        
        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)
        
        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact4.lastname)
        
        self.assertNotContains(response, entity4.name)
        self.assertNotContains(response, contact5.lastname)
        
        self.assertNotContains(response, contact7.lastname)
        