# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Crm.forms import ModelFormWithCity
from sanza.Crm.widgets import CityAutoComplete
from sanza.Crm.models import Contact
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm

class ProfileForm(ModelFormWithCity):
    
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Meta:
        model = Contact
        exclude=('uuid', 'same_as', 'imported_by', 'entity')
        fields = (
            'gender', 'lastname', 'firstname', 'birth_date', 'email', 'phone', 'mobile',
            'address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country',
            'accept_newsletter', 'accept_3rdparty',
            'photo'
        )
        
        fieldsets = [
            ('name', {'fields': ['gender', 'lastname', 'firstname', 'birth_date'], 'legend': _(u'Name')}),
            ('web', {'fields': ['email', 'phone', 'mobile'], 'legend': _(u'Phone / Web')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
            ('relationship', {'fields': ['accept_newsletter', 'accept_3rdparty'], 'legend': _(u'Relationship')}),
            ('photo', {'fields': ['photo'], 'legend': _(u'Photo')}),
        ]
        

class AcceptNewsletterRegistrationForm(RegistrationForm):
    accept_newsletter = forms.BooleanField(label=_(u'Accept newsletter'))