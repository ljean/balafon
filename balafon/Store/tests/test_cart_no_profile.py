# -*- coding: utf-8 -*-
"""unit testing"""

from datetime import datetime
import logging

from django.conf import settings
from django.core import mail
from django.test.utils import override_settings
from django.urls import reverse

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from balafon.Crm.models import Action, ActionType, Zone, ZoneType, Contact
from balafon.Crm.settings import get_default_country
from balafon.Store import models
from balafon.Store.settings import get_cart_type_name


@override_settings(BALAFON_ALLOW_CART_NO_PROFILE=True)
class CartTest(APITestCase):
    """Base class for test cases"""
    fixtures = ['zones.json']

    def setUp(self):
        super(CartTest, self).setUp()
        logging.disable(logging.CRITICAL)
        self.client = APIClient()

    def tearDown(self):
        logging.disable(logging.NOTSET)
        super(CartTest, self).tearDown()

    def test_post_cart_no_profile(self):
        """It should create a new sale and action"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        zone_type = ZoneType.objects.get_or_create(type="country")[0]
        default_country = get_default_country()
        country = Zone.objects.get_or_create(name=default_country, type=zone_type, parent=None)[0]

        contact_data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'email': 'paul@dupond.fr',
            'address': '1 rue la ré',
            'city': 'Lyon',
            'zip_code': '69000',
            'country': country.id,
        }

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0),
            'contact': contact_data,
        }

        url = reverse('store_post_cart_no_profile')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(len(response.data['warnings']), 0)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(response.data['action'], action.id)

        self.assertEqual(action.contacts.count(), 1)
        contact = action.contacts.all()[0]
        self.assertEqual(contact.lastname, contact_data['lastname'])
        self.assertEqual(contact.firstname, contact_data['firstname'])
        self.assertEqual(contact.email, contact_data['email'])
        self.assertEqual(contact.address, contact_data['address'])
        self.assertEqual(contact.city.name, contact_data['city'])
        self.assertEqual(contact.zip_code, contact_data['zip_code'])
        self.assertEqual(contact.get_country(), country)

        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])
        self.assertEqual(action.sale.payment_mode, None)
        self.assertEqual(action.sale.analysis_code, models.SaleAnalysisCode.objects.get(name='Internet'))

        self.assertEqual(action.sale.saleitem_set.count(), 2)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].unit_price(), store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].unit_price(), store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, None)

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, None)

    def test_post_cart_no_profile_full_address(self):
        """It should create a new sale and action"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        zone_type = ZoneType.objects.get_or_create(type="country")[0]
        default_country = get_default_country()
        country = Zone.objects.get_or_create(name=default_country, type=zone_type, parent=None)[0]

        contact_data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'email': 'paul@dupond.fr',
            'address': '1 rue la ré',
            'address2': 'Bat B',
            'address3': 'à gauche',
            'city': 'Lyon',
            'zip_code': '69000',
            'country': country.id,
        }

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0),
            'contact': contact_data,
        }

        url = reverse('store_post_cart_no_profile')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(len(response.data['warnings']), 0)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(response.data['action'], action.id)

        self.assertEqual(action.contacts.count(), 1)
        contact = action.contacts.all()[0]
        self.assertEqual(contact.lastname, contact_data['lastname'])
        self.assertEqual(contact.firstname, contact_data['firstname'])
        self.assertEqual(contact.email, contact_data['email'])
        self.assertEqual(contact.address, contact_data['address'])
        self.assertEqual(contact.address2, contact_data['address2'])
        self.assertEqual(contact.address3, contact_data['address3'])
        self.assertEqual(contact.city.name, contact_data['city'])
        self.assertEqual(contact.zip_code, contact_data['zip_code'])
        self.assertEqual(contact.get_country(), country)

        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])
        self.assertEqual(action.sale.payment_mode, None)
        self.assertEqual(action.sale.analysis_code, models.SaleAnalysisCode.objects.get(name='Internet'))

        self.assertEqual(action.sale.saleitem_set.count(), 2)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].unit_price(), store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].unit_price(), store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, None)

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, None)

    @override_settings(BALAFON_ALLOW_CART_NO_PROFILE=False)
    def test_post_cart_no_profile_disabled(self):
        """It should raise 404"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        zone_type = ZoneType.objects.get_or_create(type="country")[0]
        default_country = get_default_country()
        country = Zone.objects.get_or_create(name=default_country, type=zone_type, parent=None)[0]

        contact_data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'email': 'paul@dupond.fr',
            'address': '1 rue la ré',
            'city': 'Lyon',
            'zip_code': '69000',
            'country': country.id,
        }

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0),
            'contact': contact_data,
        }

        url = reverse('store_post_cart_no_profile')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        action_queryset = Action.objects.all()
        self.assertEqual(action_queryset.count(), 0)

    def _do_test_post_cart_missing(self, extra_data):
        """It should create a new sale and action"""

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        zone_type = ZoneType.objects.get_or_create(type="country")[0]
        default_country = get_default_country()
        country = Zone.objects.get_or_create(name=default_country, type=zone_type, parent=None)[0]

        contact_data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'email': 'paul@dupond.fr',
            'address': '1 rue la ré',
            'city': 'Lyon',
            'zip_code': '69000',
            'country': country.id,
        }
        contact_data.update(extra_data)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0),
            'contact': contact_data,
        }

        url = reverse('store_post_cart_no_profile')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ok'], False)
        action_queryset = Action.objects.all()
        self.assertEqual(action_queryset.count(), 0)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_post_cart_empty_lastname(self):
        self._do_test_post_cart_missing({'lastname': ''})

    def test_post_cart_empty_firstname(self):
        self._do_test_post_cart_missing({'firstname': ''})

    def test_post_cart_empty_email(self):
        self._do_test_post_cart_missing({'email': ''})

    def test_post_cart_invalid_email(self):
        self._do_test_post_cart_missing({'email': 'test'})

    def test_post_cart_empty_address(self):
        self._do_test_post_cart_missing({'address': ''})

    def test_post_cart_empty_zip_code(self):
        self._do_test_post_cart_missing({'zip_code': ''})

    def test_post_cart_empty_city(self):
        self._do_test_post_cart_missing({'city': ''})

    def test_post_cart_empty_country(self):
        self._do_test_post_cart_missing({'country': 0})

    def test_post_cart_invalid_zip_code(self):
        self._do_test_post_cart_missing({'zip_code': '1'})

    def test_post_cart_foreign_countru(self):

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        zone_type = ZoneType.objects.get_or_create(type="country")[0]
        default_country = get_default_country()
        country = Zone.objects.get_or_create(name=default_country, type=zone_type, parent=None)[0]
        other_country = Zone.objects.create(name='Foreign', type=zone_type, parent=None)

        contact_data = {
            'lastname': 'Dupond',
            'firstname': 'Paul',
            'email': 'paul@dupond.fr',
            'address': '1 rue la ré',
            'city': 'Foreign',
            'zip_code': 'AAZ',
            'country': other_country.id,
        }

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0),
            'contact': contact_data,
        }

        url = reverse('store_post_cart_no_profile')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(len(response.data['warnings']), 0)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(response.data['action'], action.id)

        self.assertEqual(action.contacts.count(), 1)
        contact = action.contacts.all()[0]
        self.assertEqual(contact.lastname, contact_data['lastname'])
        self.assertEqual(contact.firstname, contact_data['firstname'])
        self.assertEqual(contact.email, contact_data['email'])
        self.assertEqual(contact.address, contact_data['address'])
        self.assertEqual(contact.city.name, contact_data['city'])
        self.assertEqual(contact.zip_code, contact_data['zip_code'])
        self.assertEqual(contact.get_country(), other_country)

        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])
        self.assertEqual(action.sale.payment_mode, None)
        self.assertEqual(action.sale.analysis_code, models.SaleAnalysisCode.objects.get(name='Internet'))

        self.assertEqual(action.sale.saleitem_set.count(), 2)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].unit_price(), store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].unit_price(), store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 1)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, None)

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, None)