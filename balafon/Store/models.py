# -*- coding: utf-8 -*-
"""models"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import os.path
import traceback
import xlrd

from django.db import models
from django.db.models import Q, Max
from django.db.models.signals import pre_delete, post_save
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.translation import ugettext_lazy as _, ugettext

from balafon.Crm.models import Action, ActionMenu, ActionStatus, ActionType, Group
from balafon.Crm.signals import action_cloned
from balafon.Store.utils import round_currency


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
    references_text = models.TextField(
        blank=True, default="", verbose_name=_(u"references text"),
        help_text=_(u"this text will be added at the bottom of the commercial document")
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


class PricePolicy(models.Model):

    APPLY_TO_ALL = 0
    APPLY_TO_ARTICLES = 1
    APPLY_TO_CATEGORIES = 2

    APPLY_TO_CHOICES = (
        (APPLY_TO_ALL, _(u'All')),
        (APPLY_TO_ARTICLES, _(u'Articles')),
        (APPLY_TO_CATEGORIES, _(u'Categories')),
    )

    POLICIES = (
        ('from_category', _(u'Inherit from category')),
        ('multiply_purchase_by_ratio', _(u'Multiply purchase price by ratio')),
    )

    name = models.CharField(max_length=100, verbose_name=_(u'name'))
    parameters = models.CharField(max_length=100, verbose_name=_(u'parameters'), blank=True, default='')
    policy = models.CharField(max_length=100, verbose_name=_(u'policy'), choices=POLICIES)
    apply_to = models.IntegerField(default=APPLY_TO_ALL, verbose_name=_(u'apply to'), choices=APPLY_TO_CHOICES)

    class Meta:
        verbose_name = _(u"Price policy")
        verbose_name_plural = _(u"Price policies")

    def __unicode__(self):
        return self.name


class StoreItemCategory(models.Model):
    """something for organization of store items"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    order_index = models.IntegerField(verbose_name=_(u"order_index"), default=0)
    active = models.BooleanField(verbose_name=_(u"active"), default=True)
    icon = models.CharField(max_length=20, default="", blank=True)
    parent = models.ForeignKey(
        "StoreItemCategory", default=None, blank=True, null=True, verbose_name=_('parent category'),
        related_name="subcategories_set"
    )
    price_policy = models.ForeignKey(PricePolicy, default=None, blank=True, null=True, verbose_name=_(u'price policy'))

    class Meta:
        verbose_name = _(u"Store item category")
        verbose_name_plural = _(u"Store item categories")
        ordering = ['order_index', 'name']

    def __unicode__(self):
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
    get_all_articles_count.short_description = _(u'Articles total count')

    def get_articles_count(self):
        """returns articles count"""
        return self.storeitem_set.count()
    get_articles_count.short_description = _(u'Articles count')

    def get_children_count(self):
        """returns children category count"""
        return self.subcategories_set.count()
    get_children_count.short_description = _(u'Sub-categories count')

    def get_path_name(self):
        """returns name with all parents"""
        if self.parent:
            return u'{0} > {1}'.format(self.parent.get_path_name(), self.name)
        else:
            return self.name

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


class StoreItemTag(models.Model):
    """something for finding store items more easily"""
    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    order_index = models.IntegerField(verbose_name=_(u"order_index"), default=0)
    active = models.BooleanField(verbose_name=_(u"active"), default=True)
    icon = models.CharField(max_length=20, default="", blank=True)
    show_always = models.BooleanField(verbose_name=_(u"show always"), default=True)

    class Meta:
        verbose_name = _(u"Store item tag")
        verbose_name_plural = _(u"Store item tags")
        ordering = ['order_index', 'name']

    def __unicode__(self):
        return self.name


class Discount(models.Model):
    """a discount on a store item price"""
    name = models.CharField(verbose_name=_(u'name'), max_length=100)
    short_name = models.CharField(verbose_name=_(u'short name'), max_length=100, default="", blank=True)
    tags = models.ManyToManyField(StoreItemTag, blank=True, verbose_name=_(u'tags'))
    quantity = models.DecimalField(
        default=0, max_digits=9, decimal_places=2, verbose_name=_(u'quantity')
    )
    rate = models.DecimalField(
        default=0, max_digits=4, decimal_places=2, verbose_name=_(u'rate')
    )
    active = models.BooleanField(
        default=False,
        verbose_name=_(u'active'),
        help_text=_(u'Only active discounts are taken into account on a new purchase')
    )

    class Meta:
        verbose_name = _(u"Discount")
        verbose_name_plural = _(u"Discounts")
        ordering = ['rate', 'name']

    def __unicode__(self):
        return self.name

    @property
    def display_name(self):
        return self.short_name or self.name

    def calculate_discount(self, sale_item):
        """calculate a discount on a sale item"""
        if sale_item.quantity >= self.quantity:
            return round_currency(sale_item.raw_total_price() * self.rate / Decimal(100))
        return None


