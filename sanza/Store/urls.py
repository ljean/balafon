# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import patterns, url, include

from rest_framework import routers

from sanza.Store.api import StoreItemSaleViewSet, StoreItemViewSet
from sanza.Store.views.sales_documents import SalesDocumentView


router1 = routers.DefaultRouter()
router1.register(r'item_sales', StoreItemSaleViewSet)

router2 = routers.DefaultRouter()
router2.register(r'store_items', StoreItemViewSet)


urlpatterns = patterns('sanza.Store.views',
    url(
        r'^view-sales-document/(?P<action_id>\d+)/$',
        SalesDocumentView.as_view(),
        name='store_view_sales_document'
    ),

    url(r'^api/', include(router2.urls)),

    url(r'^api/(?P<action_id>\d+)/', include(router1.urls)),


    # url(
    #     r'^edit-sales-document/(?P<action_id>\d+)/$',
    #     SalesDocumentView.as_view(edit_mode=True),
    #     name='store_edit_sales_document'
    # ),
    #
    # url(
    #     r'^choose-item/$',
    #     'sales_documents.choose_item',
    #     name='store_choose_item'
    # )
)