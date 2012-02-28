# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
import json
from model_mommy import mommy
from sanza.Crm import models

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def _login(self):
        self.client.login(username="toto", password="abc")


class OpportunityTest(BaseTestCase):

    def test_add_opportunity(self):
        
        entity1 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        entity2 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        other_entity = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        
        url = reverse("crm_add_opportunity")
        response = self.client.get(url)
        
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity1.name)
        self.assertContains(response, entity2.name)
        self.assertNotContains(response, other_entity.name)
        
        response = self.client.post(url, data={'entity': entity2.id}, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.redirect_chain))
        
        self.assertContains(response, entity2.name)
        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, other_entity.name)

    def test_add_opportunity_for_entity(self):
        pass
        #self.assertEqual(response.status_code, 200)

    def test_view_opportunity(self):
        entity1 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make_one(models.Opportunity, entity=entity1)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.content)
        self.assertContains(response, opp1.name)
        
    def test_view_opportunity_actions(self):
        entity1 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        entity2 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make_one(models.Opportunity, entity=entity1)
        act1 = mommy.make_one(models.Action, opportunity=opp1, entity=entity1)
        act2 = mommy.make_one(models.Action, opportunity=opp1, entity=entity2)
        act3 = mommy.make_one(models.Action, entity=entity1)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.content)
        self.assertContains(response, opp1.name)
        self.assertContains(response, act1.name)
        self.assertContains(response, act2.name)
        self.assertNotContains(response, act3.name)
    
    def test_view_opportunity_contacts(self):
        entity1 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        entity2 = mommy.make_one(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make_one(models.Opportunity, entity=entity1)
        contact1 = mommy.make_one(models.Contact, entity=entity1)
        contact2 = mommy.make_one(models.Contact, entity=entity2)
        contact3 = mommy.make_one(models.Contact, entity=entity1)
        act1 = mommy.make_one(models.Action, opportunity=opp1, entity=entity1, contact=contact1)
        act2 = mommy.make_one(models.Action, opportunity=opp1, entity=entity2, contact=contact2)
        act3 = mommy.make_one(models.Action, entity=entity1, contact=contact3)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.content)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        
class SameAsTest(BaseTestCase):

    def test_add_same_as(self):
        entity1 = models.Entity.objects.create(name="Toto")
        entity2 = models.Entity.objects.create(name="Titi")
        contact1 = models.Contact.objects.create(entity=entity1, firstname="John", lastname="Lennon")
        contact2 = models.Contact.objects.create(entity=entity2, firstname="John", lastname="Lennon")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        
    def test_add_same_as_list(self):
        entity1 = models.Entity.objects.create(name="Toto")
        entity2 = models.Entity.objects.create(name="Titi")
        contact1 = models.Contact.objects.create(entity=entity1, firstname="John", lastname="Lennon")
        contact2 = models.Contact.objects.create(entity=entity2, firstname="John", lastname="Lennon")
        contact3 = models.Contact.objects.create(entity=entity3, firstname="Ringo", lastname="Star")
        
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
        contact3 = models.Contact.objects.get(id=contact3.id)
        
        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact3.same_as, None)
        
        
class OpportunityAutoCompleteTest(BaseTestCase):
    def test_get_add_action(self):
        response = self.client.get(reverse('crm_add_action'))
        self.assertEqual(200, response.status_code)
        
    def test_get_opportunity_name(self):
        opp = mommy.make_one(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_name', args=[opp.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp.name)
        
    def test_get_opportunity_name_unknown(self):
        opp = mommy.make_one(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_name', args=[55]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '55')
        
        url = reverse('crm_get_opportunity_name', args=[555])
        url = url.replace('555', 'toto')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        
    def test_get_opportunity_list(self):
        e1 = mommy.make_one(models.Entity, name='ABC')
        e2 = mommy.make_one(models.Entity, name='XYZ')
        opp1 = mommy.make_one(models.Opportunity, name="def", entity=e1)
        opp2 = mommy.make_one(models.Opportunity, name="Uvw", entity=e2)
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=a')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, e1.name)
        self.assertContains(response, opp1.name)
        self.assertNotContains(response, e2.name)
        self.assertNotContains(response, opp2.name)
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=U')
        self.assertEqual(200, response.status_code)
        self.assertContains(response, e2.name)
        self.assertContains(response, opp2.name)
        self.assertNotContains(response, e1.name)
        self.assertNotContains(response, opp1.name)
        
        response = self.client.get(reverse('crm_get_opportunities')+'?term=k')
        self.assertNotContains(response, e1.name)
        self.assertNotContains(response, opp1.name)
        self.assertNotContains(response, e2.name)
        self.assertNotContains(response, opp2.name)
        
class DoActionTest(BaseTestCase):
    def test_do_action(self):
        action = mommy.make_one(models.Action, done=False)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, action.detail)
        self.assertEqual(action.done, False)
        
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'detail': "tested"})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.detail, "tested")
        self.assertEqual(action.done, True)
        
    def test_do_action_and_new(self):
        action = mommy.make_one(models.Action, done=False)
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'detail': "tested", 'done_and_new': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_add_action_for_entity", args=[action.entity.id]))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.detail, "tested")
        self.assertEqual(action.done, True)
        