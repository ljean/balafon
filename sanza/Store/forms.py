# -*- coding: utf-8 -*-
"""forms"""

import floppyforms as forms
from coop_cms.forms import AlohaEditableModelForm

from sanza.Store.models import StoreItemSale


class StoreItemSaleForm(AlohaEditableModelForm):
    """A form for editing store item sales"""

    class Meta:
        model = StoreItemSale
        fields = ('sale', 'item', 'quantity')
        no_aloha_widgets = ('id', 'sale', 'item', 'quantity')

    def __init__(self, *args, **kwargs):
        print "*********", kwargs
        super(StoreItemSaleForm, self).__init__(*args, **kwargs)
        self.fields['sale'].widget = forms.HiddenInput()
        if not self.instance.id:
            self.fields['sale'].initial = self.instance.sale
