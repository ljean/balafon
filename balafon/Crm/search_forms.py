# -*- coding: utf-8 -*-
"""forms than can be included as part of the main search form"""

from __future__ import unicode_literals

from datetime import date, timedelta

from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

import floppyforms.__future__ as forms

from balafon.Crm import models
from balafon.Crm.settings import get_language_choices
from balafon.Crm.utils import (
    get_default_country, sort_by_name_callback, sort_by_entity_callback, sort_by_contact_callback
)
from balafon.Crm.widgets import CityNoCountryAutoComplete, GroupAutoComplete
from balafon.Search.forms import SearchFieldForm, TwoDatesForm, YesNoSearchFieldForm


class EntityNameSearchForm(SearchFieldForm):
    """by entity name"""
    name = 'entity_name'
    label = _('Entity name')
    
    def __init__(self, *args, **kwargs):
        super(EntityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter a part of the name of the searched entities')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__name__icontains': self.value}
    

class EntityDescriptionForm(SearchFieldForm):
    """by entity description"""

    name = 'entity_description'
    label = _('Entity description')
    
    def __init__(self, *args, **kwargs):
        super(EntityDescriptionForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(
                attrs={'placeholder': _('Enter a part of the description of the searched entities')}
            )
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__description__icontains': self.value}


class EntityNotesForm(SearchFieldForm):
    """by entity notes"""

    name = 'entity_notes'
    label = _('Entity notes')
    
    def __init__(self, *args, **kwargs):
        super(EntityNotesForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter a part of the notes of the searched entities')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__notes__icontains': self.value}


class EntityNameStartsWithSearchForm(SearchFieldForm):
    """by entity name starts with"""

    name = 'entity_name_sw'
    label = _('Entity name starts with')
    
    def __init__(self, *args, **kwargs):
        super(EntityNameStartsWithSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(
                attrs={'placeholder': _('Enter the beginning of the name of the searched entities')}
            )
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__name__istartswith': self.value}


class AddressSearchForm(SearchFieldForm):
    """by address contains"""

    name = 'address'
    label = _('Contact or entity at this address')

    def __init__(self, *args, **kwargs):
        super(AddressSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(
                attrs={'placeholder': _('Enter text contained in an address')}
            )
        )
        self._add_field(field)

    def get_lookup(self):
        """lookup"""
        value = self.value
        return (
            Q(address__icontains=value) | Q(address2__icontains=value) | Q(address3__icontains=value) |
            Q(entity__address__icontains=value) | Q(entity__address2__icontains=value) |
            Q(entity__address3__icontains=value)
        )


class HasEntityForm(YesNoSearchFieldForm):
    """contacts member of an entity"""

    name = 'has_entity'
    label = _('Has entity?')
        
    def get_lookup(self):
        """lookup"""
        no_entity = Q(entity__is_single_contact=True)
        if self.is_yes():
            return ~no_entity
        else:
            return no_entity


class BaseCitySearchForm(SearchFieldForm):
    """base class for search by city"""
    def __init__(self, *args, **kwargs):
        super(BaseCitySearchForm, self).__init__(*args, **kwargs)
        queryset = models.City.objects.order_by('name')
        field = forms.ModelChoiceField(
            queryset,
            label=self.label,
            widget=CityNoCountryAutoComplete(attrs={'placeholder': _('Enter a city'), 'size': '80'})
        )
        self._add_field(field)


class CitySearchForm(BaseCitySearchForm):
    """by city"""
    name = 'city'
    label = _('City')
    
    def get_lookup(self):
        """lookup"""
        return Q(city__id=self.value) | (Q(city__isnull=True) & Q(entity__city__id=self.value))
    

class EntityCitySearchForm(BaseCitySearchForm):
    """by city of the entity"""
    name = 'entity_city'
    label = _('Entity city')

    def get_lookup(self):
        """lookup"""
        return Q(entity__city__id=self.value)


class BaseZipCodeSearchForm(SearchFieldForm):
    """base class for search by zipcode"""
    def __init__(self, *args, **kwargs):
        super(BaseZipCodeSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter the beginning of the zip code')})
        )
        self._add_field(field)
    

class ZipCodeSearchForm(BaseZipCodeSearchForm):
    """by zip code"""
    name = 'zip_code'
    label = _('zip code')
    
    def get_lookup(self):
        """lookup"""
        return Q(zip_code__istartswith=self.value) | (Q(zip_code="") & Q(entity__zip_code__istartswith=self.value))


class EntityZipCodeSearchForm(BaseZipCodeSearchForm):
    """by zip code of the entity"""
    name = 'entity_zip_code'
    label = _('Entity zip code')
            
    def get_lookup(self):
        """lookup"""
        return Q(entity__zip_code__istartswith=self.value)
        

class ZoneSearchForm(SearchFieldForm):
    """By zone"""
    multi_values = True

    def __init__(self, *args, **kwargs):
        super(ZoneSearchForm, self).__init__(*args, **kwargs)
        type_name = self.name.replace("entity_", "")
        queryset = models.Zone.objects.filter(type__type=type_name).order_by('code', 'name')
        kwargs = kwargs or {}
        kwargs.setdefault('required', True)
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.MultipleChoiceField(
            choices=[(x.id, '{0}'.format(x)) for x in queryset.all()],
            label=self.label,
            **kwargs
        )
        self._add_field(field)
        
    def get_values(self):
        """get possible values"""
        if type(self.value) == list:
            values = self.value
        else:
            values = [self.value]
        return values
    
    def _get_widget(self):
        """get widget"""
        return forms.SelectMultiple(attrs={
            'class': "chosen-select",
            'data-placeholder': self.label,
            'style': "width: 100%", 
        })
    
    def get_queryset(self, queryset):
        """queryset"""
        group_queryset = Q(id=0)
        for zone_id in self.get_values():
            self.value = zone_id
            group_queryset = group_queryset | self.get_lookup()
        return queryset.filter(group_queryset)


class DepartmentSearchForm(ZoneSearchForm):
    """by departement"""
    name = 'department'
    label = _('Departments')
        
    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__parent__id=self.value) & Q(city__parent__type__type="department")

        qobj2 = Q(
            city__isnull=True
        ) & Q(
            entity__city__parent__id=self.value
        ) & Q(
            entity__city__parent__type__type="department"
        )
        
        return qobj1 | qobj2


class EntityDepartmentSearchForm(ZoneSearchForm):
    """by departement of the entity"""
    name = 'entity_department'
    label = _('Entity Departments')
        
    def get_queryset(self, queryset):
        """queryset"""
        queryset = super(EntityDepartmentSearchForm, self).get_queryset(queryset)
        return queryset.filter(entity__city__parent__type__type="department")

    def get_lookup(self):
        """lookup"""
        return Q(entity__city__parent__id=self.value)
        

class RegionSearchForm(ZoneSearchForm):
    """by region"""
    name = 'region'
    label = _('Regions')
        
    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__parent__parent__id=self.value) & Q(city__parent__parent__type__type="region")

        qobj2 = Q(
            city__isnull=True
        ) & Q(
            entity__city__parent__parent__id=self.value
        ) & Q(
            entity__city__parent__parent__type__type="region"
        )

        return qobj1 | qobj2


