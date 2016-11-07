# -*- coding: utf-8 -*-
"""unit testing"""

from bs4 import BeautifulSoup
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from model_mommy import mommy

from balafon.Crm.models import Action, ActionStatus, ActionType, Contact, Entity
from balafon.Crm.tests import BaseTestCase
from balafon.Store import models

CUSTOM_STYLE = '''<style>
    body {
      background: #000;
    }
</style>'''


class ViewCommercialDocumentTest(TestCase):
    """It should display commercial document"""

    def setUp(self):
        """before each test"""
        user = mommy.make(User, is_active=True, is_staff=True, is_superuser=False)
        user.set_password('abc')
        user.save()
        self.client.login(username=user.username, password='abc')
        self.user = user

    def tearDown(self):
        """after each test"""
        self.client.logout()

    def test_view_no_sale_action_type(self):
        """It should display standard document"""

        action = mommy.make(Action, type=None)
        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_read_only'], False)
        self.assertNotContains(response, CUSTOM_STYLE)

    def test_view_no_custom_template(self):
        """It should display standard document"""

        action_type = mommy.make(ActionType)
        action = mommy.make(Action, type=action_type)
        mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='')

        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, CUSTOM_STYLE)

    def test_view_contacts_and_entities(self):
        """It should display standard document with contacts and entities"""

        action_type = mommy.make(ActionType)
        action = mommy.make(Action, type=action_type)
        mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='')

        contact1 = mommy.make(Contact, lastname='abc' * 10)
        contact2 = mommy.make(Contact, lastname='def' * 10)
        contact3 = mommy.make(Contact, lastname='ghi' * 10)
        entity1 = mommy.make(Entity, name='jkl' * 10)

        action.contacts.add(contact1)
        action.contacts.add(contact2)
        action.entities.add(entity1)
        action.save()

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, contact1.fullname)
        self.assertContains(response, contact2.fullname)
        self.assertContains(response, entity1.name)
        self.assertNotContains(response, contact3.fullname)

    def test_view_custom_template(self):
        """It should display custom document"""

        action_type = mommy.make(ActionType)
        action = mommy.make(Action, type=action_type)
        mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='Store/tests/bill.html')

        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, CUSTOM_STYLE)
        self.assertContains(response, 'big head')
        self.assertContains(response, 'big foot')

    def test_view_read_only(self):
        """It should display as read only"""

        action_type = mommy.make(ActionType)
        action_status = mommy.make(ActionStatus)

        action = mommy.make(Action, type=action_type, status=action_status)

        store_type = mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='')
        store_type.readonly_status.add(action_status)
        store_type.save()

        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['is_read_only'], True)

    def test_view_status_change(self):
        """It should display as writable"""

        action_type = mommy.make(ActionType)
        action_status = mommy.make(ActionStatus)

        action = mommy.make(Action, type=action_type, status=action_status)

        store_type = mommy.make(models.StoreManagementActionType, action_type=action_type, template_name='')

        mommy.make(models.Sale, action=action)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['is_read_only'], False)

    def test_view_no_sales(self):
        """It should display page not found"""
        action = mommy.make(Action, type=None)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_view_admin_only(self):
        """It should display permission denied"""
        self.user.is_staff = False
        self.user.save()

        store_action_type = mommy.make(models.StoreManagementActionType)
        action = mommy.make(Action, type=store_action_type.action_type)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_view_anonymous(self):
        """It should redirect to login page"""
        self.client.logout()

        store_action_type = mommy.make(models.StoreManagementActionType)
        action = mommy.make(Action, type=store_action_type.action_type)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_values(self):
        """It should display item text"""

        store_action_type = mommy.make(models.StoreManagementActionType)
        action = mommy.make(Action, type=store_action_type.action_type)

        item = mommy.make(models.SaleItem, sale=action.sale, text=u'Promo été', quantity=1, pre_tax_price=10)

        url = reverse('store_view_sales_document', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.text)

    def test_view_public(self):
        """It should display item text"""

        action_type = mommy.make(ActionType, generate_uuid=True)
        mommy.make(models.StoreManagementActionType, action_type=action_type)
        action = mommy.make(Action, type=action_type)

        self.assertNotEqual(action.uuid, '')

        item = mommy.make(models.SaleItem, sale=action.sale, text=u'Promo été', quantity=1, pre_tax_price=10)

        self.client.logout()
        url = reverse('store_view_sales_document_public', args=[action.uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, item.text)

    def test_view_public_invalid_uuid(self):
        """It should not display item text"""

        action_type = mommy.make(ActionType, generate_uuid=False)
        mommy.make(models.StoreManagementActionType, action_type=action_type)
        action = mommy.make(Action, type=action_type)

        self.assertEqual(action.uuid, '')

        self.client.logout()

        dummy_uuid = 'xxxxxxxxxxxxx'
        url = reverse('store_view_sales_document_public', args=[dummy_uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = url.replace(dummy_uuid, '')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view_pdf(self):
        """It should display item text"""

        store_action_type = mommy.make(models.StoreManagementActionType)
        action = mommy.make(Action, type=store_action_type.action_type)

        contact1 = mommy.make(Contact, lastname='abc' * 10)
        action.contacts.add(contact1)
        action.save()

        mommy.make(models.SaleItem, sale=action.sale, text=u'Promo été', quantity=1, pre_tax_price=10)

        url = reverse('store_view_sales_document_pdf', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_view_public_pdf(self):
        """It should display item text"""

        action_type = mommy.make(ActionType, generate_uuid=True)
        mommy.make(models.StoreManagementActionType, action_type=action_type)
        action = mommy.make(Action, type=action_type)

        contact1 = mommy.make(Contact, lastname='abc' * 10)
        action.contacts.add(contact1)
        action.save()

        self.assertNotEqual(action.uuid, '')
        self.client.logout()

        mommy.make(models.SaleItem, sale=action.sale, text=u'Promo été', quantity=1, pre_tax_price=10)

        url = reverse('store_view_sales_document_pdf_public', args=[action.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_view_public_pdf_invalid_uuid(self):
        """It should display item text"""

        action_type = mommy.make(ActionType, generate_uuid=False)
        mommy.make(models.StoreManagementActionType, action_type=action_type)
        action = mommy.make(Action, type=action_type)

        contact1 = mommy.make(Contact, lastname='abc' * 10)
        action.contacts.add(contact1)
        action.save()

        self.assertEqual(action.uuid, '')
        self.client.logout()

        dummy_uuid = 'xxxxxxxxxxxxx'
        url = reverse('store_view_sales_document_public', args=[dummy_uuid])

        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

        url = url.replace(dummy_uuid, '')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ActionMailtoTest(BaseTestCase):
    """It should generate mailto properly"""

    def test_mail_to(self):
        """it should generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")
        contact = mommy.make(Contact, email='toto@toto.fr', lastname='Dalton', firstname='Joe')
        action.contacts.add(contact)
        action.save()
        self.assertEqual(
            action.mail_to, 'mailto:"{0}" <{1}>?subject={2}&body='.format(
                contact.fullname, contact.email, action.subject,
            )
        )

    def test_mail_to_entity(self):
        """it should generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")
        entity = mommy.make(Entity, email='toto@toto.fr')
        action.entities.add(entity)
        action.save()
        self.assertEqual(
            action.mail_to, 'mailto:"{0}" <{1}>?subject={2}&body='.format(
                entity.name, entity.email, action.subject,
            )
        )

    def test_mail_to_entity_contact(self):
        """it should generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")
        entity = mommy.make(Entity, email='toto@toto.fr')
        action.contacts.add(entity.default_contact)
        action.save()
        self.assertEqual(
            action.mail_to, 'mailto:{0}?subject={1}&body='.format(
                entity.email, action.subject,
            )
        )

    def test_mail_to_several(self):
        """it should generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")

        entity = mommy.make(Entity, email='titi@toto.fr', name='')
        action.entities.add(entity)

        contact = mommy.make(Contact, email='toto@toto.fr', lastname='', firstname='')
        action.contacts.add(contact)

        action.save()
        self.assertEqual(
            action.mail_to, 'mailto:{0},{1}?subject={2}&body='.format(
                entity.email, contact.email, action.subject,
            )
        )

    def test_mail_to_twice(self):
        """it should generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")

        entity = mommy.make(Entity, email='toto@toto.fr', name='')
        action.entities.add(entity)

        contact = mommy.make(Contact, email='toto@toto.fr', lastname='', firstname='')
        action.contacts.add(contact)

        action.save()

        self.assertEqual(
            action.mail_to, 'mailto:{0}?subject={1}&body='.format(
                entity.email, action.subject,
            )
        )

    def test_mail_to_uuid(self):
        """it should generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=True, name='Doc')
        mommy.make(models.StoreManagementActionType, action_type=action_type)
        action = mommy.make(Action, type=action_type, subject="Hello")
        contact = mommy.make(Contact, email='toto@toto.fr')
        action.contacts.add(contact)
        action.save()

        body = _(u"Here is a link to your {0}: {1}{2}").format(
            action_type.name,
            "http://" + Site.objects.get_current().domain,
            reverse('store_view_sales_document_public', args=[action.uuid])
        )

        self.assertEqual(contact.lastname, '')
        self.assertEqual(contact.firstname, '')

        self.assertEqual(
            action.mail_to, 'mailto:{0}?subject={1}&body={2}'.format(
                contact.email, action.subject, body
            )
        )

    def test_mail_to_no_email(self):
        """it should not generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")
        contact = mommy.make(Contact, email='')
        action.contacts.add(contact)
        action.save()
        self.assertEqual(
            action.mail_to, ''
        )

    def test_mail_to_no_contact(self):
        """it should not generate a mailto link"""
        action_type = mommy.make(ActionType, generate_uuid=False)
        action = mommy.make(Action, type=action_type, subject="Hello")
        action.save()
        self.assertEqual(
            action.mail_to, ''
        )


class EditSaleActionTest(BaseTestCase):
    """It should display edit action correctly"""

    def test_edit_action_calculated_amount(self):
        """edit with caculated amount"""
        contact = mommy.make(Contact)

        action_type = mommy.make(ActionType, is_amount_calculated=False)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=False
        )
        action_type = ActionType.objects.get(id=action_type.id)
        self.assertEqual(action_type.is_amount_calculated, True)

        action = mommy.make(Action, type=action_type)

        action.contacts.add(contact)
        action.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        fields = soup.select("#id_amount")
        self.assertEqual(len(fields), 1)

        self.assertEqual(fields[0]["disabled"], "disabled")

    def test_create_action_calculated_amount(self):
        """create with calculated amount"""
        action_type = mommy.make(ActionType, is_amount_calculated=False)
        mommy.make(
            models.StoreManagementActionType,
            action_type=action_type,
            show_amount_as_pre_tax=False
        )
        action_type = ActionType.objects.get(id=action_type.id)
        self.assertEqual(action_type.is_amount_calculated, True)

        url = reverse('crm_create_action', args=[0, 0]) + "?type={0}".format(action_type.id)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        fields = soup.select("#id_amount")
        self.assertEqual(len(fields), 1)

        self.assertEqual(fields[0]["disabled"], "disabled")


class CloneSaleActionTest(BaseTestCase):
    """clone an action"""

    def test_post_clone_action(self):
        """it should clone action and sale"""
        action_type_1 = mommy.make(ActionType)
        action_type_2 = mommy.make(ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        store_action_type1 = mommy.make(models.StoreManagementActionType, action_type=action_type_1)
        store_action_type2 = mommy.make(models.StoreManagementActionType, action_type=action_type_2)

        contact = mommy.make(Contact)
        entity = mommy.make(Entity)

        action = mommy.make(models.Action, type=action_type_1, done=True)

        self.assertNotEqual(action.sale, None)

        vat_rate1 = mommy.make(models.VatRate, rate="20.0")
        vat_rate2 = mommy.make(models.VatRate, rate="10.0")

        store_item = mommy.make(models.StoreItem)

        sale_item1 = mommy.make(
            models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=vat_rate1,
            sale=action.sale, order_index=1, item=store_item
        )
        sale_item2 = mommy.make(
            models.SaleItem, quantity=2, pre_tax_price="1", vat_rate=vat_rate2,
            sale=action.sale, order_index=2
        )

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertEqual(response.content, 'reload: {0}'.format(reverse('crm_edit_action', args=[new_action.id])))

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)
        self.assertEqual(new_action.amount, Decimal("12"))
        self.assertEqual(new_action.sale.saleitem_set.count(), 2)

        for original, clone in zip(original_action.sale.saleitem_set.all(), new_action.sale.saleitem_set.all()):
            self.assertEqual(original.quantity, clone.quantity)
            self.assertEqual(original.vat_rate, clone.vat_rate)
            self.assertEqual(original.pre_tax_price, clone.pre_tax_price)
            self.assertEqual(original.text, clone.text)
            self.assertEqual(original.item, clone.item)

        sale_item = new_action.sale.saleitem_set.all()[0]
        sale_item.quantity = 10
        sale_item.save()

        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)
        self.assertNotEqual(new_action.amount, original_action.amount)
        self.assertEqual(original_action.amount, Decimal("12"))
        self.assertEqual(new_action.amount, Decimal("102"))

    def test_post_clone_action_no_sale(self):
        """it should clone action and sale"""
        action_type_1 = mommy.make(ActionType)
        action_type_2 = mommy.make(ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        store_action_type1 = mommy.make(models.StoreManagementActionType, action_type=action_type_1)

        contact = mommy.make(Contact)
        entity = mommy.make(Entity)

        action = mommy.make(models.Action, type=action_type_1, done=True)

        self.assertNotEqual(action.sale, None)

        vat_rate1 = mommy.make(models.VatRate, rate="20.0")
        vat_rate2 = mommy.make(models.VatRate, rate="10.0")

        store_item = mommy.make(models.StoreItem)

        sale_item1 = mommy.make(
            models.SaleItem, quantity=1, pre_tax_price="10", vat_rate=vat_rate1,
            sale=action.sale, order_index=1, item=store_item
        )
        sale_item2 = mommy.make(
            models.SaleItem, quantity=2, pre_tax_price="1", vat_rate=vat_rate2,
            sale=action.sale, order_index=2
        )

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertEqual(response.content, 'reload: {0}'.format(reverse('crm_edit_action', args=[new_action.id])))

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)
        self.assertEqual(new_action.amount, Decimal("12.0"))
        self.assertEqual(0, models.Sale.objects.filter(action=new_action).count())
