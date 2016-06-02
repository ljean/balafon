# -*- coding: utf-8 -*-
"""forms"""

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from importlib import import_module
import re
import urllib2

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.utils.timezone import now as dt_now
from django.utils.translation import ugettext, ugettext_lazy as _

from captcha.fields import CaptchaField

from coop_cms.models import Newsletter
from coop_cms.settings import get_newsletter_templates
from coop_cms.utils import dehtml
from coop_cms.bs_forms import Form as BsForm, ModelForm as BsModelForm
import floppyforms as forms

from balafon.Crm import settings as crm_settings
from balafon.Crm.forms import ModelFormWithCity, BetterBsModelForm
from balafon.Crm.models import Group, Contact, Entity, EntityType, Action, ActionType, SubscriptionType, Subscription
from balafon.Crm.widgets import CityAutoComplete
from balafon.Emailing import models
from balafon.Emailing.utils import create_subscription_action, send_notification_email, get_language
from balafon.Emailing import settings as emailing_settings


class UnregisterForm(BsForm):
    """User wants to unregister from emailing"""
    reason = forms.CharField(required=False, widget=forms.Textarea, label=_(u"Reason"))


class UpdateEmailingForm(BsModelForm):
    """form for editing an existing emailing"""

    class Meta:
        model = models.Emailing
        fields = ('subscription_type', 'newsletter', 'lang', 'from_email', )

    def __init__(self, *args, **kwargs):
        super(UpdateEmailingForm, self).__init__(*args, **kwargs)

        subscription_choices = [(subs_type.id, subs_type.name) for subs_type in SubscriptionType.objects.all()]
        self.fields["subscription_type"].widget = forms.Select(choices=subscription_choices)

        newsletter_choices = [(newsletter.id, newsletter.subject) for newsletter in Newsletter.objects.all()]
        self.fields["newsletter"].widget = forms.Select(choices=newsletter_choices, attrs={'class': 'form-control'})

        if not getattr(settings, 'BALAFON_EMAILING_SENDER_CHOICES', None):
            self.fields["from_email"].widget = forms.HiddenInput()
        else:
            self.fields["from_email"].widget = forms.Select(choices=settings.BALAFON_EMAILING_SENDER_CHOICES)

        if not getattr(settings, 'LANGUAGES', None) or len(settings.LANGUAGES) < 2:
            self.fields["lang"].widget = forms.HiddenInput()
        else:
            language_choices = crm_settings.get_language_choices(_(u"Favorite language of the contact"))
            self.fields["lang"].widget = forms.Select(choices=language_choices, attrs={'class': 'form-control'})


