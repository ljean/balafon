# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.unit_tests import response_as_json
from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class ViewEntityTest(BaseTestCase):
    """View an entity"""

    def test_view_entity(self):
        """view entity"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = entity.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        self.assertContains(response, reverse("crm_view_contact", args=[contact.id]))
        self.assertTemplateUsed(response, "balafon/bs_base.html")

    def test_preview_entity(self):
        """view entity in popup"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = entity.get_preview_url()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, entity.name)
        self.assertContains(response, reverse("crm_view_contact", args=[contact.id]))
        self.assertTemplateUsed(response, "balafon/bs_base_raw.html")

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
        self.assertEqual(response.status_code, 404)
        self.assertEqual(models.Entity.objects.count(), 0)

        response = self.client.post(url, data={'name': "ABC", "type": 2222})
        self.assertTrue(response.status_code in [404, 405])
        self.assertEqual(models.Entity.objects.count(), 0)

        url = reverse('crm_create_entity', args=[entity_type.id])
        response = self.client.post(url, data={'name': "ABC", "type": "aaaaa"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Entity.objects.count(), 0)


class EditEntityTestCase(BaseTestCase):
    """edit entity"""

    fixtures = ['zones.json', ]

    def _check_redirect_url(self, response, next_url):
        """check redirect url"""
        redirect_url = response.redirect_chain[-1][0]
        self.assertEqual(redirect_url, "http://testserver"+next_url)

    def test_view_edit_entity(self):
        """view"""
        entity = mommy.make(models.Entity, is_single_contact=False)
        response = self.client.get(reverse('crm_edit_entity', args=[entity.id]))
        self.assertEqual(200, response.status_code)

    @override_settings(BALAFON_SHOW_BILLING_ADDRESS=True)
    def test_view_edit_show_billing_address(self):
        """view edit contact form with billing address setting On"""
        entity = mommy.make(models.Entity, is_single_contact=False)
        response = self.client.get(reverse('crm_edit_entity', args=[entity.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("#id_billing_address")))

    @override_settings(BALAFON_SHOW_BILLING_ADDRESS=False)
    def test_view_edit_hide_billing_address(self):
        """view edit contact form with billing address setting Off"""
        entity = mommy.make(models.Entity, is_single_contact=False)
        response = self.client.get(reverse('crm_edit_entity', args=[entity.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select("#id_billing_address")))

    @override_settings()
    def test_default_for_show_billing_address(self):
        """Check default value for BALAFON_SHOW_BILLING_ADDRESS"""
        del settings.BALAFON_SHOW_BILLING_ADDRESS
        entity = mommy.make(models.Entity, is_single_contact=False)
        response = self.client.get(reverse('crm_edit_entity', args=[entity.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select("#id_billing_address")))

    def test_edit_entity(self):
        """edit entity"""
        entity = mommy.make(models.Entity, is_single_contact=False)
        url = reverse('crm_edit_entity', args=[entity.id])
        data = {
            'name': 'Dupond SA',
            'city': models.City.objects.get(name="Paris").id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[entity.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        entity = models.Entity.objects.get(id=entity.id)
        self.assertEqual(entity.name, data['name'])
        self.assertEqual(entity.city.id, data['city'])

    def test_edit_entity_anonymous(self):
        """it should not change if not logged"""
        self.client.logout()

        entity = mommy.make(models.Entity, is_single_contact=False)
        url = reverse('crm_edit_entity', args=[entity.id])
        data = {
            'name': 'Dupond SA',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(302, response.status_code)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        entity = models.Entity.objects.get(id=entity.id)
        self.assertNotEqual(entity.name, data['name'])

    def test_edit_entity_not_allowed(self):
        """it should not change if not allowed"""
        self.user.is_staff = False
        self.user.save()

        entity = mommy.make(models.Entity, is_single_contact=False)
        url = reverse('crm_edit_entity', args=[entity.id])
        data = {
            'name': 'Dupond SA',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(302, response.status_code)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

        entity = models.Entity.objects.get(id=entity.id)
        self.assertNotEqual(entity.name, data['name'])

    def test_edit_entity_keep_notes(self):
        """test misisng fields nor changed"""
        entity = mommy.make(models.Entity, is_single_contact=False, notes="Toto")
        url = reverse('crm_edit_entity', args=[entity.id])
        data = {
            'name': 'Dupond SA',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)
        next_url = reverse('crm_view_entity', args=[entity.id])
        self.assertContains(response, "<script>")
        self.assertContains(response, next_url)

        entity = models.Entity.objects.get(id=entity.id)
        self.assertEqual(entity.name, data['name'])
        self.assertEqual(entity.notes, 'Toto')


class GetEntityIdTestCase(BaseTestCase):
    """edit entity"""

    def test_get_entity_no_name(self):
        """raise Http404"""
        entity = mommy.make(models.Entity, is_single_contact=False, name='ABC')
        response = self.client.get(reverse('crm_get_entity_id'))
        self.assertEqual(404, response.status_code)

    def test_get_entity_name(self):
        """return id"""
        entity1 = mommy.make(models.Entity, is_single_contact=False, name='ABC')
        mommy.make(models.Entity, is_single_contact=False, name='WABC')
        response = self.client.get(reverse('crm_get_entity_id') + '?name={0}'.format(entity1.name))
        self.assertEqual(200, response.status_code)
        data = response_as_json(response)
        self.assertEqual(data['id'], entity1.id)

    def test_get_entity_missing_name(self):
        """raise Http404"""
        entity1 = mommy.make(models.Entity, is_single_contact=False, name='ABC')
        mommy.make(models.Entity, is_single_contact=False, name='WABC')
        response = self.client.get(reverse('crm_get_entity_id') + '?name={0}'.format(entity1.name + 'D'))
        self.assertEqual(404, response.status_code)

    def test_get_duplicate_entity_name(self):
        """raise Http404"""
        entity1 = mommy.make(models.Entity, is_single_contact=False, name='ABC')
        mommy.make(models.Entity, is_single_contact=False, name='ABC')
        response = self.client.get(reverse('crm_get_entity_id') + '?name={0}'.format(entity1.name))
        self.assertEqual(404, response.status_code)

