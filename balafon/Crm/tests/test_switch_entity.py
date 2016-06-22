# -*- coding: utf-8 -*-
"""unit testing"""

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


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
        soup = BeautifulSoup(response.content)
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
        soup = BeautifulSoup(response.content)
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
        city1 = mommy.make(models.City)

        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity,
            address="Abc", zip_code="42000", city=city1, phone="007")
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

        self.assertEqual(contact.address, "Abc")
        self.assertEqual(contact.zip_code, "42000")
        self.assertEqual(contact.city, city1)
        self.assertEqual(contact.phone, "007")


    def test_make_single_contact_entity(self):
        city1 = mommy.make(models.City)

        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity, lastname="Sunsun", firstname=u"John",
            address="Abc", zip_code="42000", city=city1, phone="007")

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

        self.assertEqual(contact.address, "Abc")
        self.assertEqual(contact.zip_code, "42000")
        self.assertEqual(contact.city, city1)
        self.assertEqual(contact.phone, "007")


    def test_change_to_new_entity(self):
        city1 = mommy.make(models.City)

        entity = mommy.make(models.Entity, is_single_contact=False)
        contact = mommy.make(models.Contact, entity=entity,
            address="Abc", zip_code="42000", city=city1, phone="007")

        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_CREATE_NEW_ENTITY,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertNotEqual(contact.entity, entity)
        self.assertNotEqual(contact.entity.contact_set.count(), 1)

        self.assertEqual(contact.address, "Abc")
        self.assertEqual(contact.zip_code, "42000")
        self.assertEqual(contact.city, city1)
        self.assertEqual(contact.phone, "007")

    def test_change_single_to_existing_entity(self):
        city1 = mommy.make(models.City)

        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = mommy.make(models.Contact, entity=entity,
            address="Abc", zip_code="42000", city=city1, phone="007")
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

        self.assertEqual(contact.address, "Abc")
        self.assertEqual(contact.zip_code, "42000")
        self.assertEqual(contact.city, city1)
        self.assertEqual(contact.phone, "007")

    def test_change_single_to_contact_entity(self):
        city1 = mommy.make(models.City)

        entity = mommy.make(models.Entity, is_single_contact=True)
        contact = mommy.make(models.Contact, entity=entity,
            address="Abc", zip_code="42000", city=city1, phone="007")

        url = reverse('crm_change_contact_entity', args=[contact.id])
        data= {
            'option': self.OPTION_SWITCH_ENTITY_CONTACT,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity.is_single_contact, False)

        self.assertEqual(contact.address, "Abc")
        self.assertEqual(contact.zip_code, "42000")
        self.assertEqual(contact.city, city1)
        self.assertEqual(contact.phone, "007")

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

        errors = BeautifulSoup(response.content).select('.field-error')
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

        errors = BeautifulSoup(response.content).select('.field-error')
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

        errors = BeautifulSoup(response.content).select('.field-error')
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

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.entity, entity)