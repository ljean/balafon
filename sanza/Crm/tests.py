# -*- coding: utf-8 -*-

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()
    
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
import json
from model_mommy import mommy
from sanza.Crm import models
from django.conf import settings
from bs4 import BeautifulSoup as BS4
from django.core import management
from cStringIO import StringIO
import sys
from datetime import datetime, timedelta
import logging
from coop_cms.settings import is_perm_middleware_installed

class BaseTestCase(TestCase):
    
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto", is_staff=True)
        self.user.set_password("abc")
        self.user.save()
        self._login()
        
    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _login(self):
        self.client.login(username="toto", password="abc")

class ViewEntityTest(BaseTestCase):

    def test_view_entity(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        self.assertContains(response, reverse("crm_view_contact", args=[contact.id]))
        
    def test_view_entity_secondary_contact(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact1 = mommy.make(models.Contact, main_contact=True, entity=entity)
        contact2 = mommy.make(models.Contact, main_contact=False, entity=entity)
        
        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        url1 = reverse("crm_view_contact", args=[contact1.id])
        url2 = reverse("crm_view_contact", args=[contact2.id])
        self.assertContains(response, url1)
        self.assertContains(response, url2)
        tag1 = BS4(response.content).select('.ut-contact-{0.id} .ut-secondary-contact'.format(contact1))
        self.assertEqual(len(tag1), 0)
        tag2 = BS4(response.content).select('.ut-contact-{0.id} .ut-secondary-contact'.format(contact2))
        self.assertEqual(len(tag2), 1)
        
    def test_view_entity_has_left_contact(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact1 = mommy.make(models.Contact, has_left=False, entity=entity)
        contact2 = mommy.make(models.Contact, has_left=True, entity=entity)
        
        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        url1 = reverse("crm_view_contact", args=[contact.id])
        url2 = reverse("crm_view_contact", args=[contact2.id])
        self.assertContains(response, url1)
        self.assertContains(response, url2)
        tag1 = BS4(response.content).select('.ut-contact-{0.id} .ut-has-left'.format(contact1))
        self.assertEqual(len(tag1), 0)
        tag2 = BS4(response.content).select('.ut-contact-{0.id} .ut-has-left'.format(contact2))
        self.assertEqual(len(tag2), 1)
        
class CreateEntityTest(BaseTestCase):

    def test_view_create_entity_no_type(self):
        url = reverse('crm_create_entity', args=[0])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
    
    def test_view_create_entity_with_type(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[t.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        
    def test_create_entity_no_type(self):
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response,
            reverse("crm_view_entity", args=[e.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.type, None)
    
    def test_create_entity_with_type(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[t.id])
        response = self.client.post(url, data={'name': "ABC", "type": t.id})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response,
            reverse("crm_view_entity", args=[e.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.type, t)
        
    def test_create_entity_with_type_after(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "type": t.id})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response,
            reverse("crm_view_entity", args=[e.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.type, t)
        
    def test_create_entity_url(self):
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "website": "http://toto.fr/"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response,
            reverse("crm_view_entity", args=[e.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.website, "http://toto.fr/")
        
    def test_create_entity_url_no_scheme(self):
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "website": "toto.fr/"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response,
            reverse("crm_view_entity", args=[e.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.website, "http://toto.fr/")
        
    def test_view_create_entity_unknown_type(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[2222])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        
        response = self.client.post(url, data={'name': "ABC", "type": 2222})
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        
        url = reverse('crm_create_entity', args=[t.id])
        response = self.client.post(url, data={'name': "ABC", "type": "2222"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        
    def test_view_create_entity_invalid_type(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[2222]).replace("2222", "aaa")
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        
        response = self.client.post(url, data={'name': "ABC", "type": 2222})
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
        
        url = reverse('crm_create_entity', args=[t.id])
        response = self.client.post(url, data={'name': "ABC", "type": "aaaaa"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)
    

class OpportunityTest(BaseTestCase):

    def test_view_delete_opportunity(self):
        opportunity = mommy.make(models.Opportunity)
        
        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, models.Opportunity.objects.count())
    
    def test_delete_empty_opportunity(self):
        opportunity = mommy.make(models.Opportunity)
        
        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.post(url, {'confirm': True})
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(0, models.Opportunity.objects.count())
    
    def test_delete_opportunity_actions(self):
        opportunity = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity)
        
        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.post(url, {'confirm': True})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, models.Opportunity.objects.count())
        self.assertEqual(1, models.Action.objects.count())
        self.assertEqual(action, models.Action.objects.all()[0])
    
    
    def test_delete_opportunity_cancel(self):
        opportunity = mommy.make(models.Opportunity)
        
        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.post(url, {'confirm': False})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, models.Opportunity.objects.count())
        

    def test_view_add_action_to_opportunity(self):
        action = mommy.make(models.Action)
        opportunity = mommy.make(models.Opportunity)
        
        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(action.opportunity, None)
    
    def test_view_add_action_to_opportunity_no_opp(self):
        action = mommy.make(models.Action)
        
        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(action.opportunity, None)
    
    def test_add_action_to_opportunity(self):
        action = mommy.make(models.Action)
        opportunity = mommy.make(models.Opportunity)
        
        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.post(url, data={'opportunity': opportunity.id})
        self.assertEqual(200, response.status_code)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity)
        
    def test_add_action_to_opportunity_existing(self):
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)

        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.post(url, data={'opportunity': opportunity2.id})
        self.assertEqual(200, response.status_code)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity2)
    
    def test_add_action_to_opportunity_invalid(self):
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)
        
        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.post(url, data={'opportunity': "AAAA"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(BS4(response.content).select(".field-error")), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity1)
        
    def test_remove_action_from_opportunity(self):
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)
        
        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity1.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, None)
        
    def test_remove_action_from_opportunity_badone(self):
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)
        
        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity2.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity1)
        
    def test_remove_action_from_opportunity_no_confirm(self):
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)
        
        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity1.id])
        response = self.client.post(url, data={'confirm': 0})
        self.assertEqual(200, response.status_code)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity1)
    
    def test_remove_action_from_opportunity_no_opp(self):
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=None)
        
        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity2.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, None)
        
    def test_view_add_opportunity(self):
        url = reverse("crm_add_opportunity")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_add_opportunity(self):
        url = reverse("crm_add_opportunity")
        data = {
            'name': "ABC",
            "detail": "ooo",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(BS4(response.content).select('.field-error'), [])
        
        self.assertEqual(1, models.Opportunity.objects.count())
        o = models.Opportunity.objects.all()[0]
        for k, v in data.items():
            self.assertEqual(getattr(o, k), v)
            
    def test_add_opportunity2(self):
        url = reverse("crm_add_opportunity")
        data = {
            'name': "DEF",
            "detail": "",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(BS4(response.content).select('.field-error'), [])
        
        self.assertEqual(1, models.Opportunity.objects.count())
        o = models.Opportunity.objects.all()[0]
        for k, v in data.items():
            self.assertEqual(getattr(o, k), v)
            
    def test_add_opportunityno_name(self):
        url = reverse("crm_add_opportunity")
        data = {
            'name': "",
            "detail": "",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(BS4(response.content).select('.field-error')), 1)
        
        self.assertEqual(0, models.Opportunity.objects.count())

    def test_edit_opportunity(self):
        o = mommy.make(models.Opportunity)
        url = reverse("crm_edit_opportunity", args=[o.id])
        data = {
            'name': "ABC",
            "detail": "ooo",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(BS4(response.content).select('.field-error'), [])
        
        self.assertEqual(1, models.Opportunity.objects.count())
        o = models.Opportunity.objects.all()[0]
        for k, v in data.items():
            self.assertEqual(getattr(o, k), v)

    def test_view_opportunity(self):
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity, name="OPP1", entity=entity1)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)
        
    def test_view_opportunity_actions(self):
        entity1 = mommy.make(models.Entity, name='ent1', relationship_date='2012-01-30')
        entity2 = mommy.make(models.Entity, name='ent2', relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity, name='OPP1', entity=entity1)
        act1 = mommy.make(models.Action, subject='ABC', opportunity=opp1)
        act1.entities.add(entity1)
        act1.save()
        act2 = mommy.make(models.Action, subject='DEF', opportunity=opp1)
        act2.entities.add(entity2)
        act2.save()
        act3 = mommy.make(models.Action, subject='GHI')
        act3.entities.add(entity1)
        act3.save()
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)
        self.assertContains(response, act1.subject)
        self.assertContains(response, act2.subject)
        self.assertNotContains(response, act3.subject)
        
    #def test_mailto_opportunity_contacts(self):
    #    entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
    #    entity2 = mommy.make(models.Entity, relationship_date='2012-01-30')
    #    opp1 = mommy.make(models.Opportunity, entity=entity1)
    #    contact1 = mommy.make(models.Contact, lastname='ABC', entity=entity1, email="c1@sanza.fr")
    #    contact2 = mommy.make(models.Contact, lastname='DEF', entity=entity2, email="c2@sanza.fr")
    #    contact3 = mommy.make(models.Contact, lastname='GHI', entity=entity1, email="c3@sanza.fr")
    #    contact4 = mommy.make(models.Contact, lastname='JKL', entity=entity1)
    #    act1 = mommy.make(models.Action, opportunity=opp1)
    #    act1.contacts.add(contact1)
    #    act1.contacts.add(contact4)
    #    act1.save()
    #    act2 = mommy.make(models.Action, opportunity=opp1)
    #    act2.entities.add(entity2)
    #    act2.save()
    #    act3 = mommy.make(models.Action)
    #    act3.contacts.add(contact3)
    #    act3.save()
    #    
    #    response = self.client.get(reverse('crm_mailto_opportunity_contacts', args=[opp1.id]))
    #    self.assertEqual(302, response.status_code)
    #    content = response['Location']
    #    self.assertTrue(content.find(contact1.email)>=0)
    #    self.assertTrue(content.find(contact2.email)>=0)
    #    self.assertFalse(content.find(contact3.email)>=0)
    
    def test_view_opportunity_contacts(self):
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        entity2 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity, entity=entity1)
        contact1 = mommy.make(models.Contact, lastname='ABC', entity=entity1)
        contact2 = mommy.make(models.Contact, lastname='DEF', entity=entity2)
        contact3 = mommy.make(models.Contact, lastname='GHI', entity=entity1)
        act1 = mommy.make(models.Action, opportunity=opp1)
        act1.contacts.add(contact1)
        act1.save()
        act2 = mommy.make(models.Action, opportunity=opp1)
        act2.entities.add(entity2)
        act2.save()
        act3 = mommy.make(models.Action)
        act3.contacts.add(contact3)
        act3.save()
        
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        
    def test_view_opportunity_entity_contacts_has_left(self):
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity)
        
        contact1 = mommy.make(models.Contact, lastname='ABC', entity=entity1)
        contact2 = mommy.make(models.Contact, lastname='DEF', entity=entity1, has_left=True)
        
        act1 = mommy.make(models.Action, opportunity=opp1)
        act1.entities.add(entity1)
        act1.save()
        
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        
    def test_view_opportunity_contact_has_left(self):
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity)
        
        contact1 = mommy.make(models.Contact, lastname='ABC', entity=entity1)
        contact2 = mommy.make(models.Contact, lastname='DEF', entity=entity1, has_left=True)
        
        act1 = mommy.make(models.Action, opportunity=opp1)
        act1.contacts.add(contact1)
        act1.contacts.add(contact2)
        act1.save()
        
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        soup = BS4(response.content)
        
        self.assertEqual(len(soup.select("td.ut-contact-{0} .ut-has-left".format(contact1.id))), 0)
        self.assertEqual(len(soup.select("td.ut-contact-{0} .ut-has-left".format(contact2.id))), 1)
        
        
    def test_view_opportunityies_date_mixes(self):
        opp1 = mommy.make(models.Opportunity)
        opp2 = mommy.make(models.Opportunity)
        
        contact1 = mommy.make(models.Contact, lastname='ABC')
        act1 = mommy.make(models.Action, opportunity=opp1, planned_date='2013-11-29')
        act1.contacts.add(contact1)
        act1.save()
        
        response = self.client.get(reverse('crm_all_opportunities'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)
        self.assertContains(response, opp2.name)
        
    def test_view_opportunityies_date_mixes_none(self):
        opp1 = mommy.make(models.Opportunity)
        opp2 = mommy.make(models.Opportunity)
        
        contact1 = mommy.make(models.Contact, lastname='ABC')
        act1 = mommy.make(models.Action, opportunity=opp1)
        act1.contacts.add(contact1)
        act1.save()
        
        response = self.client.get(reverse('crm_all_opportunities'))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)
        self.assertContains(response, opp2.name)
        
        
