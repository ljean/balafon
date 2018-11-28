# -*- coding: utf-8 -*-
"""admin"""

from __future__ import unicode_literals

from django import forms
from django.db.models import CharField
from django.contrib import admin
from django.contrib.messages import success, error
from django.utils.translation import ugettext_lazy as _, ugettext

from balafon.widgets import VerboseManyToManyRawIdWidget
from balafon.Store import models
from balafon.Store.forms import StoreManagementActionTypeAdminForm, PricePolicyAdminForm, StoreItemCategoryAdminForm


admin.site.register(models.Unit)
admin.site.register(models.DeliveryPoint)


class StoreItemInline(admin.TabularInline):
    """display property on the store item"""
    model = models.StoreItem
    fields = (
        'name', 'get_admin_link', 'category', 'purchase_price', 'price_policy', 'pre_tax_price',
        'vat_rate', 'vat_incl_price_with_alert', 'available', 'published', 'stock_count', 'stock_threshold_alert'
    )
    readonly_fields = ['get_admin_link', 'stock_threshold_alert', 'vat_incl_price_with_alert', ]


class StoreParentCategoryFilter(admin.SimpleListFilter):
    """filter items which are below their stock threshold"""
    title = _('parent')
    parameter_name = 'parent_category'

    def lookups(self, request, model_admin):
        return [(0, _('None'))] + [
            (category.id, category.name)
            for category in models.StoreItemCategory.objects.filter(
                subcategories_set__isnull=False
            ).distinct().order_by('name')
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            if value == '0':
                return queryset.filter(parent__isnull=True)
            else:
                return queryset.filter(parent__id=value)
        else:
            return queryset


class StoreItemCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'parent', 'icon', 'active', 'price_policy', 'get_articles_count', 'get_all_articles_count',
        'get_children_count'
    )
    form = StoreItemCategoryAdminForm
    list_editable = ('active', )
    list_filter = (StoreParentCategoryFilter, )
    readonly_fields = ('get_all_articles_count', 'get_articles_count', 'get_children_count')
    inlines = (StoreItemInline, )


admin.site.register(models.StoreItemCategory, StoreItemCategoryAdmin)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = (StoreItemInline, )


admin.site.register(models.Brand, BrandAdmin)


class StoreItemTagAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'order_index', 'icon', 'active', 'show_always')
    list_editable = ('name', 'order_index', 'icon', 'active', 'show_always')
    fields = (
        'name', 'order_index', 'icon', 'active', 'show_always'
    )


admin.site.register(models.StoreItemTag, StoreItemTagAdmin)


class SaleItemInline(admin.TabularInline):
    """display property on the store item"""
    model = models.SaleItem
    fields = (
        'text', 'item', 'quantity', 'pre_tax_price', 'percentage', 'discount', 'calculate_discount', 'vat_rate',
        'order_index', 'is_blank', 'no_quantity', 'is_discount',
    )
    raw_id_fields = ['item']
    readonly_fields = ('calculate_discount', )


class SaleAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creation_date', 'analysis_code', )
    readonly_fields = ('creation_date', )
    search_fields = ('action__contacts__lastname', 'action__entities__name', )
    inlines = (SaleItemInline, )
    list_filter = ('analysis_code', )
    raw_id_fields = ['action', ]
admin.site.register(models.Sale, SaleAdmin)


class StoreManagementActionTypeAdmin(admin.ModelAdmin):
    """StoreManagementActionTypeAdmin"""
    list_display = ('action_type', 'template_name', 'show_amount_as_pre_tax')
    form = StoreManagementActionTypeAdminForm

admin.site.register(models.StoreManagementActionType, StoreManagementActionTypeAdmin)


