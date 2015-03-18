# -*- coding: utf-8 -*-
"""forms than can be included as part of the main search form"""

from datetime import date, timedelta

from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

import floppyforms as forms

from sanza.Crm import models
from sanza.Crm.settings import get_language_choices
from sanza.Crm.utils import get_default_country
from sanza.Crm.widgets import CityNoCountryAutoComplete, GroupAutoComplete
from sanza.Search.forms import SearchFieldForm, TwoDatesForm, YesNoSearchFieldForm



class EntityNameSearchForm(SearchFieldForm):
    """by entity name"""
    _name = 'entity_name'
    _label = _(u'Entity name')
    
    def __init__(self, *args, **kwargs):
        super(EntityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the name of the searched entities')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__name__icontains': self._value}
    

class EntityDescriptionForm(SearchFieldForm):
    """by entity description"""

    _name = 'entity_description'
    _label = _(u'Entity description')
    
    def __init__(self, *args, **kwargs):
        super(EntityDescriptionForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(
                attrs={'placeholder': _(u'Enter a part of the description of the searched entities')}
            )
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__description__icontains': self._value}


class EntityNotesForm(SearchFieldForm):
    """by entity notes"""

    _name = 'entity_notes'
    _label = _(u'Entity notes')
    
    def __init__(self, *args, **kwargs):
        super(EntityNotesForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the notes of the searched entities')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__notes__icontains': self._value}


class EntityNameStartsWithSearchForm(SearchFieldForm):
    """by entity name starts with"""

    _name = 'entity_name_sw'
    _label = _(u'Entity name starts with')
    
    def __init__(self, *args, **kwargs):
        super(EntityNameStartsWithSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(
                attrs={'placeholder': _(u'Enter the beginning of the name of the searched entities')}
            )
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__name__istartswith': self._value}


class HasEntityForm(YesNoSearchFieldForm):
    """contacts member of an entity"""

    _name = 'has_entity'
    _label = _(u'Has entity?')
        
    def get_lookup(self):
        """lookup"""
        no_entity = Q(entity__is_single_contact=True)
        if self.is_yes():
            return ~no_entity
        else:
            return no_entity


class EntityByModifiedDate(TwoDatesForm):
    """every entity modified betwwen two dates"""
    _name = 'entity_by_modified_date'
    _label = _(u'Entity by modified date')
        
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_dates()
        datetime2 += timedelta(1)
        return Q(entity__is_single_contact=False, entity__modified__gte=datetime1, entity__modified__lt=datetime2)


class ContactByModifiedDate(TwoDatesForm):
    """every contact modified between two dates"""
    _name = 'contact_by_modified_date'
    _label = _(u'Contact by modified date')
        
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_dates()
        datetime2 += timedelta(1)
        return {'modified__gte': datetime1, 'modified__lt': datetime2}


class BaseCitySearchForm(SearchFieldForm):
    """base class for search by city"""
    def __init__(self, *args, **kwargs):
        super(BaseCitySearchForm, self).__init__(*args, **kwargs)
        queryset = models.City.objects.order_by('name')
        field = forms.ModelChoiceField(
            queryset,
            label=self._label,
            widget=CityNoCountryAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
        )
        self._add_field(field)


class CitySearchForm(BaseCitySearchForm):
    """by city"""
    _name = 'city'
    _label = _(u'City')
    
    def get_lookup(self):
        """lookup"""
        return Q(city__id=self._value) | (Q(city__isnull=True) & Q(entity__city__id=self._value))
    

class EntityCitySearchForm(BaseCitySearchForm):
    """by city of the entity"""
    _name = 'entity_city'
    _label = _(u'Entity city')

    def get_lookup(self):
        """lookup"""
        return Q(entity__city__id=self._value)


class BaseZipCodeSearchForm(SearchFieldForm):
    """base class for search by zipcode"""
    def __init__(self, *args, **kwargs):
        super(BaseZipCodeSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter the beginning of the zip code')})
        )
        self._add_field(field)
    

class ZipCodeSearchForm(BaseZipCodeSearchForm):
    """by zip code"""
    _name = 'zip_code'
    _label = _(u'zip code')
    
    def get_lookup(self):
        """lookup"""
        return Q(zip_code__istartswith=self._value) | (Q(zip_code="") & Q(entity__zip_code__istartswith=self._value))


class EntityZipCodeSearchForm(BaseZipCodeSearchForm):
    """by zip code of the entity"""
    _name = 'entity_zip_code'
    _label = _(u'Entity zip code')
            
    def get_lookup(self):
        """lookup"""
        return Q(entity__zip_code__istartswith=self._value)
        

class ZoneSearchForm(SearchFieldForm):
    """By zone"""
    multi_values = True

    def __init__(self, *args, **kwargs):
        super(ZoneSearchForm, self).__init__(*args, **kwargs)
        type_name = self._name.replace("entity_", "")
        queryset = models.Zone.objects.filter(type__type=type_name).order_by('code', 'name')
        kwargs = kwargs or {}
        kwargs.setdefault('required', True)
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.MultipleChoiceField(
            choices=[(x.id, unicode(x)) for x in queryset.all()],
            label=self._label,
            **kwargs
        )
        self._add_field(field)
        
    def get_values(self):
        """get possible values"""
        if type(self._value) == list:
            values = self._value
        else:
            values = [self._value]
        return values
    
    def _get_widget(self):
        """get widget"""
        return forms.SelectMultiple(attrs={
            'class': "chosen-select",
            'data-placeholder': self._label,
            'style': "width: 100%", 
        })
    
    def get_queryset(self, queryset):
        """queryset"""
        group_queryset = Q(id=0)
        for zone_id in self.get_values():
            self._value = zone_id
            group_queryset = group_queryset | self.get_lookup()
        return queryset.filter(group_queryset)


class DepartmentSearchForm(ZoneSearchForm):
    """by departement"""
    _name = 'department'
    _label = _(u'Departments')
        
    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__parent__id=self._value) & Q(city__parent__type__type="department")

        qobj2 = Q(
            city__isnull=True
        ) & Q(
            entity__city__parent__id=self._value
        ) & Q(
            entity__city__parent__type__type="department"
        )
        
        return qobj1 | qobj2


class EntityDepartmentSearchForm(ZoneSearchForm):
    """by departement of the entity"""
    _name = 'entity_department'
    _label = _(u'Entity Departments')
        
    def get_queryset(self, queryset):
        """queryset"""
        queryset = super(EntityDepartmentSearchForm, self).get_queryset(queryset)
        return queryset.filter(entity__city__parent__type__type="department")

    def get_lookup(self):
        """lookup"""
        return Q(entity__city__parent__id=self._value)
        

class RegionSearchForm(ZoneSearchForm):
    """by region"""
    _name = 'region'
    _label = _(u'Regions')
        
    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__parent__parent__id=self._value) & Q(city__parent__parent__type__type="region")

        qobj2 = Q(
            city__isnull=True
        ) & Q(
            entity__city__parent__parent__id=self._value
        ) & Q(
            entity__city__parent__parent__type__type="region"
        )

        return qobj1 | qobj2


