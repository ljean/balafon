# -*- coding: utf-8 -*-
"""unit testing"""

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

import os.path
from bs4 import BeautifulSoup

from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


class ImportFileTest(BaseTestCase):
    """Import test"""
    contacts_import = None
    fixtures = ["zones.json"]

    def _get_file(self, file_name):
        """open a csv file for test"""
        full_name = os.path.normpath(os.path.dirname(__file__) + '/import_files/' + file_name)
        return open(full_name, 'rb')

    def _get_fields(self):
        """teh fields in the file"""
        return [
            'gender', 'firstname', 'lastname', 'email', 'phone', 'mobile', 'job',
            'notes', 'role',
            'accept_newsletter', 'accept_3rdparty',
            'entity', 'entity.type', 'entity.description', 'entity.website', 'entity.email',
            'entity.phone', 'entity.fax', 'entity.notes',
            'entity.address', 'entity.address2', 'entity.address3',
            'entity.city', 'entity.cedex', 'entity.zip_code', 'entity.country',
            'address', 'address2', 'address3', 'city', 'cedex', 'zip_code', 'country',
            'entity.groups', 'groups', 'favorite_language',
        ]

    def test_create_contacts_import(self, filename='contacts1.csv'):
        """test create new import from file"""
        url = reverse("crm_new_contacts_import")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        with self._get_file(filename) as the_file:

            data = {
                'import_file': the_file,
                'name': '',
                'encoding': 'utf-8',
                'separator': ';',
                'entity_type': '',
                'groups': [],
                'entity_name_from_email': False,
            }
            response = self.client.post(url, data=data)
            self.assertEqual(302, response.status_code)

            self.assertEqual(models.ContactsImport.objects.count(), 1)
            self.contacts_import = models.ContactsImport.objects.all()[0]

            expected_name = os.path.basename(the_file.name)
            expected_name = os.path.splitext(expected_name)[0]
            self.assertEqual(self.contacts_import.name, expected_name)

            next_url = reverse('crm_confirm_contacts_import', args=[self.contacts_import.id])
            self.assertRedirects(response, next_url)

    def test_create_contacts_import_with_name(self):
        """test create new import from file"""
        url = reverse("crm_new_contacts_import")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        with self._get_file('contacts1.csv') as the_file:

            data = {
                'import_file': the_file,
                'name': 'test',
                'encoding': 'utf-8',
                'separator': ';',
                'entity_type': '',
                'groups': [],
                'entity_name_from_email': False,
            }
            response = self.client.post(url, data=data)
            self.assertEqual(302, response.status_code)

            self.assertEqual(models.ContactsImport.objects.count(), 1)
            contacts_import = models.ContactsImport.objects.all()[0]
            self.assertEqual(contacts_import.name, "test")

    def test_view_confirm_import(self):
        """view confirm contact"""
        self.test_create_contacts_import("contacts1.csv")
        url = reverse('crm_confirm_contacts_import', args=[self.contacts_import.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)
        table = soup.select("table.ut-contacts")[0]
        #header + 1 contact
        self.assertEqual(len(table.select("tr")), 2)

        #1 line and 6 columns
        self.assertEqual(len(table.select("tr > td")), 11)

        self.assertEqual(table.select("tr > td")[0].text, u"Big corp")
        self.assertEqual(table.select("tr > td")[1].text, u"Corp")
        #self.assertEqual(table.select("tr > td")[2].text, _(u'Mr'))
        self.assertEqual(table.select("tr > td")[3].text, u"Doe")
        self.assertEqual(table.select("tr > td")[4].text, u"John")
        self.assertEqual(table.select("tr > td")[5].text, u'john.doe@mailinator.com')
        self.assertEqual(table.select("tr > td")[6].text, u"Paris")
        self.assertEqual(table.select("tr > td")[7].text, u"Lyon")
        self.assertEqual(
            [group.strip() for group in table.select("tr > td")[8].text.strip().split(";")],
            [u"Client", "Grand compte"]
        )
        self.assertEqual(table.select("tr > td")[9].text.strip(), u"marketing")
        self.assertEqual(table.select("tr > td")[10].text.strip(), u"Boss")

    def test_confirm_import(self):
        """view confirm contact"""
        self.test_create_contacts_import("contacts1.csv")
        url = reverse('crm_confirm_contacts_import', args=[self.contacts_import.id])

        data = {
            'import_file': '',
            'name': '',
            'encoding': 'utf-8',
            'separator': ';',
            'entity_type': '',
            'groups': [],
            'entity_name_from_email': False,
            'default_department': '',
            'create_contacts': 'yes'
        }

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, models.Contact.objects.count())
        contact = models.Contact.objects.all()[0]

        self.assertEqual(contact.entity.name, u"Big corp")
        self.assertEqual(contact.entity.type.name, u"Corp")
        self.assertEqual(contact.gender, models.Contact.GENDER_MALE)
        self.assertEqual(contact.lastname, u"Doe")
        self.assertEqual(contact.firstname, u"John")
        self.assertEqual(contact.email, u'john.doe@mailinator.com')
        self.assertEqual(contact.entity.email, u'contact@big-corp.com')
        self.assertEqual(contact.entity.city.name, u"Paris")
        self.assertEqual(contact.entity.city.parent.code, u"75")
        self.assertEqual(contact.city.name, u"Lyon")
        self.assertEqual(contact.city.parent.code, u"69")
        self.assertEqual(contact.group_set.count(), 1)
        self.assertEqual(contact.entity.group_set.count(), 2)
        self.assertEqual(contact.role.all()[0].name, "Boss")
        self.assertEqual(contact.favorite_language, "fr")

    def test_confirm_import_subscriptions(self):
        """view confirm contact"""
        self.test_create_contacts_import("contacts2.csv")
        url = reverse('crm_confirm_contacts_import', args=[self.contacts_import.id])

        subscription_types = (
            mommy.make(models.SubscriptionType), mommy.make(models.SubscriptionType),
        )

        data = {
            'import_file': '',
            'name': '',
            'encoding': 'utf-8',
            'separator': ';',
            'entity_type': '',
            'groups': [],
            'entity_name_from_email': False,
            'default_department': '',
            'create_contacts': 'yes'
        }

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(2, models.Contact.objects.count())

        contact_fr = models.Contact.objects.get(lastname="Oui")
        self.assertEqual(contact_fr.favorite_language, "fr")

        contact_en = models.Contact.objects.get(lastname="No")
        self.assertEqual(contact_en.favorite_language, "en")

        for subscription_type in subscription_types:
            self.assertEqual(
                0,
                models.Subscription.objects.filter(subscription_type=subscription_type, contact=contact_en).count()
            )

            self.assertEqual(
                1,
                models.Subscription.objects.filter(subscription_type=subscription_type, contact=contact_fr).count()
            )
            subscription = models.Subscription.objects.filter(
                subscription_type=subscription_type, contact=contact_fr
            ).all()[0]
            self.assertEqual(subscription.accept_subscription, True)

    def test_confirm_import_anonymous(self):
        """check no import if user is anonymous"""
        self.test_create_contacts_import("contacts1.csv")
        url = reverse('crm_confirm_contacts_import', args=[self.contacts_import.id])

        data = {
            'import_file': '',
            'name': '',
            'encoding': 'utf-8',
            'separator': ';',
            'entity_type': '',
            'groups': [],
            'entity_name_from_email': False,
            'default_department': '',
            'create_contacts': 'yes'
        }

        self.client.logout()
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, models.Contact.objects.count())

    def test_confirm_import_non_staff(self):
        """check no import if user is anonymous"""
        self.test_create_contacts_import("contacts1.csv")
        url = reverse('crm_confirm_contacts_import', args=[self.contacts_import.id])

        data = {
            'import_file': '',
            'name': '',
            'encoding': 'utf-8',
            'separator': ';',
            'entity_type': '',
            'groups': [],
            'entity_name_from_email': False,
            'default_department': '',
            'create_contacts': 'yes'
        }

        self.user.is_staff = False
        self.user.save()

        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, models.Contact.objects.count())


