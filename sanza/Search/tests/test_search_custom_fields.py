# -*- coding: utf-8 -*-
"""miscellaneous searches"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from bs4 import BeautifulSoup as BeautifulSoup4
from datetime import date, timedelta
from unittest import skipIf

from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models, search_forms
from sanza.Crm import settings as crm_settings
from sanza.Search.tests import BaseTestCase


class SearchEntityCustomFieldsTest(BaseTestCase):
    """search on custom fields"""

    def test_search_contact(self):
        """search on custom fields values"""
        custom_field_name = search_forms.UnitTestContactCustomFieldForm.custom_field_name
        name = search_forms.UnitTestContactCustomFieldForm.name

        another_field = models.CustomField.objects.create(model=models.CustomField.MODEL_CONTACT, name="ut_another")
        entity_field = models.CustomField.objects.create(model=models.CustomField.MODEL_ENTITY, name=name)

        contact1 = mommy.make(models.Contact, lastname=u"ABCDEFGH", main_contact=True, has_left=False)
        contact1.set_custom_field(custom_field_name, "Yes")

        contact2 = mommy.make(models.Contact, lastname=u"IJKLMNOP", main_contact=True, has_left=False)
        contact2.set_custom_field(custom_field_name, "No")
        contact2.set_custom_field(another_field.name, "Yes")

        contact3 = mommy.make(models.Contact, lastname=u"QRSTUVW", main_contact=True, has_left=False)
        contact3.set_custom_field(another_field.name, "Yes")

        contact4 = mommy.make(models.Contact, lastname=u"XYZZYXWV", main_contact=True, has_left=False)
        contact4.set_custom_field(custom_field_name, "Yes!")

        contact5 = mommy.make(models.Contact, lastname=u"UTSRQPNM", main_contact=True, has_left=False)
        contact5.set_custom_field(custom_field_name, "Yes")

        contact6 = mommy.make(models.Contact, lastname=u"LKJIHGFE", main_contact=True, has_left=False)
        contact6.entity.set_custom_field(custom_field_name, "Yes")

        response = self.client.post(reverse('search'), data={"gr0-_-{0}-_-0".format(name): 'Yes'})
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)
        self.assertContains(response, contact5.lastname)
        self.assertNotContains(response, contact6.lastname)

    def test_search_entity(self):
        """search on entity custom fields values"""
        custom_field_name = search_forms.UnitTestEntityCustomFieldForm.custom_field_name
        name = search_forms.UnitTestEntityCustomFieldForm.name

        another_field = models.CustomField.objects.create(model=models.CustomField.MODEL_ENTITY, name="ut_another")
        entity_field = models.CustomField.objects.create(model=models.CustomField.MODEL_CONTACT, name=name)

        contact1 = mommy.make(models.Contact, lastname=u"ABCDEFGH", main_contact=True, has_left=False)
        contact1.entity.set_custom_field(custom_field_name, "Yes")

        contact2 = mommy.make(models.Contact, lastname=u"IJKLMNOP", main_contact=True, has_left=False)
        contact2.entity.set_custom_field(custom_field_name, "No")
        contact2.entity.set_custom_field(another_field.name, "Yes")

        contact3 = mommy.make(models.Contact, lastname=u"QRSTUVW", main_contact=True, has_left=False)
        contact3.entity.set_custom_field(another_field.name, "Yes")

        contact4 = mommy.make(models.Contact, lastname=u"XYZZYXWV", main_contact=True, has_left=False)
        contact4.entity.set_custom_field(custom_field_name, "Yes!")

        contact5 = mommy.make(models.Contact, lastname=u"UTSRQPNM", main_contact=True, has_left=False)
        contact5.entity.set_custom_field(custom_field_name, "Yes")

        contact6 = mommy.make(models.Contact, lastname=u"LKJIHGFE", main_contact=True, has_left=False)
        contact6.set_custom_field(custom_field_name, "Yes")

        response = self.client.post(reverse('search'), data={"gr0-_-{0}-_-0".format(name): 'Yes'})
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)
        self.assertContains(response, contact5.lastname)
        self.assertNotContains(response, contact6.lastname)