class EntityRegionSearchForm(ZoneSearchForm):
    """by region of teh entity"""
    name = 'entity_region'
    label = _('Entity Regions')
    
    def get_queryset(self, queryset):
        """queryset"""
        queryset = super(EntityRegionSearchForm, self).get_queryset(queryset)
        return queryset.filter(entity__city__parent__type__type="department")

    def get_lookup(self):
        """queryset"""
        return Q(entity__city__parent__parent__id=self.value)


class LargeRegionSearchForm(ZoneSearchForm):
    """by region"""
    name = 'large_region'
    label = _('Large Regions')

    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__parent__parent__groups__id=self.value)

        qobj2 = Q(
            city__isnull=True
        ) & Q(
            entity__city__parent__parent__groups__id=self.value
        )

        return qobj1 | qobj2


class EntityLargeRegionSearchForm(ZoneSearchForm):
    """by region of teh entity"""
    name = 'entity_large_region'
    label = _('Entity Large Regions')

    def get_lookup(self):
        """queryset"""
        return Q(entity__city__parent__parent__groups__id=self.value)


class CountrySearchForm(ZoneSearchForm):
    """by country"""
    name = 'country'
    label = _('Countries')
        
    def get_lookup(self):
        """lookup"""
        default_country = get_default_country()
        if int(self.value) == default_country.id:
            return Q(
                city__parent__type__type='department'
            ) | (Q(
                city__isnull=True
            ) & Q(entity__city__parent__type__type='department'))
        else:
            return Q(city__parent__id=self.value) | (Q(city__isnull=True) & Q(entity__city__parent__id=self.value))


class EntityCountrySearchForm(ZoneSearchForm):
    """by country of the entity"""
    name = 'entity_country'
    label = _('Entity Countries')
        
    def get_lookup(self):
        """lookup"""
        default_country = get_default_country()
        
        if int(self.value) == default_country.id:
            return Q(entity__city__parent__type__type='department')
        else:
            return Q(entity__city__parent__id=self.value, entity__city__parent__type__type="country")


class ZoneGroupSearchForm(ZoneSearchForm):
    """by zone group"""
    name = 'zone_group'
    label = _('Zone Groups')
        
    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__groups__id=self.value)
        qobj2 = Q(city__isnull=True) & Q(entity__city__groups__id=self.value)
        return qobj1 | qobj2
    

class EntityZoneGroupSearchForm(ZoneSearchForm):
    """by zone group of entity"""
    name = 'entity_zone_group'
    label = _('Entity Zone Groups')
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__city__groups__id=self.value)


class HasCityAndZipcodeForm(YesNoSearchFieldForm):
    """by has city and address"""
    name = 'has_city_and_zip'
    label = _('Has city and zip code?')
        
    def get_lookup(self):
        """lookup"""
        contact_has_address = ~Q(zip_code='') & Q(city__isnull=False)
        entity_has_address = ~Q(entity__zip_code='') & Q(entity__city__isnull=False)
        has_address = contact_has_address | entity_has_address
        if self.is_yes():
            return has_address
        else:
            return ~has_address


class HasAddresseForm(YesNoSearchFieldForm):
    """by has city and address"""
    name = 'has_address'
    label = _('Has address?')

    def get_lookup(self):
        """lookup"""
        contact_has_address = ~Q(zip_code='') & Q(city__isnull=False) & ~Q(address='')
        entity_has_address = ~Q(entity__zip_code='') & Q(entity__city__isnull=False) & ~Q(entity__address='')
        has_address = contact_has_address | entity_has_address
        if self.is_yes():
            return has_address
        else:
            return ~has_address
            