class UnsubscribeImportFileTest(BaseTestCase):
    """Import test"""
    fixtures = ["zones.json"]

    def _get_file(self, file_name):
        """open a csv file for test"""
        full_name = os.path.normpath(os.path.dirname(__file__) + '/import_files/' + file_name)
        return open(full_name, 'rb')

    def test_view_unsubscribe_contacts_import(self):
        """view page"""
        url = reverse("crm_unsubscribe_contacts_import")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_unsubscribe(self):
        """unsubscribe emails"""

        subscription_types = (
            mommy.make(models.SubscriptionType), mommy.make(models.SubscriptionType),
        )

        contacts_to_unsubscribe = [
            mommy.make(models.Contact, email="contact1@toto.fr"),
            mommy.make(models.Contact, email="contact2@toto.fr"),
            #two contacts with same address
            mommy.make(models.Contact, email="contact2@toto.fr"),
        ]

        contacts_already_unsubscribed = [
            mommy.make(models.Contact, email="contact3@toto.fr"),
        ]

        contacts_without_subscription = [
            mommy.make(models.Contact, email="contact3@toto.fr"),
        ]

        contacts_to_keep = [
            mommy.make(models.Contact, email="contact5@toto.fr"),
        ]

        contacts_not_exiting = [
            "contact6@toto.fr"
        ]

        for contact in contacts_to_unsubscribe + contacts_already_unsubscribed + contacts_to_keep:
            for subscription_type in subscription_types:
                mommy.make(
                    models.Subscription,
                    subscription_type=subscription_type,
                    contact=contact,
                    accept_subscription=(contact not in contacts_already_unsubscribed)
                )

        url = reverse("crm_unsubscribe_contacts_import")
        with self._get_file("unsubscribe.csv") as the_file:
            data = {
                'input_file': the_file,
            }
            response = self.client.post(url, data=data)
            self.assertEqual(302, response.status_code)

            for contact in contacts_to_unsubscribe + contacts_already_unsubscribed + contacts_to_keep:
                for subscription_type in subscription_types:
                    subscription = models.Subscription.objects.get(
                        subscription_type=subscription_type, contact=contact
                    )
                    self.assertEqual(
                        subscription.accept_subscription, contact in contacts_to_keep
                    )

            for contact in contacts_without_subscription:
                for subscription_type in subscription_types:
                    self.assertEqual(
                        models.Subscription.objects.filter(
                            subscription_type=subscription_type, contact=contact
                        ).count(),
                        0
                    )

            for email in contacts_not_exiting:
                self.assertEqual(0, models.Contact.objects.filter(email=email).count())

    def test_unsubscribe_not_allowed(self):
        """non staff"""

        subscription_types = (
            mommy.make(models.SubscriptionType), mommy.make(models.SubscriptionType),
        )

        contacts_to_unsubscribe = [
            mommy.make(models.Contact, email="contact1@toto.fr"),
            mommy.make(models.Contact, email="contact2@toto.fr"),
        ]

        for contact in contacts_to_unsubscribe:
            for subscription_type in subscription_types:
                mommy.make(
                    models.Subscription,
                    subscription_type=subscription_type,
                    contact=contact,
                    accept_subscription=True
                )

        self.user.is_staff = False
        self.user.save()

        url = reverse("crm_unsubscribe_contacts_import")
        with self._get_file("unsubscribe.csv") as the_file:
            data = {
                'input_file': the_file,
            }
            response = self.client.post(url, data=data)
            self.assertEqual(302, response.status_code)

            for contact in contacts_to_unsubscribe:
                for subscription_type in subscription_types:
                    subscription = models.Subscription.objects.get(subscription_type=subscription_type, contact=contact)
                    self.assertEqual(
                        subscription.accept_subscription, True
                    )

    def test_unsubscribe_anonymous(self):
        """not logged"""

        subscription_types = (
            mommy.make(models.SubscriptionType), mommy.make(models.SubscriptionType),
        )

        contacts_to_unsubscribe = [
            mommy.make(models.Contact, email="contact1@toto.fr"),
            mommy.make(models.Contact, email="contact2@toto.fr"),
        ]

        for contact in contacts_to_unsubscribe:
            for subscription_type in subscription_types:
                mommy.make(
                    models.Subscription,
                    subscription_type=subscription_type,
                    contact=contact,
                    accept_subscription=True
                )

        self.client.logout()

        url = reverse("crm_unsubscribe_contacts_import")
        with self._get_file("unsubscribe.csv") as the_file:
            data = {
                'input_file': the_file,
            }
            response = self.client.post(url, data=data)
            self.assertEqual(302, response.status_code)

            for contact in contacts_to_unsubscribe:
                for subscription_type in subscription_types:
                    subscription = models.Subscription.objects.get(subscription_type=subscription_type, contact=contact)
                    self.assertEqual(
                        subscription.accept_subscription, True
                    )

    def test_unsubscribe_invallid_file(self):
        """invalid file"""

        url = reverse("crm_unsubscribe_contacts_import")
        data = {
            'input_file': '',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("#id_input_file .label-danger")), 1)



