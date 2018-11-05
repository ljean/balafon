# -*- coding: utf-8 -*-
"""models"""

from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal, InvalidOperation
import os.path
from six import string_types
import traceback
import xlrd

from django.db import models
from django.db.models import Q, Max
from django.db.models.signals import pre_delete, post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, ugettext

from sorl.thumbnail import default as sorl_thumbnail

from balafon.Crm.models import Action, ActionMenu, ActionStatus, ActionType, Group
from balafon.Crm.signals import action_cloned
from balafon.Store.settings import get_thumbnail_crop, get_thumbnail_size, get_image_crop, get_image_size
from balafon.Store.utils import round_currency


@python_2_unicode_compatible
class StoreManagementActionType(models.Model):
    """
    Define if an action type is linked to the store.
    If so it will be possible to link a Sale with an Action of this ActionType
    """
    action_type = models.OneToOneField(ActionType)
    template_name = models.CharField(
        default='', blank=True, max_length=100, verbose_name=_('template name'),
        help_text=_('Set the name of a custom template for commercial document')
    )
    show_amount_as_pre_tax = models.BooleanField(
        default=True,
        verbose_name=_('Show amount as pre-tax'),
        help_text=_(
            'The action amount will be update with pre-tax total if checked and with tax-included total if not'
        )
    )
    default_readonly_status = models.ForeignKey(
        ActionStatus, blank=True, verbose_name=_('default readonly status'), null=True, default=None,
        on_delete=models.SET_NULL, related_name="+"
    )
    readonly_status = models.ManyToManyField(
        ActionStatus, blank=True, verbose_name=_('readonly status'),
        help_text=_('When action has one of these status, it is not possible to modify a commercial document')
    )
    references_text = models.TextField(
        blank=True, default="", verbose_name=_("references text"),
        help_text=_("this text will be added at the bottom of the commercial document")
    )

    class Meta:
        verbose_name = _("Store management action type")
        verbose_name_plural = _("Store management action types")

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

    def __str__(self):
        return "{0}".format(self.action_type)


@python_2_unicode_compatible
class VatRate(models.Model):
    """Tax : A VAT rate"""
    rate = models.DecimalField(verbose_name=_("vat rate"), max_digits=4, decimal_places=2)
    is_default = models.BooleanField(default=False, verbose_name=_("is default"))

    @property
    def name(self):
        return "{0}%".format(self.rate)

    class Meta:
        verbose_name = _("VAT rate")
        verbose_name_plural = _("VAT rates")
        ordering = ['rate']

    def save(self, *args, **kwargs):
        return_value = super(VatRate, self).save(*args, **kwargs)
        if self.is_default:
            VatRate.objects.exclude(id=self.id).update(is_default=False)
        return return_value

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Unit(models.Model):
    """a unit"""
    name = models.CharField(verbose_name=_("name"), max_length=200)

    class Meta:
        verbose_name = _("unit")
        verbose_name_plural = _("units")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PricePolicy(models.Model):

    APPLY_TO_ALL = 0
    APPLY_TO_ARTICLES = 1
    APPLY_TO_CATEGORIES = 2

    APPLY_TO_CHOICES = (
        (APPLY_TO_ALL, _('All')),
        (APPLY_TO_ARTICLES, _('Articles')),
        (APPLY_TO_CATEGORIES, _('Categories')),
    )

    POLICIES = (
        ('from_category', _('Inherit from category')),
        ('multiply_purchase_by_ratio', _('Multiply purchase price by ratio')),
    )

    name = models.CharField(max_length=100, verbose_name=_('name'))
    parameters = models.CharField(max_length=100, verbose_name=_('parameters'), blank=True, default='')
    policy = models.CharField(max_length=100, verbose_name=_('policy'), choices=POLICIES)
    apply_to = models.IntegerField(default=APPLY_TO_ALL, verbose_name=_('apply to'), choices=APPLY_TO_CHOICES)

    class Meta:
        verbose_name = _("Price policy")
        verbose_name_plural = _("Price policies")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class StoreItemCategory(models.Model):
    """something for organization of store items"""
    name = models.CharField(verbose_name=_("name"), max_length=200)
    order_index = models.IntegerField(verbose_name=_("order_index"), default=0)
    active = models.BooleanField(verbose_name=_("active"), default=True)
    icon = models.CharField(max_length=20, default="", blank=True)
    parent = models.ForeignKey(
        "StoreItemCategory", default=None, blank=True, null=True, verbose_name=_('parent category'),
        related_name="subcategories_set"
    )
    price_policy = models.ForeignKey(PricePolicy, default=None, blank=True, null=True, verbose_name=_('price policy'))
    default_image = models.ImageField(
        upload_to='storeitemcats', blank=True, default=None, null=True, verbose_name=_('image')
    )
    accounting_code = models.CharField(max_length=20, blank=True, default="", verbose_name=_('accounting code'))

    class Meta:
        verbose_name = _("Store item category")
        verbose_name_plural = _("Store item categories")
        ordering = ['order_index', 'name']

    def __str__(self):
        return self.name

    def get_all_articles(self):
        """returns all articles"""
        all_articles = []
        for article in self.storeitem_set.all():
            all_articles.append(article)
        for sub_category in self.subcategories_set.all():
            all_articles.extend(sub_category.get_all_articles())
        return all_articles

    def get_sub_categories(self):
        """returns all sub cartegories"""
        all_categories = []
        for sub_category in self.subcategories_set.all():
            all_categories.append(sub_category)
            all_categories.extend(sub_category.get_sub_categories())
        return all_categories

    def get_all_articles_count(self):
        """returns all articles"""
        all_articles_count = self.storeitem_set.count()
        for sub_category in self.subcategories_set.all():
            all_articles_count += sub_category.get_all_articles_count()
        return all_articles_count
    get_all_articles_count.short_description = _('Articles total count')

    def get_articles_count(self):
        """returns articles count"""
        return self.storeitem_set.count()
    get_articles_count.short_description = _('Articles count')

    def get_children_count(self):
        """returns children category count"""
        return self.subcategories_set.count()
    get_children_count.short_description = _('Sub-categories count')

    def get_path_name(self):
        """returns name with all parents"""
        if self.parent:
            return '{0} > {1}'.format(self.parent.get_path_name(), self.name)
        else:
            return self.name

    def get_accounting_code(self):
        if self.accounting_code:
            return self.accounting_code
        elif self.parent:
            return self.parent.get_accounting_code()
        return ""

    def save(self, *args, **kwargs):
        """Save category"""

        self.name = self.name.strip()
        ret = super(StoreItemCategory, self).save()

        # Merge categories with same name
        siblings = StoreItemCategory.objects.filter(name=self.name, parent=self.parent).exclude(id=self.id)
        for sibling in siblings:
            for article in sibling.storeitem_set.all():
                article.category = self
                article.save()

            for sub_category in sibling.subcategories_set.all():
                sub_category.parent = self
                sub_category.save()

            sibling.delete()

        # Recalculate price for all articles in this category
        for article in self.get_all_articles():
            article.calculate_price()

        return ret


