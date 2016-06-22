# -*- coding: utf-8 -*-
"""unit testing"""

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class OpportunityTest(BaseTestCase):
    """test opportunities"""

    def test_view_delete_opportunity(self):
        """test view an opportunity"""
        opportunity = mommy.make(models.Opportunity)

        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, models.Opportunity.objects.count())

    def test_delete_empty_opportunity(self):
        """test delete an opportunity"""
        opportunity = mommy.make(models.Opportunity)

        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.post(url, {'confirm': True})
        self.assertEqual(200, response.status_code)

        self.assertEqual(0, models.Opportunity.objects.count())

    def test_delete_opportunity_actions(self):
        """test delete opportunity doesn't delete actions"""
        opportunity = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity)

        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.post(url, {'confirm': True})
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, models.Opportunity.objects.count())
        self.assertEqual(1, models.Action.objects.count())
        self.assertEqual(action, models.Action.objects.all()[0])

    def test_delete_opportunity_cancel(self):
        """test cancel delete doesn't delete"""
        opportunity = mommy.make(models.Opportunity)

        url = reverse("crm_delete_opportunity", args=[opportunity.id])
        response = self.client.post(url, {'confirm': False})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, models.Opportunity.objects.count())

    def test_view_add_action_to_opportunity(self):
        """test view add action to opportunity page"""
        action = mommy.make(models.Action)
        mommy.make(models.Opportunity)

        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertEqual(action.opportunity, None)

    def test_view_add_action_to_opportunity_no_opp(self):
        """test view add action to opportunity page: no opoportunity exists"""
        action = mommy.make(models.Action)

        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertEqual(action.opportunity, None)

    def test_add_action_to_opportunity(self):
        """test add an action to an opportunity"""
        action = mommy.make(models.Action)
        opportunity = mommy.make(models.Opportunity)

        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.post(url, data={'opportunity': opportunity.id})
        self.assertEqual(200, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity)

    def test_add_action_to_opportunity_existing(self):
        """test add an action to an opportunity which is already associated with it"""
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)

        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.post(url, data={'opportunity': opportunity2.id})
        self.assertEqual(200, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity2)

    def test_add_action_to_opportunity_invalid(self):
        """add action to an opportunity using an invalid name"""
        opportunity1 = mommy.make(models.Opportunity)
        mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)

        url = reverse("crm_add_action_to_opportunity", args=[action.id])
        response = self.client.post(url, data={'opportunity': "AAAA"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(BeautifulSoup(response.content).select(".field-error")), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity1)

    def test_remove_action_from_opportunity(self):
        """test remove action from opportunity"""
        opportunity1 = mommy.make(models.Opportunity)
        mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)

        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity1.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, None)

    def test_remove_action_from_opportunity_badone(self):
        """remove action form an opportunity and it is not member of this opportunity"""
        opportunity1 = mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)

        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity2.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity1)

    def test_remove_action_from_opportunity_no_confirm(self):
        """test remove action from opportunity without confirmation"""
        opportunity1 = mommy.make(models.Opportunity)
        mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=opportunity1)

        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity1.id])
        response = self.client.post(url, data={'confirm': 0})
        self.assertEqual(200, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, opportunity1)

    def test_remove_action_from_opportunity_no_opp(self):
        """remove action from opportunity. The action is not associated with any opportunity"""
        mommy.make(models.Opportunity)
        opportunity2 = mommy.make(models.Opportunity)
        action = mommy.make(models.Action, opportunity=None)

        url = reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity2.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.opportunity, None)

    def test_view_add_opportunity(self):
        """view an opportunity"""
        url = reverse("crm_add_opportunity")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_add_opportunity(self):
        """create an opportunity"""
        url = reverse("crm_add_opportunity")
        data = {
            'name': "ABC",
            "detail": "ooo",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(BeautifulSoup(response.content).select('.field-error'), [])

        self.assertEqual(1, models.Opportunity.objects.count())
        opportunity = models.Opportunity.objects.all()[0]
        for key, value in data.items():
            self.assertEqual(getattr(opportunity, key), value)

    def test_add_opportunity_no_desc(self):
        """create an opportunity without description"""
        url = reverse("crm_add_opportunity")
        data = {
            'name': "DEF",
            "detail": "",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(BeautifulSoup(response.content).select('.field-error'), [])

        self.assertEqual(1, models.Opportunity.objects.count())
        opportunity = models.Opportunity.objects.all()[0]
        for key, value in data.items():
            self.assertEqual(getattr(opportunity, key), value)

    def test_add_opportunity_no_name(self):
        """create an opportunity with no name"""
        url = reverse("crm_add_opportunity")
        data = {
            'name': "",
            "detail": "",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(BeautifulSoup(response.content).select('.field-error')), 1)

        self.assertEqual(0, models.Opportunity.objects.count())

    def test_edit_opportunity(self):
        """edit an opportunity"""
        opportunity = mommy.make(models.Opportunity)
        url = reverse("crm_edit_opportunity", args=[opportunity.id])
        data = {
            'name': "ABC",
            "detail": "ooo",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(BeautifulSoup(response.content).select('.field-error'), [])

        self.assertEqual(1, models.Opportunity.objects.count())
        opportunity = models.Opportunity.objects.all()[0]
        for key, value in data.items():
            self.assertEqual(getattr(opportunity, key), value)

    def test_view_opportunity(self):
        """view an opportunity"""
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity, name="OPP1", entity=entity1)
        response = self.client.get(reverse('crm_view_opportunity', args=[opp1.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp1.name)

    def test_view_opportunity_actions(self):
        """view opportunity with actions"""
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

    def test_view_opportunity_contacts(self):
        """view opportunity contacts"""
        entity1 = mommy.make(models.Entity, relationship_date='2012-01-30')
        entity2 = mommy.make(models.Entity, relationship_date='2012-01-30')
        opp1 = mommy.make(models.Opportunity, entity=entity1)
        contact1 = mommy.make(models.Contact, lastname='ABCCBA', entity=entity1)
        contact2 = mommy.make(models.Contact, lastname='DEFFED', entity=entity2)
        contact3 = mommy.make(models.Contact, lastname='GHIIGH', entity=entity1)
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
        """view opportunity with contact who left"""
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
        """view opportunity with contact who left"""
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
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select("td.ut-contact-{0} .ut-has-left".format(contact1.id))), 0)
        self.assertEqual(len(soup.select("td.ut-contact-{0} .ut-has-left".format(contact2.id))), 1)

    def test_view_opportunities_date_mixes(self):
        """view opportunities dates"""
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

    def test_view_opportunities_date_mixes_none(self):
        """view opportunity dates with action without dates"""
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


class OpportunityAutoCompleteTest(BaseTestCase):
    """Test opportunity suggestin list"""
    def test_get_add_action(self):
        """view add an action"""
        response = self.client.get(reverse('crm_add_action'))
        self.assertEqual(200, response.status_code)

    def test_get_opportunity_name(self):
        """get by name"""
        opp = mommy.make(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_name', args=[opp.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp.name)

    def test_get_opportunity_name_unknown(self):
        """unknown name"""
        mommy.make(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_name', args=[55]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '55')

        url = reverse('crm_get_opportunity_name', args=['toto'])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'toto')

    def test_get_opportunity_id(self):
        """get opportunity id from name"""
        opp = mommy.make(models.Opportunity, name="abcd")
        response = self.client.get(reverse('crm_get_opportunity_id')+"?name="+opp.name)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, opp.id)

    def test_get_opportunity_unknown(self):
        """get id when name in unkwonwn should cause 404"""
        response = self.client.get(reverse('crm_get_opportunity_id')+"?name=toto")
        self.assertEqual(404, response.status_code)

    def test_get_opportunity_list(self):
        """get list of opportunities"""
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
