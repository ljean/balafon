# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Search.forms import SearchFieldForm, TwoDatesForm, YesNoSearchFieldForm
from django.utils.translation import ugettext as _
from sanza.Crm import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
#from sanza.Crm.settings import get_default_country
from django.contrib.auth.models import User
from django.db.models import Q, Count
from sanza.Crm.widgets import CityNoCountryAutoComplete, GroupAutoComplete
from sanza.Crm.utils import get_default_country

class EntityNameSearchForm(SearchFieldForm):
    _name = 'entity_name'
    _label = _(u'Entity name')
    
    def __init__(self, *args, **kwargs):
        super(EntityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the name of the searched entities')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__name__icontains': self._value}
    
class EntityDescriptionForm(SearchFieldForm):
    _name = 'entity_description'
    _label = _(u'Entity description')
    
    def __init__(self, *args, **kwargs):
        super(EntityDescriptionForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the description of the searched entities')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__description__icontains': self._value}

class EntityNotesForm(SearchFieldForm):
    _name = 'entity_notes'
    _label = _(u'Entity notes')
    
    def __init__(self, *args, **kwargs):
        super(EntityNotesForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the notes of the searched entities')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__notes__icontains': self._value}
    
class EntityNameStartsWithSearchForm(SearchFieldForm):
    _name = 'entity_name_sw'
    _label = _(u'Entity name starts with')
    
    def __init__(self, *args, **kwargs):
        super(EntityNameStartsWithSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter the beginning of the name of the searched entities')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__name__istartswith': self._value}


class HasEntityForm(YesNoSearchFieldForm):
    _name = 'has_entity'
    _label = _(u'Has entity?')
        
    def get_lookup(self):
        no_entity = Q(entity__is_single_contact=True)
        if self.is_yes():
            return ~no_entity
        else:
            return no_entity

class EntityByModifiedDate(TwoDatesForm):
    _name = 'entity_by_modified_date'
    _label = _(u'Entity by modified date')
        
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        dt2 += timedelta(1)
        return Q(entity__is_single_contact=False, entity__modified__gte=dt1, entity__modified__lt=dt2)

class ContactByModifiedDate(TwoDatesForm):
    _name = 'contact_by_modified_date'
    _label = _(u'Contact by modified date')
        
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        dt2 += timedelta(1)
        return {'modified__gte': dt1, 'modified__lt': dt2, }

class BaseCitySearchForm(SearchFieldForm):
    
    def __init__(self, *args, **kwargs):
        super(BaseCitySearchForm, self).__init__(*args, **kwargs)
        qs = models.City.objects.order_by('name') 
        field = forms.ModelChoiceField(qs, label=self._label,
            widget = CityNoCountryAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
        )
        self._add_field(field)

class CitySearchForm(BaseCitySearchForm):
    _name = 'city'
    _label = _(u'City')
    
    def get_lookup(self):
        return Q(city__id=self._value) | (Q(city__isnull=True) & Q(entity__city__id=self._value))
    
class EntityCitySearchForm(BaseCitySearchForm):
    _name = 'entity_city'
    _label = _(u'Entity city')

    def get_lookup(self):
        return Q(entity__city__id=self._value)

