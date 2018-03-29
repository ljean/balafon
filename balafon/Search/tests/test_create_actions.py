# -*- coding: utf-8 -*-
"""test we can search contacts by action"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy


from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class ActionForContactsTest(BaseTestCase):
    """create actions from results"""

    def test_view_create_action_for_contacts(self):
        """test GET on url"""
        url = reverse('search_create_action_for_contacts')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_view_form(self):
        """test view crete action form"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = entity2.default_contact

        group = mommy.make(models.Group, name="my group")
        group.entities.add(entity1, entity2)
        group.save()

        url = reverse('search_create_action_for_contacts')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        id_contacts = soup.select('input#id_contacts')
        self.assertEqual(1, len(id_contacts))

        self.assertEqual(
            sorted([int(x) for x in id_contacts[0]['value'].split(';')]),
            sorted([contact1.id, contact2.id])
        )

    def test_view_form_not_logged(self, ):
        """test view form is not logged"""
        self.client.logout()

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        entity2 = mommy.make(models.Entity, name="Other corp")

        group = mommy.make(models.Group, name="my group")
        group.entities.add(entity1, entity2)
        group.save()

        url = reverse('search_create_action_for_contacts')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_post_create_actions_for_contacts(self):
        """test create actions for contact"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name="Big corp")
        contact3 = entity3.default_contact

        data = {
            'contacts': ";".join(['{0}'.format(i) for i in (contact1.id, contact2.id)]),
            'date': '',
            'time': '',
            'type': '',
            'subject': 'test',
            'in_charge': '',
            'detail': '',
            'planned_date': '',
            'opportunity': '',
            'create_actions': '',
        }

        url = reverse('search_create_action_for_contacts')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<script>$.colorbox.close();')

        self.assertEqual(models.Action.objects.count(), 2)

        self.assertEqual(models.Action.objects.filter(contacts=contact1).count(), 1)
        self.assertEqual(models.Action.objects.filter(contacts=contact2).count(), 1)
        self.assertEqual(models.Action.objects.filter(contacts=contact3).count(), 0)

        action1 = models.Action.objects.filter(contacts=contact1)[0]
        action2 = models.Action.objects.filter(contacts=contact2)[0]

        self.assertNotEqual(action1.id, action2.id)
        self.assertEqual(action1.contacts.count(), 1)
        self.assertEqual(action2.contacts.count(), 1)
        self.assertEqual(action1.subject, data['subject'])
        self.assertEqual(action2.subject, data['subject'])

    def test_post_create_actions_anonymous(self):
        """test can't create actions for contact if not logged"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = entity2.default_contact

        self.client.logout()

        data = {
            'contacts': ";".join(['{0}'.format(i) for i in (contact1.id, contact2.id)]),
            'date': '',
            'time': '',
            'type': '',
            'subject': 'test',
            'in_charge': '',
            'detail': '',
            'planned_date': '',
            'opportunity': '',
            'create_actions': '',
        }

        url = reverse('search_create_action_for_contacts')
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        #login url without lang prefix
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        self.assertEqual(models.Action.objects.count(), 0)

    def test_post_create_actions_not_staff(self):
        """test can't create actions for contact if not in staff"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = entity2.default_contact

        self.user.is_staff = False
        self.user.save()

        data = {
            'contacts': ";".join(['{0}'.format(i) for i in (contact1.id, contact2.id)]),
            'date': '',
            'time': '',
            'type': '',
            'subject': 'test',
            'in_charge': '',
            'detail': '',
            'planned_date': '',
            'opportunity': '',
            'create_actions': '',
        }

        url = reverse('search_create_action_for_contacts')
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        self.assertEqual(models.Action.objects.count(), 0)

    def test_post_create_actions_default_status(self):
        """test create actions for contact"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name="Big corp")
        contact3 = entity3.default_contact

        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.default_status = action_status2
        action_type.save()

        data = {
            'contacts': ";".join(['{0}'.format(i) for i in (contact1.id, contact2.id)]),
            'date': '',
            'time': '',
            'type': action_type.id,
            'subject': 'test',
            'in_charge': '',
            'detail': '',
            'planned_date': '',
            'opportunity': '',
            'create_actions': '',
        }

        url = reverse('search_create_action_for_contacts')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<script>$.colorbox.close();')

        self.assertEqual(models.Action.objects.count(), 2)

        self.assertEqual(models.Action.objects.filter(contacts=contact1).count(), 1)
        self.assertEqual(models.Action.objects.filter(contacts=contact2).count(), 1)
        self.assertEqual(models.Action.objects.filter(contacts=contact3).count(), 0)

        action1 = models.Action.objects.filter(contacts=contact1)[0]
        action2 = models.Action.objects.filter(contacts=contact2)[0]

        self.assertNotEqual(action1.id, action2.id)

        for action in (action1, action2):
            self.assertEqual(action.contacts.count(), 1)
            self.assertEqual(action.subject, data['subject'])
            self.assertEqual(action.type, action_type)
            self.assertEqual(action.status, action_status2)

    def test_post_create_actions_opportunity(self):
        """test create actions for contact"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name="Big corp")
        contact3 = entity3.default_contact

        opportunity = mommy.make(models.Opportunity)

        data = {
            'contacts': ";".join(['{0}'.format(i) for i in (contact1.id, contact2.id)]),
            'date': '',
            'time': '',
            'type': '',
            'subject': 'test',
            'in_charge': '',
            'detail': '',
            'planned_date': '',
            'opportunity': opportunity.id,
            'create_actions': '',
        }

        url = reverse('search_create_action_for_contacts')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(response, '<script>$.colorbox.close();')

        self.assertEqual(models.Action.objects.count(), 2)

        self.assertEqual(models.Action.objects.filter(contacts=contact1).count(), 1)
        self.assertEqual(models.Action.objects.filter(contacts=contact2).count(), 1)
        self.assertEqual(models.Action.objects.filter(contacts=contact3).count(), 0)

        action1 = models.Action.objects.filter(contacts=contact1)[0]
        action2 = models.Action.objects.filter(contacts=contact2)[0]

        self.assertNotEqual(action1.id, action2.id)

        for action in (action1, action2):
            self.assertEqual(action.contacts.count(), 1)
            self.assertEqual(action.subject, data['subject'])
            self.assertEqual(action.opportunity, opportunity)
