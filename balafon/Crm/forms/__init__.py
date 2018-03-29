# -*- coding: utf-8 -*-
"""Crm forms"""

from __future__ import unicode_literals

import floppyforms.__future__ as forms

from balafon.Crm.forms.actions import (
    ActionForm, ActionDocumentForm, ActionDoneForm, ActionTypeForm, CloneActionForm, SelectOpportunityForm,
    OpportunityForm, OpportunityStatusForm, UpdateActionStatusForm, UpdateActionStatus2Form
)
from balafon.Crm.forms.base import (
    BetterBsForm, BetterBsModelForm, ModelFormWithCity, FormWithCity, BsPopupModelForm, BsPopupForm
)
from balafon.Crm.forms.contacts import (
    ContactForm, SelectContactForm, SelectContactOrEntityForm, SameAsForm, SameAsPriorityForm, AddRelationshipForm,
    ContactsImportForm, ContactsImportConfirmForm, UnsubscribeContactsImportForm, SameAsSuggestionForm
)
from balafon.Crm.forms.custom_fields import (
    CustomFieldForm, ContactCustomFieldForm, EntityCustomFieldForm
)
from balafon.Crm.forms.entities import (
    EntityForm, EntityRoleForm, EntityTypeForm, ChangeContactEntityForm, SelectEntityForm,
)
from balafon.Crm.forms.groups import (
    AddContactToGroupForm, AddEntityToGroupForm, EditGroupForm
)


class ConfirmForm(forms.Form):
    """Confirmation form"""
    confirm = forms.BooleanField(initial=True, widget=forms.HiddenInput(), required=False)