class EntityRegionSearchForm(ZoneSearchForm):
    """by region of teh entity"""
    _name = 'entity_region'
    _label = _(u'Entity Regions')
    
    def get_queryset(self, queryset):
        """queryset"""
        queryset = super(EntityRegionSearchForm, self).get_queryset(queryset)
        return queryset.filter(entity__city__parent__type__type="department")

    def get_lookup(self):
        """queryset"""
        return Q(entity__city__parent__parent__id=self._value)


class CountrySearchForm(ZoneSearchForm):
    """by country"""
    _name = 'country'
    _label = _(u'Countries')
        
    def get_lookup(self):
        """lookup"""
        default_country = get_default_country()
        if int(self._value) == default_country.id:
            return Q(
                city__parent__type__type='department'
            ) | (Q(
                city__isnull=True
            ) & Q(entity__city__parent__type__type='department'))
        else:
            return Q(city__parent__id=self._value) | (Q(city__isnull=True) & Q(entity__city__parent__id=self._value))


class EntityCountrySearchForm(ZoneSearchForm):
    """by country of the entity"""
    _name = 'entity_country'
    _label = _(u'Entity Countries')
        
    def get_lookup(self):
        """lookup"""
        default_country = get_default_country()
        
        if int(self._value) == default_country.id:
            return Q(entity__city__parent__type__type='department')
        else:
            return Q(entity__city__parent__id=self._value, entity__city__parent__type__type="country")


