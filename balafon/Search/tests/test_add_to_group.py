# -*- coding: utf-8 -*-
"""test we cans earch contacts y group"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class AddToGroupActionTest(BaseTestCase):
    """Test the 'Add contact to group' action performed on search results"""

    def test_add_contact_to_group(self):
        """add a contact to group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

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
            "gr0-_-group-_-0": group.id,
            'add_to_group': 'add_to_group',
            'groups': [group2.id],
            'on_contact': True,
            'contacts': ";".join([str(contact.id) for contact in contacts])
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(reverse('crm_board_panel'))
        )

        group2 = models.Group.objects.get(id=group2.id)

        for contact in contacts:
            self.assertTrue(contact in group2.contacts.all())

        for entity in [entity1, entity2]:
            self.assertFalse(entity in group2.entities.all())

    def test_add_entity_to_group(self):
        """add entity to group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

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
            "gr0-_-group-_-0": group.id,
            'add_to_group': 'add_to_group',
            'groups': [group2.id],
            'on_contact': False,
            'contacts': ";".join([str(contact.id) for contact in contacts])
        }

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(reverse('crm_board_panel'))
        )

        group2 = models.Group.objects.get(id=group2.id)

        for contact in contacts:
            self.assertFalse(contact in group2.contacts.all())

        for entity in [entity1, entity2]:
            self.assertTrue(entity in group2.entities.all())