class StockThresholdFilter(admin.SimpleListFilter):
    """filter items which are below their stock threshold"""
    title = _('Stock level')
    parameter_name = 'stock_threshold_warning'

    THRESHOLD_ALERT = 1
    THRESHOLD_OK = 2
    THRESHOLD_NONE = 3

    def lookups(self, request, model_admin):
        return [
            (StockThresholdFilter.THRESHOLD_ALERT, ugettext("Threshold alert")),
            (StockThresholdFilter.THRESHOLD_OK, ugettext("Threshold ok")),
            (StockThresholdFilter.THRESHOLD_NONE, ugettext("Threshold missing")),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == StockThresholdFilter.THRESHOLD_NONE:
            return queryset.filter(stock_threshold__isnull=True)
        elif value in (StockThresholdFilter.THRESHOLD_ALERT, StockThresholdFilter.THRESHOLD_OK):
            warning_ids = []
            for item in queryset.filter(stock_threshold__isnull=False):
                if item.has_stock_threshold_alert():
                    warning_ids.append(item.id)
            if value == StockThresholdFilter.THRESHOLD_ALERT:
                return queryset.filter(id__in=warning_ids)
            else:
                return queryset.filter(stock_threshold__isnull=False).exclude(id__in=warning_ids)
        else:
            return queryset


class StoreCategoryFilter(admin.SimpleListFilter):
    """filter items which are below their stock threshold"""
    title = _('Store category')
    parameter_name = 'store_category'

    def lookups(self, request, model_admin):
        store_category = request.GET.get(self.parameter_name, None)

        if not store_category:
            # returns letters
            letters = sorted(set([category.name[0].upper() for category in models.StoreItemCategory.objects.all()]))
            return [('_'+letter, letter) for letter in letters]
        else:
            try:
                category = models.StoreItemCategory.objects.get(id=int(store_category))
                letter = category.name[0].upper()
            except ValueError:
                letter = store_category[1:]

            return [
                (category.id, category.name)
                for category in models.StoreItemCategory.objects.filter(
                    name__istartswith=letter
                ).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
            ]

    def queryset(self, request, queryset):
        category = self.value()
        if category:
            try:
                return queryset.filter(category__id=int(category))
            except ValueError:
                return queryset.filter(category__name__istartswith=category[1:])
        return queryset


class CertificateFilter(admin.SimpleListFilter):
    """filter items with a given certificate"""
    title = _('Certificate')
    parameter_name = 'store_certificate'

    def lookups(self, request, model_admin):
        return [(0, _('None'))] + [
            (certificate.id, certificate.name)
            for certificate in models.Certificate.objects.all().order_by('name')
        ]

    def queryset(self, request, queryset):
        certificate = self.value()
        if certificate:
            if certificate == '0':
                return queryset.filter(certificates__isnull=True)
            else:
                try:
                    return queryset.filter(certificates__id=int(certificate))
                except ValueError:
                    return queryset.none()
        return queryset


class StoreItemPropertyValueInline(admin.TabularInline):
    """display property on the store item"""
    model = models.StoreItemPropertyValue
    fields = ('property', 'value')


class StoreItemAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'fullname', 'brand', 'category', 'vat_rate', 'purchase_price', 'price_policy', 'pre_tax_price',
        'vat_incl_price', 'stock_count', 'stock_threshold_alert', 'available', 'published',
    ]
    ordering = ['name']
    list_filter = [
        'published', 'available', 'price_class', 'vat_rate', StockThresholdFilter, 'supplier', 'tags', 'category',
        CertificateFilter, 'only_for_groups',
    ]
    list_editable = ['available']
    search_fields = ['name', 'brand__name']
    readonly_fields = ['vat_incl_price', 'stock_threshold_alert', 'imported_by_file']
    raw_id_fields = ['tags', 'certificates', 'only_for_groups']
    inlines = [StoreItemPropertyValueInline]
    fieldsets = (
        (_('General'), {
            'fields': (
                'name', 'origin', 'published', 'available', 'category', 'brand', 'certificates', 'tags',
                'only_for_groups',
            )
        }),
        (_('Info'), {
            'fields': (
                'image', 'description',
            )
        }),
        (_('Price'), {
            'fields': (
                'vat_rate', 'purchase_price', 'price_policy', 'pre_tax_price', 'vat_incl_price', 'price_class',
            )
        }),
        (_('Supplier'), {
            'fields': ('supplier', 'reference', )
        }),
        (_('Stock'), {
            'fields': ('stock_count', 'stock_threshold', 'stock_threshold_alert', )
        }),
        (_('Import'), {
            'fields': ('imported_by_file', )
        }),
    )
    list_per_page = 500
    save_as = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, self.admin_site)
        else:
            return super(StoreItemAdmin,self).formfield_for_dbfield(db_field, **kwargs)
        kwargs.pop('request')
        return db_field.formfield(**kwargs)

admin.site.register(models.StoreItem, StoreItemAdmin)


class VatRateAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'name', 'is_default',
    ]
    readonly_fields = ['name']

admin.site.register(models.VatRate, VatRateAdmin)


def import_data(modeladmin, request, queryset):
    for import_file in queryset:
        import_file.import_data()
        if import_file.is_successful:
            success(
                request,
                _('The file {0} has been properly imported : {1} items have been created').format(
                    import_file, import_file.storeitem_set.count()
                )
            )
        else:
            error(
                request,
                _('Error while importing the file {0}: {1}').format(
                    import_file, import_file.error_message
                )
            )
import_data.short_description = _("Import")


class StoreItemImportAdmin(admin.ModelAdmin):
    """custom admin"""
    actions = [import_data]
    formfield_overrides = {
        CharField: {'widget': forms.TextInput(attrs={'size': 150})},
    }

admin.site.register(models.StoreItemImport, StoreItemImportAdmin)

admin.site.register(models.StoreItemProperty)

admin.site.register(models.Supplier)


class PricePolicyAdmin(admin.ModelAdmin):
    form = PricePolicyAdminForm

admin.site.register(models.PricePolicy, PricePolicyAdmin)

admin.site.register(models.Discount)

admin.site.register(models.PriceClass)

admin.site.register(models.Certificate)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('item', 'user')
    list_filter = ('item__category', 'user')

admin.site.register(models.Favorite, FavoriteAdmin)


class SaleAnalysisCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'action_type')

admin.site.register(models.SaleAnalysisCode, SaleAnalysisCodeAdmin)