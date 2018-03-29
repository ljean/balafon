# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import floppyforms.__future__ as forms


class CityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/city_autocomplete.html'


class CityNoCountryAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/city_nocountry_autocomplete.html'


class OpportunityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/opportunity_autocomplete.html'


class EntityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/entity_autocomplete.html'


class ContactAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/contact_autocomplete.html'


class ContactOrEntityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/contact_or_entity_autocomplete.html'


class GroupAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/group_autocomplete.html'
