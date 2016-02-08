# -*- coding: utf-8 -*-
"""settings"""

from django.conf import settings
from django.views.generic import TemplateView

from coop_cms.settings import load_class
from wkhtmltopdf.views import PDFTemplateView


def get_allowed_homepages():
    """returns all Balafon pages which can be set as homepage"""
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


def get_profile_form():
    """returns a form to be used for editing a user profile"""
    return load_class('BALAFON_PROFILE_FORM', 'balafon.Profile.forms.ProfileForm')


def get_registration_form():
    """returns a form to be used for editing a user profile"""
    return load_class('BALAFON_REGISTRATION_FORM', 'balafon.Profile.forms.UserRegistrationForm')


def has_entity_on_registration_form():
    """
    returns True if entity type and entity name are displayed on registration form (Profile)
    register as individual if not
    """
    return getattr(settings, 'BALAFON_ENTITY_ON_REGISTRATION_FORM', True)


def get_registration_accept_terms_of_use_link():
    """returns a link for the use of terms"""
    return getattr(settings, 'BALAFON_REGISTRATION_ACCEPT_USE_OF_TERMS_LINK', '')
