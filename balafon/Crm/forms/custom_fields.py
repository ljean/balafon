# -*- coding: utf-8 -*-
"""Crm forms"""

from __future__ import unicode_literals

import floppyforms.__future__ as forms

from balafon.Crm import models
from balafon.Crm.forms.base import BetterBsForm


class CustomFieldForm(BetterBsForm):
    """base form for custom fields"""
    def __init__(self, instance, *args, **kwargs):
        super(CustomFieldForm, self).__init__(*args, **kwargs)
        self._instance = instance
        model_type = self._get_model_type()
        custom_fields = models.CustomField.objects.filter(model=model_type)
        for field in custom_fields:
            self.fields[field.name] = forms.CharField(required=False, label=field.label or field.name)

            self.fields[field.name].widget.attrs = {'class': 'form-control'}
            if field.widget:
                self.fields[field.name].widget.attrs['class'] += ' ' + field.widget

            #No Post
            if len(args) == 0:
                self.fields[field.name].initial = getattr(instance, 'custom_field_'+field.name, '')

    def save(self, *args, **kwargs):
        """save"""
        for field in self.fields:
            model_type = self._get_model_type()
            custom_field = models.CustomField.objects.get(name=field, model=model_type)
            custom_field_value = self._create_custom_field_value(custom_field)
            custom_field_value.value = self.cleaned_data[field]
            custom_field_value.save()
        return self._instance


class EntityCustomFieldForm(CustomFieldForm):
    """form for setting custom fields on an entity"""

    def _get_model_type(self):
        """is entity"""
        return models.CustomField.MODEL_ENTITY

    @staticmethod
    def model():
        """model"""
        return models.Entity

    def _create_custom_field_value(self, custom_field):
        """save the value in database"""
        custom_field_value = models.EntityCustomFieldValue.objects.get_or_create(
            entity=self._instance, custom_field=custom_field
        )[0]
        return custom_field_value


class ContactCustomFieldForm(CustomFieldForm):
    """form for setting custom fields of a contact"""

    def _get_model_type(self):
        """type -> contact"""
        return models.CustomField.MODEL_CONTACT

    def _create_custom_field_value(self, custom_field):
        """save value in database"""
        custom_field_value = models.ContactCustomFieldValue.objects.get_or_create(
            contact=self._instance, custom_field=custom_field
        )[0]
        return custom_field_value

    @staticmethod
    def model():
        """model"""
        return models.Contact