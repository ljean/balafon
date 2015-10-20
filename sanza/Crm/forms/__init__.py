# -*- coding: utf-8 -*-
"""Crm forms"""

import floppyforms as forms

from sanza.Crm.forms.actions import (
    ActionForm, ActionDocumentForm, ActionDoneForm, ActionTypeForm, CloneActionForm, SelectOpportunityForm,
    OpportunityForm, OpportunityStatusForm, UpdateActionStatusForm
)
from sanza.Crm.forms.base import BetterBsForm, BetterBsModelForm, ModelFormWithCity, FormWithCity
from sanza.Crm.forms.contacts import (
    ContactForm, SelectContactForm, SelectContactOrEntityForm, SameAsForm, AddRelationshipForm, ContactsImportForm,
    ContactsImportConfirmForm, UnsubscribeContactsImportForm
)
from sanza.Crm.forms.custom_fields import (
    CustomFieldForm, ContactCustomFieldForm, EntityCustomFieldForm
)
from sanza.Crm.forms.entities import (
    EntityForm, EntityRoleForm, EntityTypeForm, ChangeContactEntityForm, SelectEntityForm,
)
from sanza.Crm.forms.groups import (
    AddContactToGroupForm, AddEntityToGroupForm, EditGroupForm
)


class ConfirmForm(forms.Form):
    """Confirmation form"""
    confirm = forms.BooleanField(initial=True, widget=forms.HiddenInput(), required=False)
