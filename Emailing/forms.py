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
from sanza.Crm.widgets import CityAutoComplete
from django.contrib import messages
import urllib2, re
from bs4 import BeautifulSoup
from django.utils.importlib import import_module

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
    content = forms.CharField(label=_(u'Source URL'), max_length=128, required=False)
    
    def __init__(self, *args, **kwargs):
        super(NewNewsletterForm, self).__init__(*args, **kwargs)
        
        self.allow_url_sources = getattr(settings, 'SANZA_NEWSLETTER_SOURCES', ())
        if not self.allow_url_sources:
            self.fields['content'].widget = forms.HiddenInput()
    
    def clean_content(self):
        url = self.cleaned_data['content']
        if url:
            #Check in config if the url match with something allowed
            newsletter_sources = getattr(settings, 'SANZA_NEWSLETTER_SOURCES', ())
            for (regex, selector, post_processor) in newsletter_sources:
                print "#", regex, url, re.match(regex, url)
                if re.match(regex, url):
                    try:
                        #if so get the content
                        html = urllib2.urlopen(url).read()
                        #and extract the selector content as initial content for the newsletter
                        soup = BeautifulSoup(html)
                        content = u''.join([unicode(tag) for tag in soup.select(selector)])
                        if post_processor:
                            #import the post_processor function
                            module_name, processor_name = post_processor.rsplit('.', 1)
                            module = import_module(module_name)
                            post_processor_func = getattr(module, processor_name)
                            #call the post_processor and update the content
                            content = post_processor_func(content)
                        return content
                    except Exception, msg:
                        raise ValidationError(msg)
                raise ValidationError(_(u"The url is not allowed"))
        return u''

class SubscribeForm(ModelFormWithCity):
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Meta:
        model = Contact
        fields=('gender', 'firstname', 'lastname',
            'phone', 'mobile', 'email', 'accept_newsletter', 'notes', 'address',
            'address2', 'address3', 'zip_code')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'Comments'), 'cols':'90'}),
            'lastname': forms.TextInput(attrs={'placeholder': _(u'Lastname')}),
            'firstname': forms.TextInput(attrs={'placeholder': _(u'Firstname')}),
            'phone': forms.TextInput(attrs={'placeholder': _(u'Phone')}),
            'email': forms.TextInput(attrs={'placeholder': _(u'Email')}),
            'zip_code': forms.TextInput(attrs={'placeholder': _(u'zip code')}),
            #'country': forms.HiddenInput(),
        }
        
    entity = forms.CharField(required=False)
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    action_types = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    
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
        
    def save(self, request=None):
        contact = super(SubscribeForm, self).save(commit=False)
        contact.entity = self.cleaned_data['entity']
        contact.city = self.cleaned_data['city']
        contact.save()
        #delete unknown contacts for the current entity
        contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()
        
        #force also the city on the entity
        contact.entity.city = contact.city
        
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
                [notification_email], headers = {'Reply-To': contact.email})
            try:
                email.send()
                if request:
                    messages.add_message(request, messages.SUCCESS,
                        _(u"The message have been sent"))
            except Exception, msg:
                if request:
                    messages.add_message(request, messages.ERROR,
                        _(u"The message couldn't be send."))
                
        return contact
    
        