class BaseZipCodeSearchForm(SearchFieldForm):
    
    def __init__(self, *args, **kwargs):
        super(BaseZipCodeSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter the beginning of the zip code')}))
        self._add_field(field)
    
class ZipCodeSearchForm(BaseZipCodeSearchForm):
    _name = 'zip_code'
    _label = _(u'zip code')
    
    def get_lookup(self):
        return Q(zip_code__istartswith=self._value) | (Q(zip_code="") & Q(entity__zip_code__istartswith=self._value))


class EntityZipCodeSearchForm(BaseZipCodeSearchForm):
    _name = 'entity_zip_code'
    _label = _(u'Entity zip code')
            
    def get_lookup(self):
        return Q(entity__zip_code__istartswith=self._value)
        
class ZoneSearchForm(SearchFieldForm):
    
    def __init__(self, *args, **kwargs):
        super(ZoneSearchForm, self).__init__(*args, **kwargs)
        type_name = self._name.replace("entity_", "")
        qs = models.Zone.objects.filter(type__type=type_name).order_by('code', 'name') 
        field = forms.ModelChoiceField(qs, label=self._label, widget=self._get_widget())
        self._add_field(field)
        
    def _get_widget(self):
        return forms.Select(attrs={
            'class': "chosen-select",
            'data-placeholder': self._label,
            'style': "width: 100%", 
        })
    
class DepartmentSearchForm(ZoneSearchForm):
    _name = 'department'
    _label = _(u'Department')
        
    def get_lookup(self):
        q1 = Q(city__parent__id=self._value) & Q(city__parent__type__type="department")
        q2 = Q(city__isnull=True) & Q(entity__city__parent__id=self._value) & Q(entity__city__parent__type__type="department")
        
        return q1 | q2

class EntityDepartmentSearchForm(ZoneSearchForm):
    _name = 'entity_department'
    _label = _(u'Entity Department')
        
    def get_queryset(self, qs):
        return qs.filter(self.get_lookup()).filter(entity__city__parent__type__type="department")
        
    def get_lookup(self):
        return Q(entity__city__parent__id=self._value)
        
class RegionSearchForm(ZoneSearchForm):
    _name = 'region'
    _label = _(u'Region')
        
    def get_lookup(self):
        q1 = Q(city__parent__parent__id=self._value) & Q(city__parent__parent__type__type="region")
        q2 = Q(city__isnull=True) & Q(entity__city__parent__parent__id=self._value) & Q(entity__city__parent__parent__type__type="region")
        return q1 | q2

class EntityRegionSearchForm(ZoneSearchForm):
    _name = 'entity_region'
    _label = _(u'Entity Region')
    
    def get_queryset(self, qs):
        return qs.filter(self.get_lookup()).filter(entity__city__parent__parent__type__type="region")
        
    def get_lookup(self):
        return Q(entity__city__parent__parent__id=self._value)
        
class CountrySearchForm(ZoneSearchForm):
    _name = 'country'
    _label = _(u'Country')
        
    def get_lookup(self):
        default_country = get_default_country()
        if int(self._value) == default_country.id:
            return Q(city__parent__type__type='department') | (Q(city__isnull=True) & Q(entity__city__parent__type__type='department'))
        else:
            return Q(city__parent__id=self._value) | (Q(city__isnull=True) & Q(entity__city__parent__id=self._value))
        
class EntityCountrySearchForm(ZoneSearchForm):
    _name = 'entity_country'
    _label = _(u'Entity Country')
        
    def get_lookup(self):
        default_country = get_default_country()
        
        if int(self._value) == default_country.id:
            return Q(entity__city__parent__type__type='department')
        else:
            return Q(entity__city__parent__id=self._value, entity__city__parent__type__type="country")
   

class HasCityAndZipcodeForm(YesNoSearchFieldForm):
    _name = 'has_city_and_zip'
    _label = _(u'Has city and zip code?')
        
    def get_lookup(self):
        contact_has_address = ~Q(zip_code='') & Q(city__isnull=False)
        entity_has_address = ~Q(entity__zip_code='') & Q(entity__city__isnull=False)
        has_address = contact_has_address | entity_has_address
        if self.is_yes():
            return has_address
        else:
            return ~has_address
            
class ActionInProgressForm(YesNoSearchFieldForm):
    _name = 'action'
    _label = _(u'Action in progress')
    
    #def __init__(self, *args, **kwargs):
    #    super(ActionInProgressForm, self).__init__(*args, **kwargs)
    #    choices = ((1, _('Yes')),)
    #    field = forms.ChoiceField(choices=choices, label=self._label)
    #    self._add_field(field)
        
    def get_queryset(self, qs):
        qobjs = Q(entity__action__done=False) | Q(action__done=False)
        if self.is_yes():
            return qs.filter(qobjs)
        else:
            return qs.exclude(qobjs)

class HasAction(YesNoSearchFieldForm):
    _name = 'has_action'
    _label = _(u'Has actions')
        
    def get_queryset(self, qs):
        qs = qs.annotate(num_actions=Count('action'), num_entity_actions=Count('entity__action'))
        if self.is_yes():
            return qs.filter(Q(num_actions__gt=0) | Q(num_entity_actions__gt=0))
        else:
            return qs.filter().filter(Q(num_actions__eq=0) & Q(num_entity_actions__eq=0))

# TODO ####################################        
#class NoAction(YesNoSearchFieldForm):
#    _name = 'action'
#    _label = _(u'Action in progress')
#        
#    def get_lookup(self):
#        if self.is_yes():
#            return (Q(entity__action__done=False) | Q(action__done=False))
#        else:
#            return (Q(entity__action__done=True) | Q(action__done=True))
        
class ActionByDoneDate(TwoDatesForm):
    _name = 'action_by_done_date'
    _label = _(u'Action by done date')
        
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return (
            (Q(action__done_date__gte=dt1) & Q(action__done_date__lte= dt2)) |
            (Q(entity__action__done_date__gte=dt1) & Q(entity__action__done_date__lte= dt2))
        )


class ActionByPlannedDate(TwoDatesForm):
    _name = 'action_by_planned_date'
    _label = _(u'Action by planned date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        
        l1 = Q(action__end_datetime__isnull=True) & Q(action__planned_date__gte=dt1) & Q(action__planned_date__lte=dt2)
        l2 = Q(action__end_datetime__isnull=False) & Q(action__planned_date__lte=dt2) & Q(action__end_datetime__gte=dt1)
        
        l3 = Q(entity__action__end_datetime__isnull=True) & Q(entity__action__planned_date__gte=dt1) & Q(entity__action__planned_date__lte=dt2)
        l4 = Q(entity__action__end_datetime__isnull=False) & Q(entity__action__planned_date__lte=dt2) & Q(entity__action__end_datetime__gte=dt1)
        
        return (l1 | l2 | l3 | l4)
    
class ActionByStartDate(TwoDatesForm):
    _name = 'action_by_start_date'
    _label = _(u'Action by start date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return (
            (Q(action__planned_date__gte=dt1) & Q(action__planned_date__lte= dt2)) |
            (Q(entity__action__planned_date__gte=dt1) & Q(entity__action__planned_date__lte= dt2))
        )

class ActionByUser(SearchFieldForm):
    _name = 'action_by_user'
    _label = _(u'Action by user')
    
    def __init__(self, *args, **kwargs):
        super(ActionByUser, self).__init__(*args, **kwargs)
        choices = [(u.id, unicode(u)) for u in User.objects.all()]
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return (Q(action__in_charge=self._value) | Q(entity__action__in_charge=self._value))

class ActionGteAmount(SearchFieldForm):
    _name = 'action_gte_amount'
    _label = _(u'Action with amount greater or equal to')
    
    def __init__(self, *args, **kwargs):
        super(ActionGteAmount, self).__init__(*args, **kwargs)
        field = forms.IntegerField(label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return (Q(action__amount__gte=self._value) | Q(entity__action__amount__gte=self._value))

class ActionLtAmount(SearchFieldForm):
    _name = 'action_lt_amount'
    _label = _(u'Action with amount less than')
    
    def __init__(self, *args, **kwargs):
        super(ActionLtAmount, self).__init__(*args, **kwargs)
        field = forms.IntegerField(label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return (Q(action__amount__lt=self._value) | Q(entity__action__amount__lt=self._value))
    
class ActionStatus(SearchFieldForm):
    _name = 'action_status'
    _label = _(u'Action by status')
    
    def __init__(self, *args, **kwargs):
        super(ActionStatus, self).__init__(*args, **kwargs)
        qs = models.ActionStatus.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return (Q(action__status=self._value) | Q(entity__action__status=self._value))


class TypeSearchForm(SearchFieldForm):
    _name = 'type'
    _label = _(u'Entity type')
    
    def __init__(self, *args, **kwargs):
        super(TypeSearchForm, self).__init__(*args, **kwargs)
        qs = models.EntityType.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__type__id': self._value}

class GroupSearchForm(SearchFieldForm):
    _name = 'group'
    _label = _(u'Group')
    
    def _get_widget(self):
        return GroupAutoComplete(attrs={
            'placeholder': _(u'Enter part of the group name'), 'size': '80',
        })
    
    
    def __init__(self, *args, **kwargs):
        super(GroupSearchForm, self).__init__(*args, **kwargs)
        qs = models.Group.objects.all()
        try:
            qs = qs.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except:
            qs = qs.order_by('name')
        kwargs = {}
        widget = self._get_widget()
        if widget:
            kwargs['widget'] = widget
        field = forms.ModelChoiceField(qs, label=self._label, **kwargs)
        self._add_field(field)
        
    def get_lookup(self):
        return Q(entity__group__id=self._value) | Q(group__id=self._value)

class GroupSearchFormDropdownWidget(GroupSearchForm):
    _name = 'group_dropdown'
    _label = _(u'Group (dropdown list)')
    
    def _get_widget(self):
        return forms.Select(attrs={
            'class': "chosen-select",
            'data-placeholder': _(u'Group names'),
            'style': "width: 100%", 
        })


class NotInGroupSearchForm(SearchFieldForm):
    _name = 'not_in_group'
    _label = _(u'Not in group')
    
    def __init__(self, *args, **kwargs):
        super(NotInGroupSearchForm, self).__init__(*args, **kwargs)
        qs = models.Group.objects.all()
        try:
            qs = qs.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except:
            qs = qs.order_by('name')
        field = forms.ModelChoiceField(qs, label=self._label,
            widget = GroupAutoComplete(attrs={'placeholder': _(u'Enter part of the group name'), 'size': '80'}))
        self._add_field(field)
    
    def get_lookup(self):
        return [~Q(entity__group__id=self._value), ~Q(group__id=self._value)]

class ContactAgeSearchForm(SearchFieldForm):
    _name = 'contact_age'
    _label = _(u'Contact age')
    
    def __init__(self, *args, **kwargs):
        super(ContactAgeSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label, initial='0 100')
        self._add_field(field)
        
    def get_lookup(self):
        ages = [int(x) for x in self._value.split()]
        dt_from = date.today() - timedelta(days=ages[1]*365.25)
        dt_to = date.today() - timedelta(days=ages[0]*365.25)
        return {'birth_date__gte': dt_from, 'birth_date__lte': dt_to}


class ContactNewsletterSearchForm(YesNoSearchFieldForm):
    _name = 'accept_newsletter'
    _label = _(u'Accept newsletter')
            
    def get_lookup(self):
        return {'accept_newsletter': self.is_yes()}
        
class Contact3rdPartySearchForm(YesNoSearchFieldForm):
    _name = 'accept_3rdparty'
    _label = _(u'Accept third parties')
            
    def get_lookup(self):
        return {'accept_3rdparty': self.is_yes()}

class SecondarySearchForm(SearchFieldForm):
    _name = 'secondary_contact'
    _label = _(u'Secondary contact')
    
    def __init__(self, *args, **kwargs):
        super(SecondarySearchForm, self).__init__(*args, **kwargs)
        choices = ((1, _('Include')), (0, _('Only')),)
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        value = int(self._value)
        if value == 1:
            return {} #the lookup 'main_contact' will be removed by the search form
        elif value == 0:
            return {'main_contact': False}

class ContactHasLeft(SearchFieldForm):
    _name = 'contact_has_left'
    _label = _(u'Contact has left')
    
    def __init__(self, *args, **kwargs):
        super(ContactHasLeft, self).__init__(*args, **kwargs)
        choices = ((0, _('Only')), (1, _('Include')),)
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
            
    def get_lookup(self):
        value = int(self._value)
        if value == 1:
            return {} #the lookup 'has_left' will be removed by the search form
        elif value == 0:
            return {'has_left': True}

class ContactRoleSearchForm(SearchFieldForm):
    _name = 'contact_role'
    _label = _(u'Contact role')
    
    def __init__(self, *args, **kwargs):
        super(ContactRoleSearchForm, self).__init__(*args, **kwargs)
        qs = models.EntityRole.objects.all().order_by('name') 
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return {'role': self._value}

class EmailSearchForm(SearchFieldForm):
    _name = 'contact_entity_email'
    _label = _(u'Email')
    
    def __init__(self, *args, **kwargs):
        super(EmailSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the email of a contact or an entity')}))
        self._add_field(field)
        
    def get_lookup(self):
        return Q(entity__email__icontains=self._value) | Q(email__icontains=self._value)

class ContactHasEmail(YesNoSearchFieldForm):
    _name = 'contact_has_email'
    _label = _(u'Contact has email')
            
    def get_lookup(self):
        has_no_email = (Q(email='') & Q(entity__email=''))
        if self.is_yes():
            return ~has_no_email
        else:
            return has_no_email

class ContactHasPersonalEmail(YesNoSearchFieldForm):
    _name = 'contact_has_personal_email'
    _label = _(u'Contact has pesonal email')
            
    def get_lookup(self):
        has_no_email = Q(email='')
        if self.is_yes():
            return ~has_no_email
        else:
            return has_no_email

class UnknownContact(YesNoSearchFieldForm):
    _name = 'unknown_contact'
    _label = _(u'Unknown contacts')
        
    def get_lookup(self):
        unknown_contact = (Q(firstname='') & Q(lastname=''))
        if self.is_yes():
            return unknown_contact
        else:
            return ~unknown_contact

class ActionTypeSearchForm(SearchFieldForm):
    _name = 'action_type'
    _label = _(u'Action type')
    
    def __init__(self, *args, **kwargs):
        super(ActionTypeSearchForm, self).__init__(*args, **kwargs)
        qs = models.ActionType.objects.all().order_by('name') 
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return Q(entity__action__type=self._value) | Q(action__type=self._value)

class ActionNameSearchForm(SearchFieldForm):
    _name = 'action_name'
    _label = _(u'Action subject')
    
    def __init__(self, *args, **kwargs):
        super(ActionNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched action')}))
        self._add_field(field)
        
    def get_lookup(self):
        return Q(entity__action__subject__icontains=self._value) | Q(action__subject__icontains=self._value)

class RelationshipDateForm(TwoDatesForm):
    _name = 'relationship_date'
    _label = _(u'Relationship date')
            
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return {'entity__relationship_date__gte': dt1, 'entity__relationship_date__lte': dt2}
        
class ContactNameSearchForm(SearchFieldForm):
    _name = 'contact_name'
    _label = _(u'Contact name')
    
    def __init__(self, *args, **kwargs):
        super(ContactNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the name of the searched contact')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'lastname__icontains': self._value}
    
#class ContactNotesForm(SearchFieldForm):
#    _name = 'contact_notes'
#    _label = _(u'Contact notes')
#    
#    def __init__(self, *args, **kwargs):
#        super(ContactNotesForm, self).__init__(*args, **kwargs)
#        field = forms.CharField(label=self._label,
#            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the notes of the searched contacts')}))
#        self._add_field(field)
#        
#    def get_lookup(self):
#        return {'notes__icontains': self._value}
    
class ContactFirstnameSearchForm(SearchFieldForm):
    _name = 'contact_firstname'
    _label = _(u'Contact firstname')
    
    def __init__(self, *args, **kwargs):
        super(ContactFirstnameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of the firstname of the searched contact')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'firstname__icontains': self._value}
    
class ContactNotesSearchForm(SearchFieldForm):
    _name = 'contact_notes'
    _label = _(u'Contact notes')
    
    def __init__(self, *args, **kwargs):
        super(ContactNotesSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'Enter a part of a note of the searched contact')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'notes__icontains': self._value}

#class OpportunityStatusSearchForm(SearchFieldForm):
#    _name = 'opportunity_status'
#    _label = _(u'Opportunity status')
#    
#    def __init__(self, *args, **kwargs):
#        super(OpportunityStatusSearchForm, self).__init__(*args, **kwargs)
#        qs = models.OpportunityStatus.objects.all()
#        field = forms.ModelChoiceField(qs, label=self._label)
#        self._add_field(field)
#        
#    def get_lookup(self):
#        return {'action__opportunity__status': self._value}
        
class OpportunitySearchForm(SearchFieldForm):
    _name = 'opportunity'
    _label = _(u'Opportunity')
    
    def __init__(self, *args, **kwargs):
        super(OpportunitySearchForm, self).__init__(*args, **kwargs)
        qs = models.Opportunity.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
    
    def get_lookup(self):
        return Q(action__opportunity__id=self._value) | Q(entity__action__opportunity__id=self._value)
        
class OpportunityNameSearchForm(SearchFieldForm):
    _name = 'opportunity_name'
    _label = _(u'Opportunity name')
    
    def __init__(self, *args, **kwargs):
        super(OpportunityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched opportunity')}))
        self._add_field(field)
        
    def get_lookup(self):
        return Q(action__opportunity__name__icontains=self._value) | Q(entity__action__opportunity__name__icontains=self._value)

class NoSameAsForm(YesNoSearchFieldForm):
    _name = 'no_same_as'
    _label = _(u'Allow same-as')
    
    def get_lookup(self):
        pass
    
    def get_exclude_lookup(self):
        pass
    
    def global_post_process(self, contacts):
        if self.is_yes():
            return contacts
        else:
            same_as = {}
            filtered_contacts = []
            for c in contacts:
                if c.same_as:
                    if not same_as.has_key(c.same_as.id):
                        same_as[c.same_as.id] = c.same_as
                        filtered_contacts.append(c.same_as.main_contact if c.same_as else c)
                else:
                    filtered_contacts.append(c)
            return filtered_contacts

#class OpportunityReminderForm(SearchFieldForm):
#    _name = 'opp_reminder'
#    _label = _(u'Opportunity reminder')
#    
#    def __init__(self, *args, **kwargs):
#        super(OpportunityReminderForm, self).__init__(*args, **kwargs)
#        field = forms.CharField(
#            label=self._label, initial='{0}'.format(date.today()),
#            widget=forms.TextInput(attrs={"class": "datepicker"})
#        )
#        self._add_field(field)
#
#    def _get_date(self):
#        if self._value.find('-')>=0:
#            d = [int(x) for x in self._value.split('-')]
#        else:
#            d = [int(x) for x in self._value.split('/')]
#            d.reverse()
#        return date(*d)
#    
#    def get_exclude_lookup(self):
#        d = self._get_date()
#        return {'entity__opportunity__start_date__gte': d}
#        
#    def get_lookup(self):
#        d = self._get_date()
#        return {'entity__opportunity__start_date__lte': d,
#                'entity__opportunity__end_date__gte': d, }
        

class ContactsImportSearchForm(SearchFieldForm):
    _name = 'contact_import'
    _label = _(u'Import')
    
    def __init__(self, *args, **kwargs):
        super(ContactsImportSearchForm, self).__init__(*args, **kwargs)
        qs = models.ContactsImport.objects.order_by('name') 
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return {'imported_by': self._value}

class ContactsByUpdateDate(TwoDatesForm):
    _name = 'contacts_by_update_date'
    _label = _(u'Contacts by update date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return Q(modified__gte=dt1, modified__lte=dt2)
    
class ContactsByCreationDate(TwoDatesForm):
    _name = 'contacts_by_creation_date'
    _label = _(u'Contacts by creation date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return Q(created__gte=dt1, created__lte=dt2)
    
class EntitiesByUpdateDate(TwoDatesForm):
    _name = 'entities_by_update_date'
    _label = _(u'Entities by update date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return Q(entity__modified__gte=dt1, entity__modified__lte=dt2)
    
class EntitiesByCreationDate(TwoDatesForm):
    _name = 'entities_by_creation_date'
    _label = _(u'Entities by creation date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return Q(entity__created__gte=dt1, entity__created__lte=dt2)
    
class ContactsAndEntitiesByChangeDate(TwoDatesForm):
    _name = 'contacts_and_entities_by_change_date'
    _label = _(u'Contacts and entities by change date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return Q(modified__gte=dt1, modified__lte=dt2) | Q(created__gte=dt1, created__lte=dt2) | \
            Q(entity__modified__gte=dt1, entity__modified__lte=dt2) | \
            Q(entity__created__gte=dt1, entity__created__lte=dt2)
        
class ContactsRelationshipByType(SearchFieldForm):
    _name = 'contacts_by_relationship_type'
    _label = _(u'Relationship type')
    
    def __init__(self, *args, **kwargs):
        super(ContactsRelationshipByType, self).__init__(*args, **kwargs)
        relationship_types = []
        for r in models.RelationshipType.objects.all():
            relationship_types.append((r.id, r.name))
            if r.reverse:
                relationship_types.append((-r.id, r.reverse))
        field = forms.CharField(label=self._label, widget=forms.Select(choices=relationship_types))
        self._add_field(field)
        
    def get_lookup(self):
        relationship_ids = []
        value, is_reverse = int(self._value), False
        if value<0:
            value, is_reverse = -value, True
        t = models.RelationshipType.objects.get(id=value)
        for r in models.Relationship.objects.filter(relationship_type__id=t.id):
            if t.reverse:
                if is_reverse:
                    relationship_ids.append(r.contact2.id)
                else:
                    relationship_ids.append(r.contact1.id)
            else:
                relationship_ids += [r.contact1.id, r.contact2.id]
        relationship_ids = list(set(relationship_ids))  
        return Q(id__in=(relationship_ids))
    
class ContactsRelationshipByDate(TwoDatesForm):
    _name = 'contacts_by_relationship_dates'
    _label = _(u'Relationship dates')
        
    def get_lookup(self):
        relationship_ids = []
        dt1, dt2 = self._get_dates()
        dt2 = dt2 + timedelta(1)
        for r in models.Relationship.objects.filter(created__gte=dt1, created__lt=dt2):
            relationship_ids = [r.contact1.id, r.contact2.id]
        relationship_ids = list(set(relationship_ids))  
        return Q(id__in=(relationship_ids))
    
class ContactWithCustomField(SearchFieldForm):
    _name = 'contact_with_custom_field'
    _label = _(u'Contacts with custom field')
    
    def __init__(self, *args, **kwargs):
        super(ContactWithCustomField, self).__init__(*args, **kwargs)
        custom_fields = []
        for cf in models.CustomField.objects.filter(model=models.CustomField.MODEL_CONTACT):
            custom_fields.append((cf.id, cf.label))
        field = forms.CharField(label=self._label, widget=forms.Select(choices=custom_fields))
        self._add_field(field)
        
    def get_lookup(self):
        value = int(self._value)
        cf = models.CustomField.objects.get(id=value, model=models.CustomField.MODEL_CONTACT)
        return Q(contactcustomfieldvalue__custom_field=cf)

class EntityWithCustomField(SearchFieldForm):
    _name = 'entity_with_custom_field'
    _label = _(u'Entities with custom field')
    
    def __init__(self, *args, **kwargs):
        super(EntityWithCustomField, self).__init__(*args, **kwargs)
        custom_fields = []
        for cf in models.CustomField.objects.filter(model=models.CustomField.MODEL_ENTITY):
            custom_fields.append((cf.id, cf.label))
        field = forms.CharField(label=self._label, widget=forms.Select(choices=custom_fields))
        self._add_field(field)
        
    def get_lookup(self):
        value = int(self._value)
        cf = models.CustomField.objects.get(id=value, model=models.CustomField.MODEL_ENTITY)
        return Q(entity__entitycustomfieldvalue__custom_field=cf)
    
class SortContacts(SearchFieldForm):
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
    
    def _sort_by_name(self, c):
        x = u"{0}".format(c.lastname, c.firstname) if c.entity.is_single_contact else c.entity.name
        return x.upper()
    
    def _sort_by_contact(self, c):
        x = u"{0} {1}".format(c.lastname, c.firstname)
        return x.upper()
    
    def _sort_by_entity(self, c):
        x = u"B" if c.entity.is_single_contact else u"A"
        y = self._sort_by_name(c)
        z = u"{0}".format(c.lastname, c.firstname) if not c.entity.is_single_contact else u""
        return (x, y, z)
    
    def _sort_by_zipcode(self, c):
        country = c.get_country()
        x = c.get_zip_code or u'?'
        city = c.get_city
        if not city:
            v = "C"
            w = y = "?"
        else:
            v = u"A" if ((not country) or self.default_country.id == country.id) else u"B"
            w = country.name if country else self.default_country.name
            y = city.name
        z = self._sort_by_name(c)
        return (v, w, x, y, z)
    
    def get_queryset(self, qs):
        return qs
    
    def global_post_process(self, contacts):
        callback = getattr(self, '_sort_by_{0}'.format(self._value), None)
        return sorted(contacts, key=callback)