class ActionInProgressForm(YesNoSearchFieldForm):
    """by action in progress"""
    name = 'action'
    label = _('Action in progress')
    is_action_form = True

    def get_queryset(self, queryset):
        """queryset"""
        q_objs = Q(done=False)
        if self.is_yes():
            return queryset.filter(q_objs)
        else:
            return queryset.exclude(q_objs)


class HasAction(YesNoSearchFieldForm):
    """Has an action"""
    name = 'has_action'
    label = _('Has actions')
        
    def get_queryset(self, queryset):
        """queryset"""
        queryset = queryset.annotate(num_actions=Count('action'), num_entity_actions=Count('entity__action'))
        if self.is_yes():
            return queryset.filter(Q(num_actions__gt=0) | Q(num_entity_actions__gt=0))
        else:
            return queryset.filter().filter(Q(num_actions=0) & Q(num_entity_actions=0))


class ActionByDoneDate(TwoDatesForm):
    """by action done between two dates"""
    name = 'action_by_done_date'
    label = _('Action by done date')
    is_action_form = True
        
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_datetimes()
        return Q(done_date__gte=datetime1) & Q(done_date__lte=datetime2)


class ActionByPlannedDate(TwoDatesForm):
    """by action planned between two dates"""
    name = 'action_by_planned_date'
    label = _('Action by planned date')
    is_action_form = True
    
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_datetimes()
        
        start_after_end_before = Q(
            end_datetime__isnull=True
        ) & Q(
            planned_date__gte=datetime1
        ) & Q(
            planned_date__lte=datetime2
        )

        start_before_end_after = Q(
            end_datetime__isnull=False
        ) & Q(
            planned_date__lte=datetime2
        ) & Q(
            end_datetime__gte=datetime1
        )

        return start_after_end_before | start_before_end_after


class ActionByStartDate(TwoDatesForm):
    """By action started between two dates"""
    name = 'action_by_start_date'
    label = _('Action by start date')
    is_action_form = True
    
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_datetimes()
        return Q(planned_date__gte=datetime1) & Q(planned_date__lte=datetime2)


class ActionByUser(SearchFieldForm):
    """by user in charge of an action"""
    name = 'action_by_user'
    label = _('Action by user')
    is_action_form = True
    
    def __init__(self, *args, **kwargs):
        super(ActionByUser, self).__init__(*args, **kwargs)
        choices = [(team_member.id, team_member.name) for team_member in models.TeamMember.objects.all()]
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(in_charge=self.value)


class ActionGteAmount(SearchFieldForm):
    """by action with amount greater than a value"""
    name = 'action_gte_amount'
    label = _('Action with amount greater or equal to')
    is_action_form = True
    
    def __init__(self, *args, **kwargs):
        super(ActionGteAmount, self).__init__(*args, **kwargs)
        field = forms.IntegerField(label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(amount__gte=self.value)


class ActionLtAmount(SearchFieldForm):
    """by action with amount less than a value"""
    name = 'action_lt_amount'
    label = _('Action with amount less than')
    is_action_form = True
    
    def __init__(self, *args, **kwargs):
        super(ActionLtAmount, self).__init__(*args, **kwargs)
        field = forms.IntegerField(label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(amount__lt=self.value)


class ActionStatus(SearchFieldForm):
    """by action status"""
    name = 'action_status'
    label = _('Contacts with action of status')
    is_action_form = True
    
    def __init__(self, *args, **kwargs):
        super(ActionStatus, self).__init__(*args, **kwargs)
        queryset = models.ActionStatus.objects.all()
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(status=self.value)


class ActionWithoutStatus(SearchFieldForm):
    """by action status"""
    name = 'action_without_status'
    label = _('Contacts without action of status')
    is_action_form = True

    def __init__(self, *args, **kwargs):
        super(ActionWithoutStatus, self).__init__(*args, **kwargs)
        queryset = models.ActionStatus.objects.all()
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)

    def get_lookup(self):
        """lookup"""
        return ~Q(status=self.value)


class TypeSearchForm(SearchFieldForm):
    """by entity type"""
    name = 'type'
    label = _('Entity type')
    
    def __init__(self, *args, **kwargs):
        super(TypeSearchForm, self).__init__(*args, **kwargs)
        queryset = models.EntityType.objects.all()
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__type__id': self.value}


class GroupSearchForm(SearchFieldForm):
    """by group"""
    name = 'group'
    label = _('Group')
    
    def _get_widget(self):
        """customize widget: autocomplete"""
        return GroupAutoComplete(attrs={
            'placeholder': _('Enter part of the group name'), 'size': '80',
        })

    def __init__(self, *args, **kwargs):
        super(GroupSearchForm, self).__init__(*args, **kwargs)
        queryset = models.Group.objects.all()
        try:
            queryset = queryset.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except Exception:  # pylint: disable=broad-except
            queryset = queryset.order_by('name')
        kwargs = {}
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.ModelChoiceField(queryset, label=self.label, **kwargs)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__group__id=self.value) | Q(group__id=self.value)