class Brand(models.Model):
    """A brand : cola-cola, peugeot or whatever"""
    name = models.CharField(max_length=100, verbose_name=_(u'name'))

    class Meta:
        verbose_name = _(u"Brand")
        verbose_name_plural = _(u"Brands")

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        return super(Brand, self).save(*args, **kwargs)


class Supplier(models.Model):
    """supplier"""
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _(u"Supplier")
        verbose_name_plural = _(u"Suppliers")

    def __unicode__(self):
        return self.name


class Certificate(models.Model):
    """certificate"""
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="certificates", blank=True, default="")

    @property
    def image(self):
        if self.logo:
            return self.logo.url

    class Meta:
        verbose_name = _(u"certificate")
        verbose_name_plural = _(u"certificates")

    def __unicode__(self):
        return self.name


class PriceClass(models.Model):
    """price class"""
    name = models.CharField(max_length=100, verbose_name=_(u'Name'))
    description = models.CharField(max_length=100, blank=True, default='', verbose_name=_(u'Description'))
    discounts = models.ManyToManyField(Discount, blank=True, verbose_name=_(u'Discount'))

    class Meta:
        verbose_name = _(u"Price class")
        verbose_name_plural = _(u"Price classes")

    def __unicode__(self):
        return self.name


class StoreItem(models.Model):
    """something than can be buy in this store"""

    name = models.CharField(verbose_name=_(u"name"), max_length=200)
    category = models.ForeignKey(StoreItemCategory, verbose_name=_(u"category"))
    tags = models.ManyToManyField(StoreItemTag, blank=True, verbose_name=_(u"tags"))
    vat_rate = models.ForeignKey(VatRate, verbose_name=_(u"VAT rate"))
    pre_tax_price = models.DecimalField(
        verbose_name=_(u"pre-tax price"), max_digits=9, decimal_places=2
    )
    stock_count = models.DecimalField(
        default=None, verbose_name=_(u"stock count"), blank=True, null=True, max_digits=9, decimal_places=2
    )
    stock_threshold = models.DecimalField(
        default=None, verbose_name=_(u"stock threshold"), blank=True, null=True, max_digits=9, decimal_places=2
    )
    purchase_price = models.DecimalField(
        verbose_name=_(u"purchase price"), max_digits=9, decimal_places=2, blank=True, default=None, null=True
    )
    unit = models.ForeignKey(Unit, blank=True, default=None, null=True)
    brand = models.ForeignKey(Brand, default=None, blank=True, null=True, verbose_name=_(u'brand'))
    reference = models.CharField(max_length=100, default='', blank=True, verbose_name=_(u'reference'))
    imported_by = models.ForeignKey(
        'StoreItemImport', default=None, blank=True, null=True, verbose_name=_(u'imported by')
    )
    price_policy = models.ForeignKey(PricePolicy, default=None, blank=True, null=True, verbose_name=_(u'price policy'))
    available = models.BooleanField(default=True, verbose_name=_(u'Available'))
    supplier = models.ForeignKey(Supplier, verbose_name=_('Supplier'), blank=True, default=None, null=True)
    price_class = models.ForeignKey(PriceClass, default=None, null=True, blank=True, verbose_name=_(u"price class"))
    certificates = models.ManyToManyField(Certificate, blank=True, verbose_name=_(u"certificate"))
    only_for_groups = models.ManyToManyField(
        Group, blank=True, verbose_name=_(u"only for groups"),
        help_text=_(u'If defined, only members of these groups will be able to see the item')
    )

    class Meta:
        verbose_name = _(u"Store item")
        verbose_name_plural = _(u"Store items")
        ordering = ['name']

    def __unicode__(self):
        return u'{0} > {1}{2}'.format(self.category, self.name, u' ({0})'.format(self.brand) if self.brand else '')

    def vat_incl_price(self):
        """VAT inclusive price"""
        return Decimal("{0:.2f}".format(
            round(self.pre_tax_price * (1 + self.vat_rate.rate / 100), 2)
        ))
    vat_incl_price.short_description = _(u"VAT inclusive price")

    def get_admin_link(self):
        try:
            return u'<a href="{0}" target="_extra_admin">{1}</a>'.format(
                reverse("admin:Store_storeitem_change", args=[self.id]), ugettext(u'Edit')
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
            return u'{0} ({1})'.format(self.name, u', '.join(properties))
        return self.name
    fullname.short_description = _(u'Name')

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
            alert_text = u'<img src="{0}store/img/warning-sign.png" />'.format(settings.STATIC_URL)
        return u"{0} {1}".format(
            self.stock_threshold if self.stock_threshold is not None else "",
            alert_text
        ).strip()

    stock_threshold_alert.short_description = _(u"Stock threshold")
    stock_threshold_alert.allow_tags = True

    def calculate_price(self):
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
            self.pre_tax_price = self.purchase_price * Decimal(policy_parameters)
            super(StoreItem, self).save()

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        ret = super(StoreItem, self).save(*args, **kwargs)
        self.calculate_price()
        return ret


class StoreItemProperty(models.Model):
    """a property for a store item: DLC, Colisage..."""
    name = models.CharField(max_length=100, verbose_name=_(u'name'))
    label = models.CharField(max_length=100, verbose_name=_(u'label'), default='', blank=True)
    in_fullname = models.BooleanField(
        default=False, verbose_name=_(u'in fullname'), help_text=_(u'is inserted in fullname if checked')
    )
    is_public = models.BooleanField(
        default=False, verbose_name=_(u'is public'), help_text=_(u'returned in public API')
    )

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
    category_lines_mode = models.BooleanField(
        default=False, verbose_name=_('category-lines mode'),
        help_text=_(u'If checked, the store item category are expected as merged-cells header lines')
    )
    default_brand = models.CharField(
        default='', verbose_name=_(u'default Brand'), blank=True, max_length=50,
        help_text=_(u'If defined, it will be used if no brand is given')
    )
    supplier = models.ForeignKey(Supplier, verbose_name=_('Supplier'), blank=True, default=None, null=True)
    make_available = models.BooleanField(default=False, verbose_name=_(u'articles will be available if price is set'))

    class Meta:
        verbose_name = _(u"Store item import")
        verbose_name_plural = _(u"Store item imports")

    def __unicode__(self):
        return os.path.basename(self.data.file.name)

    def get_url(self):
        return self.data.url

    def _to_decimal(self, raw_value):
        """convert string to decimal"""
        return Decimal(u'{0}'.format(raw_value))

    def _to_string(self, raw_value):
        """to string"""
        return unicode(raw_value)

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
            raw_value = u'{0}'.format(raw_value)  # float to string and the to decimal
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
        self.import_error = u''
        self.error_message = u''
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
            last_category = u''
            for row_index in xrange(sheet.nrows):

                if self.ignore_first_line and row_index == 0:
                    #ignore
                    continue

                raw_values = [sheet.cell(rowx=row_index, colx=col_index).value for col_index in xrange(sheet.ncols)]

                raw_values = [
                    raw_value.strip() if type(raw_value) is unicode else raw_value
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
                self.error_message = unicode(msg)[:100]
            except:
                self.error_message = "!!!!!"

        self.save()


class StoreItemPropertyValue(models.Model):
    """The value of a property for a given item"""
    item = models.ForeignKey(StoreItem, verbose_name=_(u'item'))
    property = models.ForeignKey(StoreItemProperty, verbose_name=_(u'property'))
    value = models.CharField(max_length=100, verbose_name=_(u'value'), blank=True, default='')

    class Meta:
        verbose_name = _(u"Store item: property value")
        verbose_name_plural = _(u"Store item: property values")

    def __unicode__(self):
        return u'{0}'.format(self.property)


class DeliveryPoint(models.Model):
    """Where to get a sale"""
    name = models.CharField(max_length=100, verbose_name=_(u"name"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Delivery point")
        verbose_name_plural = _(u"Delivery points")
        ordering = ('name',)


class SaleAnalysisCode(models.Model):
    """Where to get a sale"""
    name = models.CharField(max_length=100, verbose_name=_(u"name"))
    action_type = models.ForeignKey(ActionType, verbose_name=_(u'action type'), default=None, blank=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Analysis code")
        verbose_name_plural = _(u"Analysis codes")
        ordering = ('name',)


class Sale(models.Model):
    """A sale"""
    action = models.OneToOneField(Action, verbose_name=_(u"action"))
    delivery_point = models.ForeignKey(
        DeliveryPoint, default=None, blank=True, null=True, verbose_name=_(u"delivery point")
    )
    analysis_code = models.ForeignKey(
        SaleAnalysisCode, default=None, blank=True, null=True, verbose_name=_(u"analysis code")
    )

    def get_references_text(self):
        """This text will be added at the bottom of the commercial document"""
        text = u""
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

    def vat_incl_total_price(self):
        """return total price of the command"""
        total = Decimal(0)
        for sale_item in self.saleitem_set.all():
            total += sale_item.vat_incl_total_price()
        return total

    def pre_tax_total_price(self):
        """return total price of the command"""
        total = Decimal(0)
        for sale_item in self.saleitem_set.all():
            total += sale_item.pre_tax_total_price()
        return total

    @property
    def creation_date(self):
        return self.action.created
    creation_date.fget.short_description = _(u'Creation date')

    class Meta:
        verbose_name = _(u"Sale")
        verbose_name_plural = _(u"Sales")
        ordering = ['-action__created']

    def __unicode__(self):
        contacts = u', '.join([u'{0}'.format(item) for item in self.action.contacts.all()])
        entities = u', '.join([u'{0}'.format(item) for item in self.action.entities.all()])
        customers = u', '.join([item for item in (contacts, entities) if item])
        if customers:
            return u'{0} - {1}'.format(self.action.planned_date.date(), customers)
        else:
            return u'{0}'.format(self.action.planned_date.date())

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


class Favorite(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    item = models.ForeignKey(StoreItem, verbose_name=_(u'store item'))

    def __unicode__(self):
        return u'{0} - {1}'.format(self.user, self.item)

    class Meta:
        verbose_name = _(u"Favorite")
        verbose_name_plural = _(u"Favorites")


class SaleItem(models.Model):
    """details about the sold item"""
    sale = models.ForeignKey(Sale)
    item = models.ForeignKey(StoreItem, blank=True, default=None, null=True)
    quantity = models.DecimalField(verbose_name=_(u"quantity"), max_digits=9, decimal_places=2)
    vat_rate = models.ForeignKey(VatRate, verbose_name=_(u"VAT rate"), blank=True, null=True, default=None)
    pre_tax_price = models.DecimalField(verbose_name=_(u"pre-tax price"), max_digits=9, decimal_places=2)
    text = models.TextField(verbose_name=_(u"Text"), max_length=3000, default='', blank=True)
    order_index = models.IntegerField(default=0)
    is_blank = models.BooleanField(
        default=False, verbose_name=_(u'is blank'), help_text=_(u'displayed as an empty line')
    )
    discount = models.ForeignKey(Discount, blank=True, null=True, default=None)
    no_quantity = models.BooleanField(
        default=False, verbose_name=_(u'no quantity'), help_text=_(u'quantity and unit price are not shown on bill')
    )
    is_discount = models.BooleanField(
        default=False, verbose_name=_(u'is discount'), help_text=_(u'added after total on the bill')
    )

    class Meta:
        verbose_name = _(u"Sale item")
        verbose_name_plural = _(u"Sales items")
        ordering = ['order_index']

    def __unicode__(self):
        if self.id:
            return _(u"{1} x {0}").format(self.item, self.quantity)
        else:
            return _(u"Sale item not set")

    def vat_incl_price(self, round_value=True):
        """VAT inclusive price"""
        value = self.unit_price() + self.vat_price()
        return round_currency(value) if round_value else value

    def total_vat_price(self, round_value=True):
        """VAT price * quantity"""
        return self.quantity * self.vat_price(round_value=round_value)

    def vat_price(self, round_value=True):
        """VAT price"""
        if self.is_blank:
            return Decimal(0)
        vat_rate = self.vat_rate.rate if self.vat_rate else Decimal(0)

        value = self.unit_price() * (vat_rate / Decimal(100))
        return round_currency(value) if round_value else value

    def vat_incl_total_price(self):
        """VAT inclusive price"""
        return self.vat_incl_price() * self.quantity

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
        return self.unit_price(round_value=round_value) * self.quantity

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
        if show_amount_as_pre_tax:
            total_amount += item.pre_tax_total_price()
        else:
            total_amount += item.vat_incl_total_price()
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
