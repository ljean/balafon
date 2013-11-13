# -*- coding: utf-8 -*-

import floppyforms as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings
from django.contrib.auth.models import User
from sanza.Crm import models
from sanza.Crm.widgets import CityAutoComplete, EntityAutoComplete, OpportunityAutoComplete, ContactAutoComplete
from sanza.Crm.settings import get_default_country, NO_ENTITY_TYPE
from datetime import datetime, date
from form_utils.forms import BetterModelForm, BetterForm
from djaloha.widgets import AlohaInput
from django.utils import timezone

class AddEntityToGroupForm(forms.Form):
    group_name = forms.CharField(label=_(u"Group name"),
        widget=forms.TextInput(attrs={'size': 70, 'placeholder': _(u'start typing name and choose if exists')})
    )
    
    def __init__(self, entity, *args, **kwargs):
        self.entity = entity
        super(AddEntityToGroupForm, self).__init__(*args, **kwargs)
    
    def clean_group_name(self):
        name = self.cleaned_data['group_name']
        if models.Group.objects.filter(name=name, entities__id=self.entity.id).count() > 0:
            raise ValidationError(_(u"The entity already belong to group {0}").format(name))
        return name
    
class AddContactToGroupForm(forms.Form):
    group_name = forms.CharField(label=_(u"Group name"),
        widget=forms.TextInput(attrs={'size': 70, 'placeholder': _(u'start typing name and choose if exists')})
    )
    
    def __init__(self, contact, *args, **kwargs):
        self.contact = contact
        super(AddContactToGroupForm, self).__init__(*args, **kwargs)
    
    def clean_group_name(self):
        name = self.cleaned_data['group_name']
        if models.Group.objects.filter(name=name, contacts__id=self.contact.id).count() > 0:
            raise ValidationError(_(u"The contact already belong to group {0}").format(name))
        return name

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ('name', 'description', 'subscribe_form', 'entities', 'contacts')
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
        try:
            css = {
                'all': (settings.ADMIN_MEDIA_PREFIX+'css/widgets.css',)
            }
        except AttributeError:
            css = {
                'all': (settings.STATIC_URL+'admin/css/widgets.css',)
            }
        
    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance and not self.instance.id:
            if models.Group.objects.filter(name=name).exclude(id=self.instance.id).count()>0:
                raise ValidationError(_(u"A group with this name already exists"))
        return name
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(EditGroupForm, self).__init__(*args, **kwargs)
        
        self.fields['entities'] = forms.ModelMultipleChoiceField(
            required=False,
            queryset=models.Entity.objects.all(),
            widget=FilteredSelectMultiple(_(u"entities"), False)
        )
        
        self.fields['contacts'] = forms.ModelMultipleChoiceField(
            required=False,
            queryset=models.Contact.objects.all(),
            widget=FilteredSelectMultiple(_(u"contacts"), False)
        )

class _CityBasedForm(object):
    def _get_city_parent(self, city):
        parent = city.parent
        while parent:
            country = parent
            parent = parent.parent
        return country
    
    def _post_init(self, *args, **kwargs):
        self.country_id = 0
        if len(args):
            try:
                self.country_id = int(args[0]["country"])
            except KeyError:
                pass
        if not self.country_id:
            cn = get_default_country()
            try:
                default_country = models.Zone.objects.get(name=cn, parent__isnull=True)
            except models.Zone.DoesNotExist:
                try:
                    zt = models.ZoneType.objects.get(type="country")
                except models.ZoneType.DoesNotExist:
                    zt = models.ZoneType.objects.create(type="country", name=u"Country")
                default_country = models.Zone.objects.create(name=cn, parent=None, type=zt)
            self.country_id = default_country.id
            
        self.fields['city'].widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
        
        self.fields['country'].choices = [(0, '')]+[(z.id, z.name) for z in models.Zone.objects.filter(parent__isnull=True).order_by('name')]
        try:
            city = getattr(kwargs.get('instance'), 'city', 0)
            if city:
                self.fields['country'].initial = self._get_city_parent(city).id    
        except:
            pass
    
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
                except (ValueError, TypeError):
                    pass

                zip_code = self.cleaned_data['zip_code']
                
                try:
                    country_id = int(self.cleaned_data.get('country')) or self.country_id
                except (ValueError, TypeError):
                    country_id = self.country_id
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
                raise ValidationError(msg)

class ModelFormWithCity(BetterModelForm, _CityBasedForm):
    country = forms.ChoiceField(required=False, label=_(u'Country'))
    
    def __init__(self, *args, **kwargs):
        super(ModelFormWithCity, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)
        
