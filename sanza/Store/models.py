# -*- coding: utf-8 -*-
"""models"""

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete, post_save
from django.utils.translation import ugettext_lazy as _

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

    class Meta:
        verbose_name = _(u"Store item tag")
        verbose_name_plural = _(u"Store item tags")
        ordering = ['order_index', 'name']

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


class Sale(models.Model):
    """A sale"""
    action = models.OneToOneField(Action)

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