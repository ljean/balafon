# -*- coding: utf-8 -*-
"""models"""

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from sanza.Crm.models import Action


class VatRate(models.Model):
    """Tax : A VAT rate"""
    rate = models.DecimalField(verbose_name=_("vat rate"), max_digits=4, decimal_places=2)

    class Meta:
        verbose_name = _(u"VAT rate")
        verbose_name_plural = _(u"VAT rates")

    def __unicode__(self):
        return u"{0}%".format(self.rate)


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

    class Meta:
        verbose_name = _(u"Store item category")
        verbose_name_plural = _(u"Store item categories")

    def __unicode__(self):
        return self.name


class StoreItemTag(models.Model):
    """something for finding store items more easily"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)

    class Meta:
        verbose_name = _(u"Store item tag")
        verbose_name_plural = _(u"Store item tags")

    def __unicode__(self):
        return self.name


class StoreItem(models.Model):
    """something than can be buy in this store"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    category = models.ForeignKey(StoreItemCategory, verbose_name=_(u"category"))
    tags = models.ManyToManyField(StoreItemTag, blank=True, verbose_name=_(u"tags"))
    vat_rate = models.ForeignKey(VatRate, verbose_name=_(u"VAT rate"))
    pre_tax_price = models.DecimalField(verbose_name=_("pre-tax price"), max_digits=9, decimal_places=2)
    stock_count = models.IntegerField(default=None, verbose_name=_("stock count"), blank=True, null=True)
    stock_threshold = models.IntegerField(default=None, verbose_name=_("stock count"), blank=True, null=True)
    purchase_price = models.DecimalField(
        verbose_name=_("purchase price"), max_digits=9, decimal_places=2, blank=True, default=None, null=True
    )
    unit = models.ForeignKey(Unit, blank=True, default=None, null=True)

    class Meta:
        verbose_name = _(u"Store item")
        verbose_name_plural = _(u"Store items")

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


class ServiceItem(models.Model):
    """an extra service"""
    name = models.CharField(verbose_name=_(u"name"), max_length=500)
    vat_rate = models.ForeignKey(VatRate, verbose_name=_(u"VAT rate"))
    pre_tax_price = models.DecimalField(verbose_name=_("pre-tax price"), max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = _(u"Service item")
        verbose_name_plural = _(u"Service items")

    def __unicode__(self):
        return self.name


class Sale(models.Model):
    """A sale"""
    action = models.ForeignKey(Action, blank=True, default=None, null=True)
    store_items = models.ManyToManyField(StoreItem, through='StoreItemSale', blank=True)
    service_items = models.ManyToManyField(ServiceItem, blank=True)

    class Meta:
        verbose_name = _(u"Sale")
        verbose_name_plural = _(u"Sales")

    def __unicode__(self):
        return self.name


class StoreItemSale(models.Model):
    """details about the sold item"""
    sale = models.ForeignKey(Sale)
    item = models.ForeignKey(StoreItem)
    quantity = models.DecimalField(verbose_name=_("vat rate"), max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = _(u"Store item sale")
        verbose_name_plural = _(u"Store item sales")

    def __unicode__(self):
        return _(u"{1} x {0}").format(self.item, self.quantity)
