# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import url, include

from rest_framework import routers

from balafon.Store.api.documents import SaleVatTotalsView
from balafon.Store.api.front import (
    SaleItemViewSet, StoreItemViewSet, StoreItemCategoryViewSet, StoreItemTagViewSet, CartView, FavoriteView,
    LastSalesView
)
from balafon.Store.api.statistics import (
    SalesByCategoryView, SalesByFamilyView, SalesByTagView, SalesByItemOfCategoryView, SalesByItemOfFamilyView,
    SalesByItemOfTagView, TotalSalesView
)

store_items_router = routers.DefaultRouter()
store_items_router.register(r'store-items', StoreItemViewSet, base_name='store_store-items')
store_items_router.register(r'categories', StoreItemCategoryViewSet)
store_items_router.register(r'tags', StoreItemTagViewSet)


sales_items_router = routers.DefaultRouter()
sales_items_router.register(r'sales-items', SaleItemViewSet)

urlpatterns = [

    url(
        r'^api/cart/$',
        CartView.as_view(),
        name='store_post_cart'
    ),

    url(
        r'^api/favorites/$',
        FavoriteView.as_view(),
        name='store_favorites_api'
    ),

    url(
        r'^api/last-sales/$',
        LastSalesView.as_view(),
        name='store_last_sales_api'
    ),

    url(
        r'^api/stats/sales-by-category/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)-(?P<to_month>\d+)/$',
        SalesByCategoryView.as_view(),
        name='store_stats_sales_by_category'
    ),

    url(
        r'^api/stats/sales-by-family/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)-(?P<to_month>\d+)/$',
        SalesByFamilyView.as_view(),
        name='store_stats_sales_by_family'
    ),

    url(
        r'^api/stats/sales-by-tag/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)-(?P<to_month>\d+)/$',
        SalesByTagView.as_view(),
        name='store_stats_sales_by_tag'
    ),

    url(
        r'^api/stats/sales-by-item-cat/(?P<category_id>\d+)/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)'
        r'-(?P<to_month>\d+)/$',
        SalesByItemOfCategoryView.as_view(),
        name='store_stats_sales_by_item_of_category'
    ),

    url(
        r'^api/stats/sales-by-item-tag/(?P<tag_id>\d+)/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)'
        '-(?P<to_month>\d+)/$',
        SalesByItemOfTagView.as_view(),
        name='store_stats_sales_by_item_of_tag'
    ),

    url(
        r'^api/stats/sales-by-item-family/(?P<category_id>\d+)/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)'
        r'-(?P<to_month>\d+)/$',
        SalesByItemOfFamilyView.as_view(),
        name='store_stats_sales_by_item_of_family'
    ),

    url(
        r'^api/stats/total-sales/(?P<from_year>\d+)-(?P<from_month>\d+)/(?P<to_year>\d+)-(?P<to_month>\d+)/$',
        TotalSalesView.as_view(),
        name='store_stats_total_sales'
    ),

    url(
        r'^api/documents/sale-vat-total/(?P<sale_id>\d+)/$',
        SaleVatTotalsView.as_view(),
        name='store_documents_sale_vat_total'
    ),

    url(r'^api/', include(store_items_router.urls)),

    url(r'^api/(?P<action_id>\d+)/', include(sales_items_router.urls)),

]