class ZoneGroupSearchForm(ZoneSearchForm):
    """by zone group"""
    _name = 'zone_group'
    _label = _(u'Zone Groups')
        
    def get_lookup(self):
        """lookup"""
        qobj1 = Q(city__groups__id=self._value)
        qobj2 = Q(city__isnull=True) & Q(entity__city__groups__id=self._value)
        return qobj1 | qobj2
    

class EntityZoneGroupSearchForm(ZoneSearchForm):
    """by zone group of entity"""
    _name = 'entity_zone_group'
    _label = _(u'Entity Zone Groups')
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__city__groups__id=self._value)


class HasCityAndZipcodeForm(YesNoSearchFieldForm):
    """by has city and address"""
    _name = 'has_city_and_zip'
    _label = _(u'Has city and zip code?')
        
    def get_lookup(self):
        """lookup"""
        contact_has_address = ~Q(zip_code='') & Q(city__isnull=False)
        entity_has_address = ~Q(entity__zip_code='') & Q(entity__city__isnull=False)
        has_address = contact_has_address | entity_has_address
        if self.is_yes():
            return has_address
        else:
            return ~has_address
            

class ActionInProgressForm(YesNoSearchFieldForm):
    """by action in progress"""
    _name = 'action'
    _label = _(u'Action in progress')
    
    def get_queryset(self, queryset):
        """queryset"""
        q_objs = Q(entity__action__done=False) | Q(action__done=False)
        if self.is_yes():
            return queryset.filter(q_objs)
        else:
            return queryset.exclude(q_objs)


class HasAction(YesNoSearchFieldForm):
    """Has an action"""
    _name = 'has_action'
    _label = _(u'Has actions')
        
    def get_queryset(self, queryset):
        """queryset"""
        queryset = queryset.annotate(num_actions=Count('action'), num_entity_actions=Count('entity__action'))
        if self.is_yes():
            return queryset.filter(Q(num_actions__gt=0) | Q(num_entity_actions__gt=0))
        else:
            return queryset.filter().filter(Q(num_actions__eq=0) & Q(num_entity_actions__eq=0))


class ActionByDoneDate(TwoDatesForm):
    """by action done between two dates"""
    _name = 'action_by_done_date'
    _label = _(u'Action by done date')
        
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_dates()
        return (
            (Q(action__done_date__gte=datetime1) & Q(action__done_date__lte=datetime2)) |
            (Q(entity__action__done_date__gte=datetime1) & Q(entity__action__done_date__lte=datetime2))
        )


class ActionByPlannedDate(TwoDatesForm):
    """by action planned between two dates"""
    _name = 'action_by_planned_date'
    _label = _(u'Action by planned date')
    
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_dates()
        
        start_after_end_before = Q(
            action__end_datetime__isnull=True
        ) & Q(
            action__planned_date__gte=datetime1
        ) & Q(
            action__planned_date__lte=datetime2
        )

        start_before_end_after = Q(
            action__end_datetime__isnull=False
        ) & Q(
            action__planned_date__lte=datetime2
        ) & Q(
            action__end_datetime__gte=datetime1
        )
        
        entity_start_after_end_before = Q(
            entity__action__end_datetime__isnull=True
        ) & Q(
            entity__action__planned_date__gte=datetime1
        ) & Q(
            entity__action__planned_date__lte=datetime2
        )

        entity_start_before_end_after = Q(
            entity__action__end_datetime__isnull=False
        ) & Q(
            entity__action__planned_date__lte=datetime2
        ) & Q(
            entity__action__end_datetime__gte=datetime1
        )
        
        return (
            start_after_end_before | start_before_end_after |
            entity_start_after_end_before | entity_start_before_end_after
        )


