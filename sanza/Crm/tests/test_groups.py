# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


class GroupTest(BaseTestCase):
    """groups"""

    def test_view_add_group(self):
        """view add group"""
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_entity_to_group', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_view_add_contact_group(self):
        """view add group fro contact"""
        contact = mommy.make(models.Contact)
        url = reverse('crm_add_contact_to_group', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_add_group_new(self):
        """add entiyy to non-existing group"""
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
        """add contact to non existing group"""
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
        """add entity to existing group"""
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
        """add entity already in group"""

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
        """add entity to contact already in group"""

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
        """add contact: entity already in group"""
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
        """add contact to existing group"""
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
        """add contact already in group"""
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
        """view groups on contact"""

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
        """view entity with groups"""

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
        """remove contact from group"""

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
        """remove contact not in group"""

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
        """cancel remove contact from group"""

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
        """remove entity from group"""

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
        """remove entity not in group"""

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
        """cancel remove entity from group"""

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
        #login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)


class GetGroupsListTestCase(GroupSuggestListTestCase):
    view_name = 'crm_get_groups'


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