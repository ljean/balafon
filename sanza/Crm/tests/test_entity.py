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


class ViewEntityTest(BaseTestCase):
    """View an entity"""

    def test_view_entity(self):
        """view entity"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        self.assertContains(response, reverse("crm_view_contact", args=[contact.id]))

    def test_view_entity_secondary_contact(self):
        """view entity with secondary contact"""
        entity = mommy.make(models.Entity)
        entity.default_contact
        contact1 = mommy.make(models.Contact, main_contact=True, entity=entity)
        contact2 = mommy.make(models.Contact, main_contact=False, entity=entity)

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        url1 = reverse("crm_view_contact", args=[contact1.id])
        url2 = reverse("crm_view_contact", args=[contact2.id])
        self.assertContains(response, url1)
        self.assertContains(response, url2)
        tag1 = BeautifulSoup(response.content).select('.ut-contact-{0.id} .ut-secondary-contact'.format(contact1))
        self.assertEqual(len(tag1), 0)
        tag2 = BeautifulSoup(response.content).select('.ut-contact-{0.id} .ut-secondary-contact'.format(contact2))
        self.assertEqual(len(tag2), 1)

    def test_view_entity_has_left_contact(self):
        """view entity with 'has left' contact"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact1 = mommy.make(models.Contact, has_left=False, entity=entity)
        contact2 = mommy.make(models.Contact, has_left=True, entity=entity)

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        url1 = reverse("crm_view_contact", args=[contact.id])
        url2 = reverse("crm_view_contact", args=[contact2.id])
        self.assertContains(response, url1)
        self.assertContains(response, url2)
        tag1 = BeautifulSoup(response.content).select('.ut-contact-{0.id} .ut-has-left'.format(contact1))
        self.assertEqual(len(tag1), 0)
        tag2 = BeautifulSoup(response.content).select('.ut-contact-{0.id} .ut-has-left'.format(contact2))
        self.assertEqual(len(tag2), 1)


class CreateEntityTest(BaseTestCase):
    """Create entities"""

    def test_view_create_entity_no_type(self):
        """view the create entity page no type"""
        url = reverse('crm_create_entity', args=[0])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

    def test_view_create_entity_with_type(self):
        """view the create entity page with type"""
        entity_type = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[entity_type.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

    def test_create_entity_no_type(self):
        """create an entity with no type"""
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        entity = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response, reverse("crm_view_entity", args=[entity.id]))
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.type, None)

    def test_create_entity_with_type(self):
        """create enity with type"""
        entity_type = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[entity_type.id])
        response = self.client.post(url, data={'name': "ABC", "type": entity_type.id})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        entity = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response, reverse("crm_view_entity", args=[entity.id]))
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.type, entity_type)

    def test_create_entity_with_type_after(self):
        """create entity and set type in form"""
        entity_type = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "type": entity_type.id})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        entity = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response, reverse("crm_view_entity", args=[entity.id]))
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.type, entity_type)

    def test_create_entity_url(self):
        """create entity with website value"""
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "website": "http://toto.fr/"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        entity = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response, reverse("crm_view_entity", args=[entity.id]))
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.website, "http://toto.fr/")

    def test_create_entity_url_no_scheme(self):
        """create an entity: no http:// in website value"""
        url = reverse('crm_create_entity', args=[0])
        response = self.client.post(url, data={'name': "ABC", "website": "toto.fr/"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 1)
        entity = models.Entity.objects.all()[0]
        self.assertContains(response, 'colorbox')
        self.assertContains(response, reverse("crm_view_entity", args=[entity.id]))
        self.assertEqual(entity.name, "ABC")
        self.assertEqual(entity.website, "http://toto.fr/")

    def test_view_create_entity_unknown_type(self):
        """view the create entity page with an unknown type id"""
        entity_type = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[2222])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

        response = self.client.post(url, data={'name': "ABC", "type": 2222})
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

        url = reverse('crm_create_entity', args=[entity_type.id])
        response = self.client.post(url, data={'name': "ABC", "type": "2222"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

    def test_view_create_entity_invalid_type(self):
        """view the create entity type with an invalid value"""
        entity_type = mommy.make(models.EntityType)
        url = reverse('crm_create_entity', args=[2222]).replace("2222", "aaa")
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

        response = self.client.post(url, data={'name': "ABC", "type": 2222})
        self.assertEqual(404, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)

        url = reverse('crm_create_entity', args=[entity_type.id])
        response = self.client.post(url, data={'name': "ABC", "type": "aaaaa"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)


class EditContactAndEntityTestCase(BaseTestCase):
    fixtures = ['zones.json', ]

    def _check_redirect_url(self, response, next_url):
        redirect_url = response.redirect_chain[-1][0]
        self.assertEqual(redirect_url, "http://testserver"+next_url)

    def test_view_edit_entity(self):
        e = mommy.make(models.Entity, is_single_contact=False)
        response = self.client.get(reverse('crm_edit_entity', args=[e.id]))
        self.assertEqual(200, response.status_code)

    def test_edit_entity(self):
        e = mommy.make(models.Entity, is_single_contact=False)
        url = reverse('crm_edit_entity', args=[e.id])
        data = {
            'name': 'Dupond SA',
            'city': models.City.objects.get(name="Paris").id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[e.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        e = models.Entity.objects.get(id=e.id)
        self.assertEqual(e.name, data['name'])
        self.assertEqual(e.city.id, data['city'])

    def test_edit_entity_keep_notes(self):
        e = mommy.make(models.Entity, is_single_contact=False, notes="Toto")
        url = reverse('crm_edit_entity', args=[e.id])
        data = {
            'name': 'Dupond SA',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[e.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        e = models.Entity.objects.get(id=e.id)
        self.assertEqual(e.name, data['name'])
        self.assertEqual(e.notes, u'Toto')

    def test_view_edit_contact(self):
        c = mommy.make(models.Contact)
        response = self.client.get(reverse('crm_edit_contact', args=[c.id]))
        self.assertEqual(200, response.status_code)

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

        soup.select(f1)[0]["checked"] # Should not raise any error
        self.assertRaises(KeyError, lambda: soup.select(f2)[0]["checked"])
        self.assertRaises(KeyError, lambda: soup.select(f3)[0]["checked"])

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

    def test_edit_contact(self):
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
