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


class CustomFieldTest(BaseTestCase):
    """custom fields"""

    def test_entity_custom_field(self):
        """entity coustom field"""
        entity = mommy.make(models.Entity)
        cfv = models.CustomField.objects.create(name='siret', label='SIRET', model=models.CustomField.MODEL_ENTITY)
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        data = {'siret': '555444333222111'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(entity.custom_field_siret, data['siret'])

    def test_entity_custom_two_fields(self):
        """entity with 2 custom fields"""
        entity = mommy.make(models.Entity)
        cfv1 = models.CustomField.objects.create(name='siret', label='SIRET', model=models.CustomField.MODEL_ENTITY)
        cfv2 = models.CustomField.objects.create(name='naf', label='Code NAF', model=models.CustomField.MODEL_ENTITY)
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        data = {'siret': '555444333222111', 'naf': '56789'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(entity.custom_field_siret, data['siret'])
        self.assertEqual(entity.custom_field_naf, data['naf'])

    def test_contact_custom_field(self):
        """contact custom field"""
        contact = mommy.make(models.Contact)
        cfv = models.CustomField.objects.create(name='insee', label='INSEE', model=models.CustomField.MODEL_CONTACT)
        url = reverse('crm_edit_custom_fields', args=['contact', contact.id])
        data = {'insee': '1234567890'}
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(contact.custom_field_insee, data['insee'])

    def test_view_entity(self):
        """view entity with custom fields"""
        entity = mommy.make(models.Entity)
        cf1 = models.CustomField.objects.create(name='siret', label='SIRET', model=models.CustomField.MODEL_ENTITY)
        cf2 = models.CustomField.objects.create(name='naf', label='Code NAF', model=models.CustomField.MODEL_ENTITY)

        response = self.client.get(entity.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        data = {'siret': '555444333222111', 'naf': '56789'}
        cfv1 = models.EntityCustomFieldValue.objects.create(custom_field=cf1, entity=entity, value=data['siret'])
        cfv2 = models.EntityCustomFieldValue.objects.create(custom_field=cf2, entity=entity, value=data['naf'])

        response = self.client.get(entity.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['siret'])
        self.assertContains(response, data['naf'])

    def test_custom_field_ordering(self):
        """view ordered custom fields"""
        entity = mommy.make(models.Entity)
        cf1 = models.CustomField.objects.create(name='no_siret', label='SIRET', model=models.CustomField.MODEL_ENTITY, ordering=2)
        cf2 = models.CustomField.objects.create(name='code_naf', label='Code NAF', model=models.CustomField.MODEL_ENTITY, ordering=1)
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        pos_siret = response.content.find('no_siret')
        pos_naf = response.content.find('code_naf')
        self.assertTrue(pos_naf < pos_siret)

        cfv1 = models.EntityCustomFieldValue.objects.create(custom_field=cf1, entity=entity, value='1234567890')
        cfv2 = models.EntityCustomFieldValue.objects.create(custom_field=cf2, entity=entity, value='995588')

        response = self.client.get(entity.get_absolute_url())
        pos_siret = response.content.find('SIRET')
        pos_naf = response.content.find('Code NAF')
        self.assertTrue(pos_naf < pos_siret)

    def test_custom_field_visibility(self):
        """custom field visibility"""
        entity = mommy.make(models.Entity)
        cf1 = models.CustomField.objects.create(name='no_siret', label='SIRET', model=models.CustomField.MODEL_ENTITY, ordering=2)

        response = self.client.get(entity.get_absolute_url())
        pos_siret = response.content.find('SIRET')
        self.assertNotContains(response, 'SIRET')

        cfv1 = models.EntityCustomFieldValue.objects.create(custom_field=cf1, entity=entity, value='1234567890')

        response = self.client.get(entity.get_absolute_url())
        self.assertContains(response, 'SIRET')
        self.assertContains(response, '1234567890')

    def test_custom_field_widget(self):
        """widget"""
        entity = mommy.make(models.Entity)
        cfv1 = models.CustomField.objects.create(
            name='date_b', label='Date', model=models.CustomField.MODEL_ENTITY, widget="datepicker"
        )
        url = reverse('crm_edit_custom_fields', args=['entity', entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="datepicker"')

    def test_contact_get_custom_field(self):
        """conatct custom fields"""
        contact = mommy.make(models.Contact)

        cf_c = models.CustomField.objects.create(
            name='id_poste', label='Id Poste', model=models.CustomField.MODEL_CONTACT)

        cf_e = models.CustomField.objects.create(
            name='id_poste', label='Id Poste', model=models.CustomField.MODEL_ENTITY)

        contact1 = mommy.make(models.Contact)
        models.EntityCustomFieldValue.objects.create(custom_field=cf_e, entity=contact1.entity, value='111')

        contact2 = mommy.make(models.Contact)
        models.ContactCustomFieldValue.objects.create(custom_field=cf_c, contact=contact2, value='222')

        contact3 = mommy.make(models.Contact)
        models.ContactCustomFieldValue.objects.create(custom_field=cf_c, contact=contact3, value='333')
        models.EntityCustomFieldValue.objects.create(custom_field=cf_e, entity=contact3.entity, value='444')

        contact4 = mommy.make(models.Contact)

        self.assertEqual(contact1.get_custom_field_id_poste, '111')
        self.assertEqual(contact2.get_custom_field_id_poste, '222')
        self.assertEqual(contact3.get_custom_field_id_poste, '333')
        self.assertEqual(contact4.get_custom_field_id_poste, '')

    def test_contact_missing_custom_field(self):
        """contact custom fields missing"""
        contact = mommy.make(models.Contact)

        contact_custom_field_toto = lambda: contact.custom_field_toto
        self.assertRaises(models.CustomField.DoesNotExist, contact_custom_field_toto)

        entity_custom_field_toto = lambda: contact.entity.custom_field_toto
        self.assertRaises(models.CustomField.DoesNotExist, entity_custom_field_toto)
