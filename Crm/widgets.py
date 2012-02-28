# -*- coding: utf-8 -*-

import floppyforms as forms

class CityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/city_autocomplete.html'

class OpportunityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/opportunity_autocomplete.html'

class EntityAutoComplete(forms.HiddenInput):
    input_type = 'text'
    is_hidden = False
    template_name = 'forms/entity_autocomplete.html'
