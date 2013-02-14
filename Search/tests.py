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
from datetime import date
from django.utils.translation import ugettext as _

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
    
    def test_view_search(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_view_group(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
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
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make_one(models.Group, name=u"my group")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make_one(models.Group, name=u"my group")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.contacts.add(contact1)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.contacts.add(contact1)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.contacts.add(contact1)
        group1.contacts.add(contact2)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group1 = mommy.make_one(models.Group, name=u"my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()
        
        group2 = mommy.make_one(models.Group, name=u"oups")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
                
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
        group = mommy.make_one(models.Group, name=u"my group")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
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
        
    def test_search_has_no_email(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", email="toto1@toto.fr", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        entity3 = mommy.make_one(models.Entity, name=u"The big Org", email="toto2@toto.fr")
        contact4 = mommy.make_one(models.Contact, entity=entity3, lastname=u"ABCABC", main_contact=True, has_left=False)
        
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
        
    def _create_opportunities_for_between_date(self):
        entity1 = mommy.make_one(models.Entity, name=u"Barthez")
        entity2 = mommy.make_one(models.Entity, name=u"Amoros")
        entity3 = mommy.make_one(models.Entity, name=u"Lizarazu")
        entity4 = mommy.make_one(models.Entity, name=u"Bossis")
        entity5 = mommy.make_one(models.Entity, name=u"Blanc")
        entity6 = mommy.make_one(models.Entity, name=u"Fernandez")
        entity7 = mommy.make_one(models.Entity, name=u"Cantona")
        entity8 = mommy.make_one(models.Entity, name=u"Tigana")
        entity9 = mommy.make_one(models.Entity, name=u"Papin")
        entity10 = mommy.make_one(models.Entity, name=u"Platini")
        entity11 = mommy.make_one(models.Entity, name=u"Zidane")
        entity12 = mommy.make_one(models.Entity, name=u"Deschamps")
        entity13 = mommy.make_one(models.Entity, name=u"Giresse")
        entity14 = mommy.make_one(models.Entity, name=u"Rocheteau")
        entity15 = mommy.make_one(models.Entity, name=u"Thuram")
        
        opp1 = mommy.make_one(models.Opportunity, entity=entity1,
            start_date=date(2011, 1, 1), end_date=date(2011, 12, 31))
        opp2 = mommy.make_one(models.Opportunity, entity=entity2,
            start_date=date(2011, 4, 10), end_date=date(2011, 4, 15))
        opp3 = mommy.make_one(models.Opportunity, entity=entity3,
            start_date=date(2011, 1, 1), end_date=date(2011, 4, 10))
        opp4 = mommy.make_one(models.Opportunity, entity=entity4,
            start_date=date(2011, 4, 15), end_date=date(2011, 12, 31))
        opp5 = mommy.make_one(models.Opportunity, entity=entity5,
            start_date=date(2011, 1, 1), end_date=date(2011, 2, 1))
        opp6 = mommy.make_one(models.Opportunity, entity=entity6,
            start_date=date(2011, 7, 1), end_date=date(2011, 8, 1))
        opp7 = mommy.make_one(models.Opportunity, entity=entity7,
            start_date=date(2011, 1, 1), ended=False)
        opp8 = mommy.make_one(models.Opportunity, entity=entity8,
            start_date=date(2011, 7, 1))
        opp9 = mommy.make_one(models.Opportunity, entity=entity9)
        opp10 = mommy.make_one(models.Opportunity, entity=entity10,
            end_date=date(2011, 12, 31))
        opp11 = mommy.make_one(models.Opportunity, entity=entity11,
            end_date=date(2011, 4, 15))
        opp12 = mommy.make_one(models.Opportunity, entity=entity12,
            end_date=date(2011, 4, 15), ended=True)
        opp13 = mommy.make_one(models.Opportunity, entity=entity13,
            end_date=date(2011, 4, 15), ended=False)
        opp14 = mommy.make_one(models.Opportunity, entity=entity14,
            start_date=date(2011, 1, 1), ended=True)
        
        class MyVars: pass
        vars = MyVars()
        for k, v in locals().items():
            setattr(vars, k, v)
        return vars

        
    def test_search_opportunity_between(self):
        vars = self._create_opportunities_for_between_date()
        
        url = reverse('search')
        
        data = {"gr0-_-opportunity_between-_-0": "01/04/2011 01/05/2011"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, vars.entity1.name)
        self.assertContains(response, vars.entity2.name)
        self.assertContains(response, vars.entity3.name)
        self.assertContains(response, vars.entity4.name)
        self.assertContains(response, vars.entity7.name)
        self.assertContains(response, vars.entity11.name)
        self.assertContains(response, vars.entity12.name)
        
        self.assertNotContains(response, vars.entity5.name)
        self.assertNotContains(response, vars.entity6.name)
        self.assertNotContains(response, vars.entity8.name)
        self.assertNotContains(response, vars.entity9.name)
        self.assertNotContains(response, vars.entity10.name)
        self.assertNotContains(response, vars.entity14.name)
        self.assertNotContains(response, vars.entity15.name)
        
    def test_search_opportunity_not_between(self):
        vars = self._create_opportunities_for_between_date()
        
        url = reverse('search')
        
        data = {"gr0-_-no_opportunity_between-_-0": "01/04/2011 01/05/2011"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        
        self.assertNotContains(response, vars.entity1.name)
        self.assertNotContains(response, vars.entity2.name)
        self.assertNotContains(response, vars.entity3.name)
        self.assertNotContains(response, vars.entity4.name)
        self.assertNotContains(response, vars.entity7.name)
        self.assertNotContains(response, vars.entity11.name)
        self.assertNotContains(response, vars.entity12.name)
        self.assertNotContains(response, vars.entity9.name)
        self.assertNotContains(response, vars.entity15.name)
        
        self.assertContains(response, vars.entity5.name)
        self.assertContains(response, vars.entity6.name)
        self.assertContains(response, vars.entity8.name)
        self.assertContains(response, vars.entity10.name)
        self.assertContains(response, vars.entity14.name)
        
class MainContactAndHasLeftSearchTest(BaseTestCase):
    
    def _make_contact(self, main_contact, has_left):
        entity = mommy.make_one(models.Entity, name=u"TinyTinyCorp")
        contact = entity.contact_set.all()[0]
        contact.lastname = 'TiniMax'
        contact.firstname = 'Boss'
        contact.main_contact = main_contact
        contact.has_left = has_left
        contact.save()
        return entity, contact
    
    def _make_another_contact(self, entity, main_contact, has_left):
        contact = mommy.make_one(models.Contact, entity=entity)
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
        entity = mommy.make_one(models.Entity)
        contact = entity.contact_set.all()[0]
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
        group = mommy.make_one(models.Group)
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
        
    def test_mailto_several_emails_more_than_limit(self):
        group = mommy.make_one(models.Group)
        contacts = []
        for i in xrange(51):
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
            
    def test_get_mailto(self):
        url = reverse('search_mailto_contacts', args=[0])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        

class AddToGroupActionTest(BaseTestCase):
    
    def test_add_contact_to_group(self):
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make_one(models.Group, name="GROUP1")
        group.entities.add(entity1)
        group.entities.add(entity2)
        group.save()
        
        group2 = mommy.make_one(models.Group, name="GROUP2")
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
        entity1 = mommy.make_one(models.Entity, name=u"My tiny corp")
        contact1 = mommy.make_one(models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make_one(models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False)
        
        entity2 = mommy.make_one(models.Entity, name=u"Other corp")
        contact2 = mommy.make_one(models.Contact, entity=entity2, lastname=u"WXYZ", main_contact=True, has_left=False)
        
        group = mommy.make_one(models.Group, name="GROUP1")
        group.entities.add(entity1)
        group.entities.add(entity2)
        group.save()
        
        group2 = mommy.make_one(models.Group, name="GROUP2")
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
        