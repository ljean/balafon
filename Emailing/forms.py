# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Emailing import models
from django.utils.translation import ugettext as _
from django.conf import settings
from coop_cms.models import Newsletter
from django.core.exceptions import ValidationError
from coop_cms.settings import get_newsletter_templates
from sanza.Crm.models import Group, Contact, Entity, EntityType, Action, ActionType
from sanza.Crm.forms import ModelFormWithCity
from datetime import datetime
from django.template import Context
from django.template.loader import get_template
from django.core.mail import send_mail, EmailMessage

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
                        

class SubscribeForm(ModelFormWithCity):
    class Meta:
        model = Contact
        fields=('gender', 'firstname', 'lastname',
            'phone', 'mobile', 'email', 'city', 'accept_newsletter', 'notes', 'address',
            'address2', 'address3', 'zip_code',)
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'Comments'), 'cols':'72'}),
            'lastname': forms.TextInput(attrs={'placeholder': _(u'Lastname')}),
            'firstname': forms.TextInput(attrs={'placeholder': _(u'Firstname')}),
            'phone': forms.TextInput(attrs={'placeholder': _(u'Phone')}),
            'email': forms.TextInput(attrs={'placeholder': _(u'Email')}),
        }
        
    entity = forms.CharField(required=False)
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='')
    action_types = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='')
    
    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)
        
        self.fields['groups'].choices = [
            (g.id, g.name) for g in Group.objects.filter(subscribe_form=True)
        ]
        
        self.fields['action_types'].choices = [
            (at.id, at.name) for at in ActionType.objects.filter(subscribe_form=True)
        ]
        
    def clean_entity(self):
        entity = self.cleaned_data['entity']
        if entity:
            try:
                return Entity.objects.get(name=entity)
            except Entity.DoesNotExist:
                pass
        else:
            data = [self.cleaned_data[x] for x in ('lastname', 'firstname')]
            entity = u' '.join([x for x in data if x])

        entity_type, _is_new = EntityType.objects.get_or_create(
            name=getattr(settings, 'SANZA_DEFAULT_ENTITY_TYPE', _(u'Unknown'))
        )
        
        return Entity.objects.create(name=entity, type=entity_type)
    
    def clean_groups(self):
        try:
            groups = [Group.objects.get(id=group_id) for group_id in self.cleaned_data['groups']]
        except Group.DoesNotExist:
            raise ValidationError(_(u"Invalid group"))
        return groups
    
    def clean_action_types(self):
        try:
            action_types = [ActionType.objects.get(id=at_id) for at_id in self.cleaned_data['action_types']]
        except ActionType.DoesNotExist:
            raise ValidationError(_(u"Invalid action type"))
        return action_types
        
    def save(self):
        contact = super(SubscribeForm, self).save(commit=False)
        contact.entity = self.cleaned_data['entity']
        contact.save()
        #delete unknown contacts for the current entity
        contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()
        
        groups = self.cleaned_data['groups']
        for g in groups:
            contact.entity.group_set.add(g)
        contact.entity.save()
        
        action_types = self.cleaned_data['action_types']
        actions = []
        for at in action_types:
            action = Action.objects.create(
                subject = _(u"Contact"),
                type = at,
                planned_date = datetime.now(),
                entity = contact.entity,
                contact = contact,
            )
            actions.append(action)
            
        #send an email
        notification_email = getattr(settings, 'SANZA_NOTIFY_SUBSCRIPTIONS', '')
        if notification_email:
            data = {
                'contact': contact,
                'groups': contact.entity.group_set.all(),
                'actions': actions,
                'site': settings.COOP_CMS_SITE_PREFIX,
            }
            t = get_template('Emailing/subscribe_notification_email.txt')
            content = t.render(Context(data))
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
            
            email = EmailMessage(
                _(u'New contact'), content, from_email,
                [notification_email], headers = {'Reply-To': 'contact.email'})
            email.send()
            
        return contact
    
    