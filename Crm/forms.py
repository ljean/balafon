# -*- coding: utf-8 -*-

import floppyforms as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings
from django.contrib.auth.models import User
from sanza.Crm import models
from sanza.Crm.widgets import CityAutoComplete, EntityAutoComplete, OpportunityAutoComplete
from sanza.Crm.settings import get_default_country
from datetime import datetime

class AddEntityToGroupForm(forms.Form):
    group_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _(u'name of a group')})
    )
    
    def __init__(self, entity, *args, **kwargs):
        self.entity = entity
        super(AddEntityToGroupForm, self).__init__(*args, **kwargs)
    
    def clean_group_name(self):
        name = self.cleaned_data['group_name']
        if models.Group.objects.filter(name=name, entities__id=self.entity.id).count() > 0:
            raise ValidationError(_(u"The entity already belong to group {0}").format(name))
        return name

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        widgets = {
            'description': forms.TextInput(
                attrs={
                    'placeholder': _(u'Enter a description for your group'),
                    'size': '80',
                }
            ),
            'name': forms.TextInput(
                attrs={
                    'placeholder': _(u'Enter a name for your group'),
                    'size': '80',
                }
            ),
        }
    
    class Media:
        css = {
            'all': (settings.ADMIN_MEDIA_PREFIX+'css/widgets.css',)
        }
        
    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance and not self.instance.id:
            if models.Group.objects.filter(name=name).count()>0:
                raise ValidationError(_(u"A group with this name already exists"))
        return name
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(EditGroupForm, self).__init__(*args, **kwargs)
        
        self.fields['entities'] = forms.ModelMultipleChoiceField(
            queryset=models.Entity.objects.all(),
            widget=FilteredSelectMultiple(_(u"entities"), False)
        )
        
class ModelFormWithCity(forms.ModelForm):
    country = forms.ChoiceField(required=False, label=_(u'Country'))
    
    def __init__(self, *args, **kwargs):
        super(ModelFormWithCity, self).__init__(*args, **kwargs)
        
        if len(args):
            self.country_id = int(args[0]["country"])
        
        self.fields['country'].choices = [(0, '')]+[(z.id, z.name) for z in models.Zone.objects.filter(parent__isnull=True).order_by('name')]
        try:
            city = getattr(kwargs.get('instance'), 'city', 0)
            if city:
                self.fields['country'].initial = self._get_city_parent(city).id    
        except:
            pass
        
    def _get_city_parent(self, city):
        parent = city.parent
        while parent:
            country = parent
            parent = parent.parent
        return country
    
    def _get_country(self, id):
        if id:
            return models.Zone.objects.get(id=id, parent__isnull=True)
        else:
            cn = get_default_country()
            return models.Zone.objects.get(name=cn, parent__isnull=True)
        
    def clean_city(self):
        city = self.cleaned_data['city']
        if isinstance(city, models.City):
            return city
        else:
            try:
                if not city:
                    return None
                try:
                    id = int(city)
                    return models.City.objects.get(id=id)
                except ValueError:
                    pass

                zip_code = self.cleaned_data['zip_code']
                country_id = self.cleaned_data.get('country') or self.country_id
                country = self._get_country(country_id)
                default_country = models.Zone.objects.get(name=get_default_country(), parent__isnull=True)
                if country != default_country:
                    city, _is_new = models.City.objects.get_or_create(name=city, parent=country)
                else:
                    if len(zip_code)<2:
                        raise ValidationError(_(u'You must enter a valid zip code for selecting a new city'))
                    dep = models.Zone.objects.get(code=zip_code[:2])
                    city, _is_new = models.City.objects.get_or_create(name=city, parent=dep)
                return city
            except ValidationError:
                raise
            except Exception, msg:
                raise
                raise ValidationError(msg)
    
class EntityForm(ModelFormWithCity):
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Meta:
        model = models.Entity

class ContactForm(ModelFormWithCity):
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Meta:
        model = models.Contact
        exclude=('uuid', 'same_as')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'enter notes about the contact'), 'cols':'72'}),
            'role': forms.SelectMultiple(attrs={
                'class': 'chzn-select', 'data-placeholder': _(u'Select roles'), 'style': "width:600px;"}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["role"].help_text = ""

class MiniContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields=('gender', 'firstname', 'lastname', 'title', 'role', 'phone', 'mobile', 'email', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'enter notes about the contact'), 'cols':'72'}),
            'role': forms.SelectMultiple(attrs={
                'class': 'chzn-select', 'data-placeholder': _(u'Select roles'), 'style': "width:600px;"}),
        }

    def __init__(self, *args, **kwargs):
        super(MiniContactForm, self).__init__(*args, **kwargs)
        self.fields["role"].help_text = ""


class EntityTypeForm(forms.ModelForm):
    
    class Meta:
        model = models.EntityType