class ActionByStartDate(TwoDatesForm):
    """By action started between two dates"""
    _name = 'action_by_start_date'
    _label = _(u'Action by start date')
    
    def get_lookup(self):
        """lookup"""
        datetime1, datetime2 = self._get_dates()
        return (
            (Q(action__planned_date__gte=datetime1) & Q(action__planned_date__lte=datetime2)) |
            (Q(entity__action__planned_date__gte=datetime1) & Q(entity__action__planned_date__lte=datetime2))
        )


class ActionByUser(SearchFieldForm):
    """by user in charge of an action"""
    _name = 'action_by_user'
    _label = _(u'Action by user')
    
    def __init__(self, *args, **kwargs):
        super(ActionByUser, self).__init__(*args, **kwargs)
        choices = [(u.id, unicode(u)) for u in User.objects.all()]
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(action__in_charge=self._value) | Q(entity__action__in_charge=self._value)


class ActionGteAmount(SearchFieldForm):
    """by action with amount greater than a value"""
    _name = 'action_gte_amount'
    _label = _(u'Action with amount greater or equal to')
    
    def __init__(self, *args, **kwargs):
        super(ActionGteAmount, self).__init__(*args, **kwargs)
        field = forms.IntegerField(label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(action__amount__gte=self._value) | Q(entity__action__amount__gte=self._value)


class ActionLtAmount(SearchFieldForm):
    """by action with amount less than a value"""
    _name = 'action_lt_amount'
    _label = _(u'Action with amount less than')
    
    def __init__(self, *args, **kwargs):
        super(ActionLtAmount, self).__init__(*args, **kwargs)
        field = forms.IntegerField(label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(action__amount__lt=self._value) | Q(entity__action__amount__lt=self._value)


class ActionStatus(SearchFieldForm):
    """by action status"""
    _name = 'action_status'
    _label = _(u'Action by status')
    
    def __init__(self, *args, **kwargs):
        super(ActionStatus, self).__init__(*args, **kwargs)
        queryset = models.ActionStatus.objects.all()
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(action__status=self._value) | Q(entity__action__status=self._value)


class TypeSearchForm(SearchFieldForm):
    """by entity type"""
    _name = 'type'
    _label = _(u'Entity type')
    
    def __init__(self, *args, **kwargs):
        super(TypeSearchForm, self).__init__(*args, **kwargs)
        queryset = models.EntityType.objects.all()
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'entity__type__id': self._value}


class GroupSearchForm(SearchFieldForm):
    """by group"""
    _name = 'group'
    _label = _(u'Group')
    
    def _get_widget(self):
        """customize widget: autocomplete"""
        return GroupAutoComplete(attrs={
            'placeholder': _(u'Enter part of the group name'), 'size': '80',
        })

    def __init__(self, *args, **kwargs):
        super(GroupSearchForm, self).__init__(*args, **kwargs)
        queryset = models.Group.objects.all()
        try:
            queryset = queryset.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except Exception: #pylint: disable=broad-except
            queryset = queryset.order_by('name')
        kwargs = {}
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.ModelChoiceField(queryset, label=self._label, **kwargs)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__group__id=self._value) | Q(group__id=self._value)


