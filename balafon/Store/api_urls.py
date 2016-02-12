# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import url, include

from rest_framework import routers

from balafon.Store.api import (
    SaleItemViewSet, StoreItemViewSet, StoreItemCategoryViewSet, StoreItemTagViewSet, CartView, FavoriteView,
    LastSalesView
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

    url(r'^api/', include(store_items_router.urls)),

    url(r'^api/(?P<action_id>\d+)/', include(sales_items_router.urls)),

]