class GroupSearchFormDropdownWidget(GroupSearchForm):
    """Search by group: dropdown widget"""
    name = 'group_dropdown'
    label = _('Group (dropdown list)')
    
    def _get_widget(self):
        """dropdown widget"""
        return forms.Select(attrs={
            'class': "chosen-select",
            'data-placeholder': _('Group names'),
            'style': "width: 100%", 
        })


class MultiGroupSearchForm(SearchFieldForm):
    """Base class for searching by several groups"""
    multi_values = True

    def __init__(self, *args, **kwargs):
        super(MultiGroupSearchForm, self).__init__(*args, **kwargs)
        queryset = models.Group.objects.all()
        try:
            queryset = queryset.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except Exception: #pylint: disable=broad-except
            queryset = queryset.order_by('name')
        kwargs = kwargs or {}
        kwargs.setdefault('required', True)
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.MultipleChoiceField(
            choices=[(x.id, '{0}'.format(x)) for x in queryset.all()], label=self.label, **kwargs)
        self._add_field(field)
        
    def get_values(self):
        """values"""
        if type(self.value) == list:
            values = self.value
        else:
            values = [self.value]
        return values
    
    def _get_widget(self):
        """customize widget"""
        return forms.SelectMultiple(attrs={
            'class': "chosen-select",
            'data-placeholder': _('Select Group names'),
            'style': "width: 100%", 
        })


class GroupsMemberOfAllSearchForm(MultiGroupSearchForm):
    """members of all groups"""
    name = 'all_groups'
    label = _('Members of all groups')
    
    def get_queryset(self, queryset):
        """queryset"""
        for group_id in self.get_values():
            group_queryset = ((Q(entity__isnull=False) & Q(entity__group__id=group_id)) | Q(group__id=group_id))
            queryset = queryset.filter(group_queryset)
        return queryset


class GroupsMemberOfAnySearchForm(MultiGroupSearchForm):
    """member of one of the groups"""
    name = 'any_groups'
    label = _('Members of at least one group')
    multi_values = True
    
    def get_queryset(self, queryset):
        """queryset"""
        group_queryset = Q(id=0)
        for group_id in self.get_values():
            current_queryset = (Q(entity__isnull=False) & Q(entity__group__id=group_id)) | Q(group__id=group_id)
            group_queryset = group_queryset | current_queryset
        queryset = queryset.filter(group_queryset)
        return queryset


class GroupsMemberOfNoneSearchForm(MultiGroupSearchForm):
    """not member of any of the groups"""
    name = 'none_groups'
    label = _('Member of none of these groups')
    multi_values = True
    
    def get_queryset(self, queryset):
        """queryset"""
        for group_id in self.get_values():
            group_queryset = ((Q(entity__isnull=False) & Q(entity__group__id=group_id)) | Q(group__id=group_id))
            queryset = queryset.exclude(group_queryset)
        return queryset


class NotInGroupSearchForm(SearchFieldForm):
    """not in group"""
    name = 'not_in_group'
    label = _('Not in group')
    
    def __init__(self, *args, **kwargs):
        super(NotInGroupSearchForm, self).__init__(*args, **kwargs)
        queryset = models.Group.objects.all()
        try:
            queryset = queryset.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except Exception:  # pylint: disable=broad-except
            queryset = queryset.order_by('name')
        field = forms.ModelChoiceField(
            queryset,
            label=self.label,
            widget=GroupAutoComplete(attrs={'placeholder': _('Enter part of the group name'), 'size': '80'})
        )
        self._add_field(field)
    
    def get_lookup(self):
        """lookup"""
        return [~Q(entity__group__id=self.value), ~Q(group__id=self.value)]


class ContactAgeSearchForm(SearchFieldForm):
    """search by age"""
    name = 'contact_age'
    label = _('Contact age')
    
    def __init__(self, *args, **kwargs):
        super(ContactAgeSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self.label, initial='0 100')
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        ages = [int(x) for x in self.value.split()]
        dt_from = date.today() - timedelta(days=ages[1]*365.25)
        dt_to = date.today() - timedelta(days=ages[0]*365.25)
        return {'birth_date__gte': dt_from, 'birth_date__lte': dt_to}


class ContactAcceptSubscriptionSearchForm(SearchFieldForm):
    """by accept subscrition"""
    name = 'accept_subscription'
    label = _('Accept subscription to')
    
    def __init__(self, *args, **kwargs):
        super(ContactAcceptSubscriptionSearchForm, self).__init__(*args, **kwargs)
        queryset = models.SubscriptionType.objects.all()
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'subscription__subscription_type__id': self.value, 'subscription__accept_subscription': True}


class ContactRefuseSubscriptionSearchForm(ContactAcceptSubscriptionSearchForm):
    """by refuse subscription"""
    name = 'refuse_subscription'
    label = _('Refuse subscription to')
    
    def get_lookup(self):
        """lookup"""
        return None
        
    def get_exclude_lookup(self):
        """exclude lookup"""
        return super(ContactRefuseSubscriptionSearchForm, self).get_lookup()


class SecondarySearchForm(SearchFieldForm):
    """by secondary contact"""
    name = 'secondary_contact'
    label = _('Secondary contact')
    
    def __init__(self, *args, **kwargs):
        super(SecondarySearchForm, self).__init__(*args, **kwargs)
        choices = ((1, _('Include')), (0, _('Only')),)
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        value = int(self.value)
        if value == 1:
            #the lookup 'main_contact' will be removed by the search form
            return {}
        elif value == 0:
            return {'main_contact': False}


