# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Crm.forms import ModelFormWithCity, FormWithCity
from sanza.Crm.widgets import CityAutoComplete
from sanza.Crm.models import Contact, EntityType, Entity
from django.utils.translation import ugettext, ugettext_lazy as _
#from registration.forms import RegistrationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class ProfileForm(ModelFormWithCity):
    
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Media:
        css = {
             'all': ('css/base/jquery-ui-1.9.2.css',),
        }
        js = ('js/jquery-ui-1.9.2.js',)
    
    class Meta:
        model = Contact
        exclude=('uuid', 'same_as', 'imported_by', 'entity')
        fields = (
            'gender', 'lastname', 'firstname', 'birth_date', 'email', 'phone', 'mobile',
            'address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country',
            'accept_newsletter', 'accept_3rdparty', 'accept_notifications',
            #'photo'
        )
        
        fieldsets = [
            ('name', {'fields': ['gender', 'lastname', 'firstname', 'birth_date'], 'legend': _(u'Name')}),
            ('web', {'fields': ['email', 'phone', 'mobile'], 'legend': _(u'Phone / Web')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
            ('relationship', {'fields': ['accept_newsletter', 'accept_3rdparty'], 'legend': _(u'Relationship')}),
            #('photo', {'fields': ['photo'], 'legend': _(u'Photo')}),
        ]
        

class Email(forms.EmailField): 
    def clean(self, value):
        super(Email, self).clean(value)
        if User.objects.filter(email=value).count() > 0:
            raise forms.ValidationError(
                _(u"This email is already registered. Use the 'forgot password' link on the login page")
            )
        return value
        
class UserRegistrationForm(FormWithCity):
    email = Email(required=True, label=_(u"Email"), widget=forms.TextInput())
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(), label=_(u"Password"))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(), label=_(u"Repeat your password"))
    gender = forms.ChoiceField(_(u'gender'), required=False)
    firstname = forms.CharField(required=False, label=_(u"Firstname"))
    lastname = forms.CharField(required=False, label=_(u"Lastname"))
    entity_type = forms.ChoiceField(required=False, widget=forms.Select())
    entity = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the entity')}))
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    accept_termofuse = forms.BooleanField(label=_(u'Accept term of use'))
    accept_newsletter = forms.BooleanField(label=_(u'Accept newsletter'), required=False)
    accept_3rdparty = forms.BooleanField(label=_(u'Accept 3rd party'), required=False)
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        for (name, field) in self.fields.items():
            field.widget.attrs['placeholder'] = field.label
            #if not (name.find('accept')==0):
            if field.required:
                field.widget.attrs['required'] = "required"
        
        self.fields['gender'].choices = ((0, u'----------'),)+Contact.GENDER_CHOICE[:2] #do not display Mrs and Mr
        
        self.fields['entity_type'].choices = [(0, _(u'Individual'))]+[
            (et.id, et.name) for et in EntityType.objects.filter(subscribe_form=True)
        ]
        
    def clean_entity(self, ):
        entity_type = self.cleaned_data.get('entity_type', None)
        entity = self.cleaned_data['entity']
        if entity_type:
            if not entity:
                raise ValidationError(_(u"{0}: Please enter a name".format(entity_type)))
        return entity
        
    def clean_entity_type(self):
        try:
            entity_type_id = int(self.cleaned_data['entity_type'] or 0)
        except ValueError:
            raise ValidationError(ugettext(u'Invalid entity type'))
       
        if entity_type_id:
            try:
                return EntityType.objects.get(id=entity_type_id)
            except EntityType.DoesNotExist:
                raise ValidationError(ugettext(u'Unknown entity type'))
        
        return None
    
        
    def clean(self, *args, **kwargs):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(_(u'Passwords are not the same'))
        return super(UserRegistrationForm, self).clean(*args, **kwargs)
        
class MessageForm(forms.Form):
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'placeholder': _(u"Your message"),
    }))
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message)>10000:
            raise forms.ValidationError(_(u'Message is too long'))
        return message