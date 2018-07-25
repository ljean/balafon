# -*- coding: utf-8 -*-
"""Crm forms"""

from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms.__future__ as forms

from coop_cms.forms.base import InlineHtmlEditableModelForm

from balafon.widgets import CalcHiddenInput
from balafon.Crm import models
from balafon.Crm.forms.base import BetterBsModelForm, FormWithFieldsetMixin, BsPopupModelForm
from balafon.Crm.widgets import OpportunityAutoComplete


class ActionForm(FormWithFieldsetMixin, BetterBsModelForm):
    """form for creating or editing action"""

    date = forms.DateField(label=_(u"planned date"), required=False, widget=forms.TextInput())
    time = forms.TimeField(label=_(u"planned time"), required=False)

    end_date = forms.DateField(label=_(u"end date"), required=False, widget=forms.TextInput())
    end_time = forms.TimeField(label=_(u"end time"), required=False)

    amount = forms.DecimalField(label=_("Amount"), required=False)

    class Meta:
        """form from model"""
        model = models.Action
        fields = (
            'type', 'subject', 'date', 'time', 'status', 'status2', 'in_charge', 'detail',
            'amount', 'number', 'planned_date', 'end_date', 'end_time', 'end_datetime', 'opportunity'
        )
        fieldsets = [
            ('summary', {
                'fields': [
                    'subject', 'in_charge', 'date', 'time', 'planned_date', 'end_date', 'end_time', 'end_datetime',
                    'opportunity'
                ],
                'legend': _('Summary')
            }),
            ('type', {'fields': ['type', 'status', 'status2', 'amount', 'number'], 'legend': _('Type')}),
            ('details', {'fields': ['detail'], 'legend': _('Details')}),
        ]
        help_texts = {
            'amount': _('Amount is disabled when value is calculated'),
        }

    def __init__(self, *args, **kwargs):
        kwargs.pop('entity', None)
        instance = kwargs.get('instance', None)
        action_type = kwargs.pop('action_type', None)
        super(ActionForm, self).__init__(*args, **kwargs)
        self.title = u""
        if instance:
            action_type = instance.type
        self.action_type = action_type

        is_amount_calculated = False
        if action_type:
            is_amount_calculated = action_type.is_amount_calculated
            self.calculated_amount = Decimal("0")
            for fieldset_name, fieldset_attrs in self.Meta.fieldsets:
                if fieldset_name == 'type':
                    fieldset_attrs['legend'] = action_type.name
                    break
            self.fields['type'].widget = forms.HiddenInput()
            self.fields['type'].initial = action_type
            if instance:
                self.title = ugettext(u"Edition {0}").format(action_type.name)
            else:
                self.title = ugettext(u"Creation {0}").format(action_type.name)
        else:
            self.title = ugettext(u"Edit action") if instance else ugettext(u"Create action")

        is_auto_generated = (action_type and action_type.number_auto_generated) or \
                            (instance and instance.type and instance.type.number_auto_generated)
        if is_auto_generated:
            self.fields['number'].widget.attrs['disabled'] = 'disabled'
            self.fields['number'].required = False

        self.fields['amount'].widget.attrs['step'] = 'any'
        if is_amount_calculated:
            self.fields['amount'].widget.attrs['disabled'] = 'disabled'
        self.is_amount_calculated = is_amount_calculated

        if action_type and action_type.allowed_status.count():
            # let javascript disable the blank value if default_status
            choices = [('', "---------")]
            allowed_status = action_type.allowed_status.all()
            if instance and instance.frozen:
                allowed_status = allowed_status.filter(allowed_on_frozen=True)
            self.fields['status'].choices = choices + [
                (status.id, status.name) for status in allowed_status
            ]
            if action_type.default_status:
                self.fields['status'].initial = action_type.default_status.id
            else:
                self.fields['status'].initial = ''

        if action_type and action_type.allowed_status2.count():
            # let javascript disable the blank value if default_status2
            allowed_status2 = action_type.allowed_status2.all()
            if instance and instance.frozen:
                allowed_status2 = allowed_status2.filter(allowed_on_frozen=True)
            choices = [('', "---------")]
            self.fields['status2'].choices = choices + [
                (status.id, status.name) for status in allowed_status2
            ]
            if action_type.default_status2:
                self.fields['status2'].initial = action_type.default_status2.id
            else:
                self.fields['status2'].initial = ''
        else:
            self.fields['status2'].widget = forms.HiddenInput()

        self.fields['opportunity'].widget = forms.HiddenInput()
        self.fields['detail'].widget = forms.Textarea(attrs={'placeholder': _('enter details'), 'cols': '72'})

        self._init_dt_field("planned_date", "date", "time")
        self._init_dt_field("end_datetime", "end_date", "end_time")

    def _init_dt_field(self, dt_field, date_field, time_field):
        """init datetime fields"""
        self.fields[dt_field].widget = CalcHiddenInput()
        the_datetime = getattr(self.instance, dt_field) if self.instance else self.fields[dt_field].initial
        if the_datetime:
            self.fields[date_field].initial = the_datetime.date()
            if settings.USE_TZ:
                utc_dt = the_datetime.replace(tzinfo=timezone.utc)
                loc_dt = utc_dt.astimezone(timezone.get_current_timezone())
                self.fields[time_field].initial = loc_dt.time()
            else:
                self.fields[time_field].initial = the_datetime.time()

        is_frozen = self.instance.frozen if self.instance else False
        if is_frozen:
            self.fields[date_field].widget.attrs['disabled'] = 'disabled'
            self.fields[time_field].widget.attrs['disabled'] = 'disabled'

    def clean_status(self):
        """status validation"""
        type_of = self.cleaned_data.get('type') or self.action_type
        status = self.cleaned_data['status']
        if type_of:
            allowed_status = ([] if type_of.default_status else [None]) + list(type_of.allowed_status.all())
            if len(allowed_status) > 0 and status not in allowed_status:
                raise ValidationError(ugettext(u"This status can't not be used for this action type"))
        else:
            if status:
                raise ValidationError(ugettext(u"Please select a type before defining the status"))
        return status

    def clean_status2(self):
        """status validation"""
        type_of = self.cleaned_data['type']
        status = self.cleaned_data['status2']
        if type_of:
            allowed_status = ([] if type_of.default_status2 else [None]) + list(type_of.allowed_status2.all())
            if len(allowed_status) > 0 and status not in allowed_status:
                raise ValidationError(ugettext(u"This status can't not be used for this action type"))
        else:
            if status:
                raise ValidationError(ugettext(u"Please select a type before defining the status"))
        return status

    def clean_planned_date(self):
        """planned date validation"""
        the_date = self.cleaned_data.get("date", None)
        the_time = self.cleaned_data.get("time", None)
        if the_date:
            return datetime.combine(the_date, the_time or datetime.min.time())
        return None

    def clean_time(self):
        """time validation"""
        the_date = self.cleaned_data.get("date", None)
        the_time = self.cleaned_data.get("time", None)
        if the_time and not the_date:
            raise ValidationError(_(u"You must set a date"))
        return the_time

    def clean_end_date(self):
        """end date validation"""
        date1 = self.cleaned_data.get("date", None)
        date2 = self.cleaned_data.get("end_date", None)
        if date2:
            start_dt = self.cleaned_data["planned_date"]
            if not start_dt:
                raise ValidationError(_(u"The planned date is not defined"))
            if date1 > date2:
                raise ValidationError(_(u"The end date must be after the planned date"))
        return date2

    def clean_end_time(self):
        """end time validation"""
        date1 = self.cleaned_data.get("date", None)
        date2 = self.cleaned_data.get("end_date", None)
        time1 = self.cleaned_data.get("time", None)
        time2 = self.cleaned_data.get("end_time", None)

        if time2:
            if time2 and not date2:
                raise ValidationError(_(u"You must set a end date"))

            if date1 == date2 and (time1 or datetime.min.time()) >= time2:
                raise ValidationError(_(u"The end time must be after the planned time"))

        elif time1:
            if date1 == date2 and time1 >= datetime.min.time():
                raise ValidationError(_(u"The end time must be set"))
        return time2

    def clean_end_datetime(self):
        """clean end datetime"""
        end_date = self.cleaned_data.get("end_date", None)
        end_time = self.cleaned_data.get("end_time", None)
        if end_date:
            return datetime.combine(end_date, end_time or datetime.min.time())
        return None

    def clean_amount(self):
        if self.is_amount_calculated:
            return self.calculated_amount
        else:
            return self.cleaned_data['amount']

    def save(self, *args, **kwargs):
        return super(ActionForm, self).save(*args, **kwargs)