class GroupSearchFormDropdownWidget(GroupSearchForm):
    """Search by group: dropdown widget"""
    _name = 'group_dropdown'
    _label = _(u'Group (dropdown list)')
    
    def _get_widget(self):
        """dropdown widget"""
        return forms.Select(attrs={
            'class': "chosen-select",
            'data-placeholder': _(u'Group names'),
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
            choices=[(x.id, unicode(x)) for x in queryset.all()], label=self._label, **kwargs)
        self._add_field(field)
        
    def get_values(self):
        """values"""
        if type(self._value) == list:
            values = self._value
        else:
            values = [self._value]
        return values
    
    def _get_widget(self):
        """customize widget"""
        return forms.SelectMultiple(attrs={
            'class': "chosen-select",
            'data-placeholder': _(u'Select Group names'),
            'style': "width: 100%", 
        })


class GroupsMemberOfAllSearchForm(MultiGroupSearchForm):
    """members of all groups"""
    _name = 'all_groups'
    _label = _(u'Members of all groups')
    
    def get_queryset(self, queryset):
        """queryset"""
        for group_id in self.get_values():
            group_queryset = ((Q(entity__isnull=False) & Q(entity__group__id=group_id)) | Q(group__id=group_id))
            queryset = queryset.filter(group_queryset)
        return queryset


class GroupsMemberOfAnySearchForm(MultiGroupSearchForm):
    """member of one of the groups"""
    _name = 'any_groups'
    _label = _(u'Members of at least one group')
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
    _name = 'none_groups'
    _label = _(u'Member of none of these groups')
    multi_values = True
    
    def get_queryset(self, queryset):
        """queryset"""
        for group_id in self.get_values():
            group_queryset = ((Q(entity__isnull=False) & Q(entity__group__id=group_id)) | Q(group__id=group_id))
            queryset = queryset.exclude(group_queryset)
        return queryset


class NotInGroupSearchForm(SearchFieldForm):
    """not in group"""
    _name = 'not_in_group'
    _label = _(u'Not in group')
    
    def __init__(self, *args, **kwargs):
        super(NotInGroupSearchForm, self).__init__(*args, **kwargs)
        queryset = models.Group.objects.all()
        try:
            queryset = queryset.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except Exception: #pylint: disable=broad-except
            queryset = queryset.order_by('name')
        field = forms.ModelChoiceField(
            queryset,
            label=self._label,
            widget=GroupAutoComplete(attrs={'placeholder': _(u'Enter part of the group name'), 'size': '80'})
        )
        self._add_field(field)
    
    def get_lookup(self):
        """lookup"""
        return [~Q(entity__group__id=self._value), ~Q(group__id=self._value)]


class ContactAgeSearchForm(SearchFieldForm):
    """search by age"""
    _name = 'contact_age'
    _label = _(u'Contact age')
    
    def __init__(self, *args, **kwargs):
        super(ContactAgeSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label, initial='0 100')
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        ages = [int(x) for x in self._value.split()]
        dt_from = date.today() - timedelta(days=ages[1]*365.25)
        dt_to = date.today() - timedelta(days=ages[0]*365.25)
        return {'birth_date__gte': dt_from, 'birth_date__lte': dt_to}


class ContactAcceptSubscriptionSearchForm(SearchFieldForm):
    """by accept subscrition"""
    _name = 'accept_subscription'
    _label = _(u'Accept subscription to')
    
    def __init__(self, *args, **kwargs):
        super(ContactAcceptSubscriptionSearchForm, self).__init__(*args, **kwargs)
        queryset = models.SubscriptionType.objects.all()
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'subscription__subscription_type__id': self._value, 'subscription__accept_subscription': True}


class ContactRefuseSubscriptionSearchForm(ContactAcceptSubscriptionSearchForm):
    """by refuse subscription"""
    _name = 'refuse_subscription'
    _label = _(u'Refuse subscription to')
    
    def get_lookup(self):
        """lookup"""
        return None
        
    def get_exclude_lookup(self):
        """exclude lookup"""
        return super(ContactRefuseSubscriptionSearchForm, self).get_lookup()


class SecondarySearchForm(SearchFieldForm):
    """by secondary contact"""
    _name = 'secondary_contact'
    _label = _(u'Secondary contact')
    
    def __init__(self, *args, **kwargs):
        super(SecondarySearchForm, self).__init__(*args, **kwargs)
        choices = ((1, _('Include')), (0, _('Only')),)
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        value = int(self._value)
        if value == 1:
            #the lookup 'main_contact' will be removed by the search form
            return {}
        elif value == 0:
            return {'main_contact': False}


class ContactHasLeft(SearchFieldForm):
    """contact who left"""
    _name = 'contact_has_left'
    _label = _(u'Contact has left')
    
    def __init__(self, *args, **kwargs):
        super(ContactHasLeft, self).__init__(*args, **kwargs)
        choices = ((0, _('Only')), (1, _('Include')),)
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
            
    def get_lookup(self):
        """lookup"""
        value = int(self._value)
        if value == 1:
            #the lookup 'has_left' will be removed by the search form
            return {}
        elif value == 0:
            return {'has_left': True}


