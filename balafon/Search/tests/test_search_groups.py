# -*- coding: utf-8 -*-
"""test we can search by groups"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class GroupSearchTest(BaseTestCase):
    """Vith the search when accessing it by the group"""

    def test_view_search(self):
        """view search"""
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_search_anonymous(self):
        """view search not logged"""
        self.client.logout()
        response = self.client.get(reverse('search'))
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_search_non_staff(self):
        """view seacrch non-staff"""
        self.user.is_staff = False
        self.user.save()
        response = self.client.get(reverse('search'))
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_view_group(self):
        """view the search_group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group = mommy.make(models.Group, name="my group")

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
        """search by group"""

        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group = mommy.make(models.Group, name="my group")
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
        """search contact by group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group = mommy.make(models.Group, name="my group")
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
        """search two groups"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.entities.add(entity1)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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
        """search two groups with contacts"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.contacts.add(contact1)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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
        """search two groups contacts and entities"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.contacts.add(contact1)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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
        """search not member of group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.entities.add(entity1)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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
        """search two groups : members and not members"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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
        """search two groups on contacts: members and not members"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.contacts.add(contact1)
        group1.contacts.add(contact2)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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
        """search two groups on entities: members and not members"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()

        group2 = mommy.make(models.Group, name="oups")
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

    def test_search_groups_absurde(self):
        """search in_group and not_in_group on same group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()

        url = reverse('search')

        data = {"gr0-_-group-_-0": group1.id, "gr0-_-not_in_group-_-1": group1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_search_groups_absurde2(self):
        """search in_group and not_in_group on same group: other order"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="my group")
        group1.entities.add(entity1)
        group1.entities.add(entity2)
        group1.save()

        url = reverse('search')

        data = {"gr0-_-not_in_group-_-0": group1.id, "gr0-_-group-_-1": group1.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_search_contact_of_group(self):
        """search contacts of group"""
        entity1 = mommy.make(models.Entity, name="My tiny corp")
        contact1 = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact3 = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="The big Org")
        contact4 = mommy.make(models.Contact, entity=entity3, lastname="ABCABC", main_contact=True, has_left=False)

        group = mommy.make(models.Group, name="my group")
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


