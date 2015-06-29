# -*- coding: utf-8 -*-
"""settings"""

from django.conf import settings
from django.views.generic import TemplateView

from wkhtmltopdf.views import PDFTemplateView


def get_allowed_homepages():
    """returns all Sanza pages which can be set as homepage"""
    return (
        # CRM
        'crm_view_entities_list',
        'crm_view_entity',
        'crm_view_contact',
        'crm_view_entity_actions',
        'crm_entity_actions',
        'crm_contact_actions',
        'crm_all_actions',
        'crm_edit_group',
        'crm_see_my_groups',
        'crm_view_opportunity',
        'crm_all_opportunities',
        'crm_new_contacts_import',
        'crm_actions_of_month',
        'crm_actions_of_week',
        'crm_actions_of_day',
        'crm_actions_not_planned',

        # Emailing
        'emailing_newsletter_list',
        'emailing_view',

        # Search
        'search',
        'search_group',
        'search_cities',

        # Users
        'users_favorites_list',
    )


def get_pdf_view_base_class():
    """returns base class for Pdf --> turn it to HTML for drone.IO"""
    if getattr(settings, 'CI_DRONE', False):
        return TemplateView
    else:
        return PDFTemplateView