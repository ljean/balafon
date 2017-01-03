# -*- coding: utf-8 -*-
"""forms"""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms

from balafon.Crm.forms.base import BetterBsForm
from balafon.Crm.models import ActionStatus
from balafon.Store.models import StoreManagementActionType, PricePolicy, StoreItemCategory, SaleAnalysisCode, VatRate


class StoreManagementActionTypeAdminForm(forms.ModelForm):
    """admin form"""

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
            if parent in self.instance.get_sub_categories():
                raise forms.ValidationError(
                    ugettext(u'A category can not be parent and children of another category')
                )

        return parent


class AddExtraSaleForm(BetterBsForm):
    """A form for adding a new extra sale"""

    analysis_code = forms.ChoiceField(label=_(u'Analysis code'), required=True)
    amount = forms.DecimalField(max_digits=9, decimal_places=2, required=True, label=_(u'Amount'))
    vat_rate = forms.ChoiceField(label=_(u'VAT rate'), required=True)
    date = forms.DateField(label=_(u'Date'), required=True)

    def __init__(self, *args, **kwargs):
        super(AddExtraSaleForm, self).__init__(*args, **kwargs)

        self.valid_action_types = [item.action_type for item in StoreManagementActionType.objects.all()]

        self.fields['analysis_code'].choices = [
            (analysis_code.id, analysis_code.name)
            for analysis_code in SaleAnalysisCode.objects.filter(action_type__in=self.valid_action_types)
        ]
        self.fields['vat_rate'].choices = [
            (vat_rate.id, vat_rate.name)
            for vat_rate in VatRate.objects.all()
        ]
        self.fields['date'].initial = date.today()

    def clean_analysis_code(self):
        """validate the analysis code"""
        analysis_code_id = self.cleaned_data['analysis_code']
        try:
            return SaleAnalysisCode.objects.get(id=analysis_code_id, action_type__in=self.valid_action_types)
        except SaleAnalysisCode.DoesNotExist:
            forms.ValidationError(ugettext(u'Invalid analysis code'))

    def clean_vat_rate(self):
        """validate the analysis code"""
        vat_rate_id = self.cleaned_data['vat_rate']
        try:
            return VatRate.objects.get(id=vat_rate_id)
        except VatRate.DoesNotExist:
            forms.ValidationError(ugettext(u'Invalid analysis code'))


class StockImportForm(BetterBsForm):
    """A form for importing stock values from Excel"""

    xls_file = forms.FileField(
        label=_(u'Excel file'),
        help_text=_(u'Same format than the export file. It will update the purchase price, stock count and threshold')
    )