# -*- coding: utf-8 -*-
"""Crm forms"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms

from coop_cms.bs_forms import ModelForm as BsModelForm

from balafon.Crm import models
from balafon.Crm.forms.base import ModelFormWithAddress, FormWithFieldsetMixin, BetterBsForm
from balafon.Crm.settings import (
    get_language_choices, has_language_choices, get_subscription_default_value, show_billing_address,
    ALLOW_COUPLE_GENDER,
)
from balafon.Crm.utils import get_suggested_same_as_contacts
from balafon.Crm.widgets import ContactAutoComplete


class ContactForm(FormWithFieldsetMixin, ModelFormWithAddress):
    """Edit contact form"""
    same_as_suggestions = forms.ChoiceField(
        label=_(u'Same-as contacts'),
        choices=[],
        required=False,
        help_text=_(
            u'If this is a new contact for an existing person, you can link the different contacts between them'
        ),
        widget=forms.Select(
            attrs={'class': 'chosen-select', 'data-placeholder': _(u'Select same-as contacts'), 'style': "width: 100%;"}
        )
    )

    class Meta:
        """form is defined from model"""
        model = models.Contact
        fields = (
            'gender', 'lastname', 'firstname', 'birth_date', 'title', 'role', 'job',
            'email', 'phone', 'mobile', 'favorite_language',
            'street_number', 'street_type', 'address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country',
            'main_contact', 'email_verified', 'has_left', 'accept_notifications', 'photo',
            'billing_street_number', 'billing_street_type', 'billing_address', 'billing_address2', 'billing_address3',
            'billing_zip_code', 'billing_city', 'billing_cedex', 'billing_country', 'same_as_suggestions'
        )
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'enter notes about the contact'), 'cols': '72'}),
            'role': forms.SelectMultiple(
                attrs={'class': 'chosen-select', 'data-placeholder': _(u'Select roles'), 'style': "width: 100%;"}
            ),
        }
        fieldsets = [
            ('name', {
                'fields': [
                    'gender', 'lastname', 'firstname', 'email', 'same_as_suggestions', 'phone', 'mobile'
                ],
                'legend': _(u'Name')
            }),
            ('web', {
                'fields': [
                    'birth_date', 'title', 'role', 'job', 'favorite_language',
                ],
                'legend': _(u'Contact details')
                }
            ),
            ('address', {
                'fields': [
                    'street_number', 'street_type', 'address', 'address2', 'address3', 'zip_code', 'city',
                    'cedex', 'country'
                ],
                'legend': _(u'Address')
            }),
            ('billing_address', {
                'fields': [
                    'billing_street_number', 'billing_street_type', 'billing_address', 'billing_address2',
                    'billing_address3', 'billing_zip_code', 'billing_city', 'billing_cedex', 'billing_country'
                ],
                'legend': _(u'Billing address')
            }),
            ('relationship', {
                'fields': ['main_contact', 'email_verified', 'has_left', 'accept_notifications'],
                'legend': _(u'Options')
            }),
            ('photo', {'fields': ['photo'], 'legend': _(u'Photo')}),
        ]

    def __init__(self, *args, **kwargs):
        # Configure the fieldset with dynamic fields
        fieldset_fields = self.Meta.fieldsets[-2][1]["fields"]
        for subscription_type in models.SubscriptionType.objects.all():
            field_name = "subscription_{0}".format(subscription_type.id)
            if field_name not in fieldset_fields:
                fieldset_fields.append(field_name)

        super(ContactForm, self).__init__(*args, **kwargs)

        try:
            if self.instance and self.instance.entity and self.instance.entity.is_single_contact:
                self.fields['has_left'].widget = forms.HiddenInput()
        except models.Entity.DoesNotExist:
            pass

        self.fields["role"].help_text = _(u"Select the roles played by the contact in his entity")

        if 'balafon.Profile' not in settings.INSTALLED_APPS:
            self.fields["accept_notifications"].widget = forms.HiddenInput()

        self.fields["email_verified"].widget.attrs['disabled'] = "disabled"

        # define the allowed gender
        gender_choices = [
            ('', u'-------'),
            (models.Contact.GENDER_MALE, ugettext(u'Mr')),
            (models.Contact.GENDER_FEMALE, ugettext(u'Mrs')),
        ]
        if ALLOW_COUPLE_GENDER:
            gender_choices += [
                (models.Contact.GENDER_COUPLE, ugettext(u'Mrs and Mr'))
            ]
        self.fields['gender'].choices = gender_choices

        # create the dynamic fields
        for subscription_type in models.SubscriptionType.objects.all():
            field_name = "subscription_{0}".format(subscription_type.id)
            field = self.fields[field_name] = forms.BooleanField(
                label=subscription_type.name, required=False
            )
            if self.instance:
                try:
                    subscription = models.Subscription.objects.get(
                        subscription_type=subscription_type, contact=self.instance
                    )
                    field.initial = subscription.accept_subscription
                except models.Subscription.DoesNotExist:
                    field.initial = get_subscription_default_value()
            else:

                field.initial = get_subscription_default_value()

        if has_language_choices():
            self.fields['favorite_language'].widget = forms.Select(
                choices=get_language_choices(), attrs={'class': 'form-control'}
            )
        else:
            self.fields['favorite_language'].widget = forms.HiddenInput()

        if not self.instance or not any([self.instance.lastname, self.instance.firstname, self.instance.email]):
            # If the contact has not been created of not filled
            pass
            # keep the widget
            if len(args):
                # The form has been posted; we must initialize the list with allowed values
                contact_id = self.instance.id if self.instance else None
                post_data = args[0]
                lastname = post_data.get('lastname', '')
                firstname = post_data.get('firstname', '')
                email = post_data.get('email', '')
                same_as_contacts = get_suggested_same_as_contacts(
                    contact_id=contact_id, lastname=lastname, firstname=firstname, email=email
                )
                self.fields['same_as_suggestions'].choices = [
                    (contact.id, unicode(contact)) for contact in same_as_contacts
                ]
        else:
            # hide the field
            self.fields['same_as_suggestions'].widget = forms.HiddenInput()

    def get_fieldsets(self):
        """return the list of fieldsets"""
        for fieldset in self.Meta.fieldsets:
            if fieldset[0] == 'billing_address' and not show_billing_address():
                # Ignore 'Billing address' tab if disable in settings
                continue
            yield fieldset

    def clean_photo(self):
        """photo validation"""
        photo = self.cleaned_data["photo"]
        instance = self.instance
        if not instance:
            instance = ""
            try:
                instance.id = models.Contact.objects.latest('id').id
            except models.Contact.DoesNotExist:
                instance.id = 1
        target_name = models.get_contact_photo_dir(instance, photo)
        if len(target_name) >= models.Contact._meta.get_field('photo').max_length:
            raise ValidationError(ugettext(u"The file name is too long"))
        return photo

    def save_contact_subscriptions(self, contact):
        """save contact subscriptions"""
        for subscription_type in models.SubscriptionType.objects.all():
            field_name = "subscription_{0}".format(subscription_type.id)
            accept_subscription = self.cleaned_data[field_name]
            try:
                subscription = models.Subscription.objects.get(
                    contact=contact, subscription_type=subscription_type
                )
                if subscription.accept_subscription != accept_subscription:
                    subscription.accept_subscription = accept_subscription
                    subscription.save()
            except models.Subscription.DoesNotExist:
                if accept_subscription:
                    models.Subscription.objects.create(
                        contact=contact,
                        subscription_type=subscription_type,
                        accept_subscription=True
                    )

    def clean_same_as_suggestions(self):
        contact_id = self.cleaned_data.get('same_as_suggestions', '')
        if contact_id:
            try:
                contact = models.Contact.objects.get(id=contact_id)
                return contact
            except models.Contact.DoesNotExist:
                raise ValidationError(ugettext(u"Contact does'nt exist"))

    def save_same_as(self, this_contact):
        contact = self.cleaned_data['same_as_suggestions']
        if contact:
            # if not found create one
            if not contact.same_as:
                this_contact.same_as = models.SameAs.objects.create()
                this_contact.same_as_priority = 2
                contact.same_as = this_contact.same_as
                contact.same_as_priority = 1
                contact.save()
            else:
                this_contact.same_as = contact.same_as
                this_contact.same_as_priority = contact.same_as.contact_set.count() + 1
            this_contact.save()

    def save(self, *args, **kwargs):
        """save"""
        contact = super(ContactForm, self).save(*args, **kwargs)
        if kwargs.get('commit', True):
            self.save_contact_subscriptions(contact)
            self.save_same_as(contact)
        return contact


class SelectContactForm(forms.Form):
    """Select a contact"""

    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        super(SelectContactForm, self).__init__(*args, **kwargs)
        if choices:
            widget = forms.Select(choices=[(x.id, x.fullname) for x in choices])
            self.fields["contact"] = forms.IntegerField(label=_(u"Contact"), widget=widget)
        else:
            widget = ContactAutoComplete(
                attrs={'placeholder': _(u'Enter the name of a contact'), 'size': '50', 'class': 'colorbox'}
            )
            self.fields["contact"] = forms.CharField(label=_(u"Contact"), widget=widget)

    def clean_contact(self):
        """validation"""
        try:
            contact_id = int(self.cleaned_data["contact"])
            return models.Contact.objects.get(id=contact_id)
        except (ValueError, models.Contact.DoesNotExist):
            raise ValidationError(ugettext(u"The contact does'nt exist"))


class SelectContactOrEntityForm(forms.Form):
    """Select a contact or entity"""
    object_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    object_type = forms.CharField(widget=forms.HiddenInput(), required=True)
    name = forms.CharField(required=True, label=_('Name'))

    def clean_name(self):
        """validation"""
        object_id = self.cleaned_data.get('object_id', '')
        object_type = self.cleaned_data.get('object_type', '')
        object_class = {
            'contact': models.Contact,
            'entity': models.Entity,
        }.get(object_type, None)

        if not object_class:
            raise ValidationError(ugettext(u"Invalid type '{0}'").format(object_type))

        try:
            object_id = int(object_id)
            return object_class.objects.get(id=object_id)
        except (ValueError, object_class.DoesNotExist):
            raise ValidationError(ugettext(u"Does'nt exist"))


class SameAsPriorityForm(BetterBsForm):
    """Define "same as" priority for a contact"""
    priority = forms.IntegerField(label=_(u"Priority"))

    def __init__(self, contact, *args, **kwargs):
        super(SameAsPriorityForm, self).__init__(*args, **kwargs)
        self.contact = contact
        self.fields['priority'].initial = contact.same_as_priority

    def clean_priority(self):
        """make sure that the priority is an integer between 1 and number of same as"""
        value = self.cleaned_data['priority']
        min_value = 1
        max_value = self.contact.same_as.contact_set.count()
        if value < min_value or value > max_value:
            raise ValidationError(
                ugettext(u'Invalid value : It should be between {0} and {1}').format(
                    min_value, max_value
                )
            )
        return value


class SameAsSuggestionForm(forms.Form):
    """
    generate suggestion list from a few data.
    This form is not displayed and used by json API
    """
    id = forms.IntegerField(required=False)
    lastname = forms.CharField(required=False)
    firstname = forms.CharField(required=False)
    email = forms.CharField(required=False)

    def get_suggested_contacts(self):
        """return list a suggestions for same as"""
        contact_id = self.cleaned_data['id']
        lastname = self.cleaned_data['lastname']
        firstname = self.cleaned_data['firstname']
        email = self.cleaned_data['email']
        return get_suggested_same_as_contacts(
            contact_id=contact_id, lastname=lastname, firstname=firstname, email=email
        )


class SameAsForm(forms.Form):
    """Define "same as" for two contacts"""
    contact = forms.IntegerField(label=_(u"Contact"))

    def __init__(self, contact, *args, **kwargs):
        super(SameAsForm, self).__init__(*args, **kwargs)
        potential_contacts = get_suggested_same_as_contacts(
            contact_id=contact.id, lastname=contact.lastname, firstname=contact.firstname, email=contact.email
        )
        if contact.same_as:
            # Do not propose again current SameAs
            potential_contacts = potential_contacts.exclude(same_as=contact.same_as)
        self._same_as = [(same_as_contact.id, u"{0}".format(same_as_contact)) for same_as_contact in potential_contacts]
        if len(self._same_as):
            self.fields["contact"].widget = forms.Select(choices=self._same_as)
        else:
            self.fields["contact"].widget = forms.HiddenInput()

    def has_choices(self):
        """true if several contacts with same name"""
        return len(self._same_as)

    def clean_contact(self):
        """validation"""
        contact_id = self.cleaned_data["contact"]
        try:
            if contact_id not in [same_as[0] for same_as in self._same_as]:
                raise ValidationError(ugettext(u"Invalid contact"))
            return models.Contact.objects.get(id=contact_id)
        except models.Contact.DoesNotExist:
            raise ValidationError(ugettext(u"Contact does not exist"))


class AddRelationshipForm(forms.Form):
    """form for adding relationships"""
    relationship_type = forms.IntegerField(label=_(u"relationship type"))
    contact2 = forms.CharField(label=_(u"Contact"))

    def __init__(self, contact1, *args, **kwargs):
        super(AddRelationshipForm, self).__init__(*args, **kwargs)

        self.reversed_relation = False
        self.contact1 = contact1

        relationship_types = []
        for relationship_type in models.RelationshipType.objects.all():
            relationship_types.append((relationship_type.id, relationship_type.name))
            if relationship_type.reverse:
                relationship_types.append((-relationship_type.id, relationship_type.reverse))
        self.fields["relationship_type"].widget = forms.Select(choices=relationship_types)

        widget = ContactAutoComplete(
            attrs={'placeholder': _(u'Enter the name of a contact'), 'size': '50', 'class': 'colorbox'}
        )
        self.fields["contact2"] = forms.CharField(label=_(u"Contact"), widget=widget)

    def clean_relationship_type(self):
        """validate relationship type"""
        try:
            self.reversed_relation = False
            relationship_type = int(self.cleaned_data["relationship_type"])
            if relationship_type < 0:
                self.reversed_relation = True
                relationship_type = -relationship_type
            return models.RelationshipType.objects.get(id=relationship_type)
        except ValueError:
            raise ValidationError(ugettext(u"Invalid data"))
        except models.RelationshipType.DoesNotExist:
            raise ValidationError(ugettext(u"Relationship type does not exist"))

    def clean_contact2(self):
        """clean the contacts in relation"""
        try:
            contact2 = int(self.cleaned_data["contact2"])
            return models.Contact.objects.get(id=contact2)
        except ValueError:
            raise ValidationError(ugettext(u"Invalid data"))
        except models.Contact.DoesNotExist:
            raise ValidationError(ugettext(u"Contact does not exist"))

    def save(self):
        """save"""
        if self.reversed_relation:
            contact1 = self.cleaned_data["contact2"]
            contact2 = self.contact1
        else:
            contact1 = self.contact1
            contact2 = self.cleaned_data["contact2"]

        relationship_type = self.cleaned_data["relationship_type"]
        return models.Relationship.objects.create(
            contact1=contact1, contact2=contact2, relationship_type=relationship_type
        )


class ContactsImportForm(BsModelForm):
    """form for importing data"""
    class Meta:
        """form from model"""
        model = models.ContactsImport
        fields = ('import_file', 'name', 'encoding', 'separator', 'entity_type', 'groups', 'entity_name_from_email', )

    class Media:
        """media files"""
        css = {
            'all': ('chosen/chosen.css', 'chosen/chosen-bootstrap.css')
        }
        js = (
            'chosen/chosen.jquery.js',
        )

    def __init__(self, *args, **kwargs):
        super(ContactsImportForm, self).__init__(*args, **kwargs)

        self.fields['groups'].widget.attrs = {
            'class': 'chosen-select form-control',
            'data-placeholder': _(u'The created entities will be added to the selected groups'),
        }
        self.fields['groups'].help_text = ''

    def clean_separator(self):
        """validation"""
        if len(self.cleaned_data["separator"]) != 1:
            raise ValidationError(ugettext(u'Invalid separator {0}').format(self.cleaned_data["separator"]))
        return self.cleaned_data["separator"]


class ContactsImportConfirmForm(ContactsImportForm):
    """confirm contact import"""
    default_department = forms.ChoiceField(
        required=False,
        label=_(u'Default department'),
        help_text=_(u'The city in red will be created with this department as parent')
    )

    class Meta(ContactsImportForm.Meta):
        """from model"""
        fields = ('encoding', 'separator', 'entity_type', 'groups', 'entity_name_from_email', )

    def __init__(self, *args, **kwargs):
        super(ContactsImportConfirmForm, self).__init__(*args, **kwargs)
        zone_tuples = [(zone.code, zone.name) for zone in models.Zone.objects.filter(type__type='department')]
        self.fields['default_department'].choices = [('', '')] + zone_tuples

    def clean_default_department(self):
        """validation"""
        code = self.cleaned_data['default_department']
        if code:
            if not models.Zone.objects.filter(code=self.cleaned_data['default_department']):
                raise ValidationError(ugettext(u'Please enter a valid code'))
            return self.cleaned_data['default_department']
        else:
            return None


class UnsubscribeContactsImportForm(forms.Form):
    """A form for uploading a file"""
    input_file = forms.FileField()
