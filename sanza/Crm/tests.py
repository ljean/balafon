# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
import json
from model_mommy import mommy
from sanza.Crm import models
from django.conf import settings
from bs4 import BeautifulSoup as BS4

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto", is_staff=True)
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def _login(self):
        self.client.login(username="toto", password="abc")
        
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
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertEqual(response["Location"],
            "http://testserver"+reverse("crm_edit_contact_after_entity_created", args=[e.default_contact.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.type, None)
    
    def test_create_entity_with_type(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[t.id])
        response = self.client.post(url, data={'name': "ABC", "type": t.id})
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertEqual(response["Location"],
            "http://testserver"+reverse("crm_edit_contact_after_entity_created", args=[e.default_contact.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.type, t)
        
    def test_create_entity_with_type_after(self):
        t = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "type": t.id})
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        e = models.Entity.objects.all()[0]
        self.assertEqual(response["Location"],
            "http://testserver"+reverse("crm_edit_contact_after_entity_created", args=[e.default_contact.id]))
        self.assertEqual(e.name, "ABC")
        self.assertEqual(e.type, t)
        
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

    def test_add_opportunity(self):
        
        entity1 = mommy.make(models.Entity, name='ent1', relationship_date='2012-01-30')
        entity2 = mommy.make(models.Entity, name='ent2', relationship_date='2012-01-30')
        other_entity = mommy.make(models.Entity, name='ent3', relationship_date='2012-01-30')
        
        url = reverse("crm_add_opportunity")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
    def test_add_opportunity_for_entity(self):
        pass
        #self.assertEqual(response.status_code, 200)

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
        act1 = mommy.make(models.Action, subject='ABC', opportunity=opp1, entity=entity1)
        act2 = mommy.make(models.Action, subject='DEF', opportunity=opp1, entity=entity2)
        act3 = mommy.make(models.Action, subject='GHI', entity=entity1)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)
        self.assertContains(response, act1.subject)
        self.assertContains(response, act2.subject)
        self.assertNotContains(response, act3.subject)
    
    def test_view_opportunity_contacts(self):
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        entity2 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity, entity=entity1)
        contact1 = mommy.make(models.Contact, lastname='ABC', entity=entity1)
        contact2 = mommy.make(models.Contact, lastname='DEF', entity=entity2)
        contact3 = mommy.make(models.Contact, lastname='GHI', entity=entity1)
        act1 = mommy.make(models.Action, opportunity=opp1, entity=entity1, contact=contact1)
        act2 = mommy.make(models.Action, opportunity=opp1, entity=entity2, contact=contact2)
        act3 = mommy.make(models.Action, entity=entity1, contact=contact3)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        
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
        
    def test_make_main_view(self):
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")
        
        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)
        
        url = reverse("crm_make_main_contact", args=[contact1.id])
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
        
        url = reverse("crm_make_main_contact", args=[contact1.id])
        
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)
        
        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        
        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as.main_contact, contact1)
        
        
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
        action = mommy.make(models.Action, contact=contact)
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        data = {'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status':"", 'in_charge': "", 'contact': contact.id, 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False}
        
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.errorlist')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "tested")
        
    def test_edit_action_on_entity(self):
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, entity=entity)
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        data = {'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status':"", 'in_charge': "", 'contact': entity.default_contact.id, 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False}
        
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.errorlist')
        self.assertEqual(len(errors), 0)
        
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "tested")
        self.assertEqual(action.contact.id, entity.default_contact.id)

        
class DoActionTest(BaseTestCase):
    def test_do_action(self):
        action = mommy.make(models.Action, done=False)
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
        
    def test_do_action_entity_and_new(self):
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, done=False, entity=entity)
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'detail': "tested", 'done_and_new': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_add_action_for_entity", args=[action.entity.id]))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.detail, "tested")
        self.assertEqual(action.done, True)
        
    def test_do_action_contact_and_new(self):
        contact = mommy.make(models.Contact)
        action = mommy.make(models.Action, done=False, contact=contact)
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'detail': "tested", 'done_and_new': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_add_action_for_contact", args=[action.contact.id]))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.detail, "tested")
        self.assertEqual(action.done, True)
        
    def test_do_action_contact_and_new(self):
        action = mommy.make(models.Action, done=False)
        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'detail': "tested", 'done_and_new': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.detail, "tested")
        self.assertEqual(action.done, True)
        
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
        
    def test_remove_entity_form_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr1.entities.add(contact.entity)
        self.assertEqual(1, gr1.entities.count())
        
        url = reverse('crm_remove_entity_from_group', args=[gr1.id, contact.entity.id])
        
        data = {'confirm': "1"}
        
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
    
        
    def test_cancel_remove_entity_form_group(self):
        
        contact = mommy.make(models.Contact)
        gr1 = mommy.make(models.Group, name="GROUP1")
        gr1.entities.add(contact.entity)
        self.assertEqual(1, gr1.entities.count())
        
        url = reverse('crm_remove_entity_from_group', args=[gr1.id, contact.entity.id])
        
        data = {}
        
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
        a = mommy.make(models.Action, type=at, contact=c)
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        self.assertNotEqual(a.actiondocument, None)
        
    def test_new_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at, contact=c)
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        self.assertNotEqual(a.actiondocument, None)
        
    def test_no_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at, contact=c)
        
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
        a = mommy.make(models.Action, type=at, contact=c)
        
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
        a = mommy.make(models.Action, type=at, contact=c)
        
        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        
    def test_no_type_view(self):
        c = mommy.make(models.Contact)
        a = mommy.make(models.Action, type=None, contact=c)
        
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
        a = mommy.make(models.Action, type=at, contact=c)
        
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
        
    def test_anonymous_document_view(self):
        self.client.logout()
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at, contact=c)
        
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
        
        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
        
        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
        
    def test_not_staff_document_view(self):
        self.client.logout()
        
        user = User.objects.create(username="titi", is_staff=False)
        user.set_password("abc")
        user.save()
        self.client.login(usernname="titi", password="abc")
        
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at, contact=c)
        
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
        
class EditContactTestCase(BaseTestCase):
    fixtures = ['zones.json',]
    
    def _check_redirect_url(self, response, next_url):
        redirect_url = response.redirect_chain[-1][0]
        self.assertEqual(redirect_url, "http://testserver"+next_url)
    
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
        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.errorlist')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self._check_redirect_url(response, next_url)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.id, data['city'])
        
    def test_edit_contact_unknwonn_city(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': "ImagineCity",
            'zip_code': "42999",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.errorlist')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self._check_redirect_url(response, next_url)
        
        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.name, data['city'])
        
    def test_edit_contact_unknwonn_city_no_zipcode(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': "ImagineCity",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BS4(response.content).select('.errorlist')
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
        
        errors = BS4(response.content).select('.errorlist')
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
        
        errors = BS4(response.content).select('.errorlist')
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
        
        errors = BS4(response.content).select('.errorlist')
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
        
        errors = BS4(response.content).select('.errorlist')
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
        
        errors = BS4(response.content).select('.errorlist')
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
        
        self.assertEqual(len(soup.select("table.contact-relationships tr")), 5)# 4 + title 
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
        
        