class ActionTypeForm(forms.ModelForm):
    """action type form"""

    class Meta:
        """form from model"""
        model = models.ActionType
        fields = (
            'subscribe_form', 'set', 'last_number', 'number_auto_generated', 'default_template', 'allowed_status',
            'default_status', 'is_editable', 'action_template', 'order_index', 'is_amount_calculated',
            'next_action_types', 'not_assigned_when_cloned', 'generate_uuid', 'hide_contacts_buttons',
            'mail_to_subject', 'allowed_status2', 'default_status2',
        )


class ActionDocumentForm(InlineHtmlEditableModelForm):
    """Action document form"""
    class Meta:
        model = models.ActionDocument
        fields = ('content',)


class ActionDoneForm(forms.ModelForm):
    """form setting an action done"""

    class Meta:
        """form from model"""
        model = models.Action
        fields = ['done']
        widgets = {
            'done': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        inst = kwargs.get('instance')
        inst.done = not inst.done
        kwargs['instance'] = inst
        super(ActionDoneForm, self).__init__(*args, **kwargs)


class OpportunityForm(FormWithFieldsetMixin, BetterBsModelForm):
    """opportunity form"""
    class Meta:
        """form from model"""
        model = models.Opportunity
        fields = ('name', 'detail')

        fieldsets = [
            ('name', {'fields': ['name', 'detail'], 'legend': _('Summary')}),
        ]

    def __init__(self, *args, **kwargs):
        super(OpportunityForm, self).__init__(*args, **kwargs)
        self.fields['detail'].widget = forms.Textarea(attrs={'placeholder': _('enter details'), 'cols':'72'})


class OpportunityStatusForm(forms.ModelForm):
    """opportunity status form"""

    class Meta:
        """form from model"""
        model = models.OpportunityStatus
        fields = ('name', 'ordering', )


class SelectOpportunityForm(forms.Form):
    """Select opportunity"""

    def __init__(self, *args, **kwargs):
        kwargs.pop('choices', None)
        super(SelectOpportunityForm, self).__init__(*args, **kwargs)
        widget = OpportunityAutoComplete(
            attrs={'placeholder': _('Enter the name of a opportunity'), 'size': '50', 'class': 'colorbox'})
        self.fields["opportunity"] = forms.CharField(label=_(u"Opportunity"), widget=widget)

    def clean_opportunity(self):
        """validation"""
        try:
            opportunity_id = int(self.cleaned_data["opportunity"])
            return models.Opportunity.objects.get(id=opportunity_id)
        except (ValueError, models.Opportunity.DoesNotExist):
            raise ValidationError(ugettext(u"The opportunity does'nt exist"))


class CloneActionForm(forms.Form):
    """form for clone_action: choose which type to chooses"""
    action_type = forms.ChoiceField(required=True, choices=[], label=_('New type'))

    def __init__(self, action_type, *args, **kwargs):
        super(CloneActionForm, self).__init__(*args, **kwargs)

        choices = [
            (action_type.id, action_type.name)
            for action_type in action_type.next_action_types.all().order_by('order_index')
        ]
        self.fields['action_type'].choices = choices
        # If only 1 choice = change it to a confirmation
        if len(choices) == 1:
            self.fields['action_type'].initial = choices[0][0]
            self.fields['action_type'].widget = forms.HiddenInput()
            self.single_choice = True
            self.action_type_name = choices[0][1]
        else:
            self.single_choice = False
            self.action_type_name = ''

    def clean_action_type(self):
        action_type = self.cleaned_data['action_type']
        try:
            return models.ActionType.objects.get(id=action_type)
        except models.ActionType.DoesNotExist:
            raise forms.ValidationError(_("Invalid type"))


class UpdateActionStatusForm(BsPopupModelForm):
    """form changing the status"""

    class Meta:
        """form from model"""
        model = models.Action
        fields = (
            'status', 'status2',
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(UpdateActionStatusForm, self).__init__(*args, **kwargs)

        if instance and instance.id and instance.type and instance.type.allowed_status.count():
            # let javascript disable the blank value if default_status
            allowed_status = instance.type.allowed_status.all()
            if instance.frozen:
                allowed_status = allowed_status.filter(allowed_on_frozen=True)
            self.fields['status'].choices = [
                (status.id, status.name) for status in allowed_status
            ]

        if instance and instance.id and instance.type and instance.type.allowed_status2.count():
            # let javascript disable the blank value if default_status2
            allowed_status2 = instance.type.allowed_status2.all()
            if instance.frozen:
                allowed_status2 = allowed_status2.filter(allowed_on_frozen=True)
            self.fields['status2'].choices = [
                (status.id, status.name) for status in allowed_status2
            ]
        else:
            self.fields['status2'].widget = forms.HiddenInput()

    def clean_status(self):
        """status validation"""
        status = self.cleaned_data['status']
        action_type = self.instance.type
        allowed_status = ([] if action_type.default_status else [None]) + list(action_type.allowed_status.all())
        if len(allowed_status) > 0 and status not in allowed_status:
            raise ValidationError(ugettext("This status can't not be used for this action type"))
        return status

    def clean_status2(self):
        """status validation"""
        status = self.cleaned_data['status2']
        action_type = self.instance.type
        allowed_status = ([] if action_type.default_status2 else [None]) + list(action_type.allowed_status2.all())
        if len(allowed_status) > 0 and status not in allowed_status:
            raise ValidationError(ugettext("This status can't not be used for this action type"))
        return status


class UpdateActionStatus2Form(BsPopupModelForm):
    """form changing the status"""

    class Meta:
        """form from model"""
        model = models.Action
        fields = (
            'status2',
        )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(UpdateActionStatus2Form, self).__init__(*args, **kwargs)

        if instance and instance.id and instance.type and instance.type.allowed_status2.count():
            # let javascript disable the blank value if default_status2
            self.fields['status2'].choices = [
                (status.id, status.name) for status in instance.type.allowed_status2.all()
            ]

    def clean_status2(self):
        """status validation"""
        status = self.cleaned_data['status2']
        action_type = self.instance.type
        allowed_status = ([] if action_type.default_status2 else [None]) + list(action_type.allowed_status2.all())
        if len(allowed_status) > 0 and status not in allowed_status:
            raise ValidationError(ugettext("This status can't not be used for this action type"))
        return status


class ActionMenuAdminForm(forms.ModelForm):
    """form limit the status if instance is selected"""

    def __init__(self, *args, **kwargs):
        """constructor"""
        super(ActionMenuAdminForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance', None)

        if instance and instance.action_type and instance.action_type.allowed_status.count():
            # limit choice of status to the allowed status of the action type
            self.fields['only_for_status'].queryset = instance.action_type.allowed_status.all()