class SameAsTest(BaseTestCase):

    def test_add_same_as(self):
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as.main_contact, contact1)
        self.assertEqual(contact2.same_as.main_contact, contact1)
        
    def test_add_same_as_list(self):
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, entity=entity2, firstname="Ringo", lastname="Star")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, entity1)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, entity2)
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact3.id})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, None)
        
    def test_suggestion_list(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(1, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertTrue(contact2.id in ids)
        self.assertFalse(contact3.id in ids)
        
    def test_suggestion_list_two_choices(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(2, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertTrue(contact2.id in ids)
        self.assertFalse(contact3.id in ids)
        self.assertTrue(contact4.id in ids)
        
    def test_suggestion_list_two_choices_existing_same_as(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2]:
            c.same_as = same_as
            c.save()
            
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(1, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertFalse(contact2.id in ids)
        self.assertFalse(contact3.id in ids)
        self.assertTrue(contact4.id in ids)
        
    def test_suggestion_list_two_choices_existing_same_as_with_all(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2, contact4]:
            c.same_as = same_as
            c.save()
            
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        self.assertEqual(0, len(soup.select('select')))
        
    def test_suggestion_list_nohomonymous(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
            
        url = reverse("crm_same_as", args=[contact3.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        self.assertEqual(0, len(soup.select('select')))
        
    def test_make_main_view(self):
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)
        
        url = reverse("crm_make_main_contact", args=[contact1.id, contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as.main_contact, contact1)
    
    def test_make_main_post(self):
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)
        
        url = reverse("crm_make_main_contact", args=[contact1.id, contact1.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as.main_contact, contact1)
        
    def test_remove_same_as_two_clones(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2]:
            c.same_as = same_as
            c.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        
    def test_remove_same_as_two_clones_prio1(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        
        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2]:
            c.same_as = same_as
            c.save()
            
        same_as.main_contact = contact1
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        
        
    def test_remove_same_as_two_clones_prio2(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2]:
            c.same_as = same_as
            c.save()
            
        same_as.main_contact = contact2
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        
    def test_remove_same_as_three_clones(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2, contact3]:
            c.same_as = same_as
            c.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(same_as.main_contact, None)
        
    def test_remove_same_as_three_clones_prio1(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2, contact3]:
            c.same_as = same_as
            c.save()
        same_as.main_contact = contact1
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(same_as.main_contact, contact1)
        
    def test_remove_same_as_three_clones_prio2(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2, contact3]:
            c.same_as = same_as
            c.save()
        same_as.main_contact = contact2
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(same_as.main_contact, contact1)
        
    def test_remove_same_as_not_same(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(404, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        
    def test_remove_same_as_not_in_same_as(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2]:
            c.same_as = same_as
            c.save()
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact3.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(404, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact3.same_as, None)
        
    def test_remove_same_as_not_in_same_as_2(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2]:
            c.same_as = same_as
            c.save()
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact3.id, contact1.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(404, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact3.same_as, None)
        
    def test_remove_same_as_three_clones_prio3(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2, contact3]:
            c.same_as = same_as
            c.save()
        same_as.main_contact = contact3
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(same_as.main_contact, contact3)
        
    def test_remove_same_as_cancel(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for c in [contact1, contact2, contact3]:
            c.same_as = same_as
            c.save()
        same_as.main_contact = contact3
        same_as.save()
        
        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])
        
        response = self.client.post(url, data={})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(same_as.main_contact, contact3)
    
        
class OpportunityAutoCompleteTest(BaseTestCase):
    def test_get_add_action(self):
        response = self.client.get(reverse('crm_add_action'))
        self.assertEqual(200, response.status_code)
        
    def test_get_opportunity_name(self):
        opp = mommy.make(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_name', args=[opp.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp.name)
        
    def test_get_opportunity_name_unknown(self):
        opp = mommy.make(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_name', args=[55]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '55')
        
        url = reverse('crm_get_opportunity_name', args=['toto'])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'toto')
           
    def test_get_opportunity_id(self):
        opp = mommy.make(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_id')+"?name="+opp.name)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp.id)
        
    def test_get_opportunity_unknown(self):
        response = self.client.get(reverse('crm_get_opportunity_id')+"?name=toto")
        self.assertEqual(404, response.status_code)
        
    def test_get_opportunity_list(self):
        opp1 = mommy.make(models.Opportunity, name="defz")
        opp2 = mommy.make(models.Opportunity, name="Uvwz")
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=d')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)
        self.assertNotContains(response, opp2.name)
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=U')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp2.name)
        self.assertNotContains(response, opp1.name)
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=k')
        self.assertNotContains(response, opp1.name)
        self.assertNotContains(response, opp2.name)
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=z')
        self.assertContains(response, opp1.name)
        self.assertContains(response, opp2.name)

class EditActionTest(BaseTestCase):
    def test_edit_action(self):
        contact = mommy.make(models.Contact)
        action = mommy.make(models.Action)
        action.contacts.add(contact)
        action.save()
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        data = {'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status':"", 'in_charge': "", 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False}
        
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "tested")
        
    def test_allowed_status(self, ):
        at = mommy.make(models.ActionType)
        as1 = mommy.make(models.ActionStatus)
        as2 = mommy.make(models.ActionStatus)
        as3 = mommy.make(models.ActionStatus)
        at.allowed_status.add(as1)
        at.allowed_status.add(as2)
        at.save()
        
        url = reverse("crm_get_action_status")+"?t="+str(at.id)+"&timestamp=777"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([as1.id, as2.id], data['allowed_status'])
        self.assertEqual(0, data['default_status'])
        
    def test_allowed_status_default_value(self, ):
        at = mommy.make(models.ActionType)
        as1 = mommy.make(models.ActionStatus)
        as2 = mommy.make(models.ActionStatus)
        as3 = mommy.make(models.ActionStatus)
        at.allowed_status.add(as1)
        at.allowed_status.add(as2)
        at.default_status = as2
        at.save()
        
        url = reverse("crm_get_action_status")+"?t="+str(at.id)+"&timestamp=777"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([as1.id, as2.id], data['allowed_status'])
        self.assertEqual(as2.id, data['default_status'])
        
    def test_no_allowed_status(self, ):
        at = mommy.make(models.ActionType)
        
        url = reverse("crm_get_action_status")+"?t="+str(at.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([], data['allowed_status'])
        self.assertEqual(0, data['default_status'])
        
    def test_allowed_status_no_type(self, ):
        url = reverse("crm_get_action_status")+"?t="+str(0)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([], data['allowed_status'])
        self.assertEqual(0, data['default_status'])
        
    def test_allowed_status_unknown_type(self, ):
        url = reverse("crm_get_action_status")+"?t=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_allowed_status_unknown_type(self, ):
        url = reverse("crm_get_action_status")+"?t=toto"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_edit_action_on_entity(self):
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action)
        action.entities.add(entity)
        action.save()
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        data = {'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status':"", 'in_charge': "", 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False}
        
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "tested")
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)
        
        
    def test_edit_action_status_not_allowed(self):
        at = mommy.make(models.ActionType)
        as1 = mommy.make(models.ActionStatus)
        as2 = mommy.make(models.ActionStatus)
        as3 = mommy.make(models.ActionStatus)
        at.allowed_status.add(as1)
        at.allowed_status.add(as2)
        at.save()
        
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="not tested", type=at, status=as1)
        action.entities.add(entity)
        action.save()
    
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        data = {'subject': "tested", 'type': at.id, 'date': "", 'time': "",
            'status': as3.id, 'in_charge': "", 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False}
        
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "not tested")
        
    def test_edit_action_status_no_type(self):
        at = mommy.make(models.ActionType)
        as1 = mommy.make(models.ActionStatus)
        as2 = mommy.make(models.ActionStatus)
        as3 = mommy.make(models.ActionStatus)
        at.allowed_status.add(as1)
        at.allowed_status.add(as2)
        at.save()
        
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="not tested", type=at, status=as1)
        action.entities.add(entity)
        action.save()
    
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        data = {'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status': as3.id, 'in_charge': "", 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False}
        
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "not tested")
        
    def test_edit_action_planned_date(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_planned_date_time(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "12:25", 'planned_date': "", 'end_date': "", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 12, 25))
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_planned_time(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "", 'time': "12:25", 'planned_date': "", 'end_date': "", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        errors = BS4(response.content).select('#id_time .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_start_and_end_date(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-10", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 10, 0, 0))
        
    def test_edit_action_start_and_end_same_date(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 9, 0, 0))
        
    def test_edit_action_start_and_end_same_date_different_time(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "14:00", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "16:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 14, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 9, 16, 0))
        
    def test_edit_action_start_and_end_same_date_different_time2(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "16:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 9, 16, 0))
        
    def test_edit_action_start_and_end_same_date_different_time3(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "16:30", 'planned_date': "", 'end_date': "2014-04-10", 'end_time': "10:15", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")
        
        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 16, 30))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 10, 10, 15))
        
    def test_edit_action_start_not_set_and_end_date(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "", 'time': "", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        errors = BS4(response.content).select('#id_end_date .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_start_and_end_before(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-08", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        errors = BS4(response.content).select('#id_end_date .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
    
    def test_edit_action_start_and_end_before_time(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        errors = BS4(response.content).select('#id_end_time .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_start_and_end_before_time2(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "11:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        errors = BS4(response.content).select('#id_end_time .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_start_and_end_not_set_time(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "", 'end_time': "12:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        errors = BS4(response.content).select('#id_end_time .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_start_and_end_not_invalid1(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "AAAA", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "13:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('#id_date .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
    
    def test_edit_action_start_and_end_not_invalid2(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "AA", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "13:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('#id_time .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
    
    def test_edit_action_start_and_end_not_invalid3(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "AAA", 'end_time': "13:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('#id_end_date .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        
    def test_edit_action_start_and_end_not_invalid4(self):
        action = mommy.make(models.Action, subject="AAA")
    
        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "AA", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False, 'planned_date': ""}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('#id_end_time .field-error')
        self.assertEqual(len(errors), 1)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")
        
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
    
    def test_view_action_start_and_end_datetime(self):
        action = mommy.make(models.Action, subject="AAA",
            planned_date=datetime(2014, 4, 9, 12, 15), end_datetime=datetime(2014, 4, 10, 9, 30))
    
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BS4(response.content)
        
        self.assertEqual(soup.select("#id_date")[0]["value"], "2014-04-09")
        self.assertEqual(soup.select("#id_time")[0]["value"], "12:15:00")
        
        self.assertEqual(soup.select("#id_end_date")[0]["value"], "2014-04-10")
        self.assertEqual(soup.select("#id_end_time")[0]["value"], "09:30:00")

class BoardPanelTest(BaseTestCase):
    def test_view_board_panel(self):
        response = self.client.get(reverse("crm_board_panel"))
        
        self.assertRedirects(response, reverse('users_favorites_list'))
        #self.assertEqual(302, response.status_code)
        #self.assertEqual(response['Location'], "http://testserver{0}".format(reverse('users_favorites_list')))
        
class ActionTest(BaseTestCase):
    def test_view_add_contact_to_action(self):
        action = mommy.make(models.Action)
        url = reverse('crm_add_contact_to_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_view_add_entity_to_action(self):
        action = mommy.make(models.Action)
        url = reverse('crm_add_entity_to_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_add_contact_to_action(self):
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        url = reverse('crm_add_contact_to_action', args=[action.id])
        response = self.client.post(url, data={'contact': contact.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(action.contacts.all()[0], contact)
        
    def test_add_entity_to_action(self):
        action = mommy.make(models.Action)
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_entity_to_action', args=[action.id])
        response = self.client.post(url, data={'entity': entity.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)
        
    def test_view_entity_actions(self):
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="should be only once", archived=False)
        c1 = entity.default_contact
        c2 = mommy.make(models.Contact, entity=entity)
        action.contacts.add(c1)
        action.contacts.add(c2)
        action.entities.add(entity)
        action.save()
        
        url = reverse("crm_view_entity", args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.content.count(action.subject))
        
    def test_view_contact_actions_more_than_five(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        
        actions = [mommy.make(models.Action, subject=u"--{0}--".format(i), archived=False) for i in range(10)]
        for a in actions:
            a.contacts.add(c1)
            a.save()
        
        url = reverse("crm_view_contact", args=[c1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        for a in actions[5:]:
            self.assertContains(response, a.subject)
        
        for a in actions[:5]:
            self.assertNotContains(response, a.subject)
            
    def test_view_contact_actions_more_than_five_datetime(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        
        def _get_dt(x=0):
            n = datetime.now()
            if x > 0:
                return n + timedelta(days=x)
            elif x < 0:
                return n - timedelta(days=-x)
            return n
        
        a1 = mommy.make(models.Action, subject=u"--1--", archived=False, planned_date=_get_dt())
        a2 = mommy.make(models.Action, subject=u"--2--", archived=False, planned_date=_get_dt(-1))
        a3 = mommy.make(models.Action, subject=u"--3--", archived=False, planned_date=_get_dt(-2))
        a4 = mommy.make(models.Action, subject=u"--4--", archived=False, planned_date=_get_dt(-3))
        a5 = mommy.make(models.Action, subject=u"--5--", archived=False, planned_date=_get_dt(+1))
        a6 = mommy.make(models.Action, subject=u"--6--", archived=False, planned_date=_get_dt(+2))
        a7 = mommy.make(models.Action, subject=u"--7--", archived=False, planned_date=_get_dt(+3))
        
        for a in [a1, a2, a3, a4, a5, a6, a7]:
            a.contacts.add(c1)
            a.save()
        
        url = reverse("crm_view_contact", args=[c1.id])
        response = self.client.get(url)
        #print BS4(response.content).select(".action-subject")
        self.assertEqual(200, response.status_code)
        
        for a in [a1, a2, a5, a6, a7]:
            self.assertContains(response, a.subject)
        
        for a in [a3, a4]:
            self.assertNotContains(response, a.subject)

    def test_view_entity_actions_more_than_five_datetime(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        
        def _get_dt(x=0):
            n = datetime.now()
            if x > 0:
                return n + timedelta(days=x)
            elif x < 0:
                return n - timedelta(days=-x)
            return n
        
        a1 = mommy.make(models.Action, subject=u"--1--", archived=False, planned_date=_get_dt())
        a2 = mommy.make(models.Action, subject=u"--2--", archived=False, planned_date=_get_dt(-1))
        a3 = mommy.make(models.Action, subject=u"--3--", archived=False, planned_date=_get_dt(-2))
        a4 = mommy.make(models.Action, subject=u"--4--", archived=False, planned_date=_get_dt(-3))
        a5 = mommy.make(models.Action, subject=u"--5--", archived=False, planned_date=_get_dt(+1))
        a6 = mommy.make(models.Action, subject=u"--6--", archived=False, planned_date=_get_dt(+2))
        a7 = mommy.make(models.Action, subject=u"--7--", archived=False, planned_date=_get_dt(+3))
        
        for a in [a1, a2, a3, a4, a5, a6, a7]:
            a.contacts.add(c1)
            a.save()
        
        url = reverse("crm_view_entity", args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        for a in [a1, a2, a5, a6, a7]:
            self.assertContains(response, a.subject)
        
        for a in [a3, a4]:
            self.assertNotContains(response, a.subject)

    def test_view_contact_all_actions_by_set(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        
        at1 = mommy.make(models.ActionType)
        s1 = mommy.make(models.ActionSet)
        at2 = mommy.make(models.ActionType, set=s1)
        at3 = mommy.make(models.ActionType, set=s1)
        s2 = mommy.make(models.ActionSet)
        at4 = mommy.make(models.ActionType, set=s2)
        
        counter = 0
        visible_actions = []
        hidden_actions = []
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at1, archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
            
        for i in range(10):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at3, archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(10):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at2, archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(3):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at4, archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        url = reverse("crm_view_contact_actions", args=[c1.id, s1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        for a in visible_actions:
            self.assertContains(response, a.subject)
        
        for a in hidden_actions:
            self.assertNotContains(response, a.subject)
            
    def test_view_entity_all_actions_by_set(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        
        at1 = mommy.make(models.ActionType)
        s1 = mommy.make(models.ActionSet)
        at2 = mommy.make(models.ActionType, set=s1)
        at3 = mommy.make(models.ActionType, set=s1)
        s2 = mommy.make(models.ActionSet)
        at4 = mommy.make(models.ActionType, set=s2)
        
        counter = 0
        visible_actions = []
        hidden_actions = []
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            if i%2:
                a.contacts.add(c1)
            else:
                a.entities.add(entity)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at1, archived=False)
            if i%2:
                a.contacts.add(c1)
            else:
                a.entities.add(entity)
            a.save()
            hidden_actions.append(a)
            counter += 1
            
        for i in range(10):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at3, archived=False)
            if i%2:
                a.contacts.add(c1)
            else:
                a.entities.add(entity)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(10):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at2, archived=False)
            if i%2:
                a.contacts.add(c1)
            else:
                a.entities.add(entity)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(3):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at4, archived=False)
            if i%2:
                a.contacts.add(c1)
            else:
                a.entities.add(entity)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        url = reverse("crm_view_entity_actions", args=[entity.id, s1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        for a in visible_actions:
            self.assertContains(response, a.subject)
        
        for a in hidden_actions:
            self.assertNotContains(response, a.subject)
            
    def test_view_contact_actions_more_than_five_by_set(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        
        at1 = mommy.make(models.ActionType)
        s1 = mommy.make(models.ActionSet)
        at2 = mommy.make(models.ActionType, set=s1)
        at3 = mommy.make(models.ActionType, set=s1)
        s2 = mommy.make(models.ActionSet)
        at4 = mommy.make(models.ActionType, set=s2)
        
        counter = 0
        visible_actions = []
        hidden_actions = []
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at1, archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
            
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(3):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at1, archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at3, archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at2, archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        for i in range(2):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at2, archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(3):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at3, archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        for i in range(3):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at4, archived=False)
            a.contacts.add(c1)
            a.save()
            hidden_actions.append(a)
            counter += 1
        
        for i in range(5):
            a = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=at4, archived=False)
            a.contacts.add(c1)
            a.save()
            visible_actions.append(a)
            counter += 1
        
        
        url = reverse("crm_view_contact", args=[c1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        for a in visible_actions:
            self.assertContains(response, a.subject)
        
        for a in hidden_actions:
            self.assertNotContains(response, a.subject)


        
    def test_view_contact_actions(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        c2 = mommy.make(models.Contact, entity=entity)
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(c1)
        action1.contacts.add(c2)
        action1.entities.add(entity)
        action1.save()
        
        action2 = mommy.make(models.Action, subject="another action to do", archived=False)
        action2.contacts.add(c1)
        action2.save()
        
        action3 = mommy.make(models.Action, subject="i believe i can fly", archived=False)
        action3.entities.add(entity)
        action3.save()
        
        action4 = mommy.make(models.Action, subject="hard days night", archived=False)
        action4.contacts.add(c2)
        action4.save()
        
        url = reverse("crm_view_contact", args=[c1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.content.count(action1.subject))
        self.assertEqual(1, response.content.count(action2.subject))
        self.assertEqual(0, response.content.count(action3.subject))
        self.assertEqual(0, response.content.count(action4.subject))
        
    def test_view_remove_contact_from_action(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        c2 = mommy.make(models.Contact, entity=entity)
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(c1)
        action1.contacts.add(c2)
        action1.entities.add(entity)
        action1.save()
        
        url = reverse('crm_remove_contact_from_action', args=[action1.id, c1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 2)
        self.assertEqual(action1.entities.count(), 1)
        
    def test_remove_contact_from_action(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        c2 = mommy.make(models.Contact, entity=entity)
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(c1)
        action1.contacts.add(c2)
        action1.entities.add(entity)
        action1.save()
        
        url = reverse('crm_remove_contact_from_action', args=[action1.id, c1.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 1)
        self.assertEqual(action1.contacts.all()[0], c2)
        self.assertEqual(action1.entities.count(), 1)
        self.assertEqual(action1.entities.all()[0], entity)
    
    def test_view_remove_entity_from_action(self):
        entity = mommy.make(models.Entity)
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(c1)
        action1.contacts.add(c2)
        action1.entities.add(entity)
        action1.save()
        
        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response.content, entity.name)
        self.assertNotContains(response.content, entity.default_contact.lastname)
        
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 0)
        self.assertEqual(action1.entities.count(), 1)
        
    def test_remove_entity_from_action(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        c2 = mommy.make(models.Contact, entity=entity)
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(c1)
        action1.contacts.add(c2)
        action1.entities.add(entity)
        action1.save()
        
        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 2)
        self.assertEqual(action1.entities.count(), 0)
        
    def test_remove_entity_from_action2(self):
        entity1 = mommy.make(models.Entity, name="Corp1")
        c2 = mommy.make(models.Contact, entity=entity1)
        entity2 = mommy.make(models.Entity, name="Corp2")
        entity3 = mommy.make(models.Entity, name="Corp3")
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.entities.add(entity1)
        action1.entities.add(entity2)
        action1.entities.add(entity3)
        action1.save()
        
        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity2.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 0)
        self.assertEqual(action1.entities.count(), 2)
        sort_key = lambda x: x.id
        self.assertEqual(
            sorted(list(action1.entities.all()), key=sort_key),
            sorted([entity1, entity3], key=sort_key)
        )
        
        
    def test_view_remove_entity_from_action(self):
        entity = mommy.make(models.Entity)
        c1 = entity.default_contact
        c2 = mommy.make(models.Contact, entity=entity)
        
        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(c1)
        action1.contacts.add(c2)
        action1.entities.add(entity)
        action1.save()
        
        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(action1.contacts.count(), 2)
        self.assertEqual(action1.entities.count(), 1)
        
    def test_add_entity_to_action(self):
        action = mommy.make(models.Action)
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_entity_to_action', args=[action.id])
        response = self.client.post(url, data={'entity': entity.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)
        
    def test_view_add_action_from_board(self):
        url = reverse('crm_create_action', args=[0, 0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)
        
    def test_view_add_action_from_opportunity(self):
        opportunity = mommy.make(models.Opportunity)
        url = reverse('crm_create_action', args=[0, 0])+"?opportunity={0}".format(opportunity.id)
        response = self.client.get(url)
        self.assertEqual(BS4(response.content).select('#id_opportunity')[0]["value"], str(opportunity.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)
    
    def test_add_action_from_opportunity(self):
        opportunity = mommy.make(models.Opportunity)
        url = reverse('crm_create_action', args=[0, 0])+"?opportunity={0}".format(opportunity.id)
        data = {'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status': "", 'in_charge': "", 'detail':"ABCDEF", 'opportunity': opportunity.id,
            'amount': 0, 'number': 0}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data["subject"])
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(action.opportunity, opportunity)
        
    def test_add_action_from_board(self):
        url = reverse('crm_create_action', args=[0, 0])
        at = mommy.make(models.ActionType)
        ast = mommy.make(models.ActionStatus)
        at.allowed_status.add(ast)
        at.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        
        data = {'subject': "tested", 'type': at.id, 'date': "2014-01-31", 'time': "11:34",
            'status': ast.id, 'in_charge': user.id, 'detail':"ABCDEF",
            'amount': 200, 'number': 5}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        for x in data:
            if x in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, x).id, data[x])
            elif x in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, x), data[x])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)
        
        
    def test_view_add_action_from_contact(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_create_action', args=[0, contact.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)
    
    def test_add_action_from_contact(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_create_action', args=[0, contact.id])
        
        at = mommy.make(models.ActionType)
        ast = mommy.make(models.ActionStatus)
        at.allowed_status.add(ast)
        at.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        
        data = {'subject': "tested", 'type': at.id, 'date': "2014-01-31", 'time': "11:34",
            'status': ast.id, 'in_charge': user.id, 'detail':"ABCDEF",
            'amount': 200, 'number': 5}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        for x in data:
            if x in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, x).id, data[x])
            elif x in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, x), data[x])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.contacts.all()[0], contact)
        
        self.assertEqual(action.entities.count(), 0)
        
    def test_view_add_action_from_entity(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_create_action', args=[entity.id, 0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)
        
    def test_add_action_from_entity(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_create_action', args=[entity.id, 0])
        
        at = mommy.make(models.ActionType)
        ast = mommy.make(models.ActionStatus)
        at.allowed_status.add(ast)
        at.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        
        data = {'subject': "tested", 'type': at.id, 'date': "2014-01-31", 'time': "11:34",
            'status': ast.id, 'in_charge': user.id, 'detail':"ABCDEF",
            'amount': 200, 'number': 5}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        for x in data:
            if x in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, x).id, data[x])
            elif x in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, x), data[x])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)
    
    def test_view_edit_action(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        pld = datetime(2014, 1, 31, 11, 34, 00)
        action = mommy.make(models.Action, display_on_board=True, done=True, planned_date=pld)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()
        
        at = mommy.make(models.ActionType)
        ast = mommy.make(models.ActionStatus)
        at.allowed_status.add(ast)
        at.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BS4(response.content)
        self.assertEqual(soup.select("input#id_date")[0]["value"], "2014-01-31")
        self.assertEqual(soup.select("input#id_time")[0]["value"], "11:34:00")
        
    def test_edit_action(self):
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        action = mommy.make(models.Action, display_on_board=True, done=True)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()
        act_id = action.id
        
        at = mommy.make(models.ActionType)
        ast = mommy.make(models.ActionStatus)
        at.allowed_status.add(ast)
        at.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        
        data = {'subject': "tested", 'type': at.id, 'date': "2014-01-31", 'time': "11:34",
            'status': ast.id, 'in_charge': user.id, 'detail':"ABCDEF",
            'amount': 200, 'number': 5}
        
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.id, act_id)
        
        self.assertEqual(action.display_on_board, True)
        self.assertEqual(action.done, True)
        for x in data:
            if x in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, x).id, data[x])
            elif x in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, x), data[x])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 1)
        
class DoActionTest(BaseTestCase):
    def test_do_action(self):
        action = mommy.make(models.Action, done=False)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(action.done, False)
        
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'done': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, True)
        
    def test_undo_action(self):
        action = mommy.make(models.Action, done=True)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(action.done, True)
        
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'done': False})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, False)
        
    def test_view_action_warning_not_in_charge(self):
        user = mommy.make(User, is_active=True, is_staff=True, last_name="L", first_name="F")
        action = mommy.make(models.Action, done=True, in_charge=user)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "warning")
        
        
class GroupTest(BaseTestCase):
    
    def test_view_add_group(self):
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_entity_to_group', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_view_add_contact_group(self):
        contact = mommy.make(models.Contact)
        url = reverse('crm_add_contact_to_group', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
    
    def test_add_group_new(self):
        entity = mommy.make(models.Entity)
        data = {
            'group_name': 'toto'
        }
        url = reverse('crm_add_entity_to_group', args=[entity.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_entity', args=[entity.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.entities.all()), [entity])
        self.assertEqual(group.subscribe_form, False)
        
    def test_add_contact_group_new(self):
        contact = mommy.make(models.Contact)
        data = {
            'group_name': 'toto'
        }
        url = reverse('crm_add_contact_to_group', args=[contact.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.contacts.all()), [contact])
        self.assertEqual(group.subscribe_form, False)
        
    def test_add_group_existing(self):
        group = mommy.make(models.Group, name='toto')
        entity = mommy.make(models.Entity)
        data = {
            'group_name': group.name
        }
        url = reverse('crm_add_entity_to_group', args=[entity.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_entity', args=[entity.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.entities.all()), [entity])
        
    def test_add_already_in_group(self):
        group = mommy.make(models.Group, name='toto')
        entity = mommy.make(models.Entity)
        data = {
            'group_name': group.name
        }
        group.entities.add(entity)
        group.save()
        url = reverse('crm_add_entity_to_group', args=[entity.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, reverse('crm_view_entity', args=[entity.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.entities.all()), [entity])
        
    def test_add_entity_contact_already_in_group(self):
        group = mommy.make(models.Group, name='toto')
        contact = mommy.make(models.Contact)
        data = {
            'group_name': group.name
        }
        group.contacts.add(contact)
        group.save()
        url = reverse('crm_add_entity_to_group', args=[contact.entity.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_entity', args=[contact.entity.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.entities.all()), [contact.entity])
        self.assertEqual(list(group.contacts.all()), [contact])
        
    def test_add_contact_entity_already_in_group(self):
        group = mommy.make(models.Group, name='toto')
        contact = mommy.make(models.Contact)
        data = {
            'group_name': group.name
        }
        group.entities.add(contact.entity)
        group.save()
        url = reverse('crm_add_contact_to_group', args=[contact.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.entities.all()), [contact.entity])
        self.assertEqual(list(group.contacts.all()), [contact])
        
    def test_add_contact_group_existing(self):
        group = mommy.make(models.Group, name='toto')
        contact = mommy.make(models.Contact)
        data = {
            'group_name': group.name
        }
        url = reverse('crm_add_contact_to_group', args=[contact.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.contacts.all()), [contact])
        
    def test_add_contact_already_in_group(self):
        group = mommy.make(models.Group, name='toto')
        contact = mommy.make(models.Contact)
        group.contacts.add(contact)
        group.save()
        data = {
            'group_name': group.name
        }
        url = reverse('crm_add_contact_to_group', args=[contact.id])
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        self.assertEqual(1, models.Group.objects.count())
        group = models.Group.objects.all()[0]
        self.assertEqual(group.name, data['group_name'])
        self.assertEqual(list(group.contacts.all()), [contact])
        
    def test_view_contact(self):
        
        contact = mommy.make(models.Contact)
        
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr2 = mommy.make(models.Group, name="GROUP2")
        gr3 = mommy.make(models.Group, name="GROUP3")
        
        gr1.contacts.add(contact)
        gr2.entities.add(contact.entity)
        
        url = reverse('crm_view_contact', args=[contact.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, gr1.name)
        self.assertContains(response, gr2.name)
        self.assertNotContains(response, gr3.name)
        
    def test_view_entity(self):
        
        contact = mommy.make(models.Contact)
        
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr2 = mommy.make(models.Group, name="GROUP2")
        gr3 = mommy.make(models.Group, name="GROUP3")
        
        gr1.contacts.add(contact)
        gr2.entities.add(contact.entity)
        
        url = reverse('crm_view_entity', args=[contact.entity.id])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.assertNotContains(response, gr1.name)
        self.assertContains(response, gr2.name)
        self.assertNotContains(response, gr3.name)
        
    def test_remove_contact_form_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr1.contacts.add(contact)
        self.assertEqual(1, gr1.contacts.count())
        
        url = reverse('crm_remove_contact_from_group', args=[gr1.id, contact.id])
        
        data = {'confirm': "1"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        gr1 = models.Group.objects.get(id=gr1.id)
        self.assertEqual(0, gr1.contacts.count())
        
    def test_remove_contact_not_in_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        self.assertEqual(0, gr1.contacts.count())
        
        url = reverse('crm_remove_contact_from_group', args=[gr1.id, contact.id])
        
        data = {'confirm': "1"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        gr1 = models.Group.objects.get(id=gr1.id)
        self.assertEqual(0, gr1.contacts.count())
        
    def test_cancel_remove_contact_form_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr1.contacts.add(contact)
        self.assertEqual(1, gr1.contacts.count())
        
        url = reverse('crm_remove_contact_from_group', args=[gr1.id, contact.id])
        
        data = {}
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_contact', args=[contact.id]))
        
        gr1 = models.Group.objects.get(id=gr1.id)
        self.assertEqual(1, gr1.contacts.count())
        
    def test_remove_entity_from_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr1.entities.add(contact.entity)
        self.assertEqual(1, gr1.entities.count())
        
        url = reverse('crm_remove_entity_from_group', args=[gr1.id, contact.entity.id])
        
        data = {'confirm': True}
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_entity', args=[contact.entity.id]))
        
        gr1 = models.Group.objects.get(id=gr1.id)
        self.assertEqual(0, gr1.entities.count())
    
    def test_remove_entity_not_in_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        self.assertEqual(0, gr1.entities.count())
        
        url = reverse('crm_remove_entity_from_group', args=[gr1.id, contact.entity.id])
        
        data = {'confirm': "1"}
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_entity', args=[contact.entity.id]))
        
        gr1 = models.Group.objects.get(id=gr1.id)
        self.assertEqual(0, gr1.entities.count())
    
        
    def test_cancel_remove_entity_from_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr1.entities.add(contact.entity)
        self.assertEqual(1, gr1.entities.count())
        
        url = reverse('crm_remove_entity_from_group', args=[gr1.id, contact.entity.id])
        
        data = {'confirm': False}
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse('crm_view_entity', args=[contact.entity.id]))
        
        gr1 = models.Group.objects.get(id=gr1.id)
        self.assertEqual(1, gr1.entities.count())
        
        
class CustomFieldTest(BaseTestCase):
    
    def test_entity_custom_field(self):
        entity = mommy.make(models.Entity)
        cfv = models.CustomField.objects.create(name = 'siret', label = 'SIRET', model=models.CustomField.MODEL_ENTITY)
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        data = {'siret': '555444333222111'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(entity.custom_field_siret, data['siret'])
    
    def test_entity_custom_two_fields(self):
        entity = mommy.make(models.Entity)
        cfv1 = models.CustomField.objects.create(name = 'siret', label = 'SIRET', model=models.CustomField.MODEL_ENTITY)
        cfv2 = models.CustomField.objects.create(name = 'naf', label = 'Code NAF', model=models.CustomField.MODEL_ENTITY)
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        data = {'siret': '555444333222111', 'naf': '56789'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(entity.custom_field_siret, data['siret'])
        self.assertEqual(entity.custom_field_naf, data['naf'])
    
    def test_contact_custom_field(self):
        contact = mommy.make(models.Contact)
        cfv = models.CustomField.objects.create(name = 'insee', label = 'INSEE', model=models.CustomField.MODEL_CONTACT)
        url = reverse('crm_edit_custom_fields', args=['contact', contact.id])
        data = {'insee': '1234567890'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(contact.custom_field_insee, data['insee'])
        
    def test_view_entity(self):
        entity = mommy.make(models.Entity)
        cf1 = models.CustomField.objects.create(name = 'siret', label = 'SIRET', model=models.CustomField.MODEL_ENTITY)
        cf2 = models.CustomField.objects.create(name = 'naf', label = 'Code NAF', model=models.CustomField.MODEL_ENTITY)
        
        response = self.client.get(entity.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        data = {'siret': '555444333222111', 'naf': '56789'}
        cfv1 = models.EntityCustomFieldValue.objects.create(custom_field=cf1, entity=entity, value=data['siret'])
        cfv2 = models.EntityCustomFieldValue.objects.create(custom_field=cf2, entity=entity, value=data['naf'])
        
        response = self.client.get(entity.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['siret'])
        self.assertContains(response, data['naf'])
        
    def test_custom_field_ordering(self):
        entity = mommy.make(models.Entity)
        cf1 = models.CustomField.objects.create(name = 'no_siret', label = 'SIRET', model=models.CustomField.MODEL_ENTITY, ordering=2)
        cf2 = models.CustomField.objects.create(name = 'code_naf', label = 'Code NAF', model=models.CustomField.MODEL_ENTITY, ordering=1)
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        pos_siret = response.content.find('no_siret')
        pos_naf = response.content.find('code_naf')
        self.assertTrue(pos_naf < pos_siret)
        
        cfv1 = models.EntityCustomFieldValue.objects.create(custom_field=cf1, entity=entity, value='1234567890')
        cfv2 = models.EntityCustomFieldValue.objects.create(custom_field=cf2, entity=entity, value='995588')
        
        response = self.client.get(entity.get_absolute_url())
        pos_siret = response.content.find('SIRET')
        pos_naf = response.content.find('Code NAF')
        self.assertTrue(pos_naf < pos_siret)
        
    def test_custom_field_visibility(self):
        entity = mommy.make(models.Entity)
        cf1 = models.CustomField.objects.create(name = 'no_siret', label = 'SIRET', model=models.CustomField.MODEL_ENTITY, ordering=2)
        
        response = self.client.get(entity.get_absolute_url())
        pos_siret = response.content.find('SIRET')
        self.assertNotContains(response, 'SIRET')
        
        cfv1 = models.EntityCustomFieldValue.objects.create(custom_field=cf1, entity=entity, value='1234567890')
        
        response = self.client.get(entity.get_absolute_url())
        self.assertContains(response, 'SIRET')
        self.assertContains(response, '1234567890')
        
    def test_custom_field_widget(self):
        entity = mommy.make(models.Entity)
        cfv1 = models.CustomField.objects.create(name = 'date_b', label = 'Date', model=models.CustomField.MODEL_ENTITY, widget="datepicker")
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="datepicker"')
        
    def test_contact_get_custom_field(self):
        contact = mommy.make(models.Contact)
        
        cf_c = models.CustomField.objects.create(
            name = 'id_poste', label = 'Id Poste', model=models.CustomField.MODEL_CONTACT)
        
        cf_e = models.CustomField.objects.create(
            name = 'id_poste', label = 'Id Poste', model=models.CustomField.MODEL_ENTITY)
        
        contact1 = mommy.make(models.Contact)
        models.EntityCustomFieldValue.objects.create(custom_field=cf_e, entity=contact1.entity, value='111')
        
        contact2 = mommy.make(models.Contact)
        models.ContactCustomFieldValue.objects.create(custom_field=cf_c, contact=contact2, value='222')
        
        contact3 = mommy.make(models.Contact)
        models.ContactCustomFieldValue.objects.create(custom_field=cf_c, contact=contact3, value='333')
        models.EntityCustomFieldValue.objects.create(custom_field=cf_e, entity=contact3.entity, value='444')
        
        contact4 = mommy.make(models.Contact)
        
        self.assertEqual(contact1.get_custom_field_id_poste, '111')
        self.assertEqual(contact2.get_custom_field_id_poste, '222')
        self.assertEqual(contact3.get_custom_field_id_poste, '333')
        self.assertEqual(contact4.get_custom_field_id_poste, '')
        
        
    def test_contact_missing_custom_field(self):
        contact = mommy.make(models.Contact)
        
        contact_custom_field_toto = lambda: contact.custom_field_toto
        self.assertRaises(models.CustomField.DoesNotExist, contact_custom_field_toto)
        #self.assertEqual("", contact.custom_field_toto)
        
        entity_custom_field_toto = lambda: contact.entity.custom_field_toto
        self.assertRaises(models.CustomField.DoesNotExist, entity_custom_field_toto)
        #self.assertEqual("", contact.entity.custom_field_toto)
        

class ImportTemplateTest(BaseTestCase):

    def test_template_with_custom_fields(self):
        
        cf1 = models.CustomField.objects.create(name = 'siret', label = 'SIRET', model=models.CustomField.MODEL_ENTITY, import_order=1)
        cf2 = models.CustomField.objects.create(name = 'naf', label = 'Code NAF', model=models.CustomField.MODEL_ENTITY)
        cf3 = models.CustomField.objects.create(name = 'zip', label = 'Code', model=models.CustomField.MODEL_ENTITY, import_order=3)
        
        cf4 = models.CustomField.objects.create(name = 'abc', label = 'ABC', model=models.CustomField.MODEL_CONTACT, import_order=2)
        cf5 = models.CustomField.objects.create(name = 'def', label = 'DEF', model=models.CustomField.MODEL_CONTACT)
        cf6 = models.CustomField.objects.create(name = 'ghi', label = 'GHI', model=models.CustomField.MODEL_CONTACT, import_order=4)
        
        url = reverse('crm_contacts_import_template')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], 'text/csv')
        
        self.assertEqual(response.content.count('\n'), 1)
        pos = response.content.find('\n')
        line = response.content[:pos]
        cols = [x.strip('"') for x in line.split(";")]
        
        fields = ['gender', 'firstname', 'lastname', 'email', 'phone', 'mobile', 'job', 'notes',
            'role', 'accept_newsletter', 'accept_3rdparty', 'entity', 'entity.type',
            'entity.description', 'entity.website', 'entity.email', 'entity.phone',
            'entity.fax', 'entity.notes', 'entity.address', 'entity.address2', 'entity.address3',
            'entity.city', 'entity.cedex', 'entity.zip_code', 'entity.country', 'address', 'address2',
            'address3', 'city', 'cedex', 'zip_code', 'country', 'entity.groups', 'groups',
        ]
        import codecs
        for i, f in enumerate(fields):
            self.assertEqual(cols[i], f)
        j0 = i+1
        for j, f in enumerate([cf1, cf4, cf3, cf6]):
            self.assertEqual(cols[j0+j], unicode(f))
        
class AddressOverloadTest(BaseTestCase):

    def test_address_of_contact(self):
        
        city1 = mommy.make(models.City, name='city1')
        city2 = mommy.make(models.City, name='city2')
        
        entity_address = {
            'address': u'rue Jules Rimet',
            'address2': u'lot du stade',
            'address2': u'cité St-Laurent',
            'cedex': u'Cedex 2',
            'zip_code': u'12345',
            'city': city1,
        }
        
        contact_address = {
            'address': u'',
            'address2': u'',
            'address2': u'',
            'cedex': u'',
            'zip_code': u'',
            'city': None,
        }
        
        entity = mommy.make(models.Entity, **entity_address)
        contact = mommy.make(models.Contact, entity=entity, **contact_address)
        
        for (att, val) in entity_address.items():
            self.assertEqual(getattr(entity, att), val)
            
    def test_address_overloaded(self):
        
        city1 = mommy.make(models.City, name='city1')
        city2 = mommy.make(models.City, name='city2')
        
        entity_address = {
            'address': u'rue Jules Rimet',
            'address2': u'lot du stade',
            'address2': u'cité St-Laurent',
            'cedex': u'Cedex 2',
            'zip_code': '12345',
            'city': city1,
        }
        
        contact_address = {
            'address': u'rue des tilleuls',
            'address2': u'lot des arbres',
            'address2': u'verrerie',
            'cedex': u'Cedex 3',
            'zip_code': '12346',
            'city': city2,
        }
        
        entity = mommy.make(models.Entity, **entity_address)
        contact = mommy.make(models.Contact, entity=entity, **contact_address)
        
        for (att, val) in contact_address.items():
            self.assertEqual(getattr(contact, att), val)
            
    def test_address_overloaded_missing_fields(self):
        
        city1 = mommy.make(models.City, name='city1')
        city2 = mommy.make(models.City, name='city2')
        
        entity_address = {
            'address': u'rue Jules Rimet',
            'address2': u'lot du stade',
            'address2': u'cité St-Laurent',
            'cedex': u'Cedex 2',
            'zip_code': '12345',
            'city': city1,
        }
        
        base_contact_address = {
            'address': u'rue des tilleuls',
            'address2': u'lot des arbres',
            'address2': u'verrerie',
            'cedex': u'Cedex 3',
            'zip_code': '12346',
            'city': city2,
        }
        
        for (key, value) in base_contact_address.items():
            #create a dict with same keys but blank values
            contact_address = dict([(k, u'') for k in base_contact_address.keys()])
            contact_address[key] = value
            if key != 'city':
                contact_address['city'] = None
        
        
            entity = mommy.make(models.Entity, **entity_address)
            contact = mommy.make(models.Contact, entity=entity, **contact_address)
        
            for (att, val) in contact_address.items():
                self.assertEqual(getattr(contact, att), val)
    
    
class SingleContactTest(BaseTestCase):
    
    def test_view_add_single_contact(self):
        url = reverse('crm_add_single_contact')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Contact.objects.count(), 0)
        
    def test_add_single_contact(self):
        url = reverse('crm_add_single_contact')
        data = {
            'lastname': "Doe",
            'firstname': 'John',
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        self.assertEqual(models.Contact.objects.count(), 1)
        john_doe = models.Contact.objects.all()[0]
        self.assertEqual(john_doe.lastname, "Doe")
        self.assertEqual(john_doe.firstname, "John")
        self.assertEqual(john_doe.entity.is_single_contact, True)
        self.assertEqual(john_doe.entity.name, u"doe john")
        
    def test_add_single_contact_existing_city(self):
        url = reverse('crm_add_single_contact')
        zone = mommy.make(models.Zone)
        city = mommy.make(models.City)
        data = {
            'lastname': "Doe",
            'firstname': 'John',
            'city': city.id,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        
        self.assertEqual(models.Contact.objects.count(), 1)
        john_doe = models.Contact.objects.all()[0]
        self.assertEqual(john_doe.lastname, "Doe")
        self.assertEqual(john_doe.firstname, "John")
        self.assertEqual(john_doe.entity.is_single_contact, True)
        self.assertEqual(john_doe.city.id, city.id)
        
    def test_add_single_contact_new_city(self):
        url = reverse('crm_add_single_contact')
        zone = mommy.make(models.Zone, code="42")
        data = {
            'lastname': "Doe",
            'firstname': 'John',
            'zip_code': '42810',
            'city': "Rozier en Donzy"
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        self.assertEqual(models.Contact.objects.count(), 1)
        john_doe = models.Contact.objects.all()[0]
        self.assertEqual(john_doe.lastname, "Doe")
        self.assertEqual(john_doe.firstname, "John")
        self.assertEqual(john_doe.entity.is_single_contact, True)
        self.assertEqual(john_doe.city.name, data['city'])
        self.assertEqual(john_doe.city.parent, zone)
        
    def test_add_single_contact_unknown_code(self):
        url = reverse('crm_add_single_contact')
        data = {
            'lastname': "Doe",
            'firstname': 'John',
            'zip_code': '42810',
            'city': "Rozier en Donzy"
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        self.assertEqual(models.Contact.objects.count(), 0)
        
    def test_add_single_contact_new_city_no_zip(self):
        url = reverse('crm_add_single_contact')
        data = {
            'lastname': "Doe",
            'firstname': 'John',
            'zip_code': '',
            'city': "Rozier en Donzy"
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Contact.objects.count(), 0)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(response.redirect_chain), 0)
        
    
    def test_view_delete_contact(self):
        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = entity.default_contact
        url = reverse('crm_delete_contact', args=[contact.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Contact.objects.filter(id=contact.id).count(), 1)
        
    def test_delete_single_contact(self):
        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = entity.default_contact
        url = reverse('crm_delete_contact', args=[contact.id])
        data = {'confirm': True}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Entity.objects.filter(id=entity.id).count(), 0)
        self.assertEqual(models.Contact.objects.filter(id=contact.id).count(), 0)
        
    def test_delete_entity_contact(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = entity.default_contact
        url = reverse('crm_delete_contact', args=[contact.id])
        data = {'confirm': True}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Entity.objects.filter(id=entity.id).count(), 1)
        entity.save() #force default contact creation
        self.assertEqual(entity.contact_set.count(), 1)
        
    def test_delete_several_entity_contact(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)
        self.assertEqual(entity.contact_set.count(), 2)
        url = reverse('crm_delete_contact', args=[contact.id])
        data = {'confirm': True}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Entity.objects.filter(id=entity.id).count(), 1)
        self.assertEqual(entity.contact_set.count(), 1)

class ActionAutoGenerateNumberTestCase(TestCase):
    
    def test_create_action_with_auto_generated_number(self):
        at = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 1)
        
    def test_create_action_several_auto_generated_number(self):
        at = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 1)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 2)
        no_gen_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=False)
        a = models.Action.objects.create(type=no_gen_type, subject="a")
        self.assertEqual(a.number, 0)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 3)
        
    def test_save_action_several_auto_generated_number(self):
        at = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 1)
        a.save()
        self.assertEqual(a.number, 1)
        
    def test_create_action_several_auto_generated_types(self):
        at = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 1)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 2)
        no_gen_type = mommy.make(models.ActionType, last_number=27, number_auto_generated=True)
        a = models.Action.objects.create(type=no_gen_type, subject="a")
        self.assertEqual(a.number, 28)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 3)
        
    def test_create_action_no_number_generation(self):
        at = mommy.make(models.ActionType, last_number=0, number_auto_generated=False)
        a = models.Action.objects.create(type=at, subject="a")
        self.assertEqual(a.number, 0)
        
class GroupSuggestListTestCase(BaseTestCase):
    view_name = 'crm_get_group_suggest_list'
    
    def test_group_suggest_list1(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse(self.view_name)+'?term=a')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.name)
        self.assertContains(response, g2.name)
        self.assertNotContains(response, g3.name)
    
    def test_group_id(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse('crm_get_group_id')+'?name='+g1.name)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.id)
        self.assertNotContains(response, g2.id)
        self.assertNotContains(response, g3.id)
        
    def test_group_unknown(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse('crm_get_group_id')+'?name=ab')
        self.assertEqual(404, response.status_code)
    
    def test_group_case_insensitive(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse('crm_get_group_id')+'?name=abcd')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.id)
        self.assertNotContains(response, g2.id)
        self.assertNotContains(response, g3.id)
        
    def test_group_case_insensitive_several(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abcd")
        
        response = self.client.get(reverse('crm_get_group_id')+'?name=abcd')
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, g1.id)
        self.assertContains(response, g2.id)
        
        response = self.client.get(reverse('crm_get_group_id')+'?name=ABCD')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.id)
        self.assertNotContains(response, g2.id)
        
        response = self.client.get(reverse('crm_get_group_id')+'?name=Abcd')
        self.assertEqual(404, response.status_code)
        
    def test_group_suggest_list2(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse(self.view_name)+'?term=abcd')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.name)
        self.assertNotContains(response, g2.name)
        self.assertNotContains(response, g3.name)
        
    def test_group_suggest_list3(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse(self.view_name)+'?term=Abc')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.name)
        self.assertContains(response, g2.name)
        self.assertNotContains(response, g3.name)
        
    def test_group_suggest_list4(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse(self.view_name)+'?term=X')
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, g1.name)
        self.assertNotContains(response, g2.name)
        self.assertContains(response, g3.name)
        
    def test_group_suggest_list5(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyz")
        
        response = self.client.get(reverse(self.view_name)+'?term=k')
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, g1.name)
        self.assertNotContains(response, g2.name)
        self.assertNotContains(response, g3.name)
        
    def test_group_suggest_list6(self):
        g1 = mommy.make(models.Group, name="ABCD")
        g2 = mommy.make(models.Group, name="abc")
        g3 = mommy.make(models.Group, name="xyzC")
        
        response = self.client.get(reverse(self.view_name)+'?term=c')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, g1.name)
        self.assertContains(response, g2.name)
        self.assertContains(response, g3.name)
        
    def test_group_suggest_list_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse(self.view_name)+'?term=c')
        self.assertEqual(302, response.status_code)
        login_url = reverse('django.contrib.auth.views.login')[2:] #login url without lang prefix
        self.assertTrue(response['Location'].find(login_url)>0)


class GetGroupsListTestCase(GroupSuggestListTestCase):
    view_name = 'crm_get_groups'

class CitiesSuggestListTestCase(BaseTestCase):
    
    def setUp(self):
        super(CitiesSuggestListTestCase, self).setUp()
        self.default_country = mommy.make(models.Zone, name=settings.SANZA_DEFAULT_COUNTRY, parent=None)
        self.foreign_country = mommy.make(models.Zone, name="BB", parent=None)
        self.parent = mommy.make(models.Zone, name="AA", code="42", parent=self.default_country)
    
    def test_cities_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_cities')+'?term=c')
        self.assertEqual(200, response.status_code)
        
    def test_get_city_id(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="abce", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+city.name+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city.id)
        self.assertNotContains(response, city2.id)
        
    def test_get_city_id_case_insensitive(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="abce", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+"ABCD"+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city.id)
        self.assertNotContains(response, city2.id)
        
    def test_get_city_id_case_insensitive_twice(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="ABCD", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+"ABCD"+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "ABCD")
        
    def test_get_city_id_same_name(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        parent2 = mommy.make(models.Zone, name="AB", code="43", parent=self.default_country)
        city2 = mommy.make(models.City, name=city.name, parent=parent2)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+city.name+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city.name)
        self.assertNotContains(response, city.id)
        self.assertNotContains(response, city2.id)
        
    def test_get_foreign_city(self):
        city = mommy.make(models.City, name="abcd", parent=self.parent)
        city2 = mommy.make(models.City, name="abce", parent=self.parent)
        city_in_other_country = mommy.make(models.City, name="abcd", parent=self.foreign_country)
        response = self.client.get(reverse('crm_get_city_id')+"?name="+city.name+"&country="+str(self.foreign_country.id))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, city_in_other_country.id)
        self.assertNotContains(response, city.id)
        self.assertNotContains(response, city2.id)
        
    def test_get_city_unknown(self):
        name = "abcd"
        response = self.client.get(reverse('crm_get_city_id')+"?name="+name+"&country=0")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, name)
        
    def test_city_in_default_country(self):
        c1 = mommy.make(models.City, name="ABC", parent=self.parent)
        c2 = mommy.make(models.City, name="ABD", parent=self.parent)
        c3 = mommy.make(models.City, name="XYZ", parent=self.parent)
        c4 = mommy.make(models.City, name="ABE", parent=self.foreign_country)
        
        response = self.client.get(reverse('crm_get_cities')+'?term=a&country=0')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, c1.name)
        self.assertContains(response, c2.name)
        self.assertNotContains(response, c3.name)
        self.assertNotContains(response, c4.name)
        
    def test_city_in_foreign_country(self):
        c1 = mommy.make(models.City, name="ABC", parent=self.parent)
        c2 = mommy.make(models.City, name="ABD", parent=self.parent)
        c3 = mommy.make(models.City, name="XYZ", parent=self.parent)
        c4 = mommy.make(models.City, name="ABE", parent=self.foreign_country)
        
        response = self.client.get(reverse('crm_get_cities')+'?term=a&country={0}'.format(
            self.foreign_country.id))
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, c1.name)
        self.assertNotContains(response, c2.name)
        self.assertNotContains(response, c3.name)
        self.assertContains(response, c4.name)
        