class FormWithCity(BetterForm, _CityBasedForm):
    country = forms.ChoiceField(required=False, label=_(u'Country'))
    zip_code = forms.CharField(required=False, label=_(u'zip code'))
    city = forms.CharField(required = False, label=_(u'City'))
    
    def __init__(self, *args, **kwargs):
        super(BetterForm, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)
    
class EntityForm(ModelFormWithCity):
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        
        if NO_ENTITY_TYPE:
            self.fields["type"].widget = forms.HiddenInput()
        
    class Meta:
        model = models.Entity
        exclude = ('imported_by', 'is_single_contact')
        fieldsets = [
            ('name', {'fields': ['type', 'name', 'description', 'relationship_date'], 'legend': _(u'Name')}),
            ('web', {'fields': ['website', 'email', 'phone', 'fax'], 'legend': _(u'Phone / Web')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
            ('notes', {'fields': ['notes'], 'legend': _(u'Notes')}),
            ('logo', {'fields': ['logo'], 'legend': _(u'Logo')}),
        ]
        
    def clean_logo(self):
        logo = self.cleaned_data["logo"]
        instance = self.instance
        if not instance:
            instance = ""
            try:
                instance.id = models.Entity.objects.latest('id').id
            except models.Entity.DoesNotExist:
                instance.id = 1
        target_name = models.get_entity_logo_dir(instance, logo)
        if len(target_name) >= models.Entity._meta.get_field('logo').max_length:
            raise ValidationError(_(u"The file name is too long"))
        return logo
    

class ContactForm(ModelFormWithCity):
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Meta:
        model = models.Contact
        exclude=('uuid', 'same_as', 'imported_by', 'entity', 'relationships')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'enter notes about the contact'), 'cols':'72'}),
            'role': forms.SelectMultiple(attrs={
                'class': 'chzn-select', 'data-placeholder': _(u'Select roles'), 'style': "width:600px;"}),
        }
        fieldsets = [
            ('name', {'fields': ['gender', 'lastname', 'firstname', 'nickname', 'birth_date'], 'legend': _(u'Name')}),
            ('job', {'fields': ['title', 'role', 'job'], 'legend': _(u'Job')}),
            ('web', {'fields': ['email', 'phone', 'mobile'], 'legend': _(u'Phone / Web')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
            ('relationship', {'fields': ['main_contact', 'email_verified', 'accept_newsletter', 'accept_3rdparty', 'accept_notifications', 'has_left'], 'legend': _(u'Relationship')}),
            ('notes', {'fields': ['notes'], 'legend': _(u'Notes')}),
            ('photo', {'fields': ['photo'], 'legend': _(u'Photo')}),
        ]
        
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["role"].help_text = ""
        
        if not 'sanza.Profile' in settings.INSTALLED_APPS:
            self.fields["accept_notifications"].widget = forms.HiddenInput()
        
        self.fields["email_verified"].widget.attrs['disabled'] = "disabled"

    def clean_photo(self):
        photo = self.cleaned_data["photo"]
        instance = self.instance
        if not instance:
            instance = ""
            try:
                instance.id = models.Contact.objects.latest('id').id
            except models.Contact.DoesNotExist:
                instance.id = 1
        target_name = models.get_contact_photo_dir(instance, photo)
        if len(target_name) >= models.Contact._meta.get_field('photo').max_length:
            raise ValidationError(_(u"The file name is too long"))
        return photo


class EntityTypeForm(forms.ModelForm):
    
    class Meta:
        model = models.EntityType

class EntityRoleForm(forms.ModelForm):
    
    class Meta:
        model = models.EntityRole

class ActionForm(BetterModelForm):
    date = forms.DateField(label=_(u"planned date"), required=False, widget=forms.TextInput())
    time = forms.TimeField(label=_(u"planned time"), required=False)
    
    class Meta:
        model = models.Action
        fields = ('type', 'subject', 'date', 'time', 'status', 'in_charge', 'contact', 'opportunity', 'detail',
            'priority', 'amount', 'number', 'done', 'display_on_board', 'planned_date', 'archived')
        fieldsets = [
            ('name', {'fields': ['subject', 'type', 'status', 'date', 'time', 'planned_date', 'in_charge', 'opportunity'], 'legend': _(u'Summary')}),
            ('details', {'fields': ['done', 'priority', 'contact', 'amount', 'number', 'detail'], 'legend': _(u'Details')}),
            ('address', {'fields': ['display_on_board', 'archived'], 'legend': _(u'Display')}),
        ]

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        instance = kwargs.get('instance', None)
        super(ActionForm, self).__init__(*args, **kwargs)
        if entity and not entity.is_single_contact:
            self.fields['contact'].queryset = models.Contact.objects.filter(entity=entity)
        else:
            self.fields['contact'].widget = forms.HiddenInput()
        
        if instance and instance.id and instance.type and instance.type.allowed_status.count():
            default_status = instance.type.default_status
            choices = [] if default_status else [('', "---------")]
            self.fields['status'].choices = choices + [(s.id, s.name) for s in instance.type.allowed_status.all()]
            #self.fields['status'].initial = default_status.id if default_status else None
        #else:
        #    self.fields['status'].queryset = forms.HiddenInput()
        
        if instance and instance.entity:
            self.fields['contact'].widget = forms.Select(choices=[(x.id, x.fullname) for x in instance.entity.contact_set.all()])
        else:
            self.fields['contact'].widget = forms.HiddenInput()
            
        if 'opportunity' in self.fields:
            self.fields['opportunity'].queryset = models.Opportunity.objects.filter(ended=False)
            self.fields['opportunity'].widget = OpportunityAutoComplete(attrs={'placeholder': _(u'Enter the name of an opportunity'), 'size': '80'})
        
        self.fields['detail'].widget = forms.Textarea(attrs={'placeholder': _(u'enter details'), 'cols':'72'})
        self.fields['planned_date'].widget = forms.HiddenInput()
        dt = self.instance.planned_date if self.instance else self.fields['planned_date'].initial
        if dt:
            self.fields["date"].initial = dt.date()
            utc_dt = dt.replace(tzinfo=timezone.utc)
            loc_dt = utc_dt.astimezone(timezone.get_current_timezone())
            self.fields["time"].initial = loc_dt.time()
        
    def clean_status(self):
        t = self.cleaned_data['type']
        s = self.cleaned_data['status']
        if t:
            allowed_status = ([] if t.default_status else [None]) + list(t.allowed_status.all())
            if len(allowed_status) > 0 and not (s in allowed_status):
                raise ValidationError(_(u"This status can't not be used for this action type"))
        return s
    
    def clean_planned_date(self):
        d = self.cleaned_data["date"]
        t = self.cleaned_data.get("time", None)
        if d:
            dt = datetime.combine(d, t or datetime.min.time())
            return dt
        return None
    
class OpportunityForm(BetterModelForm):
    class Meta:
        model = models.Opportunity
        fields=('name', 'status', 'type', 'ended', 'display_on_board', 'detail')
        
        fieldsets = [
                ('name', {'fields': ['name', 'type', 'status', 'detail'], 'legend': _(u'Summary')}),
                ('address', {'fields': ['display_on_board', 'ended'], 'legend': _(u'Display')}),
            ]

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

class SelectContactForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        super(SelectContactForm, self).__init__(*args, **kwargs)
        if choices:
            widget = forms.Select(choices=[(x.id, x.fullname) for x in choices])
            self.fields["contact"] = forms.IntegerField(label=_(u"Contact"), widget=widget)
        else:
            widget = ContactAutoComplete(
                attrs={'placeholder': _(u'Enter the name of a contact'), 'size': '50', 'class': 'colorbox'})
            self.fields["contact"] = forms.CharField(label=_(u"Contact"), widget=widget)
    
    def clean_contact(self):
        try:
            contact_id = int(self.cleaned_data["contact"])
            return models.Contact.objects.get(id=contact_id)
        except (ValueError, models.Contact.DoesNotExist):
            raise ValidationError(_(u"The contact does'nt exist"))

    
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
        
        
class AddRelationshipForm(forms.Form):
    relationship_type = forms.IntegerField(label=_(u"relationship type"))
    contact2 = forms.CharField(label=_(u"Contact"))
    
    def __init__(self, contact1, *args, **kwargs):
        super(AddRelationshipForm, self).__init__(*args, **kwargs)
        
        self.contact1 = contact1
        
        relationship_types = []
        for r in models.RelationshipType.objects.all():
            relationship_types.append((r.id, r.name))
            if r.reverse:
                relationship_types.append((-r.id, r.reverse))
        self.fields["relationship_type"].widget = forms.Select(choices=relationship_types) 
        
        widget = ContactAutoComplete(
            attrs={'placeholder': _(u'Enter the name of a contact'), 'size': '50', 'class': 'colorbox'})
        self.fields["contact2"] = forms.CharField(label=_(u"Contact"), widget=widget)
        
    def clean_relationship_type(self):
        try:
            self.reversed_relation = False
            relationship_type = int(self.cleaned_data["relationship_type"])
            if relationship_type<0:
                self.reversed_relation = True
                relationship_type = -relationship_type
            return models.RelationshipType.objects.get(id=relationship_type)
        except ValueError:
            raise ValidationError(_(u"Invalid data"))
        except models.RelationshipType.DoesNotExist:
            raise ValidationError(_(u"Relationship type does not exist"))
        
    def clean_contact2(self):
        try:
            contact2 = int(self.cleaned_data["contact2"])
            return models.Contact.objects.get(id=contact2)
        except ValueError:
            raise ValidationError(_(u"Invalid data"))
        except models.Contact.DoesNotExist:
            raise ValidationError(_(u"Contact does not exist"))
        
    def save(self):
        if self.reversed_relation:
            contact1 = self.cleaned_data["contact2"]
            contact2 = self.contact1
        else:
            contact1 = self.contact1
            contact2 = self.cleaned_data["contact2"]
        
        rt = self.cleaned_data["relationship_type"]
        return models.Relationship.objects.create(
                contact1=contact1, contact2=contact2, relationship_type=rt)    
        
class ActionDoneForm(forms.ModelForm):
    
    class Meta:
        model = models.Action
        fields = ['detail']
        widgets = {
            'detail': forms.Textarea(attrs={'placeholder': _(u'give details bout the action'), 'cols':'72'})
        }
    
    
class CustomFieldForm(forms.Form):
    
    def __init__(self, instance, *args, **kwargs):
        super(CustomFieldForm, self).__init__(*args, **kwargs)
        self._instance = instance
        model_type = self._get_model_type()
        custom_fields = models.CustomField.objects.filter(model=model_type)
        for f in custom_fields:
            self.fields[f.name] = forms.CharField(required=False, label=f.label)
            if f.widget:
                self.fields[f.name].widget.attrs = {'class': f.widget}
            if len(args)==0: #No Post
                self.fields[f.name].initial = getattr(instance, 'custom_field_'+f.name, '')
                
    def save(self, *args, **kwargs):
        for f in self.fields:
            model_type = self._get_model_type()
            cf = models.CustomField.objects.get(name = f, model=model_type)
            cfv = self._create_custom_field_value(cf)
            cfv.value = self.cleaned_data[f]
            cfv.save()
        return self._instance

class EntityCustomFieldForm(CustomFieldForm):
        
    def _get_model_type(self):
        return models.CustomField.MODEL_ENTITY
    
    @staticmethod
    def model():
        return models.Entity
    
    def _create_custom_field_value(self, cf):
        cfv, _new = models.EntityCustomFieldValue.objects.get_or_create(entity = self._instance, custom_field = cf)
        return cfv
            
class ContactCustomFieldForm(CustomFieldForm):
    
    def _get_model_type(self):
        return models.CustomField.MODEL_CONTACT
    
    def _create_custom_field_value(self, cf):
        cfv, _new = models.ContactCustomFieldValue.objects.get_or_create(contact = self._instance, custom_field = cf)
        return cfv
    
    @staticmethod
    def model():
        return models.Contact


class ContactsImportForm(forms.ModelForm):
    
    class Meta:
        model = models.ContactsImport
        exclude = ('imported_by', )
        
    class Media:
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )
    
    def __init__(self, *args, **kwargs):
        super(ContactsImportForm, self).__init__(*args, **kwargs)
        
        self.fields['groups'].widget.attrs = {
            'class': 'chzn-select',
            'data-placeholder': _(u'The created entities will be added to the selected groups'),
            'style': "width:600px;"
        }
        self.fields['groups'].help_text = ''
        
    def clean_separator(self):
        if len(self.cleaned_data["separator"]) != 1:
            raise ValidationError(_(u'Invalid separator {0}').format(self.cleaned_data["separator"]))
        return self.cleaned_data["separator"]
        
        
class ContactsImportConfirmForm(ContactsImportForm):
    default_department = forms.ChoiceField(required=False, label=_(u'Default department'),
        choices=([('', '')]+[(x.code, x.name) for x in models.Zone.objects.filter(type__type='department')]),
        help_text=_(u'The city in red will be created with this department as parent'))
    
    class Meta(ContactsImportForm.Meta):
        exclude = ('imported_by', 'import_file', 'name')
    
    def clean_default_department(self):
        code = self.cleaned_data['default_department']
        if code:
            if not models.Zone.objects.filter(code=self.cleaned_data['default_department']):
                raise ValidationError(_(u'Please enter a valid code'))
            return self.cleaned_data['default_department']
        else:
            return None
        

from coop_cms.forms import AlohaEditableModelForm
class ActionDocumentForm(AlohaEditableModelForm):
    
    class Meta:
        model = models.ActionDocument
        fields = ('content',)
        