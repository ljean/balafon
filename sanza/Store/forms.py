# -*- coding: utf-8 -*-
"""forms"""

import floppyforms as forms

from sanza.Crm.models import ActionStatus
from sanza.Store.models import StoreManagementActionType


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