class ImportTemplateTest(BaseTestCase):
    """Import test"""

    def test_template_with_custom_fields(self):
        """test that custom fields are part of the template"""

        custom_fields = [
            models.CustomField.objects.create(
                name='siret', label='SIRET', model=models.CustomField.MODEL_ENTITY, import_order=1
            ),
            models.CustomField.objects.create(
                name='naf', label='Code NAF', model=models.CustomField.MODEL_ENTITY
            ),
            models.CustomField.objects.create(
                name='zip', label='Code', model=models.CustomField.MODEL_ENTITY, import_order=3
            ),
            models.CustomField.objects.create(
                name='abc', label='ABC', model=models.CustomField.MODEL_CONTACT, import_order=2
            ),
            models.CustomField.objects.create(
                name='def', label='DEF', model=models.CustomField.MODEL_CONTACT
            ),
            models.CustomField.objects.create(
                name='ghi', label='GHI', model=models.CustomField.MODEL_CONTACT, import_order=4
            )
        ]

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
            'address3', 'city', 'cedex', 'zip_code', 'country', 'entity.groups', 'groups', 'favorite_language',
        ]

        for i, field in enumerate(fields):
            self.assertEqual(cols[i], field)
        start_index_for_custom_fields = len(fields)

        for j, field in enumerate([custom_fields[0], custom_fields[3], custom_fields[2], custom_fields[5]]):
            self.assertEqual(cols[start_index_for_custom_fields+j], unicode(field))

        for field in [custom_fields[1], custom_fields[4]]:
            self.assertTrue(field not in cols)
