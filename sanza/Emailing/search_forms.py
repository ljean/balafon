# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Search.forms import SearchFieldForm, TwoDatesForm, YesNoSearchFieldForm
from django.utils.translation import ugettext as _
from sanza.Emailing import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from sanza.Crm.models import Contact

class EmailingSearchForm(SearchFieldForm):
    def __init__(self, *args, **kwargs):
        super(EmailingSearchForm, self).__init__(*args, **kwargs)
        
        qs = models.Emailing.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label, **kwargs)
        self._add_field(field)
        
    def _get_emailing(self):
        try:
            return models.Emailing.objects.get(id=self._value)
        except models.Emailing.DoesNotExist:
            raise ValidationError(_(u"Unknown emailing"))


class EmailingSentSearchForm(EmailingSearchForm):
    _name = 'emailing_sent'
    _label = _(u'Emailing sent')
    
    def get_lookup(self):
        emailing = self._get_emailing()
        return {"emailing_received": emailing.id}
        

class EmailingOpenedSearchForm(EmailingSearchForm):
    _name = 'emailing_opened'
    _label = _(u'Emailing opened')
    
    def get_lookup(self):
        emailing = self._get_emailing()
        return {"emailing_opened": emailing.id}