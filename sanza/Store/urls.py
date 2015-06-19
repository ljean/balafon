# -*- coding: utf-8 -*-
"""urls"""

from django.conf.urls import patterns, url

from sanza.Store.views.sales_documents import SalesDocumentView

urlpatterns = patterns('',
    url(
        r'^view-sales-document/(?P<action_id>\d+)/$',
        SalesDocumentView.as_view(),
        name='store_view_sales_document'
    ),

    url(
        r'^edit-sales-document/(?P<action_id>\d+)/$',
        SalesDocumentView.as_view(edit_mode=True),
        name='store_edit_sales_document'
    ),
)