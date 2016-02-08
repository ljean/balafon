# -*- coding: utf-8 -*-
"""unit testing"""

from bs4 import BeautifulSoup

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class LastModifiedTest(BaseTestCase):
    """View an entity"""

    def test_create_entity(self):
        """create an entity: check user is set as last_modified_by"""
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        entity = models.Entity.objects.all()[0]
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.last_modified_by, self.user)

    def test_update_entity(self):
        """update an entity: check user is set as last_modified_by"""
        user2 = User.objects.create(username="user2", is_staff=True)
        user2.set_password("abc")
        user2.save()
        self.client.login(username="user2", password="abc")

        entity = mommy.make(models.Entity, is_single_contact=False)
        url = reverse('crm_edit_entity', args=[entity.id])
        data = {
            'name': 'Dupond SA',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        entity = models.Entity.objects.get(id=entity.id)
        self.assertEqual(entity.name, data['name'])
        self.assertEqual(entity.last_modified_by, user2)

    def test_save_no_request(self):
        """save an entity should be possible out of request"""

        entity = mommy.make(models.Entity, is_single_contact=False, name="ABC")
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.last_modified_by, None)

        entity.name = "DEF"
        entity.save()
        self.assertEqual(entity.name, "DEF")
        self.assertEqual(entity.last_modified_by, None)

    def test_create_contact(self):
        """create a contact: check user is set as last_modified_by"""
        url = reverse('crm_add_single_contact')
        data = {
            'lastname': "Doe",
            'firstname': 'John',
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        self.assertEqual(models.Contact.objects.count(), 1)
        john_doe = models.Contact.objects.all()[0]
        self.assertEqual(john_doe.lastname, "Doe")
        self.assertEqual(john_doe.firstname, "John")
        self.assertEqual(john_doe.entity.is_single_contact, True)
        self.assertEqual(john_doe.last_modified_by, self.user)

    def test_create_action(self):
        """create an action: check user is set as last_modified_by"""
        url = reverse('crm_create_action', args=[0, 0])

        data = {
            'subject': "tested", 'type': '', 'date': "2014-01-31", 'time': "11:34",
            'status': '', 'in_charge': '', 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data["subject"])
        self.assertEqual(action.last_modified_by, self.user)

