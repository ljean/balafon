# -*- coding: utf-8 -*-
"""models"""

import datetime
from decimal import Decimal
import traceback
import xlrd

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete, post_save
from django.utils.translation import ugettext_lazy as _, ugettext

from sanza.Crm.models import Action, ActionMenu, ActionStatus, ActionType
from sanza.Crm.signals import action_cloned


class StoreManagementActionType(models.Model):
    """
    Define if an action type is linked to the store.
    If so it will be possible to link a Sale with an Action of this ActionType
    """
    action_type = models.OneToOneField(ActionType)
    template_name = models.CharField(
        default='', blank=True, max_length=100, verbose_name=_(u'template name'),
        help_text=_(u'Set the name of a custom template for commercial document')
    )
    show_amount_as_pre_tax = models.BooleanField(
        default=True,
        verbose_name=_(u'Show amount as pre-tax'),
        help_text=_(
            u'The action amount will be update with pre-tax total if checked and with tax-included total if not'
        )
    )
    readonly_status = models.ManyToManyField(
        ActionStatus, blank=True, verbose_name=_(u'readonly status'),
        help_text=_(u'When action has one of these status, it is not possible to modify a commercial document')
    )

    class Meta:
        verbose_name = _(u"Store management action type")
        verbose_name_plural = _(u"Store management action types")

    def save(self, *args, **kwargs):
        """save: create the corresponding menu"""
        ret = super(StoreManagementActionType, self).save(*args, **kwargs)
        if self.id and self.action_type:

            ActionMenu.create_action_menu(
                action_type=self.action_type,
                view_name='store_view_sales_document',
                label=self.action_type.name,
                icon='file',
                a_attrs=''
            )

            if not self.action_type.is_amount_calculated:
                self.action_type.is_amount_calculated = True
                self.action_type.save()
        return ret

    def __unicode__(self):
        return u"{0}".format(self.action_type)


class VatRate(models.Model):
    """Tax : A VAT rate"""
    rate = models.DecimalField(verbose_name=_(u"vat rate"), max_digits=4, decimal_places=2)
    is_default = models.BooleanField(default=False, verbose_name=_("is default"))

    @property
    def name(self):
        return u"{0}%".format(self.rate)

    class Meta:
        verbose_name = _(u"VAT rate")
        verbose_name_plural = _(u"VAT rates")
        ordering = ['rate']

    def save(self, *args, **kwargs):
        return_value = super(VatRate, self).save(*args, **kwargs)
        if self.is_default:
            VatRate.objects.exclude(id=self.id).update(is_default=False)
        return return_value

    def __unicode__(self):
        return self.name


class Unit(models.Model):
    """a unit"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)

    class Meta:
        verbose_name = _(u"unit")
        verbose_name_plural = _(u"units")

    def __unicode__(self):
        return self.name


class StoreItemCategory(models.Model):
    """something for organization of store items"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    order_index = models.IntegerField(verbose_name=_(u"order_index"), default=0)
    active = models.BooleanField(verbose_name=_(u"active"), default=True)
    icon = models.CharField(max_length=20, default="", blank=True)

    class Meta:
        verbose_name = _(u"Store item category")
        verbose_name_plural = _(u"Store item categories")
        ordering = ['order_index', 'name']

    def __unicode__(self):
        return self.name


