# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Search.forms import SearchFieldForm, TwoDatesForm, YesNoSearchFieldForm
from django.utils.translation import ugettext as _
from sanza.Crm import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from sanza.Crm.settings import get_default_country
from django.contrib.auth.models import User
from django.db.models import Q
from sanza.Crm.widgets import CityNoCountryAutoComplete, GroupAutoComplete

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

class CitySearchForm(SearchFieldForm):
    _name = 'city'
    _label = _(u'City')
    
    def __init__(self, *args, **kwargs):
        super(CitySearchForm, self).__init__(*args, **kwargs)
        qs = models.City.objects.order_by('name') 
        field = forms.ModelChoiceField(qs, label=self._label,
            widget = CityNoCountryAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
        )
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__city__id': self._value}
        
class ZoneSearchForm(SearchFieldForm):
    def __init__(self, *args, **kwargs):
        super(ZoneSearchForm, self).__init__(*args, **kwargs)
        qs = models.Zone.objects.filter(type__type=self._name).order_by('code', 'name') 
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
class DepartmentSearchForm(ZoneSearchForm):
    _name = 'department'
    _label = _(u'Department')
        
    def get_lookup(self):
        return Q(entity__city__parent__id=self._value) | Q(city__parent__id=self._value)
        
class RegionSearchForm(ZoneSearchForm):
    _name = 'region'
    _label = _(u'Region')
        
    def get_lookup(self):
        return Q(entity__city__parent__parent__id=self._value) | Q(city__parent__parent__id=self._value)
        
class CountrySearchForm(ZoneSearchForm):
    _name = 'country'
    _label = _(u'Country')
        
    def get_lookup(self):
        default_country_name = get_default_country()
        default_country = models.Zone.objects.get(name=default_country_name, type__type=self._name)
        if int(self._value) == default_country.id:
            return Q(entity__city__parent__type__type='department') | Q(city__parent__type__type='department')
        else:
            return Q(entity__city__parent__id=self._value) | Q(city__parent__id=self._value)
            
class ActionInProgressForm(YesNoSearchFieldForm):
    _name = 'action'
    _label = _(u'Action in progress')
        
    def get_lookup(self):
        if self.is_yes():
            return {'entity__action__done': False}
    
    def get_exclude_lookup(self):
        return {'entity__action__done': False}
            
class ActionByDoneDate(TwoDatesForm):
    _name = 'action_by_done_date'
    _label = _(u'Action by done date')
        
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return {'entity__action__done_date__gte': dt1, 'entity__action__done_date__lte': dt2, }


class ActionByPlannedDate(TwoDatesForm):
    _name = 'action_by_planned_date'
    _label = _(u'Action by planned date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return {'entity__action__planned_date__gte': dt1,
                'entity__action__planned_date__lte': dt2, }

class ActionByUser(SearchFieldForm):
    _name = 'action_by_user'
    _label = _(u'Action by user')
    
    def __init__(self, *args, **kwargs):
        super(ActionByUser, self).__init__(*args, **kwargs)
        choices = [(u.id, unicode(u)) for u in User.objects.all()]
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__action__in_charge': self._value}

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
    
    def __init__(self, *args, **kwargs):
        super(GroupSearchForm, self).__init__(*args, **kwargs)
        qs = models.Group.objects.all()
        try:
            qs = qs.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except:
            qs = qs.order_by('name')
        field = forms.ModelChoiceField(qs, label=self._label,
            widget = GroupAutoComplete(attrs={'placeholder': _(u'Enter part of the group name'), 'size': '80'}))
        self._add_field(field)
        
    def get_lookup(self):
        return Q(entity__group__id=self._value)

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
        pass
        
    def get_exclude_lookup(self):
        return {'entity__group__id': self._value}


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
        return {'entity__action__type': self._value}

class ActionNameSearchForm(SearchFieldForm):
    _name = 'action_name'
    _label = _(u'Action name')
    
    def __init__(self, *args, **kwargs):
        super(ActionNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched action')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__action__subject__icontains': self._value}

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

class OpportunityStatusSearchForm(SearchFieldForm):
    _name = 'opportunity_status'
    _label = _(u'Opportunity status')
    
    def __init__(self, *args, **kwargs):
        super(OpportunityStatusSearchForm, self).__init__(*args, **kwargs)
        qs = models.OpportunityStatus.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__opportunity__status': self._value,
                'entity__opportunity__ended': False}

