# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import patterns, url, include

from rest_framework import routers

from sanza.Store.api import SaleItemViewSet, StoreItemViewSet
from sanza.Store.views.sales_documents import SalesDocumentView


store_items_router = routers.DefaultRouter()
store_items_router.register(r'store-items', StoreItemViewSet)

sales_items_router = routers.DefaultRouter()
sales_items_router.register(r'sales-items', SaleItemViewSet)


urlpatterns = patterns('sanza.Store.views',
    url(
        r'^view-sales-document/(?P<action_id>\d+)/$',
        SalesDocumentView.as_view(),
        name='store_view_sales_document'
    ),

    url(r'^api/', include(store_items_router.urls)),

    url(r'^api/(?P<action_id>\d+)/', include(sales_items_router.urls)),
)