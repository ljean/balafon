# -*- coding: utf-8 -*-
"""admin"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _, ugettext

from sanza.Store import models
from sanza.Store.forms import StoreManagementActionTypeAdminForm


admin.site.register(models.Unit)
admin.site.register(models.DeliveryPoint)

class StoreItemCategoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'order_index', 'icon', 'active')
    list_editable = ('name', 'order_index', 'icon', 'active')

admin.site.register(models.StoreItemCategory, StoreItemCategoryAdmin)


class StoreItemTagAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'name', 'order_index', 'icon', 'active')
    list_editable = ('name', 'order_index', 'icon', 'active')

admin.site.register(models.StoreItemTag, StoreItemTagAdmin)


admin.site.register(models.Sale)
admin.site.register(models.SaleItem)


class StoreManagementActionTypeAdmin(admin.ModelAdmin):
    """StoreManagementActionTypeAdmin"""
    form = StoreManagementActionTypeAdminForm

admin.site.register(models.StoreManagementActionType, StoreManagementActionTypeAdmin)


class StockThresholdFilter(admin.SimpleListFilter):
    """filter items which are below their stock threshold"""
    title = _(u'Stock level')
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


class StoreItemAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'name', 'category', 'vat_rate', 'purchase_price', 'pre_tax_price', 'vat_incl_price', 'stock_count',
        'stock_threshold_alert', 'unit'
    ]
    ordering = ['name']
    list_filter = ['category', 'tags', StockThresholdFilter]
    search_fields = ['name']
    readonly_fields = ['vat_incl_price', 'stock_threshold_alert']


admin.site.register(models.StoreItem, StoreItemAdmin)


class VatRateAdmin(admin.ModelAdmin):
    """custom admin view"""
    list_display = [
        'name', 'is_default',
    ]
    readonly_fields = ['name']

admin.site.register(models.VatRate, VatRateAdmin)