class ContactEntitiesSuggestListTestCase(BaseTestCase):
    
    #def setUp(self):
    #    super(ContactEntitiesSuggestListTestCase, self).setUp()
    
    def test_entities_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_entities')+'?term=c')
        self.assertEqual(302, response.status_code)
        login_url = reverse('django.contrib.auth.views.login')[2:] #login url without lang prefix
        self.assertTrue(response['Location'].find(login_url)>0)
    
    def test_contacts_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_contacts')+'?term=c')
        self.assertEqual(302, response.status_code)
        login_url = reverse('django.contrib.auth.views.login')[2:] #login url without lang prefix
        self.assertTrue(response['Location'].find(login_url)>0)
        
    def test_entities(self):
        e1 = mommy.make(models.Entity, name="ABCD")
        e2 = mommy.make(models.Entity, name="CDE")
        e3 = mommy.make(models.Entity, name="dce")
        e4 = mommy.make(models.Entity, name="XYZ")
        
        response = self.client.get(reverse('crm_get_entities')+'?term=c')
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, e1.name)
        self.assertContains(response, e2.name)
        self.assertContains(response, e3.name)
        self.assertNotContains(response, e4.name)
        
    def test_contacts(self):
        e1 = mommy.make(models.Entity, name="ABCD")
        e2 = mommy.make(models.Entity, name="ZZZ")
        
        c1 = mommy.make(models.Contact, lastname="Zcz", entity=e1)
        c2 = mommy.make(models.Contact, lastname="aaa", entity=e1)
        c3 = mommy.make(models.Contact, lastname="bbb", entity=e2)
        
        response = self.client.get(reverse('crm_get_contacts')+'?term=c')
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, c1.lastname)
        self.assertContains(response, c2.lastname)
        self.assertNotContains(response, c3.lastname)
        
    def test_get_contact_id(self):
        
        e1 = mommy.make(models.Entity, name="ABCD")
        e2 = mommy.make(models.Entity, name="ZZZ")
        
        c1 = mommy.make(models.Contact, lastname="Zcz", entity=e1)
        c2 = mommy.make(models.Contact, lastname="aaa", entity=e1)
        c3 = mommy.make(models.Contact, lastname="bbb", entity=e2)
        
        
        response = self.client.get(reverse('crm_get_contact_id')+"?name="+c1.lastname)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, c1.id)
        
    def test_get_contact_id_from_entity(self):
        
        e1 = mommy.make(models.Entity, name="ABCD")
        e2 = mommy.make(models.Entity, name="ZZZ")
        
        c1 = mommy.make(models.Contact, lastname="Zcz", entity=e1)
        c2 = mommy.make(models.Contact, lastname="aaa", entity=e1)
        #c3 = mommy.make(models.Contact, lastname="bbb", entity=e2)
        c3 = e2.default_contact
        e2.default_contact.lastname = "bbb"
        e2.default_contact.save()
        
        response = self.client.get(reverse('crm_get_contact_id')+"?name="+e2.name)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, c3.id)
        
    def test_no_contacts(self):
        
        e1 = mommy.make(models.Entity, name="ABCD")
        e1.default_contact.lastname = "abc"
        e1.default_contact.save()
        
        response = self.client.get(reverse('crm_get_contact_id')+"?name=ZZZZ")
        self.assertEqual(404, response.status_code)
        
    def test_several_contacts(self):
        
        e1 = mommy.make(models.Entity, name="ABCD")
        
        c1 = mommy.make(models.Contact, lastname="Zcz", entity=e1)
        c2 = mommy.make(models.Contact, lastname="aaa", entity=e1)
        
        response = self.client.get(reverse('crm_get_contact_id')+"?name="+e1.name)
        self.assertEqual(404, response.status_code)
        

