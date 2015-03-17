# -*- coding: utf-8 -*-
"""search forms : this forms are included in main search form"""

from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

import floppyforms as forms

from sanza.Emailing import models
from sanza.Search.forms import SearchFieldForm


class EmailingSearchForm(SearchFieldForm):
    """Base class for emailing searches"""
    allowed_status = []

    def __init__(self, *args, **kwargs):
        super(EmailingSearchForm, self).__init__(*args, **kwargs)
        
        queryset = models.Emailing.objects.all()
        if self.allowed_status:
            queryset = queryset.filter(status__in=self.allowed_status)
        queryset = queryset.order_by("-created", "-id")

        field = forms.ModelChoiceField(queryset, label=self._label, **kwargs)
        self._add_field(field)
        
    def _get_emailing(self):
        """get list of emailings"""
        try:
            return models.Emailing.objects.get(id=self._value)
        except models.Emailing.DoesNotExist:
            raise ValidationError(_(u"Unknown emailing"))


class EmailingSentSearchForm(EmailingSearchForm):
    """Emailing sent to"""
    _name = 'emailing_sent'
    _label = _(u'Emailing sent')
    allowed_status = [models.Emailing.STATUS_SENDING, models.Emailing.STATUS_SENT]
    
    def get_lookup(self):
        """get all contacts who received the emailing"""
        emailing = self._get_emailing()
        return {"emailing_received": emailing.id}
        

class EmailingOpenedSearchForm(EmailingSearchForm):
    """Emailing opened"""
    _name = 'emailing_opened'
    _label = _(u'Emailing opened')
    allowed_status = [models.Emailing.STATUS_SENDING, models.Emailing.STATUS_SENT]
    
    def get_lookup(self):
        """get all contacts who opened the emailing"""
        emailing = self._get_emailing()
        return {"emailing_opened": emailing.id}


class EmailingSendToSearchForm(EmailingSearchForm):
    """Emailing send to"""
    _name = 'emailing_send'
    _label = _(u'Emailing send to')
    allowed_status = [models.Emailing.STATUS_SENDING, models.Emailing.STATUS_EDITING, models.Emailing.STATUS_SCHEDULED]

    def get_lookup(self):
        """get all contacts for whom we send the emailing"""
        emailing = self._get_emailing()
        return {"emailing_to_be_received": emailing.id}


class EmailingBounceSearchForm(EmailingSearchForm):
    """Emailing bounce"""
    _name = 'emailing_bounce'
    _label = _(u'Emailing bounce')
    allowed_status = [models.Emailing.STATUS_SENDING, models.Emailing.STATUS_SENT]

    def get_lookup(self):
        """get all contacts with a bounce for this emailing"""
        emailing = self._get_emailing()
        q_objects = Q(emailing_hard_bounce=emailing.id)
        q_objects |= Q(emailing_soft_bounce=emailing.id)
        q_objects |= Q(emailing_spam=emailing.id)
        q_objects |= Q(emailing_unsub=emailing.id)
        q_objects |= Q(emailing_rejected=emailing.id)
        return q_objects


class EmailingContactsSearchForm(EmailingSearchForm):
    """Emailing send to"""
    _name = 'emailing_contacts'
    _label = _(u'Emailing contacts')

    def get_lookup(self):
        """get all contacts for this emailing"""
        emailing = self._get_emailing()
        return Q(emailing_received=emailing.id) | Q(emailing_to_be_received=emailing.id)
