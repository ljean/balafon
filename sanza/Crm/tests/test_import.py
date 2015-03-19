# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.core.urlresolvers import reverse

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


class ImportTemplateTest(BaseTestCase):

    def test_template_with_custom_fields(self):

        cf1 = models.CustomField.objects.create(
            name='siret', label='SIRET', model=models.CustomField.MODEL_ENTITY, import_order=1
        )
        cf2 = models.CustomField.objects.create(name='naf', label='Code NAF', model=models.CustomField.MODEL_ENTITY)
        cf3 = models.CustomField.objects.create(
            name='zip', label='Code', model=models.CustomField.MODEL_ENTITY, import_order=3
        )

        cf4 = models.CustomField.objects.create(
            name='abc', label='ABC', model=models.CustomField.MODEL_CONTACT, import_order=2
        )
        cf5 = models.CustomField.objects.create(name='def', label='DEF', model=models.CustomField.MODEL_CONTACT
        )
        cf6 = models.CustomField.objects.create(
            name='ghi', label='GHI', model=models.CustomField.MODEL_CONTACT, import_order=4
        )

        url = reverse('crm_contacts_import_template')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], 'text/csv')

        self.assertEqual(response.content.count('\n'), 1)
        pos = response.content.find('\n')
        line = response.content[:pos]
        cols = [x.strip('"') for x in line.split(";")]

        fields = [
            'gender', 'firstname', 'lastname', 'email', 'phone', 'mobile', 'job', 'notes',
            'role', 'accept_newsletter', 'accept_3rdparty', 'entity', 'entity.type',
            'entity.description', 'entity.website', 'entity.email', 'entity.phone',
            'entity.fax', 'entity.notes', 'entity.address', 'entity.address2', 'entity.address3',
            'entity.city', 'entity.cedex', 'entity.zip_code', 'entity.country', 'address', 'address2',
            'address3', 'city', 'cedex', 'zip_code', 'country', 'entity.groups', 'groups',
        ]

        for i, field in enumerate(fields):
            self.assertEqual(cols[i], field)
        j0 = i+1

        for j, field in enumerate([cf1, cf4, cf3, cf6]):
            self.assertEqual(cols[j0+j], unicode(field))
