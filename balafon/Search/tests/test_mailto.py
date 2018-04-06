# -*- coding: utf-8 -*-
"""test mailto action on search results"""

from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from model_mommy import mommy

from balafon.Crm import models

from balafon.Search.tests import BaseTestCase


class MailtoContactsTest(BaseTestCase):
    """Test Mailto Action from search results"""

    def setUp(self):
        """before each tests"""
        super(MailtoContactsTest, self).setUp()
        settings.BALAFON_MAILTO_LIMIT = 50

    def _create_contact(self, email=''):
        """create a contact"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact.lastname = 'TiniMax'
        contact.firstname = 'Boss'
        contact.email = email
        contact.main_contact = True
        contact.has_left = False
        contact.save()
        return entity, contact

    def test_mailto_no_email(self):
        """test mailto without emails"""
        entity = self._create_contact()[0]
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, _('Mailto: Error, no emails defined'))

    def test_mailto_one_email(self):
        """test mailto one email"""
        email = 'toto@mailinator.com'
        entity, contact = self._create_contact(email)
        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('mailto:') == 0)
        self.assertTrue(response['Location'].find(email) > 0)
        self.assertTrue(response['Location'].find(contact.lastname) > 0)
        self.assertTrue(response['Location'].find(contact.firstname) > 0)

    def test_mailto_one_email_bcc(self):
        """test mailto one email bcc"""
        email = 'toto@mailinator.com'
        entity, contact = self._create_contact(email)
        url = reverse('search_mailto_contacts', args=[1])
        data = {"gr0-_-entity_name-_-0": entity.name}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('mailto:') == 0)
        self.assertTrue(response['Location'].find(email) > 0)
        self.assertTrue(response['Location'].find(contact.lastname) > 0)
        self.assertTrue(response['Location'].find(contact.firstname) > 0)

    def test_mailto_several_emails(self):
        """test mailto several emails"""
        group = mommy.make(models.Group)
        contacts = []
        for i in range(50):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()

        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('mailto:') == 0)
        for contact in contacts:
            self.assertTrue(response['Location'].find(contact.email) > 0)
            self.assertTrue(response['Location'].find(contact.lastname) > 0)
            self.assertTrue(response['Location'].find(contact.firstname) > 0)

    def test_more_than_limit_text(self):
        """mailto sevaral emails more than limit: text mode"""
        group = mommy.make(models.Group)
        settings.BALAFON_MAILTO_LIMIT_AS_TEXT = True
        contacts = []
        for i in range(settings.BALAFON_MAILTO_LIMIT + 1):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()

        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        content = response.content.decode('utf-8')
        for contact in contacts:
            self.assertTrue(content.find(contact.email) > 0)
            self.assertTrue(content.find(contact.lastname) > 0)
            self.assertTrue(content.find(contact.firstname) > 0)

    def test_more_than_limit_clicks(self):
        """mailto sevaral emails more than limit: click mode """
        group = mommy.make(models.Group)
        settings.BALAFON_MAILTO_LIMIT_AS_TEXT = False
        contacts = []
        for i in range(settings.BALAFON_MAILTO_LIMIT * 2):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()

        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        content = response.content.decode('utf-8')
        self.assertEqual(2, content.count('class="email-group"'))

    def test_more_than_limit_clicks_not_exact(self):
        """mailto more than limit with not full groups"""
        group = mommy.make(models.Group)
        settings.BALAFON_MAILTO_LIMIT_AS_TEXT = False
        contacts = []
        for i in range(settings.BALAFON_MAILTO_LIMIT + 1):
            email = 'toto{0}@mailinator.com'.format(i)
            entity, contact = self._create_contact(email)
            contacts.append(contact)
            group.entities.add(entity)
        group.save()

        url = reverse('search_mailto_contacts', args=[0])
        data = {"gr0-_-group-_-0": group.id}
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        content = response.content.decode('utf-8')
        self.assertEqual(2, content.count('class="email-group"'))

    def test_get_mailto(self):
        """GET request on mailto action url"""
        url = reverse('search_mailto_contacts', args=[0])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