class ContactRoleSearchForm(SearchFieldForm):
    """by role"""
    _name = 'contact_role'
    _label = _(u'Contact role')
    
    def __init__(self, *args, **kwargs):
        super(ContactRoleSearchForm, self).__init__(*args, **kwargs)
        queryset = models.EntityRole.objects.all().order_by('name')
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'role': self._value}


class EmailSearchForm(SearchFieldForm):
    """by email"""
    _name = 'contact_entity_email'
    _label = _(u'Email')
    
    def __init__(self, *args, **kwargs):
        super(EmailSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the email of a contact or an entity')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__email__icontains=self._value) | Q(email__icontains=self._value)


class ContactHasEmail(YesNoSearchFieldForm):
    """by has email"""
    _name = 'contact_has_email'
    _label = _(u'Contact has email')
            
    def get_lookup(self):
        """lookup"""
        has_no_email = (Q(email='') & Q(entity__email=''))
        if self.is_yes():
            return ~has_no_email
        else:
            return has_no_email


class ContactHasPersonalEmail(YesNoSearchFieldForm):
    """by has an email set on the contact (ignore if set on entity)"""
    _name = 'contact_has_personal_email'
    _label = _(u'Contact has pesonal email')
            
    def get_lookup(self):
        """queryset"""
        has_no_email = Q(email='')
        if self.is_yes():
            return ~has_no_email
        else:
            return has_no_email


class UnknownContact(YesNoSearchFieldForm):
    """no name"""
    _name = 'unknown_contact'
    _label = _(u'Unknown contacts')
        
    def get_lookup(self):
        """lookup"""
        unknown_contact = (Q(firstname='') & Q(lastname=''))
        if self.is_yes():
            return unknown_contact
        else:
            return ~unknown_contact


class ActionTypeSearchForm(SearchFieldForm):
    """by type of action"""
    _name = 'action_type'
    _label = _(u'Action type')
    
    def __init__(self, *args, **kwargs):
        super(ActionTypeSearchForm, self).__init__(*args, **kwargs)
        queryset = models.ActionType.objects.all().order_by('name')
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__action__type=self._value) | Q(action__type=self._value)