class NewEmailingForm(BsForm):
    """Form for creating a new emailing"""

    subscription_type = forms.IntegerField(label=_(u"Subscription Type"))
    newsletter = forms.IntegerField(label=_(u"Newsletter"))
    subject = forms.CharField(
        label=_(u"Subject"), required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Subject of the newsletter')})
    )
    contacts = forms.CharField(widget=forms.HiddenInput())
    lang = forms.CharField(
        required=False,
        label=_(u"Language"),
        widget=forms.Select(choices=[('', _(u'Default'))] + list(settings.LANGUAGES))
    )
    from_email = forms.CharField(required=False, label=_(u"Sent from"))

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and 'contacts' in initial:
            initial_contacts = u';'.join([unicode(contact.id) for contact in initial['contacts']])
            initial.pop('contacts')
        super(NewEmailingForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts

        newsletter_choices = [
            (0, ugettext(u'-- New --'))
        ] + [
            (newsletter.id, newsletter.subject) for newsletter in Newsletter.objects.all().order_by('-id')
        ]
        self.fields["newsletter"].widget = forms.Select(choices=newsletter_choices, attrs={'class': 'form-control'})

        subscription_choices = [(subscription.id, subscription.name) for subscription in SubscriptionType.objects.all()]
        self.fields["subscription_type"].widget = forms.Select(
            choices=subscription_choices, attrs={'class': 'form-control'}
        )

        if len(settings.LANGUAGES) < 2:
            self.fields['lang'].widget = forms.HiddenInput()

        if getattr(settings, 'BALAFON_EMAILING_SENDER_CHOICES', None):
            self.fields['from_email'].widget = forms.Select(
                choices=settings.BALAFON_EMAILING_SENDER_CHOICES, attrs={'class': 'form-control'}
            )
        else:
            self.fields['from_email'].widget = forms.HiddenInput()

    def get_contacts(self):
        """get the list of contacts stored by ids"""
        ids = self.cleaned_data["contacts"].split(";")
        return models.Contact.objects.filter(id__in=ids)

    def clean_subject(self):
        """subject validation"""
        newsletter_id = int(self.cleaned_data['newsletter'])
        subject = self.cleaned_data['subject']
        if newsletter_id == 0 and not subject:
            raise ValidationError(ugettext(u"Please enter a subject for the newsletter"))
        return subject

    def clean_subscription_type(self):
        """validation of subscription type. Return the subscription type object"""
        try:
            subscription_type = int(self.cleaned_data['subscription_type'])
            return SubscriptionType.objects.get(id=subscription_type)
        except (ValueError, KeyError, SubscriptionType.DoesNotExist):
            raise ValidationError(ugettext(u"Please select a valid subscription"))


class NewNewsletterForm(BsForm):
    """Create a new newsletter"""
    subject = forms.CharField(
        label=_(u"Subject"),
        widget=forms.TextInput(attrs={'placeholder': _(u'Subject of the newsletter')})
    )
    template = forms.ChoiceField(label=_(u"Template"), choices=get_newsletter_templates(None, None))
    source_url = forms.URLField(label=_(u'Source URL'), required=False)
    content = forms.CharField(label=_(u'Content'), required=False, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(NewNewsletterForm, self).__init__(*args, **kwargs)
        
        self.source_content = ""
        
        self.allow_url_sources = getattr(settings, 'BALAFON_NEWSLETTER_SOURCES', ())
        if not self.allow_url_sources:
            self.fields['source_url'].widget = forms.HiddenInput()
    
    def clean_source_url(self):
        """
        clean source url: If an url is given download newsletter content from this source
        It can be used for people using a different tool for writing their newsletter
        """
        url = self.cleaned_data['source_url']
        if url:
            # Check in config if the url match with something allowed
            newsletter_sources = getattr(settings, 'BALAFON_NEWSLETTER_SOURCES', ())
            for (regex, selector, post_processor) in newsletter_sources:
                if re.match(regex, url):
                    try:
                        # if so get the content
                        html = urllib2.urlopen(url).read()
                        # and extract the selector content as initial content for the newsletter
                        soup = BeautifulSoup(html, "html.parser")
                        content = u''.join([unicode(tag) for tag in soup.select(selector)])
                        if post_processor:
                            # import the post_processor function
                            module_name, processor_name = post_processor.rsplit('.', 1)
                            module = import_module(module_name)
                            post_processor_func = getattr(module, processor_name)
                            # call the post_processor and update the content
                            content = post_processor_func(content)
                        self.source_content = content
                        return url
                    except Exception, msg:
                        raise ValidationError(msg)
            raise ValidationError(ugettext(u"The url is not allowed"))
        return u''

    def clean_content(self):
        """content validation"""
        url = self.cleaned_data['source_url']
        if url:
            return self.source_content
        return u''


class EmailSubscribeForm(BetterBsModelForm):
    """Register to an emailing with just email address"""
    email = forms.EmailField(
        required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': _(u'Email'), 'size': '80'})
    )
    
    class Meta:
        model = Contact
        fields = ('email', 'favorite_language')

    def __init__(self, *args, **kwargs):
        self.subscription_type = kwargs.pop('subscription_type', None)
        super(EmailSubscribeForm, self).__init__(*args, **kwargs)

        self.fields['favorite_language'].widget = forms.HiddenInput()
        if crm_settings.has_language_choices():
            self.fields['favorite_language'].initial = get_language()
    
    def save(self, request=None):
        """save"""
        contact = super(EmailSubscribeForm, self).save(commit=False)
        
        if crm_settings.ALLOW_SINGLE_CONTACT:
            contact.entity = Entity.objects.create(name=contact.email, type=None, is_single_contact=True)
        else:
            et_id = getattr(settings, 'BALAFON_INDIVIDUAL_ENTITY_ID', 1)
            entity_type = EntityType.objects.get(id=et_id)
            contact.entity = Entity.objects.create(name=contact.email, type=entity_type)
        contact.save()
        #delete unknown contacts for the current entity
        contact.entity.contact_set.exclude(id=contact.id).delete()

        queryset = SubscriptionType.objects.filter(site=Site.objects.get_current())

        form_subscription_type = self.subscription_type
        default_subscription_type = emailing_settings.get_default_subscription_type()
        if not form_subscription_type and default_subscription_type:
            form_subscription_type = default_subscription_type

        if form_subscription_type:
            queryset = queryset.filter(id=form_subscription_type)

        subscriptions = []
        for subscription_type in queryset:
            subscription = Subscription.objects.get_or_create(contact=contact, subscription_type=subscription_type)[0]
            subscription.accept_subscription = True
            subscription.subscription_date = datetime.now()
            subscription.save()
            subscriptions.append(subscription_type.name)
        
        create_subscription_action(contact, subscriptions)
        if subscriptions:
            send_notification_email(request, contact, [], "")
        else:
            send_notification_email(request, contact, [], u"Error: "+ugettext(u"No subscription_type defined"))
                
        return contact


class SubscriptionTypeFormMixin(object):
    """Base class requiring subscription type"""
    subscription_required = False
    subscription_types_count = 0

    def _add_subscription_types_field(self, contact=None):
        """add the subscription_type field dynamically"""
        subscription_types = list(self.get_queryset())
        self.subscription_types_count = len(subscription_types)
        if self.subscription_types_count > 0:
            if self.subscription_types_count > 1:
                help_text = ugettext('Check the boxes of the newsletters that you want to receive')
            else:
                help_text = ugettext('Check the box if you want to receive our newsletter')

            initial = None
            if contact:
                initial = u','.join(
                    [
                        str(subscription.subscription_type.id)
                        for subscription in contact.subscription_set.all()
                        if subscription.accept_subscription
                    ]
                )

            self.fields['subscription_types'] = forms.MultipleChoiceField(
                widget=forms.CheckboxSelectMultiple(),
                label='',
                help_text=help_text,
                required=self.subscription_required and (self.subscription_types_count == 1),
                initial=initial,
                choices=[(subscription_type.id, subscription_type.name) for subscription_type in subscription_types]
            )

        else:
            self.fields['subscription_types'] = forms.MultipleChoiceField(
                widget=forms.HiddenInput(),
                label='',
                required=False,
                choices=[]
            )

    def get_queryset(self):
        """returns subscription_types"""
        return SubscriptionType.objects.filter(site=Site.objects.get_current())

    def clean_subscription_types(self):
        """validation"""
        try:
            subscription_types = [
                SubscriptionType.objects.get(id=st_id) for st_id in self.cleaned_data['subscription_types']
            ]
        except SubscriptionType.DoesNotExist:
            raise ValidationError(_(u"Invalid subscription type"))

        if self.subscription_required and not (len(subscription_types)):
            if self.subscription_types_count > 1:
                raise ValidationError(_(u"You must check a least one subscription"))
            else:
                raise ValidationError(_(u"This field is required"))
        return subscription_types

    def _save_subscription_types(self, contact):
        """save"""
        subscriptions = []
        for subscription_type in self.get_queryset():

            subscription = Subscription.objects.get_or_create(
                contact=contact,
                subscription_type=subscription_type
            )[0]

            if subscription_type in self.cleaned_data['subscription_types']:
                subscription.accept_subscription = True
                subscription.subscription_date = datetime.now()
                #This is added to the notification email
                subscriptions.append(subscription_type.name)
            else:
                subscription.accept_subscription = False
            subscription.save()
        return subscriptions


class SubscribeForm(ModelFormWithCity, SubscriptionTypeFormMixin):
    """Subscribe to emailing"""

    city = forms.CharField(
        required=False, label=_(u'City'),
        widget=CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    entity_type = forms.ChoiceField(required=False, widget=forms.Select())
    entity = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the entity')})
    )
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    action_types = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': _(u'Message'), 'cols':'90'}))
    captcha = CaptchaField(help_text=_(u"Make sure you are a human"))
    favorite_language = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Contact
        fields = (
            'gender', 'firstname', 'lastname', 'phone', 'mobile', 'email', 'address',
            'address2', 'address3', 'zip_code'
        )
        widgets = {
            'lastname': forms.TextInput(attrs={'placeholder': _(u'Lastname'), 'required': 'required'}),
            'firstname': forms.TextInput(attrs={'placeholder': _(u'Firstname')}),
            'phone': forms.TextInput(attrs={'placeholder': _(u'Phone')}),
            'email': forms.TextInput(attrs={'placeholder': _(u'Email'), 'required': 'required'}),
            'zip_code': forms.TextInput(attrs={'placeholder': _(u'zip code')}),
        }

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True
        #self.fields['lastname'].required = True
        
        # Do not display (Mrs and M) gender on subscribe form
        self.fields['gender'].choices = self.fields['gender'].choices[:3]

        entity_types_choices = []

        if crm_settings.ALLOW_SINGLE_CONTACT:
            entity_types_choices.append((0, _(u'Individual')))
        else:
            entity_types_choices.append((0, ''))

        entity_types_choices.extend([
            (et.id, et.name) for et in EntityType.objects.filter(subscribe_form=True)
        ])

        self.fields['entity_type'].choices = entity_types_choices

        self.fields['groups'].choices = [
            (group.id, group.name) for group in Group.objects.filter(subscribe_form=True)
        ]
        
        self.fields['action_types'].choices = [
            (action_type.id, action_type.name) for action_type in ActionType.objects.filter(subscribe_form=True)
        ]
        
        self._add_subscription_types_field()

        if crm_settings.has_language_choices():
            self.fields['favorite_language'].initial = get_language()
    
    def clean_entity_type(self):
        """validation"""
        try:
            entity_type = int(self.cleaned_data['entity_type'])
            if entity_type:
                return EntityType.objects.get(id=entity_type)
            return None
        except (ValueError, EntityType.DoesNotExist):
            raise ValidationError(ugettext(u"Invalid entity type"))
        
    def get_entity(self):
        """get entity from form"""
        entity_type = self.cleaned_data.get('entity_type', None)
        entity = self.cleaned_data['entity']
        if entity_type:
            if entity:
                return Entity.objects.create(name=entity, type=entity_type)
        else:
            if crm_settings.ALLOW_SINGLE_CONTACT:
                return Entity.objects.create(name=entity, type=None, is_single_contact=True)
            else:
                et_id = getattr(settings, 'BALAFON_INDIVIDUAL_ENTITY_ID', 1)
                entity_type = EntityType.objects.get(id=et_id)
                entity_name = u"{0} {1}".format(
                    self.cleaned_data['lastname'], self.cleaned_data['firstname'])
                return Entity.objects.create(name=entity_name, type=entity_type)
            
    def clean_entity(self):
        """validation"""
        entity_type = self.cleaned_data.get('entity_type', None)
        entity = self._dehtmled_field("entity")
        if entity_type:
            if not entity:
                raise ValidationError(u"{0}: {1}".format(entity_type.name, ugettext(u"Please enter a name")))
        else:
            data = [self.cleaned_data[x] for x in ('lastname', 'firstname')]
            entity = u' '.join([x for x in data if x]).strip().upper()
            
        return entity
         
    def _dehtmled_field(self, fieldname, **kwargs):
        """html to text for a field content"""
        value = self.cleaned_data[fieldname]
        return dehtml(value, **kwargs)
        
    def clean_lastname(self):
        """validate lastname"""
        return self._dehtmled_field("lastname")
    
    def clean_firstname(self):
        """validate firstname"""
        return self._dehtmled_field("firstname")
    
    def clean_phone(self):
        """validate phone"""
        return self._dehtmled_field("phone")
    
    def clean_mobile(self):
        """validate mobile phone"""
        return self._dehtmled_field("mobile")
    
    def clean_address(self):
        """validate address"""
        return self._dehtmled_field("address")
    
    def clean_address2(self):
        """valiadate address line 2"""
        return self._dehtmled_field("address2")
    
    def clean_address3(self):
        """validate address line 3"""
        return self._dehtmled_field("address3")
    
    def clean_message(self):
        """validate message"""
        message = self._dehtmled_field("message", allow_spaces=True)
        if len(message) > 10000:
            raise ValidationError(ugettext(u"Your message is too long"))
        return message
    
    def clean_groups(self):
        """validate groups"""
        try:
            groups = [Group.objects.get(id=group_id) for group_id in self.cleaned_data['groups']]
        except Group.DoesNotExist:
            raise ValidationError(ugettext(u"Invalid group"))
        return groups
    
    def clean_action_types(self):
        """validate action types"""
        try:
            action_types = [ActionType.objects.get(id=at_id) for at_id in self.cleaned_data['action_types']]
        except ActionType.DoesNotExist:
            raise ValidationError(ugettext(u"Invalid action type"))
        return action_types

    def save(self, request=None):
        """save"""
        contact = super(SubscribeForm, self).save(commit=False)
        contact.entity = self.get_entity()
        contact.city = self.cleaned_data['city']
        contact.favorite_language = self.cleaned_data.get('favorite_language', '')
        contact.save()
        # delete unknown contacts for the current entity
        contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()
        
        # force also the city on the entity
        contact.entity.city = contact.city

        groups = self.cleaned_data['groups']
        for group in groups:
            contact.entity.group_set.add(group)
        contact.entity.save()
        
        subscriptions = self._save_subscription_types(contact)
        
        message = self.cleaned_data["message"]

        if message:
            action_type = ActionType.objects.get_or_create(name=ugettext(u"Message"))[0]
            action = Action.objects.create(
                subject=ugettext(u"Message from web site"),
                type=action_type,
                planned_date=datetime.now(),
                detail=message,
                display_on_board=True
            )
            action.contacts.add(contact)
            action.save()
        
        if subscriptions:
            create_subscription_action(contact, subscriptions)
        
        action_types = self.cleaned_data['action_types']
        actions = []
        for action_type in action_types:
            action = Action.objects.create(
                subject=ugettext(u"Contact"),
                type=action_type,
                planned_date=datetime.now(),
                display_on_board=True
            )
            action.contacts.add(contact)
            action.save()
            actions.append(action)
            
        # send an email
        send_notification_email(request, contact, actions, message)
        
        return contact


class NewsletterSchedulingForm(forms.ModelForm):
    """Define the newsletter sending date"""
    class Meta:
        model = models.Emailing
        fields = ('scheduling_dt',)

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = {'scheduling_dt': dt_now() + timedelta(minutes=5)}
        super(NewsletterSchedulingForm, self).__init__(*args, **kwargs)

    def clean_scheduling_dt(self):
        """validate datetime"""
        sch_dt = self.cleaned_data['scheduling_dt']

        if not sch_dt:
            raise ValidationError(ugettext(u"This field is required"))

        if sch_dt < dt_now():
            raise ValidationError(ugettext(u"The scheduling date must be in future"))

        return sch_dt


class MinimalSubscribeForm(BetterBsModelForm, SubscriptionTypeFormMixin):
    """Subscribe to emailing"""
    subscription_required = True

    favorite_language = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Contact
        fields = (
            'email', 'firstname', 'lastname'
        )
        widgets = {
            'lastname': forms.TextInput(attrs={'placeholder': _(u'Lastname')}),
            'firstname': forms.TextInput(attrs={'placeholder': _(u'Firstname')}),
            'email': forms.TextInput(attrs={'placeholder': _(u'Email'), 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super(MinimalSubscribeForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True

        self._add_subscription_types_field()

        if crm_settings.has_language_choices():
            self.fields['favorite_language'].initial = get_language()

    def get_entity(self):
        """get entity from form"""
        name = u'{0} {1}'.format(self.cleaned_data['lastname'], self.cleaned_data['firstname'])
        if crm_settings.ALLOW_SINGLE_CONTACT:
            return Entity.objects.create(name=name, type=None, is_single_contact=True)
        else:
            et_id = getattr(settings, 'BALAFON_INDIVIDUAL_ENTITY_ID', 1)
            entity_type = EntityType.objects.get(id=et_id)
            return Entity.objects.create(name=name, type=entity_type)

    def save(self, request=None):
        """save"""
        contact = super(MinimalSubscribeForm, self).save(commit=False)
        contact.entity = self.get_entity()
        contact.favorite_language = self.cleaned_data.get('favorite_language', '')
        contact.save()
        # delete unknown contacts for the current entity
        contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()

        subscriptions = self._save_subscription_types(contact)
        if subscriptions:
            create_subscription_action(contact, subscriptions)

        # send an email
        send_notification_email(request, contact, [], '')

        return contact