@python_2_unicode_compatible
class StoreItemTag(models.Model):
    """something for finding store items more easily"""
    name = models.CharField(verbose_name=_("name"), max_length=200)
    order_index = models.IntegerField(verbose_name=_("order_index"), default=0)
    active = models.BooleanField(verbose_name=_("active"), default=True)
    icon = models.CharField(max_length=20, default="", blank=True)
    show_always = models.BooleanField(verbose_name=_("show always"), default=True)

    class Meta:
        verbose_name = _("Store item tag")
        verbose_name_plural = _("Store item tags")
        ordering = ['order_index', 'name']

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Discount(models.Model):
    """a discount on a store item price"""
    name = models.CharField(verbose_name=_('name'), max_length=100)
    short_name = models.CharField(verbose_name=_('short name'), max_length=100, default="", blank=True)
    tags = models.ManyToManyField(StoreItemTag, blank=True, verbose_name=_('tags'))
    quantity = models.DecimalField(
        default=0, max_digits=9, decimal_places=2, verbose_name=_('quantity')
    )
    rate = models.DecimalField(
        default=0, max_digits=4, decimal_places=2, verbose_name=_('rate')
    )
    active = models.BooleanField(
        default=False,
        verbose_name=_('active'),
        help_text=_('Only active discounts are taken into account on a new purchase')
    )

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")
        ordering = ['rate', 'name']

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        return self.short_name or self.name

    def calculate_discount(self, sale_item):
        """calculate a discount on a sale item"""
        if sale_item.quantity >= self.quantity:
            return round_currency(sale_item.raw_total_price() * self.rate / Decimal(100))
        return None


