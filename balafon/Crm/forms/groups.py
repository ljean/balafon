# -*- coding: utf-8 -*-
"""Crm forms"""

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms

from coop_cms.bs_forms import ModelForm as BsModelForm

from balafon.Crm import models


class AddEntityToGroupForm(forms.Form):
    """form for adding an entity to a group"""
    group_name = forms.CharField(
        label=_(u"Group name"),
        widget=forms.TextInput(attrs={'size': 70, 'placeholder': _(u'start typing name and choose if exists')})
    )

    def __init__(self, entity, *args, **kwargs):
        self.entity = entity
        super(AddEntityToGroupForm, self).__init__(*args, **kwargs)

    def clean_group_name(self):
        """"validation"""
        name = self.cleaned_data['group_name']
        if models.Group.objects.filter(name=name, entities__id=self.entity.id).count() > 0:
            raise ValidationError(ugettext(u"The entity already belong to group {0}").format(name))
        return name


class AddContactToGroupForm(forms.Form):
    """form for adding a contact to a group"""
    group_name = forms.CharField(
        label=_(u"Group name"),
        widget=forms.TextInput(attrs={'size': 70, 'placeholder': _(u'start typing name and choose if exists')})
    )

    def __init__(self, contact, *args, **kwargs):
        self.contact = contact
        super(AddContactToGroupForm, self).__init__(*args, **kwargs)

    def clean_group_name(self):
        """validation"""
        name = self.cleaned_data['group_name']
        if models.Group.objects.filter(name=name, contacts__id=self.contact.id).count() > 0:
            raise ValidationError(ugettext(u"The contact already belong to group {0}").format(name))
        return name


class EditGroupForm(BsModelForm):
    """form for editing a group"""

    class Meta:
        """Define the form from model"""
        model = models.Group
        fields = ('name', 'description', 'background_color', 'fore_color', 'subscribe_form', 'entities', 'contacts')
        widgets = {
            'description': forms.TextInput(
                attrs={
                    'placeholder': _(u'Enter a description for your group'),
                    'size': '80',
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'placeholder': _(u'Enter a name for your group'),
                    'size': '80',
                }
            ),
        }

    def clean_name(self):
        """name validation"""
        name = self.cleaned_data['name']
        if self.instance and not self.instance.id:
            if models.Group.objects.filter(name=name).exclude(id=self.instance.id).count() > 0:
                raise ValidationError(ugettext(u"A group with this name already exists"))
        return name

    def _clean_list(self, the_list):
        return [int(id_) for id_ in the_list.strip('[').strip(']').split(',') if id_]

    def clean_entities(self):
        """name validation"""
        entities_ids = self._clean_list(self.cleaned_data['entities'])
        return entities_ids

    def clean_contacts(self):
        """name validation"""
        contacts_ids = self._clean_list(self.cleaned_data['contacts'])
        return contacts_ids

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(EditGroupForm, self).__init__(*args, **kwargs)

        self.fields['entities'] = forms.CharField(
            widget=forms.HiddenInput(),
            required=False
        )

        self.fields['contacts'] = forms.CharField(
            widget=forms.HiddenInput(),
            required=False
        )
