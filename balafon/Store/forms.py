# -*- coding: utf-8 -*-
"""forms"""

from decimal import Decimal, InvalidOperation

from django.utils.translation import ugettext

import floppyforms as forms

from balafon.Crm.models import ActionStatus
from balafon.Store.models import StoreManagementActionType, PricePolicy, StoreItemCategory


class StoreManagementActionTypeAdminForm(forms.ModelForm):
    """admin form"""

    class Meta:
        model = StoreManagementActionType
        fields = ['action_type', 'template_name', 'show_amount_as_pre_tax', 'readonly_status']

    def __init__(self, *args, **kwargs):
        super(StoreManagementActionTypeAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id and self.instance.action_type:
            self.fields['readonly_status'].queryset = self.instance.action_type.allowed_status
        else:
            self.fields['readonly_status'].queryset = ActionStatus.objects.none()
            self.fields['readonly_status'].widget = forms.HiddenInput()


class PricePolicyAdminForm(forms.ModelForm):
    """Assert than price policy is correct"""

    class Meta:
        model = PricePolicy
        fields = ('name', 'policy', 'parameters', 'apply_to', )

    def clean_parameters(self):
        parameters = self.cleaned_data['parameters']
        policy = self.cleaned_data['policy']
        if policy == 'multiply_purchase_by_ratio':
            try:
                Decimal(parameters)
            except InvalidOperation:
                text = ugettext(u'{0} is not a valid decimal'.format(parameters))
                if ',' in parameters:
                    text += u' ' + ugettext(u'Did you use coma rather than dot as decimal separator?')
                raise forms.ValidationError(text)
        return parameters


class StoreItemCategoryAdminForm(forms.ModelForm):
    """Assert than price policy is correct"""

    class Meta:
        model = StoreItemCategory
        fields = ('name', 'parent', 'price_policy', 'order_index', 'active', 'icon', )

    def clean_parent(self):
        parent = self.cleaned_data['parent']
        if self.instance and parent == self.instance:
            raise forms.ValidationError(ugettext(u'A category can not be its own parent'))

        if self.instance:
            print self.instance.get_sub_categories()
            if parent in self.instance.get_sub_categories():
                raise forms.ValidationError(
                    ugettext(u'A category can not be parent and children of another category')
                )

        return parent