class MultiGroupSearchTest(BaseTestCase):
    """search on multiple groups form"""

    def test_search_all_groups_only_1(self):
        """all groups: members of 1 only"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.entities.add(entity1)
        group1.save()

        url = reverse('search')
        groups = (group1.id, )
        data = {"gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_all_groups(self):
        """all groups: members of all"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.entities.add(entity1)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.entities.add(entity1)
        group2.entities.add(entity2)
        group2.save()

        url = reverse('search')
        groups = (group1.id, group2.id)
        data = {"gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_any_groups(self):
        """search member any groups"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.entities.add(entity1)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.entities.add(entity1)
        group2.entities.add(entity2)
        group2.save()

        url = reverse('search')
        groups = (group1.id, group2.id)
        data = {"gr0-_-any_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertContains(response, contact1b.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_none_groups(self):
        """search contact who are not member of given groups"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.entities.add(entity1)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.entities.add(entity1)
        group2.entities.add(entity2)
        group2.save()

        url = reverse('search')
        groups = (group1.id, group2.id)
        data = {"gr0-_-none_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact3.lastname)

    def test_search_all_groups_contact(self):
        """search member of all groups: contacts"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.contacts.add(contact1a)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.contacts.add(contact1a)
        group2.entities.add(entity2)
        group2.save()

        url = reverse('search')
        groups = (group1.id, group2.id)
        data = {"gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_any_groups_contact(self):
        """search member of any groups: contacts"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.contacts.add(contact1a)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.contacts.add(contact1a)
        group2.entities.add(entity2)
        group2.save()

        url = reverse('search')
        groups = (group1.id, group2.id)
        data = {"gr0-_-any_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_none_groups_contact(self):
        """search not member of any of the groups: contacts"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.contacts.add(contact1a)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.contacts.add(contact1a)
        group2.entities.add(entity2)
        group2.save()

        url = reverse('search')
        groups = (group1.id, group2.id)
        data = {"gr0-_-none_groups-_-0": ['{0}'.format(x) for x in groups]}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact1a.lastname)
        self.assertContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertContains(response, entity3.name)
        self.assertContains(response, contact3.lastname)

    def test_search_all_groups_no_choice(self):
        """search all_groups: no value set"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        url = reverse('search')
        data = {"gr0-_-all_groups-_-0": ''}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertNotEqual([], soup.select('.field-error'))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

    def test_search_any_groups_no_choice(self):
        """search any_groups: no value set"""

        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        url = reverse('search')
        data = {"gr0-_-any_groups-_-0": ''}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertNotEqual([], soup.select('.field-error'))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

    def test_search_any_groups_invalid_choice(self):
        """search any_groups: invalid value"""

        url = reverse('search')
        data = {"gr0-_-any_groups-_-0": 'blabla'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertNotEqual([], soup.select('.field-error'))

    def test_search_none_groups_no_choice(self):
        """search none_groups: no value set"""

        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        url = reverse('search')
        data = {"gr0-_-none_groups-_-0": ''}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertNotEqual([], soup.select('.field-error'))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

    def test_search_groups_combine_all_none(self):
        """search combining all and none"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.contacts.add(contact1a)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.contacts.add(contact1a)
        group2.entities.add(entity2)
        group2.save()

        groups = [group1.id, group2.id]

        response = self.client.post(
            reverse('search'),
            data={
                "gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups],
                "gr0-_-none_groups-_-1": ['{0}'.format(x) for x in groups],
            }
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual([], BeautifulSoup(response.content).select('.field-error'))

        self.assertNotContains(response, entity1.name)
        self.assertNotContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_groups_combine_all_any(self):
        """search combining all and any"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.contacts.add(contact1a)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.contacts.add(contact1a)
        group2.entities.add(entity2)
        group2.save()

        groups = [group1.id, group2.id]

        response = self.client.post(
            reverse('search'),
            data={
                "gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups],
                "gr0-_-any_groups-_-1": ['{0}'.format(x) for x in groups],
            }
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual([], BeautifulSoup(response.content).select('.field-error'))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)

    def test_search_groups_union_all_any(self):
        """search union of all and any"""
        entity1 = mommy.make(models.Entity, name="#Tiny corp")
        contact1a = mommy.make(models.Contact, entity=entity1, lastname="ABCD", main_contact=True, has_left=False)
        contact1b = mommy.make(models.Contact, entity=entity1, lastname="IJKL", main_contact=True, has_left=False)

        entity2 = mommy.make(models.Entity, name="#Other corp")
        contact2 = mommy.make(models.Contact, entity=entity2, lastname="WXYZ", main_contact=True, has_left=False)

        entity3 = mommy.make(models.Entity, name="#Big corp")
        contact3 = mommy.make(models.Contact, entity=entity3, lastname="XDER", main_contact=True, has_left=False)

        group1 = mommy.make(models.Group, name="#group1")
        group1.contacts.add(contact1a)
        group1.save()

        group2 = mommy.make(models.Group, name="#group2")
        group2.contacts.add(contact1a)
        group2.entities.add(entity2)
        group2.save()

        groups = [group1.id, group2.id]

        response = self.client.post(
            reverse('search'),
            data={
                "gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups],
                "gr1-_-any_groups-_-0": ['{0}'.format(x) for x in groups],
            }
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual([], BeautifulSoup(response.content).select('.field-error'))

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertNotContains(response, contact1b.lastname)

        self.assertContains(response, entity2.name)
        self.assertContains(response, contact2.lastname)

        self.assertNotContains(response, entity3.name)
        self.assertNotContains(response, contact3.lastname)


class ContactWithEmailInGroupSearchForm(BaseTestCase):
    """search on multiple groups form"""

    def test_search_all_groups_only_1(self):
        """all groups: members of 1 only"""
        entity1 = mommy.make(models.Entity, name=u"#Tiny corp")
        contact1a = mommy.make(
            models.Contact, entity=entity1, lastname=u"ABCD", main_contact=True, has_left=False, email="test1@abcd.fr"
        )
        contact1b = mommy.make(
            models.Contact, entity=entity1, lastname=u"IJKL", main_contact=True, has_left=False, email="test2@abcd.fr"
        )
        contact1c = mommy.make(
            models.Contact, entity=entity1, lastname=u"MNOP", main_contact=True, has_left=False, email="test1@abcd.fr"
        )
        contact1d = mommy.make(
            models.Contact, entity=entity1, lastname=u"QRST", main_contact=True, has_left=False, email="test3@abcd.fr"
        )

        entity2 = mommy.make(models.Entity, name=u"#Other corp")
        contact2a = mommy.make(
            models.Contact, entity=entity2, lastname=u"UVWX", main_contact=True, has_left=False, email="test1@abcd.fr"
        )
        contact2b = mommy.make(
            models.Contact, entity=entity2, lastname=u"YZAB", main_contact=True, has_left=False, email="test3@abcd.fr"
        )

        group1 = mommy.make(models.Group, name=u"#group1")
        group1.entities.add(entity1)
        group1.save()

        group2 = mommy.make(models.Group, name=u"#group2")
        group2.contacts.add(contact2a)
        group2.contacts.add(contact1b)
        group2.save()

        url = reverse('search')
        groups = (group1.id, )
        data = {'gr0-_-all_groups-_-0': [str(x) for x in groups], "gr0-_-email_in_group-_-1": group2.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, entity1.name)
        self.assertContains(response, contact1a.lastname)
        self.assertContains(response, contact1b.lastname)
        self.assertContains(response, contact1c.lastname)
        self.assertNotContains(response, contact1d.lastname)

        self.assertNotContains(response, entity2.name)
        self.assertNotContains(response, contact2a.lastname)
        self.assertNotContains(response, contact2b.lastname)