class StoreItemTag(models.Model):
    """something for finding store items more easily"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    order_index = models.IntegerField(verbose_name=_(u"order_index"), default=0)
    active = models.BooleanField(verbose_name=_(u"active"), default=True)
    icon = models.CharField(max_length=20, default="", blank=True)

    class Meta:
        verbose_name = _(u"Store item tag")
        verbose_name_plural = _(u"Store item tags")
        ordering = ['order_index', 'name']

    def __unicode__(self):
        return self.name


class Brand(models.Model):
    """A brand : cola-cola, peugeot or whatever"""
    name = models.CharField(max_length=100, verbose_name=_(u'name'))

    class Meta:
        verbose_name = _(u"Brand")
        verbose_name_plural = _(u"Brands")

    def __unicode__(self):
        return self.name


class StoreItem(models.Model):
    """something than can be buy in this store"""

    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    category = models.ForeignKey(StoreItemCategory, verbose_name=_(u"category"))
    tags = models.ManyToManyField(StoreItemTag, blank=True, verbose_name=_(u"tags"))
    vat_rate = models.ForeignKey(VatRate, verbose_name=_(u"VAT rate"))
    pre_tax_price = models.DecimalField(verbose_name=_(u"pre-tax price"), max_digits=9, decimal_places=2)
    stock_count = models.IntegerField(default=None, verbose_name=_(u"stock count"), blank=True, null=True)
    stock_threshold = models.IntegerField(default=None, verbose_name=_(u"stock count"), blank=True, null=True)
    purchase_price = models.DecimalField(
        verbose_name=_(u"purchase price"), max_digits=9, decimal_places=2, blank=True, default=None, null=True
    )
    unit = models.ForeignKey(Unit, blank=True, default=None, null=True)
    brand = models.ForeignKey(Brand, default=None, blank=True, null=True, verbose_name=_(u'brand'))
    reference = models.CharField(max_length=100, default='', blank=True, verbose_name=_(u'reference'))
    imported_by = models.ForeignKey(
        'StoreItemImport', default=None, blank=True, null=True, verbose_name=_(u'imported by')
    )

    class Meta:
        verbose_name = _(u"Store item")
        verbose_name_plural = _(u"Store items")
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def vat_incl_price(self):
        """VAT inclusive price"""
        return self.pre_tax_price * (1 + self.vat_rate.rate / 100)
    vat_incl_price.short_description = _(u"VAT inclusive price")

    def set_property(self, property_name, value):
        """create and set a property for this item"""
        the_property = StoreItemProperty.objects.get_or_create(name=property_name)[0]
        property_value = StoreItemPropertyValue.objects.get_or_create(property=the_property, item=self)[0]
        property_value.value = value
        property_value.save()

    def get_property(self, property_name):
        """create and set a property for this item"""
        the_property = StoreItemProperty.objects.get_or_create(name=property_name)[0]
        try:
            property_value = StoreItemPropertyValue.objects.get(property=the_property, item=self)
            return property_value.value
        except StoreItemPropertyValue.DoesNotExist:
            return ''

    def has_stock_threshold_alert(self):
        """returns True if stock is below threshold"""
        if self.stock_threshold:
            return self.stock_count <= self.stock_threshold
        return False

    def stock_threshold_alert(self):
        """
        return threshold value with warning sign if stock is below this value
        To be used in admin
        """
        alert_text = ""
        if self.has_stock_threshold_alert():
            alert_text = u'<img src="{0}store/img/warning-sign" />'.format(settings.STATIC_URL)
        return u"{0} {1}".format(
            self.stock_threshold if self.stock_threshold is not None else "",
            alert_text
        ).strip()

    stock_threshold_alert.short_description = _(u"Stock threshold")
    stock_threshold_alert.allow_tags = True


class StoreItemProperty(models.Model):
    """a property for a store item: DLC, Colisage..."""
    name = models.CharField(max_length=100, verbose_name=_(u'name'))
    label = models.CharField(max_length=100, verbose_name=_(u'name'), default='', blank=True)

    class Meta:
        verbose_name = _(u"Store item: property value")
        verbose_name_plural = _(u"Store item: properties")

    def __unicode__(self):
        return self.label or self.name


class StoreItemImport(models.Model):
    """Makes possible to import store item"""
    data = models.FileField(
        upload_to='store_item_imports',
        verbose_name=_(u"Import file"),
        help_text=_(u'An Excel file (*.xls) with the data')
    )
    tags = models.ManyToManyField(
        StoreItemTag,
        blank=True,
        verbose_name=_(u"tags"),
        help_text=_(u'Tags that can be added to the items')
    )
    fields = models.CharField(
        max_length=300,
        default='name,brand,reference,category,purchase_price,vat_rate',
        verbose_name=_(u"fields"),
        help_text=_(u"Fields to import in order: if the attribute doesn't exist, create a custom property")
    )
    last_import_date = models.DateTimeField(default=None, blank=True, null=True, verbose_name=_(u"last import"))
    import_error = models.TextField(default='', blank=True, verbose_name=_(u'import error'))
    is_successful = models.BooleanField(default=True, verbose_name=_('is successful'))
    ignore_first_line = models.BooleanField(default=True, verbose_name=_('ignore first line'))
    margin_rate = models.DecimalField(
        default=None, null=True, verbose_name=_('margin_rate'), max_digits=9, decimal_places=2
    )
    error_message = models.CharField(
        default='', blank=True, max_length=100, verbose_name=_(u'error message')
    )

    class Meta:
        verbose_name = _(u"Store item import")
        verbose_name_plural = _(u"Store item imports")

    def __unicode__(self):
        return self.data.url

    def get_url(self):
        return self.data.url

    def _to_decimal(self, raw_value):
        """convert string to decimal"""
        return Decimal(raw_value)

    def _to_itself(self, raw_value):
        """dummy : just a function to use in the dict"""
        return raw_value

    def _to_brand(self, raw_value):
        """convert string to brand"""
        if raw_value:
            return Brand.objects.get_or_create(name=raw_value)[0]

    def _to_category(self, raw_value):
        """convert string to category"""
        raw_value = raw_value or ugettext('Uncategorized')
        return StoreItemCategory.objects.get_or_create(name=raw_value)[0]

    def _to_vat(self, raw_value):
        """convert string to vat"""
        if raw_value:
            return VatRate.objects.get_or_create(rate=Decimal(raw_value))[0]
        else:
            try:
                return VatRate.objects.get(is_default=True)
            except VatRate.DoesNotExist:
                try:
                    return VatRate.objects.all()[0]
                except IndexError:
                    return VatRate.objects.create(is_default=True, rate=Decimal("20.0"))

    def import_data(self):
        """import data from xls file"""
        self.last_import_date = datetime.datetime.now()
        self.import_error = u''
        self.error_message = u''
        self.is_successful = False
        self.save()
        self.is_successful = True  # Assume everything will be ok :-)
        try:
            book = xlrd.open_workbook(file_contents=self.data.read())
            sheet = book.sheet_by_index(0)

            fields = self.fields.split(',')

            fields_conversion = {
                'name': self._to_itself,
                'reference': self._to_itself,
                'purchase_price': self._to_decimal,
                'brand': self._to_brand,
                'category': self._to_category,
                'vat_rate': self._to_vat,
                'pre_tax_price': self._to_decimal,
            }

            for row_index in xrange(sheet.nrows):

                if self.ignore_first_line and row_index == 0:
                    #ignore
                    continue

                store_item = StoreItem()
                properties = []

                #for all fields
                for field, col_index in zip(fields, xrange(sheet.ncols)):
                    raw_value = sheet.cell(rowx=row_index, colx=col_index).value

                    if field in fields_conversion:
                        #call the function associated with this field
                        value = fields_conversion[field](raw_value)
                        setattr(store_item, field, value)
                    else:
                        #for extra fields : create a property (once the object has been saved)
                        properties.append((field, raw_value))

                if 'pre_tax_price' not in fields:
                    if 'purchase_price' in fields:
                        margin_rate = self.margin_rate or 1
                        store_item.pre_tax_price = store_item.purchase_price * margin_rate
                    else:
                        store_item.pre_tax_price = 0

                if 'vat_rate' not in fields:
                    store_item.vat_rate = self._to_vat(None)  # force default

                if 'category' not in fields:
                    store_item.category = self._to_category(None)  # force default

                store_item.imported_by = self
                store_item.save()

                for (property_field, value) in properties:
                    store_item.set_property(property_field, value)

                for tag in self.tags.all():
                    store_item.tags.add(tag)
                    store_item.save()

        except Exception as msg:  # pylint: disable=broad-except
            error_stack = traceback.format_exc()
            self.import_error = repr(error_stack)
            self.is_successful = False
            self.error_message = unicode(msg)[:100]

        self.save()




class StoreItemPropertyValue(models.Model):
    """The value of a property for a given item"""
    item = models.ForeignKey(StoreItem, verbose_name=_(u'item'))
    property = models.ForeignKey(StoreItemProperty, verbose_name=_(u'property'))
    value = models.CharField(max_length=100, verbose_name=_(u'value'))

    class Meta:
        verbose_name = _(u"Store item: property value")
        verbose_name_plural = _(u"Store item: property values")

    def __unicode__(self):
        return self.name


class DeliveryPoint(models.Model):
    """Where to get a sale"""
    name = models.CharField(max_length=100, verbose_name=_(u"name"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Delivery point")
        verbose_name_plural = _(u"Delivery points")
        ordering = ('name',)


class Sale(models.Model):
    """A sale"""
    action = models.OneToOneField(Action)
    delivery_point = models.ForeignKey(
        DeliveryPoint, default=None, blank=True, null=True, verbose_name=_(u"delivery point")
    )

    class Meta:
        verbose_name = _(u"Sale")
        verbose_name_plural = _(u"Sales")

    def __unicode__(self):
        return unicode(self.action)

    def clone(self, new_sale):
        """clone a sale: clone its items"""
        for item in self.saleitem_set.all():
            item.clone(new_sale)


class SaleItem(models.Model):
    """details about the sold item"""
    sale = models.ForeignKey(Sale)
    item = models.ForeignKey(StoreItem, blank=True, default=None, null=True)
    quantity = models.DecimalField(verbose_name=_(u"quantity"), max_digits=9, decimal_places=2)
    vat_rate = models.ForeignKey(VatRate, verbose_name=_(u"VAT rate"))
    pre_tax_price = models.DecimalField(verbose_name=_(u"pre-tax price"), max_digits=9, decimal_places=2)
    text = models.TextField(verbose_name=_(u"Text"), max_length=3000, default='', blank=True)
    order_index = models.IntegerField(default=0)

    class Meta:
        verbose_name = _(u"Sale item")
        verbose_name_plural = _(u"Sales items")
        ordering = ['order_index']

    def __unicode__(self):
        if self.id:
            return _(u"{1} x {0}").format(self.item, self.quantity)
        else:
            return _(u"Sale item not set")

    def vat_incl_price(self):
        """VAT inclusive price"""
        return self.pre_tax_price * (1 + self.vat_rate.rate / 100)

    def vat_incl_total_price(self):
        """VAT inclusive price"""
        return self.vat_incl_price() * self.quantity

    def save(self, *args, **kwargs):
        if self.order_index == 0:
            self.order_index = SaleItem.objects.filter(sale=self.sale).count() + 1
        return super(SaleItem, self).save(*args, **kwargs)

    def clone(self, new_sale):
        """clone it for a new sale"""
        return SaleItem.objects.create(
            sale=new_sale,
            item=self.item,
            quantity=self.quantity,
            vat_rate=self.vat_rate,
            pre_tax_price=self.pre_tax_price,
            text=self.text,
            order_index=self.order_index
        )


def update_action_amount(sale_item, delete_me=False):
    """update the corresponding action amount """
    action = sale_item.sale.action
    queryset = action.sale.saleitem_set.all()
    if delete_me:
        queryset = queryset.exclude(id=sale_item.id)
    total_amount = 0
    try:
        show_amount_as_pre_tax = action.type.storemanagementactiontype.show_amount_as_pre_tax
    except (AttributeError, StoreManagementActionType.DoesNotExist):
        show_amount_as_pre_tax = False
    for item in queryset:
        pre_tax_value = item.pre_tax_price * item.quantity
        if show_amount_as_pre_tax:
            total_amount += pre_tax_value
        else:
            total_amount += pre_tax_value * (100 + item.vat_rate.rate) / 100
    action.amount = total_amount
    action.save()


def on_save_sale_item(sender, instance, created, **kwargs):
    """update the corresponding action amount when item is added or updated"""
    update_action_amount(instance, False)


def on_delete_sale_item(sender, instance, **kwargs):
    """update the corresponding action amount when item is deleted"""
    update_action_amount(instance, True)


post_save.connect(on_save_sale_item, sender=SaleItem)
pre_delete.connect(on_delete_sale_item, sender=SaleItem)


def create_action_sale(sender, instance, created, **kwargs):
    """create sale automatically"""
    action = instance
    if action.type and StoreManagementActionType.objects.filter(action_type=action.type).exists():
        try:
            #It would raise exception if sale doesn't exist
            action.sale
        except Sale.DoesNotExist:
            Sale.objects.create(action=action)

post_save.connect(create_action_sale, sender=Action)


def on_action_cloned(sender, original_action, new_action, **kwargs):
    """clone the associated sale when an action is cloned"""
    try:
        if original_action.sale and new_action.sale:
            original_action.sale.clone(new_action.sale)
    except Sale.DoesNotExist:
        pass

action_cloned.connect(on_action_cloned, sender=Action)