# -*- coding: utf-8 -*-
"""test we can search contacts by action"""

from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


@override_settings(BALAFON_LABELS_PDF_TEMPLATES=None)
class PrintLabelsPdfTest(BaseTestCase):
    """create actions from results"""

    def test_view_print_labels_pdf(self):
        """test GET on url"""
        url = reverse('search_print_labels_pdf')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_view_form(self):
        """test view crete action form"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        url = reverse('search_print_labels_pdf')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        id_contacts = soup.select('input#id_contacts')
        self.assertEqual(1, len(id_contacts))
        self.assertEqual(
            sorted([int(x) for x in id_contacts[0]['value'].split(';')]),
            sorted([contact1.id, contact2.id])
        )

        id_start_at = soup.select('input#id_start_at')
        self.assertEqual(1, len(id_start_at))
        self.assertEqual('0', id_start_at[0]['value'])

        id_search_dict = soup.select('input#id_search_dict')
        self.assertEqual(1, len(id_search_dict))
        self.assertEqual('{"gr0": [{"group": "' + str(group.id) + '"}]}', id_search_dict[0]['value'])

        id_template = soup.select('select#id_template')
        self.assertEqual(1, len(id_template))
        self.assertEqual(4, len(id_template[0].select('option')))

    def test_view_form_not_logged(self):
        """test view form is not logged"""
        self.client.logout()

        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        entity2 = mommy.make(models.Entity, name=u"Other corp")

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        url = reverse('search_print_labels_pdf')

        data = {"gr0-_-group-_-0": group.id}

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    @skipIf(getattr(settings, 'SKIP_PDF_UNITTESTS', False), 'PDF disabled')
    def test_post_print_labels_pdf(self):
        """test create actions for contact"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name=u"Big corp")
        contact3 = entity3.default_contact

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        data = {
            'contacts': u";".join([unicode(i) for i in (contact1.id, contact2.id)]),
            'start_at': '0',
            'template': 'pdf/labels_24.html',
            'print_labels_pdf': 'Generate',
            'search_dict': '{"gr0": [{"group": "' + str(group.id) + '"}]}',
        }

        url = reverse('search_print_labels_pdf')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    @skipIf(getattr(settings, 'SKIP_PDF_UNITTESTS', False), 'PDF disabled')
    def test_post_print_labels_pdf_start_at(self):
        """test create actions for contact"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact
        entity3 = mommy.make(models.Entity, name=u"Big corp")
        contact3 = entity3.default_contact

        group = mommy.make(models.Group, name=u"my group")
        group.entities.add(entity1, entity2)
        group.save()

        data = {
            'contacts': u";".join([unicode(i) for i in (contact1.id, contact2.id)]),
            'start_at': '3',
            'template': 'pdf/labels_24.html',
            'print_labels_pdf': 'Generate',
            'search_dict': '{"gr0": [{"group": "' + str(group.id) + '"}]}',
        }

        url = reverse('search_print_labels_pdf')
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_post_print_anonymous(self):
        """test can't create actions for contact if not logged"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact

        self.client.logout()

        data = {
            'contacts': u";".join([unicode(i) for i in (contact1.id, contact2.id)]),
            'start_at': 0,
            'template': 'pdf/labels_24.html',
            'print_labels_pdf': 'Generate',

        }

        url = reverse('search_print_labels_pdf')
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_post_print_not_staff(self):
        """test can't create actions for contact if not in staff"""
        entity1 = mommy.make(models.Entity, name=u"My tiny corp")
        contact1 = entity1.default_contact
        entity2 = mommy.make(models.Entity, name=u"Other corp")
        contact2 = entity2.default_contact

        self.user.is_staff = False
        self.user.save()

        data = {
            'contacts': u";".join([unicode(i) for i in (contact1.id, contact2.id)]),
            'start_at': 0,
            'template': 'pdf/labels_24.html',
            'print_labels_pdf': 'Generate',
        }

        url = reverse('search_print_labels_pdf')
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)
        # login url without lang prefix
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)