class ActionNameSearchForm(SearchFieldForm):
    """by subject of action"""
    _name = 'action_name'
    _label = _(u'Action subject')
    
    def __init__(self, *args, **kwargs):
        super(ActionNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched action')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return Q(entity__action__subject__icontains=self._value) | Q(action__subject__icontains=self._value)


class RelationshipDateForm(TwoDatesForm):
    """by date of relationship"""
    _name = 'relationship_date'
    _label = _(u'Relationship date')
            
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_dates()
        return {'entity__relationship_date__gte': start_datetime, 'entity__relationship_date__lte': end_datetime}


class ContactNameSearchForm(SearchFieldForm):
    """by contact name"""
    _name = 'contact_name'
    _label = _(u'Contact name')
    
    def __init__(self, *args, **kwargs):
        super(ContactNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the name of the searched contact')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'lastname__icontains': self._value}


class ContactLanguageSearchForm(SearchFieldForm):
    """by contact language"""
    _name = 'contact_lang'
    _label = _(u'Contact language')

    def __init__(self, *args, **kwargs):
        super(ContactLanguageSearchForm, self).__init__(*args, **kwargs)
        field = forms.ChoiceField(
            label=self._label,
            choices=get_language_choices()
        )
        self._add_field(field)
        field.required = False

    def get_lookup(self):
        """lookup"""
        return {'favorite_language': self._value}


class ContactFirstnameSearchForm(SearchFieldForm):
    """by firstname"""
    _name = 'contact_firstname'
    _label = _(u'Contact firstname')
    
    def __init__(self, *args, **kwargs):
        super(ContactFirstnameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the firstname of the searched contact')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'firstname__icontains': self._value}
    

class ContactNotesSearchForm(SearchFieldForm):
    """by notes"""
    _name = 'contact_notes'
    _label = _(u'Contact notes')
    
    def __init__(self, *args, **kwargs):
        super(ContactNotesSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of a note of the searched contact')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'notes__icontains': self._value}


class OpportunitySearchForm(SearchFieldForm):
    """by opportunity"""
    _name = 'opportunity'
    _label = _(u'Opportunity')
    
    def __init__(self, *args, **kwargs):
        super(OpportunitySearchForm, self).__init__(*args, **kwargs)
        queryset = models.Opportunity.objects.all()
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
    
    def get_lookup(self):
        """lookup"""
        return Q(action__opportunity__id=self._value) | Q(entity__action__opportunity__id=self._value)
        

class OpportunityNameSearchForm(SearchFieldForm):
    """by opportunity name"""
    _name = 'opportunity_name'
    _label = _(u'Opportunity name')
    
    def __init__(self, *args, **kwargs):
        super(OpportunityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched opportunity')})
        )
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        queryset1 = Q(action__opportunity__name__icontains=self._value)
        queryset2 = Q(entity__action__opportunity__name__icontains=self._value)
        return queryset1 | queryset2


class NoSameAsForm(YesNoSearchFieldForm):
    """Allow same as contact in results"""
    _name = 'no_same_as'
    _label = _(u'Allow same-as')
    
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
                        same_as[contact.same_as.id] = contact.same_as
                        filtered_contacts.append(contact.same_as.main_contact if contact.same_as else contact)
                else:
                    filtered_contacts.append(contact)
            return filtered_contacts


class ContactsImportSearchForm(SearchFieldForm):
    """by import"""
    _name = 'contact_import'
    _label = _(u'Import')
    
    def __init__(self, *args, **kwargs):
        super(ContactsImportSearchForm, self).__init__(*args, **kwargs)
        queryset = models.ContactsImport.objects.order_by('name')
        field = forms.ModelChoiceField(queryset, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        return {'imported_by': self._value}


class ContactsByUpdateDate(TwoDatesForm):
    """by update date"""
    _name = 'contacts_by_update_date'
    _label = _(u'Contacts by update date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_dates()
        return Q(modified__gte=start_datetime, modified__lte=end_datetime)
    

class ContactsByCreationDate(TwoDatesForm):
    """by creation date"""
    _name = 'contacts_by_creation_date'
    _label = _(u'Contacts by creation date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_dates()
        return Q(created__gte=start_datetime, created__lte=end_datetime)


class EntitiesByUpdateDate(TwoDatesForm):
    """by entity update date"""
    _name = 'entities_by_update_date'
    _label = _(u'Entities by update date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_dates()
        return Q(entity__modified__gte=start_datetime, entity__modified__lte=end_datetime)
    

class EntitiesByCreationDate(TwoDatesForm):
    """by entity creation date"""
    _name = 'entities_by_creation_date'
    _label = _(u'Entities by creation date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_dates()
        return Q(entity__created__gte=start_datetime, entity__created__lte=end_datetime)
    

class ContactsAndEntitiesByChangeDate(TwoDatesForm):
    """by change date"""
    _name = 'contacts_and_entities_by_change_date'
    _label = _(u'Contacts and entities by change date')
    
    def get_lookup(self):
        """lookup"""
        start_datetime, end_datetime = self._get_dates()
        return Q(modified__gte=start_datetime, modified__lte=end_datetime) | \
            Q(created__gte=start_datetime, created__lte=end_datetime) | \
            Q(entity__modified__gte=start_datetime, entity__modified__lte=end_datetime) | \
            Q(entity__created__gte=start_datetime, entity__created__lte=end_datetime)
        

class ContactsRelationshipByType(SearchFieldForm):
    """by type of relationship"""
    _name = 'contacts_by_relationship_type'
    _label = _(u'Relationship type')
    
    def __init__(self, *args, **kwargs):
        super(ContactsRelationshipByType, self).__init__(*args, **kwargs)
        relationship_types = []
        for relationship_type in models.RelationshipType.objects.all():
            relationship_types.append((relationship_type.id, relationship_type.name))
            if relationship_type.reverse:
                relationship_types.append((-relationship_type.id, relationship_type.reverse))
        field = forms.CharField(label=self._label, widget=forms.Select(choices=relationship_types))
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        relationship_ids = []
        value, is_reverse = int(self._value), False
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
    _name = 'contacts_by_relationship_dates'
    _label = _(u'Relationship dates')
        
    def get_lookup(self):
        """lookup"""
        relationship_ids = []
        start_datetime, end_datetime = self._get_dates()
        end_datetime = end_datetime + timedelta(1)
        queryset = models.Relationship.objects.filter(created__gte=start_datetime, created__lt=end_datetime)
        for relationship_type in queryset:
            relationship_ids = [relationship_type.contact1.id, relationship_type.contact2.id]
        relationship_ids = list(set(relationship_ids))  
        return Q(id__in=relationship_ids)
    

class ContactWithCustomField(SearchFieldForm):
    """by contact with custom field"""
    _name = 'contact_with_custom_field'
    _label = _(u'Contacts with custom field')
    
    def __init__(self, *args, **kwargs):
        super(ContactWithCustomField, self).__init__(*args, **kwargs)
        custom_fields = []
        for custom_field in models.CustomField.objects.filter(model=models.CustomField.MODEL_CONTACT):
            custom_fields.append((custom_field.id, custom_field.label))
        field = forms.CharField(label=self._label, widget=forms.Select(choices=custom_fields))
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        value = int(self._value)
        custom_field = models.CustomField.objects.get(id=value, model=models.CustomField.MODEL_CONTACT)
        return Q(contactcustomfieldvalue__custom_field=custom_field)


class EntityWithCustomField(SearchFieldForm):
    """by entity custom field"""
    _name = 'entity_with_custom_field'
    _label = _(u'Entities with custom field')
    
    def __init__(self, *args, **kwargs):
        super(EntityWithCustomField, self).__init__(*args, **kwargs)
        custom_fields = []
        for custom_field in models.CustomField.objects.filter(model=models.CustomField.MODEL_ENTITY):
            custom_fields.append((custom_field.id, custom_field.label))
        field = forms.CharField(label=self._label, widget=forms.Select(choices=custom_fields))
        self._add_field(field)
        
    def get_lookup(self):
        """lookup"""
        value = int(self._value)
        custom_field = models.CustomField.objects.get(id=value, model=models.CustomField.MODEL_ENTITY)
        return Q(entity__entitycustomfieldvalue__custom_field=custom_field)
    

class SortContacts(SearchFieldForm):
    """sort contacts"""
    _name = 'sort'
    _label = _(u'Sort contacts')
    _contacts_display = True
    
    def __init__(self, *args, **kwargs):
        super(SortContacts, self).__init__(*args, **kwargs)
        choices = (
            ('name', _(u'Name')),
            ('entity', _(u'Entity')),
            ('contact', _(u'Contact')),
            ('zipcode', _(u'Zipcode')),
        ) 
        field = forms.CharField(
            label=self._label,
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
        """sort by name"""
        if contact.entity.is_single_contact:
            value = u"{0} {1}".format(contact.lastname, contact.firstname)
        else:
            value = contact.entity.name
        return value.upper()
    
    def _sort_by_contact(self, contact):
        """sort by contact name"""
        return u"{0} {1}".format(contact.lastname, contact.firstname).upper()
    
    def _sort_by_entity(self, contact):
        """sort by entity"""
        value1 = u"B" if contact.entity.is_single_contact else u"A"
        value2 = self._sort_by_name(contact)
        value3 = u"{0} {1}".format(contact.lastname, contact.firstname) if not contact.entity.is_single_contact else u""
        return value1, value2, value3
    
    def _sort_by_zipcode(self, contact):
        """sort by zipcode"""
        country = contact.get_country()
        value1 = contact.get_zip_code or u'?'
        city = contact.get_city
        if not city:
            prefix1 = "C"
            prefix2 = value2 = "?"
        else:
            prefix1 = u"A" if ((not country) or self.default_country.id == country.id) else u"B"
            prefix2 = country.name if country else self.default_country.name
            value2 = city.name
        value3 = self._sort_by_name(contact)
        return prefix1, prefix2, value1, value2, value3
    
    def get_queryset(self, queryset):
        """queryset"""
        return queryset
    
    def global_post_process(self, contacts):
        """filter the final results"""
        callback = getattr(self, '_sort_by_{0}'.format(self._value), None)
        return sorted(contacts, key=callback)
