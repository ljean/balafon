# -*- coding: utf-8 -*-
"""forms"""

from django.utils.translation import ugettext_lazy as _

import floppyforms as forms
from coop_cms.forms import AlohaEditableModelForm

from sanza.Crm.forms import BetterBsForm
from sanza.Store.models import StoreItem


# class ChooseStoreItemForm(BetterBsForm):
#     """Select a form item"""
#     item = forms.ModelChoiceField(queryset=StoreItem.objects.none(), label=_(u"Item"))
#
#     def __init__(self, *args, **kwargs):
#         super(ChooseStoreItemForm, self).__init__(*args, **kwargs)
#         self.fields['item'].queryset = StoreItem.objects.all()
#
#
# class StoreItemSaleForm(AlohaEditableModelForm):
#     """A form for editing store item sales"""
#
#     class Meta:
#         model = StoreItemSale
#         fields = ('sale', 'text', 'item', 'quantity', 'pre_tax_price', 'vat_rate',)
#         no_aloha_widgets = ('id', 'DELETE', 'sale', 'item', 'quantity', 'pre_tax_price', 'vat_rate',)
#
#     def __init__(self, *args, **kwargs):
#         sale = kwargs.pop('sale', None)
#         super(StoreItemSaleForm, self).__init__(*args, **kwargs)
#         self.fields['sale'].widget = forms.HiddenInput()
#         if sale:
#             self.fields['sale'].initial = sale
