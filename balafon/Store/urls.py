# -*- coding: utf-8 -*-
"""urls"""

from __future__ import unicode_literals

from django.conf.urls import url

from balafon.Store.views.sales_documents import (
    SalesDocumentView, SalesDocumentPdfView, SalesDocumentPublicView, SalesDocumentPublicPdfView
)
from balafon.Store.views.statistics import StaticticsIndexView, AddExtraSaleView
from balafon.Store.views.xls_export import (
    StockXlsView, StockAlertXlsView, StoreXlsCatalogueView, StockImportView, StoreItemXlsView, ActionSummaryFormView,
    ActionSummaryXlsView
)


urlpatterns = [
    url(
        r'^view-sales-document/(?P<action_id>\d+)/$',
        SalesDocumentView.as_view(),
        name='store_view_sales_document'
    ),

    url(
        r'^document/(?P<action_uuid>[\w\d-]+)/$',
        SalesDocumentPublicView.as_view(),
        name='store_view_sales_document_public'
    ),

    url(
        r'^view-sales-document/(?P<action_id>\d+)/pdf/$',
        SalesDocumentPdfView.as_view(),
        name='store_view_sales_document_pdf'
    ),

    url(
        r'^document/(?P<action_uuid>[\w\d-]+)/pdf/$',
        SalesDocumentPublicPdfView.as_view(),
        name='store_view_sales_document_pdf_public'
    ),

    url(r"^admin/export-stock/$", StockXlsView.as_view(), name='store_store_item_admin_export'),

    url(
        r"^admin/export-stock-alert/$",
        StockAlertXlsView.as_view(),
        name='store_store_item_admin_export_alert'
    ),
    url(
        r"^admin/store-catalogue/(?P<category_id>\d+)$",
        StoreXlsCatalogueView.as_view(),
        name=r'store_xls_catalogue'
    ),

    url(
        r"^admin/store-articles/(?P<category_id>\d+)/(?P<supplier_id>\d+)/$",
        StoreItemXlsView.as_view(),
        name=r'store_xls_articles'
    ),

    url(
        r'statistics/index/$',
        StaticticsIndexView.as_view(),
        name=r'store_statistics_index'
    ),

    url(
        'statistics/add-extra-sale/$',
        AddExtraSaleView.as_view(),
        name=r'store_add_extra_sale'
    ),

    url(
        r"^admin/import-stock/$",
        StockImportView.as_view(),
        name='store_import_stock'
    ),

    url(
        r"^admin/actions-summary/(?P<action_type_id>\d+)/$",
        ActionSummaryFormView.as_view(),
        name='store_actions_summary'
    ),

    url(
        r"^admin/actions-summary-xls/(?P<action_type_id>\d+)/(?P<start_date>.+)/(?P<end_date>.+)/$",
        ActionSummaryXlsView.as_view(),
        name='store_actions_summary_xls'
    ),

]