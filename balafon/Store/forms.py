# -*- coding: utf-8 -*-
"""forms"""

from __future__ import unicode_literals

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms.__future__ as forms

from coop_cms.utils import RequestManager, RequestNotFound

from balafon.Crm.forms.base import BetterBsForm
from balafon.Crm.models import ActionStatus
from balafon.Store.models import (
    StoreManagementActionType, PricePolicy, StoreItemCategory, SaleAnalysisCode, VatRate, update_action_amount
)


class StoreManagementActionTypeAdminForm(forms.ModelForm):
    """admin form"""
    initial_show_amount_as_pre_tax = None

    def __init__(self, *args, **kwargs):
        super(StoreManagementActionTypeAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id and self.instance.action_type:
            self.initial_show_amount_as_pre_tax = self.instance.show_amount_as_pre_tax
            self.fields['readonly_status'].queryset = self.instance.action_type.allowed_status
        else:
            self.fields['readonly_status'].queryset = ActionStatus.objects.none()
            self.fields['readonly_status'].widget = forms.HiddenInput()

    def save(self, *args, **kwargs):
        show_amount_as_pre_tax = self.cleaned_data['show_amount_as_pre_tax']
        recalculate = False
        if self.instance and self.initial_show_amount_as_pre_tax != show_amount_as_pre_tax:
            recalculate = True
        ret = super(StoreManagementActionTypeAdminForm, self).save(*args, **kwargs)
        if recalculate:
            action_type = self.instance.action_type
            for action in action_type.action_set.all():
                try:
                    update_action_amount(action.sale)
                except (AttributeError, StoreManagementActionType.DoesNotExist):
                    pass
            try:
                request = RequestManager().get_request()
                if request:
                    messages.success(
                        request,
                        _('Recalculate {0} {1}').format(action_type.action_set.count(), action_type)
                    )
            except (RequestNotFound, AttributeError):
                pass
        return ret


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
                text = ugettext('{0} is not a valid decimal'.format(parameters))
                if ',' in parameters:
                    text += ' ' + ugettext('Did you use coma rather than dot as decimal separator?')
                raise forms.ValidationError(text)
        return parameters


class StoreItemCategoryAdminForm(forms.ModelForm):
    """Assert than price policy is correct"""

    class Meta:
        model = StoreItemCategory
        fields = ('name', 'parent', 'price_policy', 'order_index', 'active', 'icon', 'default_image', )

    def clean_parent(self):
        parent = self.cleaned_data['parent']
        if self.instance and parent == self.instance:
            raise forms.ValidationError(ugettext('A category can not be its own parent'))

        if self.instance:
            if parent in self.instance.get_sub_categories():
                raise forms.ValidationError(
                    ugettext('A category can not be parent and children of another category')
                )

        return parent


class AddExtraSaleForm(BetterBsForm):
    """A form for adding a new extra sale"""

    analysis_code = forms.ChoiceField(label=_('Analysis code'), required=True)
    amount = forms.DecimalField(max_digits=9, decimal_places=2, required=True, label=_('Amount'))
    vat_rate = forms.ChoiceField(label=_('VAT rate'), required=True)
    date = forms.DateField(label=_('Date'), required=True)

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
            forms.ValidationError(ugettext('Invalid analysis code'))

    def clean_vat_rate(self):
        """validate the analysis code"""
        vat_rate_id = self.cleaned_data['vat_rate']
        try:
            return VatRate.objects.get(id=vat_rate_id)
        except VatRate.DoesNotExist:
            forms.ValidationError(ugettext('Invalid analysis code'))


class StockImportForm(BetterBsForm):
    """A form for importing stock values from Excel"""

    xls_file = forms.FileField(
        label=_('Excel file'),
        help_text=_('Same format than the export file. It will update the purchase price, stock count and threshold')
    )


class DateRangeForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today()
        first_day_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            month_of_next = 1
            year_of_next = today.year + 1
        else:
            month_of_next = today.month + 1
            year_of_next = today.year
        first_day_of_next_month = date(year_of_next, month_of_next, 1)
        last_day_of_month = first_day_of_next_month - timedelta(days=1)

        self.fields['start_date'] = forms.DateField(label=_("From"), required=True, initial=first_day_of_month)
        self.fields['end_date'] = forms.DateField(label=_("To"), required=True, initial=last_day_of_month)