class ContactHasLeft(SearchFieldForm):
    """contact who left"""
    name = 'contact_has_left'
    label = _('Contact has left')
    
    def __init__(self, *args, **kwargs):
        super(ContactHasLeft, self).__init__(*args, **kwargs)
        choices = ((0, _('Only')), (1, _('Include')),)
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)
            
    def get_lookup(self):
        """lookup"""
        value = int(self.value)
        if value == 1:
            #the lookup 'has_left' will be removed by the search form
            return {}
        elif value == 0:
            return {'has_left': True}


class ContactRoleSearchForm(SearchFieldForm):
    """by role"""
    name = 'contact_role'
    label = _('Contact role')
    
    def __init__(self, *args, **kwargs):
        super(ContactRoleSearchForm, self).__init__(*args, **kwargs)
        queryset = models.EntityRole.objects.all().order_by('name')
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'role': self.value}


class EmailSearchForm(SearchFieldForm):
    """by email"""
    name = 'contact_entity_email'
    label = _('Email')
    
    def __init__(self, *args, **kwargs):
        super(EmailSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter a part of the email of a contact or an entity')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__email__icontains=self.value) | Q(email__icontains=self.value)


class ContactHasEmail(YesNoSearchFieldForm):
    """by has email"""
    name = 'contact_has_email'
    label = _('Contact has email')
            
    def get_lookup(self):
        """lookup"""
        has_no_email = (Q(email='') & Q(entity__email=''))
        if self.is_yes():
            return ~has_no_email
        else:
            return has_no_email


class ContactHasPersonalEmail(YesNoSearchFieldForm):
    """by has an email set on the contact (ignore if set on entity)"""
    name = 'contact_has_personal_email'
    label = _('Contact has pesonal email')
            
    def get_lookup(self):
        """queryset"""
        has_no_email = Q(email='')
        if self.is_yes():
            return ~has_no_email
        else:
            return has_no_email


class UnknownContact(YesNoSearchFieldForm):
    """no name"""
    name = 'unknown_contact'
    label = _('Unknown contacts')
        
    def get_lookup(self):
        """lookup"""
        unknown_contact = (Q(firstname='') & Q(lastname=''))
        if self.is_yes():
            return unknown_contact
        else:
            return ~unknown_contact


class ActionTypeSearchForm(SearchFieldForm):
    """by type of action"""
    name = 'action_type'
    label = _('Action type')
    is_action_form = True

    def __init__(self, *args, **kwargs):
        super(ActionTypeSearchForm, self).__init__(*args, **kwargs)
        queryset = models.ActionType.objects.all().order_by('name')
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(type=self.value)


class ActionNameSearchForm(SearchFieldForm):
    """by subject of action"""
    name = 'action_name'
    label = _('Action subject')
    is_action_form = True

    def __init__(self, *args, **kwargs):
        super(ActionNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('enter a part of the name of the searched action')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(subject__icontains=self.value)


class ExcludeActionNameSearchForm(ActionNameSearchForm):
    """by subject of action"""
    name = 'exclude_action_name'
    label = _(u'No Action with subject')
    is_action_form = True
    is_exclude_action_form = True


class RelationshipDateForm(TwoDatesForm):
    """by date of relationship"""
    name = 'relationship_date'
    label = _('Relationship date')
            
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_datetimes()
        return {'entity__relationship_date__gte': start_datetime, 'entity__relationship_date__lte': end_datetime}


class ContactNameSearchForm(SearchFieldForm):
    """by contact name"""
    name = 'contact_name'
    label = _('Contact name')
    
    def __init__(self, *args, **kwargs):
        super(ContactNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter a part of the name of the searched contact')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'lastname__icontains': self.value}


class ContactLanguageSearchForm(SearchFieldForm):
    """by contact language"""
    name = 'contact_lang'
    label = _('Contact language')

    def __init__(self, *args, **kwargs):
        super(ContactLanguageSearchForm, self).__init__(*args, **kwargs)
        field = forms.ChoiceField(
            label=self.label,
            choices=get_language_choices()
        )
        self._add_field(field)
        field.required = False

    def get_lookup(self):
        """lookup"""
        return {'favorite_language': self.value}


class ContactFirstnameSearchForm(SearchFieldForm):
    """by firstname"""
    name = 'contact_firstname'
    label = _('Contact firstname')
    
    def __init__(self, *args, **kwargs):
        super(ContactFirstnameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter a part of the firstname of the searched contact')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'firstname__icontains': self.value}
    

class ContactNotesSearchForm(SearchFieldForm):
    """by notes"""
    name = 'contact_notes'
    label = _('Contact notes')
    
    def __init__(self, *args, **kwargs):
        super(ContactNotesSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('Enter a part of a note of the searched contact')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'notes__icontains': self.value}


class OpportunitySearchForm(SearchFieldForm):
    """by opportunity"""
    name = 'opportunity'
    label = _('Opportunity')
    is_action_form = True
    
    def __init__(self, *args, **kwargs):
        super(OpportunitySearchForm, self).__init__(*args, **kwargs)
        queryset = models.Opportunity.objects.all()
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
    
    def get_lookup(self):
        """lookup"""
        return Q(opportunity__id=self.value)
        

class OpportunityNameSearchForm(SearchFieldForm):
    """by opportunity name"""
    name = 'opportunity_name'
    label = _('Opportunity name')
    is_action_form = True
    
    def __init__(self, *args, **kwargs):
        super(OpportunityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label,
            widget=forms.TextInput(attrs={'placeholder': _('enter a part of the name of the searched opportunity')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(opportunity__name__icontains=self.value)


class NoSameAsForm(YesNoSearchFieldForm):
    """Allow same as contact in results"""
    name = 'no_same_as'
    label = _('Allow same-as')
    
    def get_lookup(self):
        """lookup"""
        pass
    
    def get_exclude_lookup(self):
        """exclude lookup"""
        pass
    
    def global_post_process(self, contacts):
        """this filters the full list of results"""
        if self.is_yes():
            return contacts
        else:
            same_as = {}
            filtered_contacts = []
            for contact in contacts:
                if contact.same_as:
                    if contact.same_as.id not in same_as:
                        same_as[contact.same_as.id] = contact
                        # filtered_contacts.append(contact.same_as.main_contact if contact.same_as else contact)
                        filtered_contacts.append(contact)
                    else:
                        # If the current contact has better priority (lower is better). Take this one
                        other_contact = same_as[contact.same_as.id]
                        if other_contact.same_as_priority > contact.same_as_priority:
                            contact_index = filtered_contacts.index(other_contact)
                            filtered_contacts[contact_index] = contact
                else:
                    filtered_contacts.append(contact)
            return filtered_contacts


class HasSameAsForm(SearchFieldForm):
    """all contacts with same as"""
    name = 'has_same_as'
    label = _('Has same-as')

    def __init__(self, *args, **kwargs):
        super(HasSameAsForm, self).__init__(*args, **kwargs)
        choices = ((0, _('No same as')), (1, _('Only top priority same-as')), (2, _('All priorities same-as')),)
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)

    def get_lookup(self):
        """lookup"""
        value = int(self.value)

        if value == 0:
            return Q(same_as__isnull=True)
        elif value == 1:
            return Q(same_as__isnull=False, same_as_priority=1)
        elif value == 2:
            return Q(same_as__isnull=False)

        
class NoSameEmailForm(SearchFieldForm):
    """Allow same as contact in results"""
    name = 'no_same_email'
    label = _('Duplicate emails')

    def __init__(self, *args, **kwargs):
        super(NoSameEmailForm, self).__init__(*args, **kwargs)
        choices = ((0, _('Exclude')), (1, _('Only')),)
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)
    
    def get_lookup(self):
        """lookup"""
        pass
    
    def get_exclude_lookup(self):
        """exclude lookup"""
        pass
    
    def global_post_process(self, contacts):
        """this filters the full list of results"""
        try:
            value = int(self.value)
        except ValueError:
            value = -1
        emails = {}
        filtered_contacts = []
        for contact in contacts:
            email = contact.get_email
            if email:
                if email not in emails:
                    emails[email] = contact
                    if value == 0:
                        filtered_contacts.append(contact)
                else:
                    if value == 1:
                        filtered_contacts.append(contact)
        return filtered_contacts


class DuplicatedContactsForm(SearchFieldForm):
    """Allow same as contact in results"""
    name = 'duplicated_contacts'
    label = _('Duplicated contacts')

    def __init__(self, *args, **kwargs):
        super(DuplicatedContactsForm, self).__init__(*args, **kwargs)
        choices = ((1, _('same firstname and lastname')), (2, _('same lastname')), )
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)

    def get_lookup(self):
        """lookup"""
        pass

    def get_exclude_lookup(self):
        """exclude lookup"""
        pass

    def global_post_process(self, contacts):
        """this filters the full list of results"""
        keys = {}
        filtered_contacts = []
        try:
            value = int(self.value)
        except ValueError:
            value = 1
        for contact in contacts:
            if contact.lastname:  # ignore contacts without names
                key = contact.lastname if value == 2 else contact.fullname   # lastname only or fullname
                if key:
                    if key in keys:
                        filtered_contacts.append(contact)
                        filtered_contacts.append(keys[key])
                    else:
                        keys[key] = contact
        return filtered_contacts


class ContactsImportSearchForm(SearchFieldForm):
    """by import"""
    name = 'contact_import'
    label = _('Import')
    
    def __init__(self, *args, **kwargs):
        super(ContactsImportSearchForm, self).__init__(*args, **kwargs)
        queryset = models.ContactsImport.objects.order_by('name')
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'imported_by': self.value}


class ByUserBaseFormSearchForm(SearchFieldForm):
    """by import"""

    def __init__(self, *args, **kwargs):
        super(ByUserBaseFormSearchForm, self).__init__(*args, **kwargs)
        queryset = User.objects.filter(is_staff=True).order_by('username')
        field = forms.ModelChoiceField(queryset, label=self.label)
        self._add_field(field)


class ContactsAndEntitiesModifiedBySearchForm(ByUserBaseFormSearchForm):
    """by import"""
    name = 'contacts_and_entities_modified_by'
    label = _('Contacts and entities modified by')

    def get_lookup(self):
        """lookup"""
        return Q(last_modified_by__id=self.value) | Q(entity__last_modified_by__id=self.value)


class ContactsModifiedBySearchForm(ByUserBaseFormSearchForm):
    """by import"""
    name = 'contacts_modified_by'
    label = _('Contacts and entities modified by')

    def get_lookup(self):
        """lookup"""
        return Q(last_modified_by__id=self.value)


class EntitiesModifiedBySearchForm(ByUserBaseFormSearchForm):
    """by import"""
    name = 'entities_modified_by'
    label = _('Contacts and entities modified by')

    def get_lookup(self):
        """lookup"""
        return Q(entity__last_modified_by__id=self.value)


class EntityByModifiedDate(TwoDatesForm):
    """every entity modified betwwen two dates"""
    name = 'entity_by_modified_date'
    label = _('Entity by modified date')

    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_datetimes()
        datetime2 += timedelta(1)
        return Q(entity__is_single_contact=False, entity__modified__gte=datetime1, entity__modified__lt=datetime2)


class ContactByModifiedDate(TwoDatesForm):
    """every contact modified between two dates"""
    name = 'contact_by_modified_date'
    label = _('Contact by modified date')

    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_datetimes()
        datetime2 += timedelta(1)
        return {'modified__gte': datetime1, 'modified__lt': datetime2}


class ContactsByCreationDate(TwoDatesForm):
    """by creation date"""
    name = 'contacts_by_creation_date'
    label = _('Contacts by creation date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_datetimes()
        return Q(created__gte=start_datetime, created__lte=end_datetime)


class EntitiesByCreationDate(TwoDatesForm):
    """by entity creation date"""
    name = 'entities_by_creation_date'
    label = _('Entities by creation date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_datetimes()
        return Q(
            entity__is_single_contact=False, entity__created__gte=start_datetime, entity__created__lte=end_datetime
        )
    

class ContactsAndEntitiesByChangeDate(TwoDatesForm):
    """by change date"""
    name = 'contacts_and_entities_by_change_date'
    label = _('Contacts and entities by change date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_datetimes()
        return Q(modified__gte=start_datetime, modified__lte=end_datetime) | \
            Q(created__gte=start_datetime, created__lte=end_datetime) | \
            Q(entity__modified__gte=start_datetime, entity__modified__lte=end_datetime) | \
            Q(entity__created__gte=start_datetime, entity__created__lte=end_datetime)
        

class ContactsRelationshipByType(SearchFieldForm):
    """by type of relationship"""
    name = 'contacts_by_relationship_type'
    label = _('Relationship type')
    
    def __init__(self, *args, **kwargs):
        super(ContactsRelationshipByType, self).__init__(*args, **kwargs)
        relationship_types = []
        for relationship_type in models.RelationshipType.objects.all():
            relationship_types.append((relationship_type.id, relationship_type.name))
            if relationship_type.reverse:
                relationship_types.append((-relationship_type.id, relationship_type.reverse))
        field = forms.CharField(label=self.label, widget=forms.Select(choices=relationship_types))
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        relationship_ids = []
        value, is_reverse = int(self.value), False
        if value < 0:
            value, is_reverse = -value, True
        relationship_type = models.RelationshipType.objects.get(id=value)
        for relationship in models.Relationship.objects.filter(relationship_type__id=relationship_type.id):
            if relationship_type.reverse:
                if is_reverse:
                    relationship_ids.append(relationship.contact2.id)
                else:
                    relationship_ids.append(relationship.contact1.id)
            else:
                relationship_ids += [relationship.contact1.id, relationship.contact2.id]
        relationship_ids = list(set(relationship_ids))  
        return Q(id__in=relationship_ids)
    

class ContactsRelationshipByDate(TwoDatesForm):
    """by relationship date"""
    name = 'contacts_by_relationship_dates'
    label = _('Relationship dates')
        
    def get_lookup(self):
        """lookup"""
        relationship_ids = []
        start_datetime, end_datetime = self._get_datetimes()
        end_datetime = end_datetime + timedelta(1)
        queryset = models.Relationship.objects.filter(created__gte=start_datetime, created__lt=end_datetime)
        for relationship_type in queryset:
            relationship_ids = [relationship_type.contact1.id, relationship_type.contact2.id]
        relationship_ids = list(set(relationship_ids))  
        return Q(id__in=relationship_ids)
    

class ContactWithCustomField(SearchFieldForm):
    """by contact with custom field"""
    name = 'contact_with_custom_field'
    label = _('Contacts with custom field')
    
    def __init__(self, *args, **kwargs):
        super(ContactWithCustomField, self).__init__(*args, **kwargs)
        custom_fields = []
        for custom_field in models.CustomField.objects.filter(model=models.CustomField.MODEL_CONTACT):
            custom_fields.append((custom_field.id, custom_field.label))
        field = forms.CharField(label=self.label, widget=forms.Select(choices=custom_fields))
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        value = int(self.value)
        custom_field = models.CustomField.objects.get(id=value, model=models.CustomField.MODEL_CONTACT)
        return Q(contactcustomfieldvalue__custom_field=custom_field)


class EntityWithCustomField(SearchFieldForm):
    """by entity custom field"""
    name = 'entity_with_custom_field'
    label = _('Entities with custom field')
    
    def __init__(self, *args, **kwargs):
        super(EntityWithCustomField, self).__init__(*args, **kwargs)
        custom_fields = []
        for custom_field in models.CustomField.objects.filter(model=models.CustomField.MODEL_ENTITY):
            custom_fields.append((custom_field.id, custom_field.label))
        field = forms.CharField(label=self.label, widget=forms.Select(choices=custom_fields))
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        value = int(self.value)
        custom_field = models.CustomField.objects.get(id=value, model=models.CustomField.MODEL_ENTITY)
        return Q(entity__entitycustomfieldvalue__custom_field=custom_field)
    

class CustomFieldBaseSearchForm(SearchFieldForm):
    """Base class for any Custom Field """
    custom_field_name = ''
    model = None
    widget = None

    def __init__(self, *args, **kwargs):
        super(CustomFieldBaseSearchForm, self).__init__(*args, **kwargs)

        self.custom_field = models.CustomField.objects.get_or_create(
            name=self.custom_field_name, model=self.model
        )[0]

        label = self.custom_field.label or self.custom_field.name

        field = forms.CharField(
            label=label,
            widget=self.widget
        )
        self._add_field(field)

    def get_lookup(self):
        """lookup"""
        value = self.value
        custom_field = self.custom_field

        if custom_field.model == models.CustomField.MODEL_ENTITY:
            queryset = models.EntityCustomFieldValue.objects.filter(custom_field=self.custom_field, value=value)
            entity_ids = [custom_field_value.entity.id for custom_field_value in queryset]
            return Q(entity__id__in=entity_ids)
        else:
            queryset = models.ContactCustomFieldValue.objects.filter(custom_field=self.custom_field, value=value)
            contact_ids = [custom_field_value.contact.id for custom_field_value in queryset]
            return Q(id__in=contact_ids)


class UnitTestEntityCustomFieldForm(CustomFieldBaseSearchForm):
    """Unit test for entity"""
    custom_field_name = 'ut_cf_entity'
    name = 'cf_ut_cf_entity'
    model = models.CustomField.MODEL_ENTITY
    label = "entity custom field"


class UnitTestContactCustomFieldForm(CustomFieldBaseSearchForm):
    """Unit test for contacts"""
    custom_field_name = 'ut_cf_contact'
    name = 'cf_ut_cf_contact'
    model = models.CustomField.MODEL_CONTACT
    label = "contact custom field"


class SortContacts(SearchFieldForm):
    """sort contacts"""
    name = 'sort'
    label = _('Sort contacts')
    contacts_display = True
    is_sort_form = True
    
    def __init__(self, *args, **kwargs):
        super(SortContacts, self).__init__(*args, **kwargs)
        choices = (
            ('entity', _('Entity name')),
            ('contact', _('Contact name')),
            ('name', _('Entity or Contact name')),
            ('zipcode', _('Zipcode')),
        ) 
        field = forms.CharField(
            label=self.label,
            widget=forms.Select(
                choices=choices,
                attrs={
                    'class': "chosen-select",
                    'style': "width: 100%",
                }
            )
        )
        self._add_field(field)
        self.default_country = get_default_country()

    def _sort_by_name(self, contact):
        return sort_by_name_callback(contact)

    def _sort_by_entity(self, contact):
        return sort_by_entity_callback(contact)

    def _sort_by_contact(self, contact):
        return sort_by_contact_callback(contact)

    def _sort_by_zipcode(self, contact):
        """sort by zipcode"""
        country = contact.get_country()
        value1 = contact.get_zip_code or '?'
        city = contact.get_city
        if not city:
            prefix1 = "C"
            prefix2 = value2 = "?"
        else:
            prefix1 = "A" if ((not country) or self.default_country.id == country.id) else "B"
            prefix2 = country.name if country else self.default_country.name
            value2 = city.name
        value3 = self._sort_by_name(contact)
        return prefix1, prefix2, value1, value2, value3
    
    def get_queryset(self, queryset):
        """queryset"""
        return queryset
    
    def global_post_process(self, contacts):
        """filter the final results"""
        callback = getattr(self, '_sort_by_{0}'.format(self.value), None)
        return sorted(contacts, key=callback)


class ContactWithEmailInGroupSearchForm(SearchFieldForm):
    """get contacts with someone with the same email in group"""
    name = 'email_in_group'
    label = _(u'Some with same email in group')

    def _get_widget(self):
        """customize widget: autocomplete"""
        return GroupAutoComplete(attrs={
            'placeholder': _(u'Enter part of the group name'), 'size': '80',
        })

    def __init__(self, *args, **kwargs):
        super(ContactWithEmailInGroupSearchForm, self).__init__(*args, **kwargs)
        queryset = models.Group.objects.all()
        try:
            queryset = queryset.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except Exception:  # pylint: disable=broad-except
            queryset = queryset.order_by('name')
        kwargs = {}
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.ModelChoiceField(queryset, label=self.label, **kwargs)
        self._add_field(field)

    # def get_lookup(self):
    #     """lookup"""
    #     return Q(entity__group__id=self.value) | Q(group__id=self.value)

    def global_post_process(self, contacts):
        """filter the final results"""
        group_contacts = models.Contact.objects.filter(Q(entity__group__id=self.value) | Q(group__id=self.value))

        contacts_with_same_email_in_group = []
        for contact in contacts:
            email = contact.get_email
            if group_contacts.filter(Q(email=email) | Q(email='', entity__email=email)):
                contacts_with_same_email_in_group.append(contact)

        return contacts_with_same_email_in_group
