# -*- coding: utf-8 -*-
"""unit testing"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class ViewContactTest(BaseTestCase):
    """It should display contact info"""

    def test_view_entity(self):
        """view contact"""
        contact = mommy.make(models.Contact)
        url = contact.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact.lastname)
        self.assertTemplateUsed(response, "balafon/bs_base.html")

    def test_preview_entity(self):
        """view contact in popup"""
        contact = mommy.make(models.Contact)
        url = contact.get_preview_url()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, contact.lastname)
        self.assertTemplateUsed(response, "balafon/bs_base_raw.html")


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
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("select#id_same_as_suggestions")))

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

    def test_entities_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_entities')+'?term=c')
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_contacts_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('crm_get_contacts')+'?term=c')
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

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


class ContactViewUrlTest(BaseTestCase):
    """Test the get_view_url method of contact"""

    def test_view_single_contact_url(self):
        """test get_view_url for single_contact"""

        site = Site.objects.get_current()
        entity = mommy.make(models.Entity, type=None, is_single_contact=True)
        self.assertEqual(
            entity.default_contact.get_view_url(),
            "//{0}{1}".format(site.domain, reverse('crm_view_entity', args=[entity.id]))
        )

    def test_view_entity_contact_url(self):
        """test get_view_url for entity contacts"""

        site = Site.objects.get_current()
        entity = mommy.make(models.Entity, type=None, is_single_contact=False)
        self.assertEqual(
            entity.default_contact.get_view_url(),
            "//{0}{1}".format(site.domain, reverse('crm_view_contact', args=[entity.default_contact.id]))
        )


class EditContactTest(BaseTestCase):
    """It should be possible to edit a contact"""
    fixtures = ['zones.json', ]

    def test_view_edit_contact(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact, lastname='ABCD')
        url = reverse('crm_edit_contact', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("input#id_same_as_suggestions")))

    @override_settings(BALAFON_SHOW_BILLING_ADDRESS=True)
    def test_view_edit_contact_show_billing_address(self):
        """view edit contact form with billing address setting On"""
        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("#id_billing_address")))

    @override_settings(BALAFON_SHOW_BILLING_ADDRESS=False)
    def test_view_edit_contact_hide_billing_address(self):
        """view edit contact form with billing address setting Off"""
        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select("#id_billing_address")))

    @override_settings()
    def test_default_for_show_billing_address(self):
        """Check default value for BALAFON_SHOW_BILLING_ADDRESS"""
        del settings.BALAFON_SHOW_BILLING_ADDRESS
        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("#id_billing_address")))

    def test_edit_contact(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        contact = models.Contact.objects.get(id=contact.id)

        for field in ('lastname', 'firstname'):
            self.assertEqual(getattr(contact, field), data[field])

    def test_edit_contact_anonymous(self):
        """view edit contact form"""
        self.client.logout()

        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        contact = models.Contact.objects.get(id=contact.id)

        for field in ('lastname', 'firstname'):
            self.assertNotEqual(getattr(contact, field), data[field])

    def test_edit_contact_not_allowed(self):
        """view edit contact form"""
        self.user.is_staff = False
        self.user.save()

        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
        }
        response = self.client.post(url, data=data)

        self.assertEqual(302, response.status_code)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        contact = models.Contact.objects.get(id=contact.id)

        for field in ('lastname', 'firstname'):
            self.assertNotEqual(getattr(contact, field), data[field])

    def test_edit_contact_address(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'email': 'contact@test.fr',
            'phone': '0406060606',
            'mobile': '0406060606',
            'address': '1 rue Dupond',
            'zip_code': '42810',
            'city': "Rozier",
            'country': '',
            'billing_address': '3 rue bbb',
            'billing_zip_code': '42110',
            'billing_city': "Feurs",
            'billing_country': '',
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)

        contact = models.Contact.objects.get(id=contact.id)

        field_names = (
            'lastname', 'firstname', 'email', 'mobile', 'phone', 'address', 'billing_address', 'zip_code',
            'billing_zip_code',
        )

        for field in field_names:
            self.assertEqual(getattr(contact, field), data[field])

        self.assertEqual(contact.city.name, data['city'])
        self.assertEqual(contact.billing_city.name, data['billing_city'])

    def test_edit_contact_city(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': models.City.objects.get(name="Paris").id,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.id, data['city'])

    def test_edit_contact_keep_note(self):
        c = mommy.make(models.Contact, notes="Toto")
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.notes, "Toto")

    def test_edit_contact_utf(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': u'Mémé',
            'firstname': u'Pépé',
            "email": u"pepe@mémé.fr"
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.email, data['email'])

    def test_edit_contact_utf2(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': u'Mémé',
            'firstname': u'Pépé',
            "email": u"pépé@mémé.fr"
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        c = models.Contact.objects.get(id=c.id)
        self.assertNotEqual(c.lastname, data['lastname'])
        self.assertNotEqual(c.firstname, data['firstname'])
        self.assertNotEqual(c.email, data['email'])

    @override_settings(SECRET_KEY=u"super-héros")
    def test_create_contact_uuid(self):
        data = {
            'lastname': u'Mémé',
            'firstname': u'Pépé',
            "email": u"pepe@mémé.fr"
        }
        c = mommy.make(models.Contact, **data)

        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.email, data['email'])

    def test_edit_contact_unknown_city(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': "ImagineCity",
            'zip_code': "42999",
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.name, data['city'])

    def test_edit_contact_unknown_city_no_zipcode(self):
        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': "ImagineCity",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(response.redirect_chain), 0)

        c = models.Contact.objects.get(id=c.id)
        self.assertNotEqual(c.lastname, data['lastname'])
        self.assertNotEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city, None)


class EditContactSameAsTest(BaseTestCase):
    """It should be possible to edit a contact"""
    fixtures = ['zones.json', ]

    def test_view_edit_contact_with_email(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact, lastname='', firstname='', email='contact@company.com')
        url = reverse('crm_edit_contact', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("input#id_same_as_suggestions")))

    def test_view_edit_contact_unknown(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("select#id_same_as_suggestions")))

    def test_view_add_contact_with_email(self):
        """view edit contact form"""
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_contact', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("select#id_same_as_suggestions")))

    def test_edit_contact_same_as(self):
        """view edit contact form"""
        same_contact = mommy.make(models.Contact, lastname='Dupond', firstname='Paul', email='contact@abc.fr')
        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': same_contact.lastname.upper(),
            'firstname': same_contact.firstname,
            'email': 'contact@def.fr',
            'same_as_suggestions': same_contact.id
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        contact = models.Contact.objects.get(id=contact.id)
        same_contact = models.Contact.objects.get(id=same_contact.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertEqual(getattr(contact, field), data[field])

        self.assertNotEqual(contact.same_as, None)
        self.assertEqual(same_contact.same_as, contact.same_as)
        self.assertEqual(same_contact.same_as_priority, 1)
        self.assertEqual(contact.same_as_priority, 2)

    def test_edit_contact_same_as_email(self):
        """view edit contact form"""
        same_contact = mommy.make(models.Contact, lastname='Dupond', firstname='Paul', email='contact@abc.fr')
        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': 'Durand',
            'firstname': 'Pierre',
            'email': same_contact.email,
            'same_as_suggestions': same_contact.id
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        contact = models.Contact.objects.get(id=contact.id)
        same_contact = models.Contact.objects.get(id=same_contact.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertEqual(getattr(contact, field), data[field])

        self.assertNotEqual(contact.same_as, None)
        self.assertEqual(same_contact.same_as, contact.same_as)
        self.assertEqual(same_contact.same_as_priority, 1)
        self.assertEqual(contact.same_as_priority, 2)

    def test_edit_contact_same_as_existing(self):
        """view edit contact form"""
        same_as = mommy.make(models.SameAs)
        same_contact1 = mommy.make(
            models.Contact, lastname='Dupond', firstname='Paul', email='contact@abc.fr',
            same_as=same_as, same_as_priority=1
        )
        same_contact2 = mommy.make(
            models.Contact, lastname='Dupond', firstname='Paul', same_as=same_as, same_as_priority=2
        )

        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': same_contact1.lastname,
            'firstname': same_contact1.firstname,
            'email': 'contact@def.fr',
            'same_as_suggestions': same_contact1.id
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        contact = models.Contact.objects.get(id=contact.id)
        same_contact1 = models.Contact.objects.get(id=same_contact1.id)
        same_contact2 = models.Contact.objects.get(id=same_contact2.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertEqual(getattr(contact, field), data[field])

        self.assertEqual(contact.same_as, same_as)
        self.assertEqual(same_contact1.same_as, same_as)
        self.assertEqual(same_contact2.same_as, same_as)
        self.assertEqual(same_contact1.same_as_priority, 1)
        self.assertEqual(same_contact2.same_as_priority, 2)
        self.assertEqual(contact.same_as_priority, 3)

    def test_edit_contact_invalid(self):
        """view edit contact form"""
        same_contact = mommy.make(models.Contact, lastname=u'Dupond', firstname=u'Paul', email=u'contact@abc.fr')

        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': u'Durand',
            'firstname': u'Pierre',
            'email': u'contact@def.fr',
            'same_as_suggestions': same_contact.id
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        contact = models.Contact.objects.get(id=contact.id)
        same_contact = models.Contact.objects.get(id=same_contact.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertNotEqual(getattr(contact, field), data[field])

        self.assertEqual(contact.same_as, None)
        self.assertEqual(contact.same_as_priority, 0)
        self.assertEqual(same_contact.same_as, None)
        self.assertEqual(same_contact.same_as_priority, 0)

    def test_edit_contact_invalid2(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': u'Durand',
            'firstname': u'Pierre',
            'email': u'contact@def.fr',
            'same_as_suggestions': "hjkhk"
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        contact = models.Contact.objects.get(id=contact.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertNotEqual(getattr(contact, field), data[field])

        self.assertEqual(contact.same_as, None)
        self.assertEqual(contact.same_as_priority, 0)

    def test_edit_contact_invalid3(self):
        """view edit contact form"""
        contact = mommy.make(models.Contact, lastname='', firstname='', email='')
        url = reverse('crm_edit_contact', args=[contact.id])

        data = {
            'lastname': u'Durand',
            'firstname': u'Pierre',
            'email': u'contact@def.fr',
            'same_as_suggestions': contact.id + 1
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        contact = models.Contact.objects.get(id=contact.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertNotEqual(getattr(contact, field), data[field])

        self.assertEqual(contact.same_as, None)
        self.assertEqual(contact.same_as_priority, 0)

    def test_add_contact_same_as(self):
        """view edit contact form"""
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_contact', args=[entity.id])

        same_contact = mommy.make(models.Contact, lastname='Dupond', firstname='Paul', email='contact@abc.fr')

        data = {
            'lastname': same_contact.lastname.upper(),
            'firstname': same_contact.firstname,
            'email': 'contact@def.fr',
            'same_as_suggestions': same_contact.id
        }
        response = self.client.post(url, data=data)

        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        contact = models.Contact.objects.get(entity=entity.id, lastname=data['lastname'])
        same_contact = models.Contact.objects.get(id=same_contact.id)

        for field in ('lastname', 'firstname', 'email'):
            self.assertEqual(getattr(contact, field), data[field])

        self.assertNotEqual(contact.same_as, None)
        self.assertEqual(same_contact.same_as, contact.same_as)
        self.assertEqual(same_contact.same_as_priority, 1)
        self.assertEqual(contact.same_as_priority, 2)

    def test_add_single_contact_same_as(self):
        """view edit contact form"""
        same_contact = mommy.make(models.Contact, lastname='Dupond', firstname='Paul', email='contact@abc.fr')
        url = reverse('crm_add_single_contact')

        data = {
            'lastname': same_contact.lastname.upper(),
            'firstname': same_contact.firstname,
            'email': 'contact@def.fr',
            'same_as_suggestions': same_contact.id
        }
        response = self.client.post(url, data=data)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        self.assertEqual(200, response.status_code)
        same_contact = models.Contact.objects.get(id=same_contact.id)
        contact = models.Contact.objects.get(lastname=data['lastname'])

        for field in ('lastname', 'firstname', 'email'):
            self.assertEqual(getattr(contact, field), data[field])

        self.assertNotEqual(contact.same_as, None)
        self.assertEqual(same_contact.same_as, contact.same_as)
        self.assertEqual(same_contact.same_as_priority, 1)
        self.assertEqual(contact.same_as_priority, 2)


class EditContactSubscriptionTest(BaseTestCase):
    """It should be possible to edit a contact"""
    fixtures = ['zones.json', ]

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=False)
    def test_add_contact_subscription_set(self):
        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)

        url = reverse('crm_add_single_contact')
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'subscription_{0}'.format(st1.id): True,
            'subscription_{0}'.format(st2.id): False,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        c = models.Contact.objects.get(lastname=data['lastname'], firstname=data['firstname'])
        self.assertEqual(models.Subscription.objects.get(subscription_type=st1, contact=c).accept_subscription, True)
        self.assertEqual(models.Subscription.objects.filter(subscription_type=st2, contact=c).count(), 0)

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=False)
    def test_view_edit_contact_subscriptions(self):
        c = mommy.make(models.Contact)
        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)
        st3 = mommy.make(models.SubscriptionType)

        s1 = models.Subscription.objects.create(subscription_type=st1, contact=c, accept_subscription=True)
        s2 = models.Subscription.objects.create(subscription_type=st2, contact=c, accept_subscription=False)

        response = self.client.get(reverse('crm_edit_contact', args=[c.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        f1, f2, f3 = '#id_subscription_{0}'.format(st1.id), '#id_subscription_{0}'.format(st2.id), '#id_subscription_{0}'.format(st3.id)

        self.assertEqual(1, len(soup.select(f1)))
        self.assertEqual(1, len(soup.select(f2)))
        self.assertEqual(1, len(soup.select(f3)))

        soup.select(f1)[0]["checked"]  # Should not raise any error
        self.assertRaises(KeyError, lambda: soup.select(f2)[0]["checked"])
        self.assertRaises(KeyError, lambda: soup.select(f3)[0]["checked"])

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=True)
    def test_view_edit_contact_subscriptions_default_set(self):
        c = mommy.make(models.Contact)
        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)
        st3 = mommy.make(models.SubscriptionType)

        s1 = models.Subscription.objects.create(subscription_type=st1, contact=c, accept_subscription=True)
        s2 = models.Subscription.objects.create(subscription_type=st2, contact=c, accept_subscription=False)

        response = self.client.get(reverse('crm_edit_contact', args=[c.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        f1, f2, f3 = '#id_subscription_{0}'.format(st1.id), '#id_subscription_{0}'.format(st2.id), '#id_subscription_{0}'.format(st3.id)

        self.assertEqual(1, len(soup.select(f1)))
        self.assertEqual(1, len(soup.select(f2)))
        self.assertEqual(1, len(soup.select(f3)))

        soup.select(f1)[0]["checked"]
        self.assertRaises(KeyError, lambda: soup.select(f2)[0]["checked"])
        soup.select(f3)[0]["checked"]

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=False)
    def test_view_add_contact_subscriptions(self):
        entity = mommy.make(models.Entity)

        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)
        st3 = mommy.make(models.SubscriptionType)

        response = self.client.get(reverse('crm_add_contact', args=[entity.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        f1, f2, f3 = '#id_subscription_{0}'.format(st1.id), '#id_subscription_{0}'.format(st2.id), '#id_subscription_{0}'.format(st3.id)

        self.assertEqual(1, len(soup.select(f1)))
        self.assertEqual(1, len(soup.select(f2)))
        self.assertEqual(1, len(soup.select(f3)))

        #Is not checked
        self.assertRaises(KeyError, lambda: soup.select(f1)[0]["checked"])
        self.assertRaises(KeyError, lambda: soup.select(f2)[0]["checked"])
        self.assertRaises(KeyError, lambda: soup.select(f3)[0]["checked"])

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=False)
    def test_view_add_single_contact_subscriptions(self):
        entity = mommy.make(models.Entity)

        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)
        st3 = mommy.make(models.SubscriptionType)

        response = self.client.get(reverse('crm_add_single_contact'))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        f1, f2, f3 = '#id_subscription_{0}'.format(st1.id), '#id_subscription_{0}'.format(st2.id), '#id_subscription_{0}'.format(st3.id)

        self.assertEqual(1, len(soup.select(f1)))
        self.assertEqual(1, len(soup.select(f2)))
        self.assertEqual(1, len(soup.select(f3)))

        #Is not checked
        self.assertRaises(KeyError, lambda: soup.select(f1)[0]["checked"])
        self.assertRaises(KeyError, lambda: soup.select(f2)[0]["checked"])
        self.assertRaises(KeyError, lambda: soup.select(f3)[0]["checked"])

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=True)
    def test_view_add_contact_subscriptions_default_set(self):
        entity = mommy.make(models.Entity)

        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)
        st3 = mommy.make(models.SubscriptionType)

        response = self.client.get(reverse('crm_add_contact', args=[entity.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        f1, f2, f3 = '#id_subscription_{0}'.format(st1.id), '#id_subscription_{0}'.format(st2.id), '#id_subscription_{0}'.format(st3.id)

        self.assertEqual(1, len(soup.select(f1)))
        self.assertEqual(1, len(soup.select(f2)))
        self.assertEqual(1, len(soup.select(f3)))

        #Is checked
        soup.select(f1)[0]["checked"]
        soup.select(f2)[0]["checked"]
        soup.select(f3)[0]["checked"]

    @override_settings(BALAFON_SUBSCRIPTION_DEFAULT_VALUE=True)
    def test_view_add_single_contact_subscriptions_default_set(self):
        entity = mommy.make(models.Entity)

        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)
        st3 = mommy.make(models.SubscriptionType)

        response = self.client.get(reverse('crm_add_single_contact'))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        f1, f2, f3 = '#id_subscription_{0}'.format(st1.id), '#id_subscription_{0}'.format(st2.id), '#id_subscription_{0}'.format(st3.id)

        self.assertEqual(1, len(soup.select(f1)))
        self.assertEqual(1, len(soup.select(f2)))
        self.assertEqual(1, len(soup.select(f3)))

        #Is checked
        soup.select(f1)[0]["checked"]
        soup.select(f2)[0]["checked"]
        soup.select(f3)[0]["checked"]

    def test_add_contact_subscription_set(self):
        entity = mommy.make(models.Entity)

        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)

        c = mommy.make(models.Contact)
        url = reverse('crm_add_contact', args=[entity.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'subscription_{0}'.format(st1.id): True,
            'subscription_{0}'.format(st2.id): False,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[entity.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        c = models.Contact.objects.get(lastname=data['lastname'], firstname=data['firstname'], entity=entity)
        self.assertEqual(models.Subscription.objects.get(subscription_type=st1, contact=c).accept_subscription, True)
        self.assertEqual(models.Subscription.objects.filter(subscription_type=st2, contact=c).count(), 0)

    def test_add_single_contact_subscription_set(self):

        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)

        c = mommy.make(models.Contact)
        url = reverse('crm_add_single_contact')
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'subscription_{0}'.format(st1.id): True,
            'subscription_{0}'.format(st2.id): False,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        self.assertContains(response, "<script>")

        c = models.Contact.objects.get(
            lastname=data['lastname'], firstname=data['firstname'], entity__is_single_contact=True
        )
        self.assertEqual(models.Subscription.objects.get(subscription_type=st1, contact=c).accept_subscription, True)
        self.assertEqual(models.Subscription.objects.filter(subscription_type=st2, contact=c).count(), 0)

    def test_edit_contact_subscription_not_set(self):
        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)

        c = mommy.make(models.Contact)
        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': models.City.objects.get(name="Paris").id,
            'subscription_{0}'.format(st1.id): True,
            'subscription_{0}'.format(st2.id): False,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.id, data['city'])
        self.assertEqual(models.Subscription.objects.get(subscription_type=st1, contact=c).accept_subscription, True)
        self.assertEqual(models.Subscription.objects.filter(subscription_type=st2, contact=c).count(), 0)

    def test_edit_contact_subscription_set(self):
        st1 = mommy.make(models.SubscriptionType)
        st2 = mommy.make(models.SubscriptionType)

        c = mommy.make(models.Contact)

        s1 = models.Subscription.objects.create(subscription_type=st1, contact=c, accept_subscription=False)
        s2 = models.Subscription.objects.create(subscription_type=st2, contact=c, accept_subscription=False)

        url = reverse('crm_edit_contact', args=[c.id])
        data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'city': models.City.objects.get(name="Paris").id,
            'subscription_{0}'.format(st1.id): True,
            'subscription_{0}'.format(st2.id): False,
        }
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_contact', args=[c.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        c = models.Contact.objects.get(id=c.id)
        self.assertEqual(c.lastname, data['lastname'])
        self.assertEqual(c.firstname, data['firstname'])
        self.assertEqual(c.city.id, data['city'])
        self.assertEqual(models.Subscription.objects.get(subscription_type=st1, contact=c).accept_subscription, True)
        self.assertEqual(models.Subscription.objects.get(subscription_type=st2, contact=c).accept_subscription, False)