class ActionDocumentTestCase(BaseTestCase):
    
    def test_new_document_edit(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        self.assertNotEqual(a.actiondocument, None)
        
    def test_new_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        self.assertNotEqual(a.actiondocument, None)
        
    def test_no_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        a = models.Action.objects.get(id=a.id)
        try:
            doc = a.actiondocument
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)
        
    def test_no_document_edit(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        a = models.Action.objects.get(id=a.id)
        try:
            doc = a.actiondocument
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)
        
    def test_no_document_pdf(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        
    def test_no_type_view(self):
        c = mommy.make(models.Contact)
        a = mommy.make(models.Action, type=None)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        
        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        
        a = models.Action.objects.get(id=a.id)
        try:
            doc = a.actiondocument
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)
        
    def test_view_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        #Create
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        a.actiondocument.content = "This is a test for document actions"
        a.actiondocument.save()
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, a.actiondocument.content)
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, a.actiondocument.content)
        
    #def test_pdf_document_view(self):
    #    c = mommy.make(models.Contact)
    #    at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
    #    a = mommy.make(models.Action, type=at, contact=c)
    #    
    #    response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
    #    self.assertEqual(200, response.status_code)
        
    def _check_anonymous_not_allowed(self, response, url):
        if is_perm_middleware_installed():
            self.assertEqual(302, response.status_code)
            auth_url = reverse("auth_login")
            self.assertRedirects(response, auth_url+'?next='+url)
        else:
            self.assertEqual(403, response.status_code)
            
    def test_anonymous_document_view(self):
        self.client.logout()
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        url = reverse('crm_edit_action_document', args=[a.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)
        
        url = reverse('crm_view_action_document', args=[a.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)
        
        url = reverse('crm_pdf_action_document', args=[a.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)
        
    def test_not_staff_document_view(self):
        self.client.logout()
        
        user = User.objects.create(username="titi", is_staff=False, is_active=True)
        user.set_password("abc")
        user.save()
        self.client.login(username="titi", password="abc")
        
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
        
        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
        

class EditGroupTestCase(BaseTestCase):
    def test_view_edit_group(self):
        g = mommy.make(models.Group)
        response = self.client.get(reverse('crm_edit_group', args=[g.id]))
        self.assertEqual(200, response.status_code)
        
    def test_edit_group(self):
        g = mommy.make(models.Group)
        data = {
            'name': 'my group name',
            'description': 'my group description',
        }
        response = self.client.post(reverse('crm_edit_group', args=[g.id]), data=data)
        self.assertEqual(302, response.status_code)
        g = models.Group.objects.get(id=g.id)
        self.assertEqual(g.name, data['name'])
        self.assertEqual(g.description, data['description'])
        
class EditContactAndEntityTestCase(BaseTestCase):
    fixtures = ['zones.json',]
    
    def _check_redirect_url(self, response, next_url):
        redirect_url = response.redirect_chain[-1][0]
        self.assertEqual(redirect_url, "http://testserver"+next_url)
    
    def test_view_edit_entity(self):
        e = mommy.make(models.Entity, is_single_contact=False)
        response = self.client.get(reverse('crm_edit_entity', args=[e.id]))
        self.assertEqual(200, response.status_code)
        
    def test_edit_entity(self):
        e = mommy.make(models.Entity, is_single_contact=False)
        url = reverse('crm_edit_entity', args=[e.id])
        data = {
            'name': 'Dupond SA',
            'city': models.City.objects.get(name="Paris").id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[e.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)
        
        e = models.Entity.objects.get(id=e.id)
        self.assertEqual(e.name, data['name'])
        self.assertEqual(e.city.id, data['city'])
        
    def test_edit_entity_keep_notes(self):
        e = mommy.make(models.Entity, is_single_contact=False, notes="Toto")
        url = reverse('crm_edit_entity', args=[e.id])
        data = {
            'name': 'Dupond SA',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[e.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)
        
        e = models.Entity.objects.get(id=e.id)
        self.assertEqual(e.name, data['name'])
        self.assertEqual(e.notes, u'Toto')
        
    def test_view_edit_contact(self):
        c = mommy.make(models.Contact)
        response = self.client.get(reverse('crm_edit_contact', args=[c.id]))
        self.assertEqual(200, response.status_code)
        
    def test_edit_contact(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': models.City.objects.get(name="Paris").id,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.id, data['city'])
    
    def test_edit_contact_keep_note(self):
        c = mommy.make(models.Contact, notes="Toto")
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.notes, "Toto")
        
        
    def test_edit_contact_utf(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': u'Mémé',
            'firstname': u'Pépé',
            "email": u"pepe@mémé.fr"
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.email, data['email'])
    
    def test_edit_contact_utf2(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': u'Mémé',
            'firstname': u'Pépé',
            "email": u"pépé@mémé.fr"
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertNotEqual(c.lastname, data['lastname'])
        self.assertNotEqual(c.firstname, data['firstname'])
        self.assertNotEqual(c.email, data['email'])
        
    def test_create_contact_uuid(self):
        data = {
            'lastname': u'Mémé',
            'firstname': u'Pépé',
            "email": u"pepe@mémé.fr"
        }
        c = mommy.make(models.Contact, **data)
        
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.email, data['email'])
        
    def test_edit_contact_unknown_city(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': "ImagineCity",
            'zip_code': "42999",
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.name, data['city'])
        
    def test_edit_contact_unknown_city_no_zipcode(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': "ImagineCity",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(response.redirect_chain), 0)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertNotEqual(c.lastname, data['lastname'])
        self.assertNotEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city, None)
        
class RelationshipTest(BaseTestCase):

    def test_view_add_relationship(self):
        entity1 = mommy.make(models.Entity, name="The Beatles")
        entity2 = mommy.make(models.Entity, name="Apple Records")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="Paul", lastname="McCartney")
        
        relation_type = mommy.make(models.RelationshipType, name="Partners")
        
        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, relation_type.name)

    def test_add_relationship(self):
        entity1 = mommy.make(models.Entity, name="The Beatles")
        entity2 = mommy.make(models.Entity, name="Apple Records")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="Paul", lastname="McCartney")
        
        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")
        
        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': contact2.id, 'relationship_type': relation_type.id})
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        r = models.Relationship.objects.get(contact1=contact1, contact2=contact2)
        self.assertEqual(r.relationship_type, relation_type)
        
    def test_add_reversed_relationship(self):
        contact1 = mommy.make(models.Contact, firstname="Alex", lastname="Ferguson")
        contact2 = mommy.make(models.Contact, firstname="Eric", lastname="Cantona")
        
        relation_type = mommy.make(models.RelationshipType, name="Coach of", reverse="Player of")
        
        url = reverse("crm_add_relationship", args=[contact2.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, relation_type.name)
        self.assertContains(response, relation_type.reverse)
        
        response = self.client.post(url, data={'contact2': contact1.id, 'relationship_type': -relation_type.id})
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        r = models.Relationship.objects.get(contact1=contact1, contact2=contact2)
        self.assertEqual(r.relationship_type, relation_type)
        
    def test_add_relationship_no_contact(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        
        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")
        
        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': '', 'relationship_type': relation_type.id})
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        self.assertEqual(0, models.Relationship.objects.filter(contact1=contact1, contact2=contact2).count())
        
    def test_add_relationship_no_type(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        
        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")
        
        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': contact2.id, 'relationship_type': ''})
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        self.assertEqual(0, models.Relationship.objects.filter(contact1=contact1, contact2=contact2).count())
        
    def test_add_relationship_invaliddata(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        
        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")
        
        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': "AAAA", 'relationship_type': 'ZZZZZ'})
        self.assertEqual(200, response.status_code)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 2)
        
        self.assertEqual(0, models.Relationship.objects.filter(contact1=contact1, contact2=contact2).count())
        
    def test_get_relationship(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        relationship_type = mommy.make(models.RelationshipType, name="Partenaires")
        
        models.Relationship.objects.create(contact1=contact1, contact2=contact2, relationship_type=relationship_type)
        
        for r in contact1.get_relationships():
            self.assertEqual(r.contact, contact2)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.name)
            
        for r in contact2.get_relationships():
            self.assertEqual(r.contact, contact1)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.name)
            
    def test_get_relationship_with_reverse(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        relationship_type = mommy.make(models.RelationshipType, name="Parain", reverse="Filleul")
        
        models.Relationship.objects.create(contact1=contact1, contact2=contact2, relationship_type=relationship_type)
        
        for r in contact1.get_relationships():
            self.assertEqual(r.contact, contact2)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.name)
            
        for r in contact2.get_relationships():
            self.assertEqual(r.contact, contact1)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.reverse)
            
    def test_view_relationships(self):
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker")
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        leia = mommy.make(models.Contact, firstname="Leia", lastname="Princess")
        ian = mommy.make(models.Contact, firstname="Ian", lastname="Solo")
        chewe = mommy.make(models.Contact, firstname="Chewbacca")
    
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        father = mommy.make(models.RelationshipType, name="Father", reverse="Child")
        friends = mommy.make(models.RelationshipType, name="Friend")
        
        models.Relationship.objects.create(contact1=anakin, contact2=luke, relationship_type=father)
        models.Relationship.objects.create(contact1=anakin, contact2=leia, relationship_type=father)
        models.Relationship.objects.create(contact1=obi, contact2=luke, relationship_type=master)
        models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        models.Relationship.objects.create(contact1=luke, contact2=ian, relationship_type=friends)
        models.Relationship.objects.create(contact1=chewe, contact2=luke, relationship_type=friends)
        
        response = self.client.get(reverse("crm_view_contact", args=[luke.id]))
        soup = BS4(response.content)
        
        self.assertEqual(len(soup.select("table tr.relationship")), 4)# 4 + title 
        self.assertEqual(len(soup.select(".add-relation")), 1) # add button is enabled
        
        self.assertContains(response, anakin.fullname)
        self.assertContains(response, obi.fullname)
        self.assertContains(response, ian.fullname)
        self.assertContains(response, chewe.fullname)
        self.assertNotContains(response, leia.fullname)
        
    def test_view_relations_disabeld(self):
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker")
        
        response = self.client.get(reverse("crm_view_contact", args=[luke.id]))
        soup = BS4(response.content)
        
        self.assertEqual(len(soup.select("table.contact-relationships")), 0)
        self.assertEqual(len(soup.select(".add-relation")), 0)# add button is disabled
        
    def test_view_no_relations(self):
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker")
        friends = mommy.make(models.RelationshipType, name="Friend")
        
        response = self.client.get(reverse("crm_view_contact", args=[luke.id]))
        soup = BS4(response.content)
        
        self.assertEqual(len(soup.select("table.contact-relationships")), 0)
        self.assertEqual(len(soup.select(".add-relation")), 1)# add button is disabled
       
    def test_view_delete_relationship(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        
        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        
        response = self.client.get(reverse("crm_delete_relationship", args=[obi.id, r.id]))
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(1, models.Relationship.objects.filter(id=r.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=obi.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=anakin.id).count())
        
    def test_cancel_delete_relationship(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        
        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        
        response = self.client.post(
            reverse("crm_delete_relationship", args=[obi.id, r.id]), {})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(1, models.Relationship.objects.filter(id=r.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=obi.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=anakin.id).count())
            
        
    def test_delete_relationship(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        
        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        
        response = self.client.post(
            reverse("crm_delete_relationship", args=[obi.id, r.id]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(0, models.Relationship.objects.filter(id=r.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=obi.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=anakin.id).count())
        
    def test_delete_unknown_relationship(self):
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        
        response = self.client.get(
            reverse("crm_delete_relationship", args=[obi.id, 100]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(
            reverse("crm_delete_relationship", args=[obi.id, 100]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)
        
    def test_delete_relationship_unknown_contact(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        
        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        
        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        
        response = self.client.post(
            reverse("crm_delete_relationship", args=[8765, r.id]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(
            reverse("crm_delete_relationship", args=[8755, r.id]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)
        
        
class FindSameAsTest(BaseTestCase):

    def test_find_same_as(self):
        
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))
        
    def test_find_same_as_with_group(self):
        
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', "SameAs", verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))
        qs = models.Group.objects.filter(name="SameAs")
        self.assertEqual(1, qs.count())
        self.assertEqual(qs[0].contacts.count(), 2)
        self.assertFalse(contact1 in qs[0].contacts.all())
        self.assertTrue(contact2 in qs[0].contacts.all())
        self.assertTrue(contact3 in qs[0].contacts.all())
        
    def test_find_same_as_with_existing_group(self):
        
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        
        gr = models.Group.objects.create(name="SameAs")
        gr.contacts.add(contact1)
        gr.save()
        
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', "SameAs", verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))
        
        qs = models.Group.objects.filter(name="SameAs")
        self.assertEqual(1, qs.count())
        self.assertEqual(qs[0].contacts.count(), 3)
        self.assertTrue(contact1 in qs[0].contacts.all())
        self.assertTrue(contact2 in qs[0].contacts.all())
        self.assertTrue(contact3 in qs[0].contacts.all())
        
    def test_find_same_as_with_no_name(self):
        
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact4 = mommy.make(models.Contact, firstname="", lastname="")
        contact5 = mommy.make(models.Contact, firstname="", lastname="")
        
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', "SameAs", verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))
        
        qs = models.Group.objects.filter(name="SameAs")
        self.assertEqual(1, qs.count())
        self.assertEqual(qs[0].contacts.count(), 2)
        self.assertFalse(contact1 in qs[0].contacts.all())
        self.assertTrue(contact2 in qs[0].contacts.all())
        self.assertTrue(contact3 in qs[0].contacts.all())
        self.assertFalse(contact4 in qs[0].contacts.all())
        self.assertFalse(contact5 in qs[0].contacts.all())
   
class ChangeContactEntityTest(BaseTestCase):
   
    OPTION_ADD_TO_EXISTING_ENTITY = 1
    OPTION_CREATE_NEW_ENTITY = 2
    OPTION_SWITCH_SINGLE_CONTACT = 3
    OPTION_SWITCH_ENTITY_CONTACT = 4
    
    def test_view_change_contact_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        url = reverse('crm_change_contact_entity', args=[contact.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BS4(response.content)
        expected = [
            self.OPTION_ADD_TO_EXISTING_ENTITY,
            self.OPTION_CREATE_NEW_ENTITY,
            self.OPTION_SWITCH_SINGLE_CONTACT,
            #self.OPTION_SWITCH_ENTITY_CONTACT
        ]
        self.assertEqual(
            [x["value"] for x in soup.select("select option")],
            ["0"]+[str(x) for x in expected]
        )
        
    def test_view_change_contact_entity_single(self):
        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = mommy.make(models.Contact, entity=entity)
        url = reverse('crm_change_contact_entity', args=[contact.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        soup = BS4(response.content)
        expected = [
            self.OPTION_ADD_TO_EXISTING_ENTITY,
            #self.OPTION_CREATE_NEW_ENTITY,
            #self.OPTION_SWITCH_SINGLE_CONTACT,
            self.OPTION_SWITCH_ENTITY_CONTACT
        ]
        self.assertEqual(
            [x["value"] for x in soup.select("select option")],
            ["0"]+[str(x) for x in expected]
        )
        
    def test_change_contact_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        entity2 = mommy.make(models.Entity, is_single_contact=False)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_ADD_TO_EXISTING_ENTITY,
            'entity': entity2.id
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity, entity2)
        
    def test_make_single_contact_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity, lastname="Sunsun", firstname=u"John")
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_SWITCH_SINGLE_CONTACT,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity.is_single_contact, True)
        entity = models.Entity.objects.get(id=entity.id)
        self.assertNotEqual(contact.entity.id, entity.id)
        self.assertEqual(contact.entity.name, u"{0} {1}".format(contact.lastname, contact.firstname).lower())
        
    
    def test_change_to_new_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_CREATE_NEW_ENTITY,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertNotEqual(contact.entity, entity)
        self.assertNotEqual(contact.entity.contact_set.count(), 1)
    
    def test_change_single_to_existing_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = mommy.make(models.Contact, entity=entity)
        entity2 = mommy.make(models.Entity, is_single_contact=False)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_ADD_TO_EXISTING_ENTITY,
            'entity': entity2.id,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity.is_single_contact, False)
        self.assertEqual(contact.entity, entity2)
    
    def test_change_single_to_contact_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = mommy.make(models.Contact, entity=entity)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_SWITCH_ENTITY_CONTACT,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity.is_single_contact, False)
    
    def test_change_contact_entity_no_value(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_SWITCH_ENTITY_CONTACT,
            'entity': '',
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity, entity)
    
    def test_change_contact_entity_invalid_value(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_ADD_TO_EXISTING_ENTITY,
            'entity': 'AAA',
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity, entity)
    
    def test_change_contact_to_single_contact_entity(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        entity2 = mommy.make(models.Entity, is_single_contact=True)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_SWITCH_ENTITY_CONTACT,
            'entity': entity2.id,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity, entity)
        
    def test_change_unknown_command(self):
        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity)
        entity2 = mommy.make(models.Entity, is_single_contact=True)
        
        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': 555,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        errors = BS4(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity, entity)
    
class ActionArchiveTest(BaseTestCase):
   
    def test_view_monthly_action(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=31))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=31))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
    def test_view_monthly_action_end_dt(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 29), end_datetime=datetime(2014, 5, 2))
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 4, 2))
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 3, 30))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime(2014, 5, 1), end_datetime=datetime(2014, 5, 2))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        a6 = mommy.make(models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 8))
        a7 = mommy.make(models.Action, subject="#ACT7#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 5, 2))
        a8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 29))
        
        url = reverse('crm_actions_of_month', args=[2014, 4])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        self.assertContains(response, a6.subject)
        self.assertContains(response, a7.subject)
        self.assertContains(response, a8.subject)
        
        
    def test_view_weekly_action(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=7))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=7))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        
        n = datetime.now()
        url = reverse('crm_actions_of_week', args=[n.year, n.strftime("%U")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
    def test_view_weekly_action_end_dt(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 15))
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime(2014, 4, 1), end_datetime=datetime(2014, 4, 9))
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime(2014, 4, 1), end_datetime=datetime(2014, 4, 2))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime(2014, 4, 15), end_datetime=datetime(2014, 4, 16))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        a6 = mommy.make(models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 8))
        a7 = mommy.make(models.Action, subject="#ACT7#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 5, 2))
        a8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 9))
        
        url = reverse('crm_actions_of_week', args=[2014, 14])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        self.assertContains(response, a6.subject)
        self.assertContains(response, a7.subject)
        self.assertContains(response, a8.subject)

    def test_view_daily_action(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=1))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=1))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        
        n = datetime.now()
        url = reverse('crm_actions_of_day', args=[n.year, n.month, n.day])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
    def test_view_daily_action_end_dt(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 9))
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime(2014, 4, 8), end_datetime=datetime(2014, 4, 12))
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime(2014, 4, 8), end_datetime=datetime(2014, 4, 8))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime(2014, 4, 10), end_datetime=datetime(2014, 4, 10))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        a6 = mommy.make(models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 9))
        a7 = mommy.make(models.Action, subject="#ACT7#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 10))
        a8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 9))
        
        url = reverse('crm_actions_of_day', args=[2014, 4, 9])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        self.assertContains(response, a6.subject)
        self.assertContains(response, a7.subject)
        self.assertContains(response, a8.subject)
    
    def test_view_monthly_action_in_charge_filter(self):
        u = mommy.make(User, first_name="Joe", is_staff=True)
        v = mommy.make(User, first_name="Jack", is_staff=True)
        w = mommy.make(User, first_name="William", is_staff=True)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), in_charge=u)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), in_charge=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), in_charge=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), in_charge=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=u{0},u{1}".format(u.id, v.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [u"u{0}".format(y.id) for y in [u, v]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_monthly_action_type_filter(self):
        u = mommy.make(models.ActionType)
        v = mommy.make(models.ActionType)
        w = mommy.make(models.ActionType)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=u)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=t{0},t{1}".format(u.id, v.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [u"t{0}".format(y.id) for y in [u, v]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_monthly_action_type_none(self):
        u = mommy.make(models.ActionType)
        v = mommy.make(models.ActionType)
        w = mommy.make(models.ActionType)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=u)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=t0"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(["t0"], [x["value"] for x in soup.select("select option[selected=selected]")])
        
    def test_view_monthly_action_type_none_and_defined(self):
        u = mommy.make(models.ActionType)
        v = mommy.make(models.ActionType)
        w = mommy.make(models.ActionType)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=u)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=t0,t{0}".format(u.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [u"t0"] +[u"t{0}".format(y.id) for y in [u,]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_monthly_action_filter_invalid(self):
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=abc"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
    
    def test_view_monthly_action_filter_invalid_user(self):
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=u2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_monthly_action_filter_invalid_type(self):
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=t2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_monthly_action_type_in_charge_filter(self):
        u = mommy.make(User, first_name="Joe", is_staff=True)
        v = mommy.make(models.ActionType)
        w = mommy.make(models.ActionType)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), in_charge=u, type=v)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), in_charge=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())
        
        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])+"?filter=u{0},t{1}".format(u.id, v.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [u"t{0}".format(v.id)] + [u"u{0}".format(u.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_not_planned_action(self):
        u = mommy.make(User, first_name="Joe", is_staff=True)
        v = mommy.make(models.ActionType)
        w = mommy.make(models.ActionType)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=None, in_charge=u, type=v)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=None, in_charge=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=None, type=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=None, type=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now(), in_charge=u, type=v)
        
        n = datetime.now()
        url = reverse('crm_actions_not_planned')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
    def test_view_not_planned_action_type_in_charge_filter(self):
        u = mommy.make(User, first_name="Joe", is_staff=True)
        v = mommy.make(models.ActionType)
        w = mommy.make(models.ActionType)
        
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=None, in_charge=u, type=v)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=None, in_charge=u)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=None, type=v)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=None, type=w)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now(), in_charge=u, type=v)
        
        n = datetime.now()
        url = reverse('crm_actions_not_planned')+"?filter=u{0},t{1}".format(u.id, v.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
        soup = BS4(response.content)
        self.assertEqual(
            [u"t{0}".format(v.id)] + [u"u{0}".format(u.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        
class ViewContactsTest(BaseTestCase):
   
    def test_view_contacts(self):
        e1 = mommy.make(models.Entity)
        c1 = e1.default_contact
        c1.lastname = "#Contact{0}#".format(c1.id)
        c1.save()
        
        e2 = mommy.make(models.Entity, is_single_contact=True)
        c2 = e2.default_contact
        c2.lastname = "#Contact{0}#".format(c2.id)
        c2.save()
        
        url = reverse('crm_view_entities_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, e1.name)
        self.assertContains(response, c1.lastname)
        self.assertNotContains(response, e2.name)
        self.assertContains(response, c2.lastname)
        
    def test_view_entities_actions(self):
        e1 = mommy.make(models.Entity)
        c1 = e1.default_contact
        c1.lastname = "#Contact{0}#".format(c1.id)
        c1.save()
        
        a1 = mommy.make(models.Action, subject="#Action1#", done=True, done_date=datetime.now())
        a1.entities.add(e1)
        a1.save()
        
        a2 = mommy.make(models.Action, subject="#Action2#", done=True, done_date=datetime.now()-timedelta(days=1))
        a2.entities.add(e1)
        a2.save()
        
        a3 = mommy.make(models.Action, subject="#Action3#", done=False, planned_date=datetime.now())
        a3.entities.add(e1)
        a3.save()
        
        a4 = mommy.make(models.Action, subject="#Action4#", done=False, planned_date=datetime.now()+timedelta(days=1))
        a4.entities.add(e1)
        a4.save()
        
        a5 = mommy.make(models.Action, subject="#Action5#", done=False)
        a5.entities.add(e1)
        a5.save()
        
        url = reverse('crm_view_entities_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, e1.name)
        self.assertContains(response, c1.lastname)
        self.assertContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        
    def test_view_contact_actions(self):
        e1 = mommy.make(models.Entity)
        c1 = e1.default_contact
        c1.lastname = "#Contact{0}#".format(c1.id)
        c1.save()
        
        a1 = mommy.make(models.Action, subject="#Action1#", done=True, done_date=datetime.now())
        a1.contacts.add(c1)
        a1.save()
        
        a2 = mommy.make(models.Action, subject="#Action2#", done=True, done_date=datetime.now()-timedelta(days=1))
        a2.contacts.add(c1)
        a2.save()
        
        a3 = mommy.make(models.Action, subject="#Action3#", done=False, planned_date=datetime.now())
        a3.contacts.add(c1)
        a3.save()
        
        a4 = mommy.make(models.Action, subject="#Action4#", done=False, planned_date=datetime.now()+timedelta(days=1))
        a4.contacts.add(c1)
        a4.save()
        
        a5 = mommy.make(models.Action, subject="#Action5#", done=False)
        a5.contacts.add(c1)
        a5.save()
        
        url = reverse('crm_view_entities_list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, e1.name)
        self.assertContains(response, c1.lastname)
        self.assertContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        