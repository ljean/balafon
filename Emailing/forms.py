# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Emailing import models
from django.utils.translation import ugettext as _
from django.conf import settings
from coop_cms.models import Newsletter
from django.core.exceptions import ValidationError
from coop_cms.settings import get_newsletter_templates
from sanza.Crm.models import Group, Contact, Entity

class UnregisterForm(forms.Form):
    reason = forms.CharField(required=False, widget=forms.Textarea, label=_(u"Reason"))
    
    
class NewEmailingForm(forms.Form):
    newsletter = forms.IntegerField(label=_(u"Newsletter"))
    subject = forms.CharField(label=_(u"Subject"), required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Subject of the newsletter')}))
    contacts = forms.CharField(widget=forms.HiddenInput())
        
    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        return models.Contact.objects.filter(id__in=ids)
    
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        super(NewEmailingForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
        newsletter_choices = [(0, _(u'-- New --'))] + [(n.id, n.subject) for n in Newsletter.objects.all()]
        self.fields["newsletter"].widget = forms.Select(choices=newsletter_choices)
        
    def clean_subject(self):
        newsletter_id = int(self.cleaned_data['newsletter'])
        subject = self.cleaned_data['subject']
        if newsletter_id==0 and not subject:
            raise ValidationError(_(u"Please enter a subject for the newsletter"))
        return subject
    
class NewNewsletterForm(forms.Form):
    subject = forms.CharField(label=_(u"Subject"), 
        widget=forms.TextInput(attrs={'placeholder': _(u'Subject of the newsletter')}))
    template = forms.ChoiceField(label=_(u"Template"), choices = get_newsletter_templates(None, None))
                        

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields=('gender', 'firstname', 'lastname', 'phone', 'mobile', 'email', 'accept_newsletter', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'Comments'), 'cols':'72'}),
        }
        
    entity = forms.CharField(required=False)
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=[
        (g.id, g.name) for g in Group.objects.filter(subscribe_form=True)
    ])
    
    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        #
        #print self.fields['groups'].choices
        #
        
    def clean_entity(self):
        entity = self.cleaned_data['entity']
        if entity:
            entity, _is_new = Entity.objects.get_or_create(name=entity)
        else:
            entity = Entity.objects.create(name=self.cleaned_data['lastname'])
        return entity
    
    def clean_groups(self):
        try:
            groups = [Group.objects.get(id=group_id) for group_id in self.cleaned_data['groups']]
        except Group.DoesNotExist:
            raise ValidationError(_(u"Invalid group"))
        return groups
        
    def save(self):
        contact = super(SubscribeForm, self).save(commit=False)
        contact.entity = self.cleaned_data['entity']
        contact.save()
        
        groups = self.cleaned_data['groups']
        for g in groups:
            contact.entity.group_set.add(g)
        contact.entity.save()
        
        return contact
    
    