class RelationshipForm(forms.ModelForm):
    
    class Meta:
        model = models.Relationship

class EntityRoleForm(forms.ModelForm):
    
    class Meta:
        model = models.EntityRole

class ActivitySectorForm(forms.ModelForm):
    
    class Meta:
        model = models.ActivitySector

class ActionForm(forms.ModelForm):
    date = forms.DateField(label=_(u"planned date"), required=False)
    time = forms.TimeField(label=_(u"planned time"), required=False)
    
    class Meta:
        model = models.Action
        fields = ('subject', 'date', 'time', 'type', 'in_charge', 'contact', 'opportunity', 'detail',
            'priority', 'done', 'display_on_board', 'planned_date')

    def __init__(self, entity, *args, **kwargs):
        super(ActionForm, self).__init__(*args, **kwargs)
        if entity:
            self.fields['contact'].queryset = models.Contact.objects.filter(entity=entity)
        self.fields['opportunity'].queryset = models.Opportunity.objects.filter(ended=False)
        self.fields['opportunity'].widget = OpportunityAutoComplete(attrs={'placeholder': _(u'Enter the name of an opportunity'), 'size': '80'})
        
        self.fields['detail'].widget = forms.Textarea(attrs={'placeholder': _(u'enter details'), 'cols':'72'})
        self.fields['planned_date'].widget = forms.HiddenInput()
        dt = self.instance.planned_date if self.instance else self.fields['planned_date'].initial
        if dt:
            self.fields["date"].initial = dt.date()
            self.fields["time"].initial = dt.time()
        
        
    def clean_planned_date(self):
        d = self.cleaned_data["date"]
        t = self.cleaned_data.get("time", None)
        if d:
            return datetime.combine(d, t or datetime.min.time())
        return None

class ActionForContactsForm(ActionForm):
    contacts = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = models.Action
        fields = ('date', 'time', 'type', 'subject', 'in_charge', 'opportunity', 'detail',
            'priority', 'planned_date', 'contacts')
        
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        super(ActionForContactsForm, self).__init__(None, *args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
        self.fields['opportunity'].widget = OpportunityAutoComplete(
            attrs={'placeholder': _(u'Enter the name of an opportunity'), 'size': '80', 'class': 'colorbox'})
        
    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        return models.Contact.objects.filter(id__in=ids)
    
class OpportunityForm(forms.ModelForm):
    class Meta:
        model = models.Opportunity
        fields=('name', 'status', 'type', 'start_date', 'end_date', 'ended', 'display_on_board', 'probability', 'amount', 'detail')

    def __init__(self, *args, **kwargs):
        super(OpportunityForm, self).__init__(*args, **kwargs)
        self.fields['detail'].widget = forms.Textarea(attrs={'placeholder': _(u'enter details'), 'cols':'72'})
        
class OpportunityStatusForm(forms.ModelForm):
    
    class Meta:
        model = models.OpportunityStatus

class ActionTypeForm(forms.ModelForm):
    
    class Meta:
        model = models.ActionType

class SelectEntityForm(forms.Form):
    entity = forms.CharField(label=_(u"Entity"))
    
    def __init__(self, *args, **kwargs):
        super(SelectEntityForm, self).__init__(*args, **kwargs)
        self.fields["entity"].widget = EntityAutoComplete(
            attrs={'placeholder': _(u'Enter the name of an entity'), 'size': '50', 'class': 'colorbox'})

    def clean_entity(self):
        try:
            entity_id = int(self.cleaned_data["entity"])
            return models.Entity.objects.get(id=entity_id)
        except (ValueError, models.Entity.DoesNotExist):
            raise ValidationError(_(u"The entity does'nt exist"))
    
class SameAsForm(forms.Form):
    contact = forms.IntegerField(label=_(u"Contact"))
    
    def __init__(self, contact, *args, **kwargs):
        super(SameAsForm, self).__init__(*args, **kwargs)
        self._same_as = [(c.id, u"{0} - {1}".format(unicode(c), c.entity))
            for c in models.Contact.objects.filter(
                lastname__iexact=contact.lastname, firstname__iexact=contact.firstname
            ).exclude(id=contact.id)
        ]
        self.fields["contact"].widget = forms.Select(choices=self._same_as)
        
    def clean_contact(self):
        contact_id = self.cleaned_data["contact"]
        try:
            if contact_id not in [x[0] for x in self._same_as]:
                raise ValidationError(_(u"Invalid contact"))
            return models.Contact.objects.get(id=contact_id)
        except models.Contact.DoesNotExist:
            raise ValidationError(_(u"Contact does not exist"))
        
        
class ActionDoneForm(forms.ModelForm):
    
    class Meta:
        model = models.Action
        fields = ['detail']
        widgets = {
            'detail': forms.Textarea(attrs={'placeholder': _(u'give details bout the action'), 'cols':'72'})
        }
    
    
    