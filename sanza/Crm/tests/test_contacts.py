# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from bs4 import BeautifulSoup

from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


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
        errors = BeautifulSoup(response.content).select('.field-error')
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
        errors = BeautifulSoup(response.content).select('.field-error')
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

        errors = BeautifulSoup(response.content).select('.field-error')
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

        errors = BeautifulSoup(response.content).select('.field-error')
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

        errors = BeautifulSoup(response.content).select('.field-error')
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


class ContactEntitiesSuggestListTestCase(BaseTestCase):

    #def setUp(self):
    #    super(ContactEntitiesSuggestListTestCase, self).setUp()

    def test_entities_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_entities')+'?term=c')
        self.assertEqual(302, response.status_code)
        #login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_contacts_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_contacts')+'?term=c')
        self.assertEqual(302, response.status_code)
        #login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

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

    def test_view_contacts_filter_by_letter(self):
        e1 = mommy.make(models.Entity, name="ABC")
        c1 = e1.default_contact
        c1.lastname = "A{0}A".format(c1.id)
        c1.save()

        e2 = mommy.make(models.Entity, is_single_contact=True, name="AFF")
        c2 = e2.default_contact
        c2.lastname = "A{0}A".format(c2.id)
        c2.save()

        e3 = mommy.make(models.Entity, name="DAA")
        c3 = e3.default_contact
        c3.lastname = "A{0}A".format(c3.id)
        c3.save()

        url = reverse('crm_view_entities_list')+"?filter=A"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, e1.name)
        self.assertContains(response, c1.lastname)
        self.assertNotContains(response, e2.name)
        self.assertContains(response, c2.lastname)
        self.assertNotContains(response, e3.name)
        self.assertNotContains(response, c3.lastname)