@python_2_unicode_compatible
class Brand(models.Model):
    """A brand : cola-cola, peugeot or whatever"""
    name = models.CharField(max_length=100, verbose_name=_('name'))

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        return super(Brand, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Supplier(models.Model):
    """supplier"""
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Certificate(models.Model):
    """certificate"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="certificates", blank=True, default="")

    @property
    def image(self):
        if self.logo:
            return self.logo.url

    class Meta:
        verbose_name = _("certificate")
        verbose_name_plural = _("certificates")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PriceClass(models.Model):
    """price class"""
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.CharField(max_length=100, blank=True, default='', verbose_name=_('Description'))
    discounts = models.ManyToManyField(Discount, blank=True, verbose_name=_('Discount'))

    class Meta:
        verbose_name = _("Price class")
        verbose_name_plural = _("Price classes")

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class StoreItem(models.Model):
    """something than can be buy in this store"""

    name = models.CharField(verbose_name=_("name"), max_length=200)
    category = models.ForeignKey(StoreItemCategory, verbose_name=_("category"))
    tags = models.ManyToManyField(StoreItemTag, blank=True, verbose_name=_("tags"))
    vat_rate = models.ForeignKey(VatRate, verbose_name=_("VAT rate"))
    pre_tax_price = models.DecimalField(
        verbose_name=_("pre-tax price"), max_digits=11, decimal_places=4
    )
    stock_count = models.DecimalField(
        default=None, verbose_name=_("stock count"), blank=True, null=True, max_digits=9, decimal_places=2
    )
    stock_threshold = models.DecimalField(
        default=None, verbose_name=_("stock threshold"), blank=True, null=True, max_digits=9, decimal_places=2
    )
    purchase_price = models.DecimalField(
        verbose_name=_("purchase price"), max_digits=9, decimal_places=2, blank=True, default=None, null=True
    )
    unit = models.ForeignKey(Unit, blank=True, default=None, null=True)
    brand = models.ForeignKey(Brand, default=None, blank=True, null=True, verbose_name=_('brand'))
    reference = models.CharField(max_length=100, default='', blank=True, verbose_name=_('reference'))
    imported_by = models.ForeignKey(
        'StoreItemImport', default=None, blank=True, null=True, verbose_name=_('imported by')
    )
    price_policy = models.ForeignKey(PricePolicy, default=None, blank=True, null=True, verbose_name=_('price policy'))
    available = models.BooleanField(default=True, verbose_name=_('Available'))
    published = models.BooleanField(default=True, verbose_name=_('Published'))
    supplier = models.ForeignKey(Supplier, verbose_name=_('Supplier'), blank=True, default=None, null=True)
    price_class = models.ForeignKey(PriceClass, default=None, null=True, blank=True, verbose_name=_("price class"))
    certificates = models.ManyToManyField(Certificate, blank=True, verbose_name=_("certificate"))
    only_for_groups = models.ManyToManyField(
        Group, blank=True, verbose_name=_("only for groups"),
        help_text=_('If defined, only members of these groups will be able to see the item')
    )
    origin = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Origine'))
    image = models.ImageField(upload_to='storeitems', blank=True, default=None, null=True, verbose_name=_('image'))
    description = models.TextField(blank=True, verbose_name=_('description'), default="")
    item_accounting_code = models.CharField(max_length=20, blank=True, default="", verbose_name=_('accounting code'))

    class Meta:
        verbose_name = _("Store item")
        verbose_name_plural = _("Store items")
        ordering = ['name']

    def __str__(self):
        return '{0} > {1}{2}'.format(self.category, self.name, ' ({0})'.format(self.brand) if self.brand else '')

    def _to_decimal(self, value):
        if value is None:
            value = 0
        return Decimal("{0:.2f}".format(value, 2))

    def _to_vat_incl(self, value):
        if value is None:
            value = 0
        if self.vat_rate:
            vat_value = self.vat_rate.rate
        else:
            vat_value = 0
        return self._to_decimal(value * (1 + vat_value / 100))

    def vat_incl_price(self):
        """VAT inclusive price"""
        return self._to_vat_incl(self.pre_tax_price)
    vat_incl_price.short_description = _("VAT inclusive price")

    def vat_incl_price_with_alert(self):
        """VAT inclusive price"""
        price = self.vat_incl_price()
        calculated_pre_tax_price = self.get_calculated_price()
        if calculated_pre_tax_price is not None:
            calculated_price = self._to_vat_incl(calculated_pre_tax_price)
            if calculated_price != price:
                return '{0} <div style="color:red">Attention! calcul = {1}</div>'.format(price, calculated_price)
        return '{0}'.format(price)

    vat_incl_price_with_alert.short_description = _("VAT inclusive price")
    vat_incl_price_with_alert.allow_tags = True

    def get_admin_link(self):
        try:
            return '<a href="{0}" target="_extra_admin">{1}</a>'.format(
                reverse("admin:Store_storeitem_change", args=[self.id]), ugettext('Edit')
            )
        except NoReverseMatch:
            return ''
    get_admin_link.short_description = 'Url'
    get_admin_link.allow_tags = True

    def fullname(self):
        properties = []
        for the_property in StoreItemProperty.objects.filter(in_fullname=True):
            try:
                property_value = StoreItemPropertyValue.objects.get(property=the_property, item=self)
                properties.append(property_value.value)
            except StoreItemPropertyValue.DoesNotExist:
                pass
        if properties:
            return '{0} ({1})'.format(self.name, ', '.join(properties))
        return self.name
    fullname.short_description = _('Name')

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

    @property
    def public_properties(self):
        """get an dict of the public properties: name and values"""
        public_properties = {}
        for the_property in StoreItemProperty.objects.filter(is_public=True):
            try:
                property_value = StoreItemPropertyValue.objects.get(property=the_property, item=self)
            except StoreItemPropertyValue.DoesNotExist:
                property_value = None
            public_properties[the_property.name] = property_value.value
        return public_properties

    @property
    def discounts(self):
        """return all available discounts for this store item"""
        return Discount.objects.filter(
            active=True
        ).filter(
            Q(tags__in=self.tags.all()) | Q(priceclass=self.price_class, priceclass__isnull=False)
        ).distinct().order_by('quantity')

    def has_stock_threshold_alert(self):
        """returns True if stock is below threshold"""
        if self.stock_count is not None and self.stock_threshold is not None:
            return self.stock_count <= self.stock_threshold
        return False

    def stock_threshold_alert(self):
        """
        return threshold value with warning sign if stock is below this value
        To be used in admin
        """
        alert_text = ""
        if self.has_stock_threshold_alert():
            alert_text = '<img src="{0}store/img/warning-sign.png" />'.format(settings.STATIC_URL)
        return "{0} {1}".format(
            self.stock_threshold if self.stock_threshold is not None else "",
            alert_text
        ).strip()

    stock_threshold_alert.short_description = _("Stock threshold")
    stock_threshold_alert.allow_tags = True

    def get_calculated_price(self):
        """calculate article price according to the defined policy"""

        price_policy = self.price_policy.policy if self.price_policy else ''
        policy_parameters = self.price_policy.parameters if self.price_policy else ''

        # look for actual policy price
        if price_policy == 'from_category':
            category = self.category
            while price_policy == 'from_category':
                if category and category.price_policy:
                    price_policy = category.price_policy.policy
                    policy_parameters = category.price_policy.parameters
                else:
                    price_policy = ''

                if price_policy == 'from_category':
                    category = category.parent

        if price_policy == 'multiply_purchase_by_ratio' and self.purchase_price is not None:
            return self.purchase_price * Decimal(policy_parameters)

    def calculate_price(self):
        """calculate article price according to the defined policy"""
        calculated_price = self.get_calculated_price()
        if calculated_price is not None:
            self.pre_tax_price = calculated_price
            super(StoreItem, self).save()

    def as_thumbnail(self):
        size = get_thumbnail_size()
        crop = get_thumbnail_crop()
        image = self.image
        if not image:
            image = self.category.default_image
        if image:
            return sorl_thumbnail.backend.get_thumbnail(image.file, size, crop=crop).url

    def as_image(self):
        size = get_image_size()
        crop = get_image_crop()
        image = self.image
        if not image:
            image = self.category.default_image
        if image:
            return sorl_thumbnail.backend.get_thumbnail(image.file, size, crop=crop).url

    @property
    def imported_by_file(self):
        if self.imported_by:
            try:
                return self.imported_by.path
            except Exception as err:
                return str(err)
        else:
            return "-"

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        ret = super(StoreItem, self).save(*args, **kwargs)
        self.calculate_price()
        return ret

    def root_category(self):
        if self.category and self.category.parent:
            parent = self.category.parent
            while parent.parent:
                parent = parent.parent
            return parent

    @property
    def accounting_code(self):
        if self.item_accounting_code:
            return self.item_accounting_code
        elif self.category:
            return self.category.get_accounting_code()
        return ""


@python_2_unicode_compatible
class StoreItemProperty(models.Model):
    """a property for a store item: DLC, Colisage..."""
    name = models.CharField(max_length=100, verbose_name=_('name'))
    label = models.CharField(max_length=100, verbose_name=_('label'), default='', blank=True)
    in_fullname = models.BooleanField(
        default=False, verbose_name=_('in fullname'), help_text=_('is inserted in fullname if checked')
    )
    is_public = models.BooleanField(
        default=False, verbose_name=_('is public'), help_text=_('returned in public API')
    )

    class Meta:
        verbose_name = _("Store item: property value")
        verbose_name_plural = _("Store item: properties")

    def __str__(self):
        return self.label or self.name


@python_2_unicode_compatible
class StoreItemImport(models.Model):
    """Makes possible to import store item"""
    data = models.FileField(
        upload_to='store_item_imports',
        verbose_name=_("Import file"),
        help_text=_('An Excel file (*.xls) with the data')
    )
    tags = models.ManyToManyField(
        StoreItemTag,
        blank=True,
        verbose_name=_("tags"),
        help_text=_('Tags that can be added to the items')
    )
    fields = models.CharField(
        max_length=300,
        default='name,brand,reference,category,purchase_price,vat_rate',
        verbose_name=_("fields"),
        help_text=_("Fields to import in order: if the attribute doesn't exist, create a custom property")
    )
    last_import_date = models.DateTimeField(default=None, blank=True, null=True, verbose_name=_("last import"))
    import_error = models.TextField(default='', blank=True, verbose_name=_('import error'))
    is_successful = models.BooleanField(default=True, verbose_name=_('is successful'))
    ignore_first_line = models.BooleanField(default=True, verbose_name=_('ignore first line'))
    margin_rate = models.DecimalField(
        default=None, null=True, verbose_name=_('margin_rate'), max_digits=9, decimal_places=2
    )
    error_message = models.CharField(
        default='', blank=True, max_length=100, verbose_name=_('error message')
    )
    category_lines_mode = models.BooleanField(
        default=False, verbose_name=_('category-lines mode'),
        help_text=_('If checked, the store item category are expected as merged-cells header lines')
    )
    default_brand = models.CharField(
        default='', verbose_name=_('default Brand'), blank=True, max_length=50,
        help_text=_('If defined, it will be used if no brand is given')
    )
    supplier = models.ForeignKey(Supplier, verbose_name=_('Supplier'), blank=True, default=None, null=True)
    make_available = models.BooleanField(default=False, verbose_name=_('articles will be available if price is set'))

    class Meta:
        verbose_name = _("Store item import")
        verbose_name_plural = _("Store item imports")

    def __str__(self):
        return os.path.basename(self.data.file.name)

    def get_url(self):
        return self.data.url

    def _to_decimal(self, raw_value):
        """convert string to decimal"""
        return Decimal('{0}'.format(raw_value))

    def _to_string(self, raw_value):
        """to string"""
        return '{0}'.format(raw_value)

    def _to_brand(self, raw_value):
        """convert string to brand"""
        if raw_value:
            return Brand.objects.get_or_create(name=raw_value)[0]

    def _to_unit(self, raw_value):
        """convert string to unit"""
        if raw_value:
            return Unit.objects.get_or_create(name=raw_value)[0]

    def _to_supplier(self, raw_value):
        """convert string to provider"""
        if raw_value:
            return Supplier.objects.get_or_create(name=raw_value)[0]

    def _to_category(self, raw_value):
        """convert string to category"""
        raw_value = raw_value or ugettext('Uncategorized')
        return StoreItemCategory.objects.get_or_create(name=raw_value)[0]

    def _to_vat(self, raw_value):
        """convert string to vat"""
        if raw_value:
            raw_value = '{0}'.format(raw_value)  # float to string and the to decimal
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
        self.last_import_date = datetime.now()
        self.import_error = ''
        self.error_message = ''
        self.is_successful = False
        self.save()
        self.is_successful = True  # Assume everything will be ok :-)
        try:
            book = xlrd.open_workbook(file_contents=self.data.read(), formatting_info=True)
            sheet = book.sheet_by_index(0)

            fields = self.fields.split(',')

            fields_conversion = {
                'name': self._to_string,
                'reference': self._to_string,
                'brand': self._to_brand,
                'supplier': self._to_supplier,
                'unit': self._to_unit,
                'category': self._to_category,
                'vat_rate': self._to_vat,
            }

            price_conversion = {
                'purchase_price': self._to_decimal,
                'pre_tax_price': self._to_decimal,
            }

            if self.category_lines_mode:
                category_lines = [line[0] for line in sheet.merged_cells]
            else:
                category_lines = []
            last_category = ''
            for row_index in range(sheet.nrows):

                if self.ignore_first_line and row_index == 0:
                    # ignore
                    continue

                raw_values = [sheet.cell(rowx=row_index, colx=col_index).value for col_index in range(sheet.ncols)]

                raw_values = [
                    raw_value.strip() if isinstance(raw_value, string_types) else raw_value
                    for raw_value in raw_values
                ]

                if not any(raw_values):
                    # blank lines
                    continue

                if row_index in category_lines:
                    last_category = sheet.cell(rowx=row_index, colx=0).value
                    continue

                store_item = StoreItem(supplier=self.supplier)
                properties = []

                # for all fields
                for index, field in enumerate(fields):

                    if index < len(raw_values):
                        raw_value = raw_values[index]
                    else:
                        raw_value = None

                    if field in fields_conversion:
                        # call the function associated with this field
                        value = fields_conversion[field](raw_value)
                        if value:
                            setattr(store_item, field, value)
                    elif field in price_conversion:
                        try:
                            value = price_conversion[field](raw_value)
                            setattr(store_item, field, value)
                        except (ValueError, InvalidOperation):
                            setattr(store_item, field, Decimal(0))
                    else:
                        # for extra fields : create a property (once the object has been saved)
                        if raw_value:
                            properties.append((field, raw_value))

                if not store_item.name:
                    # empty line : ignore
                    continue

                if ('brand' not in fields or not store_item.brand) and self.default_brand:
                    store_item.brand = self._to_brand(self.default_brand)

                if 'pre_tax_price' not in fields:
                    if 'purchase_price' in fields:
                        margin_rate = self.margin_rate or 1
                        store_item.pre_tax_price = store_item.purchase_price * margin_rate
                    else:
                        store_item.pre_tax_price = 0

                store_item.available = self.make_available
                if not store_item.pre_tax_price:
                    store_item.available = False

                if 'vat_rate' not in fields:
                    store_item.vat_rate = self._to_vat(None)  # force default

                if 'category' not in fields:
                    if last_category:
                        store_item.category = self._to_category(last_category)
                    else:
                        store_item.category = self._to_category(None)

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
            try:
                self.error_message = '{0}'.format(msg)[:100]
            except:
                self.error_message = "!!!!!"

        self.save()


@python_2_unicode_compatible
class StoreItemPropertyValue(models.Model):
    """The value of a property for a given item"""
    item = models.ForeignKey(StoreItem, verbose_name=_('item'))
    property = models.ForeignKey(StoreItemProperty, verbose_name=_('property'))
    value = models.CharField(max_length=100, verbose_name=_('value'), blank=True, default='')

    class Meta:
        verbose_name = _("Store item: property value")
        verbose_name_plural = _("Store item: property values")

    def __str__(self):
        return '{0}'.format(self.property)


@python_2_unicode_compatible
class DeliveryPoint(models.Model):
    """Where to get a sale"""
    name = models.CharField(max_length=100, verbose_name=_("name"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Delivery point")
        verbose_name_plural = _("Delivery points")
        ordering = ('name',)


@python_2_unicode_compatible
class SaleAnalysisCode(models.Model):
    """Where to get a sale"""
    name = models.CharField(max_length=100, verbose_name=_("name"))
    action_type = models.ForeignKey(ActionType, verbose_name=_('action type'), default=None, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Analysis code")
        verbose_name_plural = _("Analysis codes")
        ordering = ('name',)


@python_2_unicode_compatible
class Sale(models.Model):
    """A sale"""
    action = models.OneToOneField(Action, verbose_name=_("action"))
    delivery_point = models.ForeignKey(
        DeliveryPoint, default=None, blank=True, null=True, verbose_name=_("delivery point")
    )
    analysis_code = models.ForeignKey(
        SaleAnalysisCode, default=None, blank=True, null=True, verbose_name=_("analysis code")
    )

    def get_references_text(self):
        """This text will be added at the bottom of the commercial document"""
        text = ""
        if self.action and self.action.type:
            try:
                text = StoreManagementActionType.objects.get(action_type=self.action.type).references_text
            except StoreManagementActionType.DoesNotExist:
                pass
        return text

    def vat_total_amounts(self):
        """returns amount of VAT by VAT rate"""
        # calculate price for each VAT rate
        total_by_vat = {}
        pre_tax_by_vat = {}
        for sale_item in self.saleitem_set.all():
            if sale_item.vat_rate:
                if sale_item.vat_rate.id in total_by_vat:
                    total_by_vat[sale_item.vat_rate.id] += sale_item.total_vat_price(round_value=False)
                    pre_tax_by_vat[sale_item.vat_rate.id] += sale_item.pre_tax_total_price(round_value=False)
                else:
                    total_by_vat[sale_item.vat_rate.id] = sale_item.total_vat_price(round_value=False)
                    pre_tax_by_vat[sale_item.vat_rate.id] = sale_item.pre_tax_total_price(round_value=False)
        # returns vat rate in order
        vat_totals = []
        for vat_rate in sorted(VatRate.objects.all(), key=lambda _vat: _vat.rate):
            if vat_rate.id in total_by_vat:
                vat_totals.append(
                    {
                        'vat_rate': vat_rate,
                        'pre_tax_total': round_currency(pre_tax_by_vat[vat_rate.id]),
                        'amount': round_currency(total_by_vat[vat_rate.id])
                    }
                )
        return vat_totals

    def accounting_code_amounts(self):
        """returns amount by code"""
        # calculate price for each VAT rate
        total_vat_by_code = {}
        pre_tax_by_code = {}
        total_tax_incl_by_code = {}
        for sale_item in self.saleitem_set.all():
            if sale_item.item:
                accounting_code = sale_item.item.accounting_code
            else:
                accounting_code = ''

            if accounting_code in total_vat_by_code:
                total_vat_by_code[accounting_code] += sale_item.total_vat_price(round_value=False)
                pre_tax_by_code[accounting_code] += sale_item.pre_tax_total_price(round_value=False)
                total_tax_incl_by_code[accounting_code] += sale_item.vat_incl_total_price(round_value=False)
            else:
                total_vat_by_code[accounting_code] = sale_item.total_vat_price(round_value=False)
                pre_tax_by_code[accounting_code] = sale_item.pre_tax_total_price(round_value=False)
                total_tax_incl_by_code[accounting_code] = sale_item.vat_incl_total_price(round_value=False)

        # returns codes in order
        accounting_data = []
        accounting_codes = sorted(total_vat_by_code.keys())
        for accounting_code in accounting_codes:
            accounting_data.append(
                {
                    'accounting_code': accounting_code,
                    'pre_tax_total': round_currency(pre_tax_by_code[accounting_code]),
                    'vat_total': round_currency(total_vat_by_code[accounting_code]),
                    'vat_incl_total': round_currency(total_tax_incl_by_code[accounting_code]),
                }
            )
        return accounting_data

    def total_vat(self):
        """returns amount of VAT by VAT rate"""
        # calculate price for each VAT rate
        total_vat = Decimal(0)
        for sale_item in self.saleitem_set.all():
            total_vat += sale_item.quantity * sale_item.vat_price()
        return round_currency(total_vat)

    def vat_incl_total_price(self):
        """return total price of the command"""
        total = Decimal(0)
        for sale_item in self.saleitem_set.all():
            total += sale_item.vat_incl_total_price(round_value=False)
        return round_currency(total)

    def pre_tax_total_price(self):
        """return total price of the command"""
        total = Decimal(0)
        for sale_item in self.saleitem_set.all():
            total += sale_item.pre_tax_total_price()
        return total

    @property
    def creation_date(self):
        return self.action.created
    creation_date.fget.short_description = _('Creation date')

    class Meta:
        verbose_name = _("Sale")
        verbose_name_plural = _("Sales")
        ordering = ['-action__created']

    def __str__(self):
        contacts = ', '.join(['{0}'.format(item) for item in self.action.contacts.all()])
        entities = ', '.join(['{0}'.format(item) for item in self.action.entities.all()])
        customers = ', '.join([item for item in (contacts, entities) if item])
        if customers:
            return '{0} - {1}'.format(self.action.planned_date.date(), customers)
        else:
            return '{0}'.format(self.action.planned_date.date())

    def clone(self, new_sale):
        """clone a sale: clone its items"""
        for item in self.saleitem_set.all():
            item.clone(new_sale)

    def calculate_discounts(self):
        """calculate the discount for a product"""
        for sale_item in self.saleitem_set.all():
            sale_item.calculate_discount()
            sale_item.save()

    def save(self, *args, **kwargs):
        """save and recalculate the discounts"""
        ret = super(Sale, self).save(*args, **kwargs)
        self.calculate_discounts()
        return ret


@python_2_unicode_compatible
class Favorite(models.Model):
    user = models.ForeignKey(User, verbose_name=_('user'))
    item = models.ForeignKey(StoreItem, verbose_name=_('store item'))

    def __str__(self):
        return '{0} - {1}'.format(self.user, self.item)

    class Meta:
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")


@python_2_unicode_compatible
class SaleItem(models.Model):
    """details about the sold item"""
    sale = models.ForeignKey(Sale)
    item = models.ForeignKey(StoreItem, blank=True, default=None, null=True)
    quantity = models.DecimalField(verbose_name=_("quantity"), max_digits=9, decimal_places=2)
    vat_rate = models.ForeignKey(VatRate, verbose_name=_("VAT rate"), blank=True, null=True, default=None)
    pre_tax_price = models.DecimalField(verbose_name=_("pre-tax price"), max_digits=11, decimal_places=4)
    text = models.TextField(verbose_name=_("Text"), max_length=3000, default='', blank=True)
    order_index = models.IntegerField(default=0)
    is_blank = models.BooleanField(
        default=False, verbose_name=_('is blank'), help_text=_('displayed as an empty line')
    )
    discount = models.ForeignKey(Discount, blank=True, null=True, default=None)
    no_quantity = models.BooleanField(
        default=False, verbose_name=_('no quantity'), help_text=_('quantity and unit price are not shown on bill')
    )
    is_discount = models.BooleanField(
        default=False, verbose_name=_('is discount'), help_text=_('added after total on the bill')
    )
    percentage = models.DecimalField(
        verbose_name=_('percentage'), default=Decimal(100), max_digits=5, decimal_places=2,
        help_text=_('Only a percentage of the item price')
    )

    class Meta:
        verbose_name = _("Sale item")
        verbose_name_plural = _("Sales items")
        ordering = ['order_index']

    def __str__(self):
        if self.id:
            return _("{1} x {0}").format(self.item, self.quantity)
        else:
            return _("Sale item not set")

    def vat_incl_price(self, round_value=True):
        """VAT inclusive price"""
        value = self.unit_price() + self.vat_price(round_value=False)
        return round_currency(value) if round_value else value

    def total_vat_price(self, round_value=True):
        """VAT price * quantity"""
        value = self.vat_price(round_value=False) * self.quantity * (self.percentage / Decimal(100))
        return round_currency(value) if round_value else value

    def vat_price(self, round_value=True):
        """VAT price"""
        if self.is_blank:
            return Decimal(0)
        vat_rate = self.vat_rate.rate if self.vat_rate else Decimal(0)

        value = self.unit_price() * (vat_rate / Decimal(100))
        return round_currency(value) if round_value else value

    def vat_incl_total_price(self, round_value=True):
        """VAT inclusive price"""
        vat_incl_price = self.vat_incl_price(round_value=False) * self.quantity * (self.percentage / Decimal(100))
        return round_currency(vat_incl_price) if round_value else vat_incl_price

    def raw_total_price(self, round_value=True):
        """VAT inclusive price"""
        if self.is_blank:
            return Decimal(0)
        value = self.pre_tax_price * self.quantity
        return round_currency(value) if round_value else value

    def pre_tax_total_price(self, round_value=False):
        """VAT inclusive price"""
        if self.is_blank:
            return Decimal(0)
        tax_total_price = self.unit_price(round_value=False) * self.quantity * (self.percentage / Decimal(100))
        return round_currency(tax_total_price) if round_value else tax_total_price

    def unit_price(self, round_value=False):
        """pre tax price with discount"""
        if self.is_blank:
            return Decimal(0)
        unit_price = self.pre_tax_price - self.calculate_discount()
        return round_currency(unit_price) if round_value else unit_price

    def save(self, *args, **kwargs):
        if self.order_index == 0:
            max_value = SaleItem.objects.filter(sale=self.sale).aggregate(
                max_value=Max('order_index')
            )['max_value'] or 0
            self.order_index = max_value + 1

        if self.is_blank:
            self.pre_tax_price = Decimal(0)
            self.quantity = 0
            self.item = None
            self.text = ''
            self.vat_rate = None

        self.calculate_discount()
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
            is_blank=self.is_blank,
            discount=self.discount,
            order_index=self.order_index
        )

    def calculate_discount(self):
        """calculate the discount"""
        max_discount = Decimal(0)
        better_discount = None
        if self.item:
            for discount in self.item.discounts:
                discount_value = discount.calculate_discount(self)
                if discount_value and discount_value > max_discount:
                    max_discount = discount_value
                    better_discount = discount
        if better_discount != self.discount:
            self.discount = better_discount

        if self.quantity:
            discount_price = max_discount / self.quantity
        else:
            discount_price = Decimal(0)
        return round_currency(discount_price)


def update_action_amount(sale, delete_sale_item=None):
    """update the corresponding action amount """
    action = sale.action
    queryset = sale.saleitem_set.all()
    if delete_sale_item:
        queryset = queryset.exclude(id=delete_sale_item.id)
    total_amount = 0
    try:
        show_amount_as_pre_tax = action.type.storemanagementactiontype.show_amount_as_pre_tax
    except (AttributeError, StoreManagementActionType.DoesNotExist):
        show_amount_as_pre_tax = False
    for item in queryset:
        if show_amount_as_pre_tax:
            total_amount += item.pre_tax_total_price()
        else:
            value = item.vat_incl_total_price(round_value=False)
            total_amount += value
    action.amount = round_currency(total_amount)
    action.save()


def on_save_sale_item(sender, instance, created, **kwargs):
    """update the corresponding action amount when item is added or updated"""
    update_action_amount(instance.sale)


def on_delete_sale_item(sender, instance, **kwargs):
    """update the corresponding action amount when item is deleted"""
    update_action_amount(instance.sale, instance)


post_save.connect(on_save_sale_item, sender=SaleItem)
pre_delete.connect(on_delete_sale_item, sender=SaleItem)


def create_action_sale(sender, instance, created, **kwargs):
    """create sale automatically"""
    action = instance
    if action.type and StoreManagementActionType.objects.filter(action_type=action.type).exists():
        try:
            # It would raise exception if sale doesn't exist
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


def freeze_readonly_action(sender, instance, created, **kwargs):
    """update the corresponding action amount when item is added or updated"""
    if instance.type and not instance.frozen:
        try:
            action_type_cfg = StoreManagementActionType.objects.get(action_type=instance.type)
            if instance.status in action_type_cfg.readonly_status.all():
                instance.frozen = True
                instance.save()
        except StoreManagementActionType.DoesNotExist:
            pass


post_save.connect(freeze_readonly_action, sender=Action)
