# -*- coding: utf-8 -*-
"""unit testing"""

from datetime import datetime
from decimal import Decimal
import logging
from unittest import skipIf

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import mail
from django.utils.translation import ugettext as _

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from balafon.Crm.models import Action, ActionType
from balafon.Profile.utils import create_profile_contact
from balafon.Store import models
from balafon.Store.settings import get_cart_type_name


class BaseTestCase(APITestCase):
    """Base class for test cases"""

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto", is_active=True, is_staff=False)
        self.user.set_password("abc")
        self.user.save()
        self.client = APIClient()
        self._login()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _login(self):
        self.client.login(username="toto", password="abc")


@skipIf(not ("balafon.Profile" in settings.INSTALLED_APPS), "registration not installed")
class CartTest(BaseTestCase):
    """Test that cart is process properly"""

    def test_post_cart(self):
        """It should create a new sale and action"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

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

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

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
        self.assertEqual(mail.outbox[0].to, [profile.contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, None)

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, None)

    def test_post_cart_notes(self):
        """It should create a new sale and action"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'notes': 'This is a text',
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

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

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, _(u'Notes'))
        self.assertEqual(action.detail, data['notes'])
        self.assertEqual(action.planned_date, data['purchase_datetime'])

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

    def test_post_cart_long_notes(self):
        """It should create a new sale and action"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'notes': 'abc'*100,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

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

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, _(u'Notes'))
        self.assertEqual(action.detail, data['notes'])
        self.assertEqual(action.planned_date, data['purchase_datetime'])

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

    def test_post_cart_notes_several_lines(self):
        """It should create a new sale and action"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem)
        store_item2 = mommy.make(models.StoreItem)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'notes': 'a\nB\nc',
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

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

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, _(u'Notes'))
        self.assertEqual(action.detail, 'a\nB\nc')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

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

    def test_post_cart_update_stock(self):
        """It should create a new sale and action and update the stock"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem, stock_count=Decimal('10'))
        store_item2 = mommy.make(models.StoreItem, stock_count=Decimal('0.5'))

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

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

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

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
        self.assertEqual(mail.outbox[0].to, [profile.contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, Decimal("8"))

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, Decimal("-0.5"))

    def test_post_cart_not_available(self):
        """It should create a new sale and ignore articles which are not available"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem, stock_count=Decimal('10'))
        store_item2 = mommy.make(models.StoreItem, stock_count=Decimal('0.5'), available=False)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(len(response.data['warnings']), 1)
        self.assertEqual(response.data['deliveryDate'], data['purchase_datetime'])
        self.assertEqual(response.data['deliveryPlace'], delivery_point.name)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

        self.assertEqual(action.sale.saleitem_set.count(), 1)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].unit_price(), store_item1.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 2)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [profile.contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, Decimal("8"))

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, Decimal("0.5"))

    def test_post_cart_empty(self):
        """It should create a new sale and ignore articles which are not available"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem, stock_count=Decimal('10'), available=False)
        store_item2 = mommy.make(models.StoreItem, stock_count=Decimal('0.5'), available=False)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 2},
                {'id': store_item2.id, 'quantity': 1},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], False)
        self.assertEqual(len(response.data['warnings']), 2)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 0)

        self.assertEqual(len(mail.outbox), 0)

        store_item1 = models.StoreItem.objects.get(id=store_item1.id)
        self.assertEqual(store_item1.stock_count, Decimal("10"))

        store_item2 = models.StoreItem.objects.get(id=store_item2.id)
        self.assertEqual(store_item2.stock_count, Decimal("0.5"))

    def test_cart_when_deleted_article(self):
        """The cart should not be removed if store_item is deleted"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        store_item1 = mommy.make(models.StoreItem, stock_count=Decimal('10'))
        store_item2 = mommy.make(models.StoreItem, stock_count=Decimal('0.5'))

        sale = mommy.make(models.Sale)

        sale_item1 = mommy.make(
            models.SaleItem,
            sale=sale,
            item=store_item1,
            quantity=2,
            vat_rate=store_item1.vat_rate,
            pre_tax_price=store_item1.pre_tax_price
        )

        sale_item2 = mommy.make(
            models.SaleItem,
            sale=sale,
            item=store_item2,
            quantity=1,
            vat_rate=store_item2.vat_rate,
            pre_tax_price=store_item2.pre_tax_price
        )

        store_item1.delete()

        self.assertEqual(1, models.Sale.objects.count())
        self.assertEqual(sale.id, models.Sale.objects.all()[0].id)

    def test_cart_with_discount(self):
        """The cart should take account discount into account"""

        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact

        discount = mommy.make(
            models.Discount, active=True, name="10% si + de 5", rate=Decimal("10"), quantity=Decimal("5")
        )
        price_class = mommy.make(models.PriceClass, name="Vrac")
        price_class.discounts.add(discount)
        price_class.save()

        store_item1 = mommy.make(models.StoreItem, pre_tax_price=Decimal('10'), price_class=price_class)
        store_item2 = mommy.make(models.StoreItem, pre_tax_price=Decimal('1'), price_class=price_class)
        store_item3 = mommy.make(models.StoreItem, pre_tax_price=Decimal('2'), price_class=None)

        delivery_point = mommy.make(models.DeliveryPoint)

        data = {
            'items': [
                {'id': store_item1.id, 'quantity': 5},
                {'id': store_item2.id, 'quantity': 2},
                {'id': store_item3.id, 'quantity': 5},
            ],
            'delivery_point': delivery_point.id,
            'purchase_datetime': datetime(2015, 7, 23, 12, 0)
        }

        url = reverse('store_post_cart')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['ok'], True)
        self.assertEqual(len(response.data['warnings']), 0)

        action_type = ActionType.objects.get(name=get_cart_type_name())

        action_queryset = Action.objects.filter(type=action_type)
        self.assertEqual(action_queryset.count(), 1)
        action = action_queryset[0]

        self.assertEqual(list(action.contacts.all()), [contact])
        self.assertEqual(action.subject, '')
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, data['purchase_datetime'])

        self.assertEqual(action.sale.saleitem_set.count(), 3)
        self.assertEqual(action.sale.saleitem_set.all()[0].item, store_item1)
        self.assertEqual(action.sale.saleitem_set.all()[0].text, store_item1.name)
        self.assertEqual(action.sale.saleitem_set.all()[0].unit_price(), store_item1.pre_tax_price * Decimal("0.9"))
        self.assertEqual(action.sale.saleitem_set.all()[0].vat_rate, store_item1.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[0].quantity, 5)

        self.assertEqual(action.sale.saleitem_set.all()[1].item, store_item2)
        self.assertEqual(action.sale.saleitem_set.all()[1].text, store_item2.name)
        self.assertEqual(action.sale.saleitem_set.all()[1].unit_price(), store_item2.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[1].vat_rate, store_item2.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[1].quantity, 2)

        self.assertEqual(action.sale.saleitem_set.all()[2].item, store_item3)
        self.assertEqual(action.sale.saleitem_set.all()[2].text, store_item3.name)
        self.assertEqual(action.sale.saleitem_set.all()[2].unit_price(), store_item3.pre_tax_price)
        self.assertEqual(action.sale.saleitem_set.all()[2].vat_rate, store_item3.vat_rate)
        self.assertEqual(action.sale.saleitem_set.all()[2].quantity, 5)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, [profile.contact.email])
        self.assertEqual(mail.outbox[1].to, [settings.BALAFON_NOTIFICATION_EMAIL])