class OpportunityNameSearchForm(SearchFieldForm):
    _name = 'opportunity_name'
    _label = _(u'Opportunity name')
    
    def __init__(self, *args, **kwargs):
        super(OpportunityNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched opportunity')}))
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__opportunity__name__icontains': self._value}

class NoOpportunityWithNameSearchForm(SearchFieldForm):
    _name = 'no_opportunity_with_name'
    _label = _(u'No opportunity with name')
    
    def __init__(self, *args, **kwargs):
        super(NoOpportunityWithNameSearchForm, self).__init__(*args, **kwargs)
        field = forms.CharField(label=self._label,
            widget=forms.TextInput(attrs={'placeholder': _(u'enter a part of the name of the searched opportunity')}))
        self._add_field(field)
        
    def get_lookup(self):
        pass
    
    def get_exclude_lookup(self):
        return {'entity__opportunity__name__icontains': self._value}

class OpportunityByEndDate(TwoDatesForm):
    _name = 'opportunity_by_end_date'
    _label = _(u'Opportunity by end date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return {'entity__opportunity__end_date__gte': dt1,
                'entity__opportunity__end_date__lte': dt2, }

class OpportunityByStartDate(TwoDatesForm):
    _name = 'opportunity_by_start_date'
    _label = _(u'Opportunity by start date')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        return {'entity__opportunity__start_date__gte': dt1,
                'entity__opportunity__start_date__lte': dt2, }

class OpportunityBetween(TwoDatesForm):
    _name = 'opportunity_between'
    _label = _(u'Opportunity between')
    
    def get_lookup(self):
        dt1, dt2 = self._get_dates()
        q_obj1 = Q(entity__opportunity__end_date__gte=dt1) & Q(entity__opportunity__start_date__lte=dt2) \
            & Q(entity__opportunity__end_date__isnull=False) & Q(entity__opportunity__start_date__isnull=False)
        
        q_obj2 = Q(entity__opportunity__end_date__isnull=True) & Q(entity__opportunity__start_date__lte=dt2) \
            & Q(entity__opportunity__start_date__gte=dt1)
        
        q_obj3 = Q(entity__opportunity__end_date__isnull=True) & Q(entity__opportunity__ended=False) \
            & Q(entity__opportunity__start_date__lte=dt1)
        
        q_obj4 = Q(entity__opportunity__start_date__isnull=True) & Q(entity__opportunity__end_date__gte=dt1) \
            & Q(entity__opportunity__end_date__lte=dt2)
        
        return q_obj1 | q_obj2 | q_obj3 | q_obj4
    
class NoOpportunityBetween(OpportunityBetween):
    _name = 'no_opportunity_between'
    _label = _(u'No opportunity between')
    
    def get_lookup(self):
        q_obj = super(NoOpportunityBetween, self).get_lookup()
        return ~q_obj
        
class OpportunityTypeSearchForm(SearchFieldForm):
    _name = 'opportunity_type'
    _label = _(u'Opportunity type')
    
    def __init__(self, *args, **kwargs):
        super(OpportunityTypeSearchForm, self).__init__(*args, **kwargs)
        qs = models.OpportunityType.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
        
    def get_lookup(self):
        return {'entity__opportunity__type': self._value}

class NoOpportunityOfTypeSearchForm(SearchFieldForm):
    _name = 'no_opportunity_of_type'
    _label = _(u'No opportunity of type')
    
    def __init__(self, *args, **kwargs):
        super(NoOpportunityOfTypeSearchForm, self).__init__(*args, **kwargs)
        qs = models.OpportunityType.objects.all()
        field = forms.ModelChoiceField(qs, label=self._label)
        self._add_field(field)
    
    def get_lookup(self):
        pass
        
    def get_exclude_lookup(self):
        return {'entity__opportunity__type': self._value}

class OpportunityInProgressForm(YesNoSearchFieldForm):
    _name = 'opportunity_in_progress'
    _label = _(u'Opportunity in progress')
    
    def get_lookup(self):
        if self.is_yes():
            return {'entity__opportunity__ended': False}
    
    def get_exclude_lookup(self):
        return {'entity__opportunity__ended': False}

class NoSameAsForm(YesNoSearchFieldForm):
    _name = 'no_same_as'
    _label = _(u'Allow same-as')
    
    def get_lookup(self):
        pass
    
    def get_exclude_lookup(self):
        pass
    
    def post_process(self, contacts):
        if self.is_yes():
            return contacts
        else:
            same_as = {}
            filtered_contacts = []
            for c in contacts:
                if c.same_as:
                    if not same_as.has_key(c.same_as.id):
                        same_as[c.same_as.id] = c.same_as
                        filtered_contacts.append(c)
                else:
                    filtered_contacts.append(c)
            return filtered_contacts

class OpportunityReminderForm(SearchFieldForm):
    _name = 'opp_reminder'
    _label = _(u'Opportunity reminder')
    
    def __init__(self, *args, **kwargs):
        super(OpportunityReminderForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label, initial='{0}'.format(date.today()),
            widget=forms.TextInput(attrs={"class": "datepicker"})
        )
        self._add_field(field)

    def _get_date(self):
        if self._value.find('-')>=0:
            d = [int(x) for x in self._value.split('-')]
        else:
            d = [int(x) for x in self._value.split('/')]
            d.reverse()
        return date(*d)
    
    def get_exclude_lookup(self):
        d = self._get_date()
        return {'entity__opportunity__start_date__gte': d}
        
    def get_lookup(self):
        d = self._get_date()
        return {'entity__opportunity__start_date__lte': d,
                'entity__opportunity__end_date__gte': d, }
        

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
