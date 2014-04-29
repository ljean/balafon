# -*- coding: utf-8 -*-

import floppyforms as forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.conf import settings
from django.contrib.auth.models import User
from sanza.Crm import models
from sanza.Crm.widgets import CityAutoComplete, EntityAutoComplete, OpportunityAutoComplete, ContactAutoComplete
from sanza.Crm.settings import NO_ENTITY_TYPE
from sanza.Crm.utils import get_default_country
from datetime import datetime, date
from form_utils.forms import BetterModelForm, BetterForm
from djaloha.widgets import AlohaInput
from django.utils import timezone
from coop_cms.bs_forms import Form as BsForm, ModelForm as BsModelForm, BootstrapableMixin

class BetterBsForm(BetterForm, BootstrapableMixin):
    class Media:
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )
        
    def __init__(self, *args, **kwargs):
        super(BetterBsForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()
        for field in self.fields.values():
            if field.widget.__class__.__name__ == forms.Select().__class__.__name__:
                klass = field.widget.attrs.get("class", "") 
                if not "chosen-select" in klass:
                    field.widget.attrs["class"] = klass + " chosen-select"

class BetterBsModelForm(BetterModelForm, BootstrapableMixin):
    class Media:
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )
        
    def __init__(self, *args, **kwargs):
        super(BetterBsModelForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()
        for field in self.fields.values():
            if field.widget.__class__.__name__ == forms.Select().__class__.__name__:
                klass = field.widget.attrs.get("class", "") 
                if not "chosen-select" in klass:
                    field.widget.attrs["class"] = klass + " chosen-select"

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
            raise ValidationError(ugettext(u"The entity already belong to group {0}").format(name))
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
            raise ValidationError(ugettext(u"The contact already belong to group {0}").format(name))
        return name

class EditGroupForm(BsModelForm):
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
                'all': (
                    settings.ADMIN_MEDIA_PREFIX+'css/widgets.css',
                    'css/bootstrap-transfer.css',
                )
            }
            js = (
                'js/bootstrap-transfer.js',
            )
        except AttributeError:
            css = {
                'all': (
                    settings.STATIC_URL+'admin/css/widgets.css',
                    'css/bootstrap-transfer.css',
                )
            }
            js = (
                'js/bootstrap-transfer.js',
            )
        
    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance and not self.instance.id:
            if models.Group.objects.filter(name=name).exclude(id=self.instance.id).count()>0:
                raise ValidationError(ugettext(u"A group with this name already exists"))
        return name
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(EditGroupForm, self).__init__(*args, **kwargs)
        
        widget = forms.SelectMultiple(attrs={'class': "bootstrap-transfer"})
        
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
            self.country_id = get_default_country().id
            
        self.fields['city'].widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
        
        self.fields['country'].choices = [(0, '')]+[(z.id, z.name) for z in models.Zone.objects.filter(parent__isnull=True).order_by('name')]
        try:
            city = getattr(kwargs.get('instance'), 'city', 0)
            if city:
                self.fields['country'].initial = self._get_city_parent(city).id    
        except:
            pass
    
    def _get_country(self, country_id):
        if country_id:
            return models.Zone.objects.get(id=country_id, parent__isnull=True, type__type="country")
        else:
            return get_default_country()
        
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
                default_country = get_default_country()
                if country != default_country:
                    city, _is_new = models.City.objects.get_or_create(name=city, parent=country)
                else:
                    if len(zip_code)<2:
                        raise ValidationError(ugettext(u'You must enter a valid zip code for selecting a new city'))
                    dep = models.Zone.objects.get(code=zip_code[:2])
                    city, _is_new = models.City.objects.get_or_create(name=city, parent=dep)
                return city
            except ValidationError:
                raise
            except Exception, msg:
                raise ValidationError(msg)

class ModelFormWithCity(BetterBsModelForm, _CityBasedForm):
    country = forms.ChoiceField(required=False, label=_(u'Country'))
    
    def __init__(self, *args, **kwargs):
        super(ModelFormWithCity, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)
        
class FormWithCity(BetterBsForm, _CityBasedForm):
    country = forms.ChoiceField(required=False, label=_(u'Country'))
    zip_code = forms.CharField(required=False, label=_(u'zip code'))
    city = forms.CharField(required = False, label=_(u'City'))
    
    def __init__(self, *args, **kwargs):
        super(FormWithCity, self).__init__(*args, **kwargs)
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
        exclude = ('imported_by', 'is_single_contact', 'notes')
        fieldsets = [
            ('name', {'fields': ['type', 'name', 'description', 'relationship_date'], 'legend': _(u'Name')}),
            ('web', {'fields': ['website', 'email', 'phone', 'fax'], 'legend': _(u'Enity details')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
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
            raise ValidationError(ugettext(u"The file name is too long"))
        return logo
    

class ContactForm(ModelFormWithCity):
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Meta:
        model = models.Contact
        exclude=('uuid', 'same_as', 'imported_by', 'entity', 'relationships', 'nickname', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': _(u'enter notes about the contact'), 'cols':'72'}),
            'role': forms.SelectMultiple(attrs={
                'class': 'chosen-select', 'data-placeholder': _(u'Select roles'), 'style': "width: 100%;"}),
        }
        fieldsets = [
            ('name', {'fields': ['gender', 'lastname', 'firstname', 'birth_date', 'title', 'role', 'job'], 'legend': _(u'Name')}),
            ('web', {'fields': ['email', 'phone', 'mobile'], 'legend': _(u'Contact details')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
            ('relationship', {'fields': ['main_contact', 'email_verified', 'accept_newsletter', 'accept_3rdparty', 'accept_notifications', 'has_left'], 'legend': _(u'Options')}),
            ('photo', {'fields': ['photo'], 'legend': _(u'Photo')}),
        ]
        
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["role"].help_text = _(u"Select the roles played by the contact in his entity")
        
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
            raise ValidationError(ugettext(u"The file name is too long"))
        return photo


class EntityTypeForm(forms.ModelForm):
    
    class Meta:
        model = models.EntityType

class EntityRoleForm(forms.ModelForm):
    
    class Meta:
        model = models.EntityRole

class ActionForm(BetterBsModelForm):
    date = forms.DateField(label=_(u"planned date"), required=False, widget=forms.TextInput())
    time = forms.TimeField(label=_(u"planned time"), required=False)
    
    end_date = forms.DateField(label=_(u"end date"), required=False, widget=forms.TextInput())
    end_time = forms.TimeField(label=_(u"end time"), required=False)
    
    class Meta:
        model = models.Action
        fields = ('type', 'subject', 'date', 'time', 'status', 'in_charge', 'detail',
            'amount', 'number', 'planned_date', 'end_date', 'end_time', 'end_datetime', 'opportunity')
        fieldsets = [
            ('summary', {'fields': ['subject', 'date', 'time', 'planned_date', 'end_date', 'end_time', 'end_datetime',
                'in_charge', 'opportunity'], 'legend': _(u'Summary')}),
            ('type', {'fields': ['type', 'status', 'amount', 'number'], 'legend': _(u'Type')}),
            ('details', {'fields': ['detail'], 'legend': _(u'Details')}),
        ]

    def __init__(self, *args, **kwargs):
        entity = kwargs.pop('entity', None)
        instance = kwargs.get('instance', None)
        super(ActionForm, self).__init__(*args, **kwargs)
        
        if instance and instance.id and instance.type and instance.type.allowed_status.count():
            default_status = instance.type.default_status
            #choices = [] if default_status else [('', "---------")]
            choices = [('', "---------")] # let javascript disable the blank value if default_status
            self.fields['status'].choices = choices + [(s.id, s.name) for s in instance.type.allowed_status.all()]
            #self.fields['status'].initial = default_status.id if default_status else None
        
        self.fields['opportunity'].widget = forms.HiddenInput()    
        self.fields['detail'].widget = forms.Textarea(attrs={'placeholder': _(u'enter details'), 'cols':'72'})
        
        self._init_dt_field("planned_date", "date", "time")
        self._init_dt_field("end_datetime", "end_date", "end_time")
        
    def _init_dt_field(self, dt_field, date_field, time_field):
        self.fields[dt_field].widget = forms.HiddenInput()
        dt = getattr(self.instance, dt_field) if self.instance else self.fields[dt_field].initial
        if dt:
            self.fields[date_field].initial = dt.date()
            if settings.USE_TZ:
                utc_dt = dt.replace(tzinfo=timezone.utc)
                loc_dt = utc_dt.astimezone(timezone.get_current_timezone())
                self.fields[time_field].initial = loc_dt.time()
            else:
                self.fields[time_field].initial = dt.time()
        
    def clean_status(self):
        t = self.cleaned_data['type']
        s = self.cleaned_data['status']
        if t:
            allowed_status = ([] if t.default_status else [None]) + list(t.allowed_status.all())
            if len(allowed_status) > 0 and not (s in allowed_status):
                raise ValidationError(ugettext(u"This status can't not be used for this action type"))
        else:
            if s:
                raise ValidationError(ugettext(u"Please select a type before defining the status"))
        return s
    
    def clean_planned_date(self):
        d = self.cleaned_data.get("date", None)
        t = self.cleaned_data.get("time", None)
        if d:
            dt = datetime.combine(d, t or datetime.min.time())
            return dt
        return None
    
    def clean_time(self):
        d = self.cleaned_data.get("date", None)
        t = self.cleaned_data.get("time", None)
        if t and not d:
            raise ValidationError(_(u"You must set a date"))
        return t
    
    def clean_end_date(self):
        d1 = self.cleaned_data.get("date", None)
        d2 = self.cleaned_data.get("end_date", None)
        if d2:
            start_dt = self.cleaned_data["planned_date"]
            if not start_dt:
                raise ValidationError(_(u"The planned date is not defined"))
            if d1 > d2:
                raise ValidationError(_(u"The end date must be after the planned date"))
        return d2
            
    def clean_end_time(self):
        d1 = self.cleaned_data.get("date", None)
        d2 = self.cleaned_data.get("end_date", None)
        t1 = self.cleaned_data.get("time", None)
        t2 = self.cleaned_data.get("end_time", None)
        if t2:
            if t2 and not d2:
                raise ValidationError(_(u"You must set a end date"))
                
            if d1==d2 and (t1 or datetime.min.time())>=t2:
                raise ValidationError(_(u"The end time must be after the planned time"))
        elif t1:
            if d1==d2 and t1>=datetime.min.time():
                raise ValidationError(_(u"The end time must be set"))
        return t2
    
    def clean_end_datetime(self):
        d = self.cleaned_data.get("end_date", None)
        t = self.cleaned_data.get("end_time", None)
        dt = None
        if d:
            return datetime.combine(d, t or datetime.min.time())
        return None
    
class OpportunityForm(BetterBsModelForm):
    class Meta:
        model = models.Opportunity
        fields=('name', 'detail')
        
        fieldsets = [
                ('name', {'fields': ['name', 'detail'], 'legend': _(u'Summary')}),
                #('address', {'fields': ['display_on_board', 'ended'], 'legend': _(u'Show')}),
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
            raise ValidationError(ugettext(u"The entity does'nt exist"))

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
            raise ValidationError(ugettext(u"The contact does'nt exist"))
        
class SelectOpportunityForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', None)
        super(SelectOpportunityForm, self).__init__(*args, **kwargs)
        widget = OpportunityAutoComplete(
            attrs={'placeholder': _(u'Enter the name of a opportunity'), 'size': '50', 'class': 'colorbox'})
        self.fields["opportunity"] = forms.CharField(label=_(u"Opportunity"), widget=widget)

    def clean_opportunity(self):
        try:
            opportunity_id = int(self.cleaned_data["opportunity"])
            return models.Opportunity.objects.get(id=opportunity_id)
        except (ValueError, models.Opportunity.DoesNotExist):
            raise ValidationError(ugettext(u"The opportunity does'nt exist"))
        
class SameAsForm(forms.Form):
    contact = forms.IntegerField(label=_(u"Contact"))
    
    def __init__(self, contact, *args, **kwargs):
        super(SameAsForm, self).__init__(*args, **kwargs)
        potential_contacts = models.Contact.objects.filter(
            lastname__iexact=contact.lastname, firstname__iexact=contact.firstname,
        ).exclude(id=contact.id)
        if contact.same_as:
            potential_contacts = potential_contacts.exclude(same_as=contact.same_as) # Do not propose again current SameAs
        self._same_as = [(c.id, u"{0}".format(c)) for c in potential_contacts]
        if len(self._same_as):
            self.fields["contact"].widget = forms.Select(choices=self._same_as)
        else:
            self.fields["contact"].widget = forms.HiddenInput()    
    
    def has_choices(self):
        return len(self._same_as)
        
    def clean_contact(self):
        contact_id = self.cleaned_data["contact"]
        try:
            if contact_id not in [x[0] for x in self._same_as]:
                raise ValidationError(ugettext(u"Invalid contact"))
            return models.Contact.objects.get(id=contact_id)
        except models.Contact.DoesNotExist:
            raise ValidationError(ugettext(u"Contact does not exist"))
        
        
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
            raise ValidationError(ugettext(u"Invalid data"))
        except models.RelationshipType.DoesNotExist:
            raise ValidationError(ugettext(u"Relationship type does not exist"))
        
    def clean_contact2(self):
        try:
            contact2 = int(self.cleaned_data["contact2"])
            return models.Contact.objects.get(id=contact2)
        except ValueError:
            raise ValidationError(ugettext(u"Invalid data"))
        except models.Contact.DoesNotExist:
            raise ValidationError(ugettext(u"Contact does not exist"))
        
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
        fields = ['done']
        widgets = {
            'done': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        inst = kwargs.get('instance')
        inst.done = not inst.done
        kwargs['instance'] = inst
        super(ActionDoneForm, self).__init__(*args, **kwargs)    
    
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


class ContactsImportForm(BsModelForm):
    
    class Meta:
        model = models.ContactsImport
        exclude = ('imported_by', )
        
    class Media:
        css = {
            'all': ('chosen/chosen.css', 'chosen/chosen-bootstrap.css')
        }
        js = (
            'chosen/chosen.jquery.js',
        )
    
    def __init__(self, *args, **kwargs):
        super(ContactsImportForm, self).__init__(*args, **kwargs)
        
        self.fields['groups'].widget.attrs = {
            'class': 'chosen-select form-control',
            'data-placeholder': _(u'The created entities will be added to the selected groups'),
            #'style': "width:600px;"
        }
        self.fields['groups'].help_text = ''
        
        
    def clean_separator(self):
        if len(self.cleaned_data["separator"]) != 1:
            raise ValidationError(ugettext(u'Invalid separator {0}').format(self.cleaned_data["separator"]))
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
                raise ValidationError(ugettext(u'Please enter a valid code'))
            return self.cleaned_data['default_department']
        else:
            return None
        

from coop_cms.forms import AlohaEditableModelForm
class ActionDocumentForm(AlohaEditableModelForm):
    
    class Meta:
        model = models.ActionDocument
        fields = ('content',)
        
class ChangeContactEntityForm(forms.Form):
    OPTION_ADD_TO_EXISTING_ENTITY = 1
    OPTION_CREATE_NEW_ENTITY = 2
    OPTION_SWITCH_SINGLE_CONTACT = 3
    OPTION_SWITCH_ENTITY_CONTACT = 4
    
    OPTION_CHOICES = (
        (0, ""),
        (OPTION_ADD_TO_EXISTING_ENTITY, _(u"Reassign to an existing entity")),
        (OPTION_CREATE_NEW_ENTITY, _(u"Create a new entity")),
        (OPTION_SWITCH_SINGLE_CONTACT, _(u"Switch to single contact")),
        (OPTION_SWITCH_ENTITY_CONTACT, _(u"Switch to entity contact")),
    )
    
    option = forms.ChoiceField(label=_(u"What to do?"))
    entity = forms.IntegerField(label=_(u"Which one?"), required=False, widget=EntityAutoComplete(
        attrs={'placeholder': _(u'Enter the name of the entity'), 'size': '50', 'class': 'colorbox'}))
    
    def __init__(self, contact, *args, **kwargs):
        self.contact = contact
        super(ChangeContactEntityForm, self).__init__(*args, **kwargs)
        if contact.entity.is_single_contact:
            choices = [c for c in self.OPTION_CHOICES
                if not (c[0] in (self.OPTION_CREATE_NEW_ENTITY, self.OPTION_SWITCH_SINGLE_CONTACT)) ]
        else:
            choices = [c for c in self.OPTION_CHOICES
                if (c[0] != self.OPTION_SWITCH_ENTITY_CONTACT) ]
    
        self.fields['option'].choices = choices
        
        self.meth_map = {
            self.OPTION_ADD_TO_EXISTING_ENTITY: self._add_to_existing_entity,
            self.OPTION_CREATE_NEW_ENTITY: self._create_new_entity,
            self.OPTION_SWITCH_SINGLE_CONTACT: self._switch_single_contact,
            self.OPTION_SWITCH_ENTITY_CONTACT: self._switch_entity_contact,
        }
        
    def clean_option(self):
        try:
            option = int(self.cleaned_data["option"])
            if option == 0:
                raise ValidationError(ugettext(u"Please select one of this options"))
            try:
                self.meth_map[option]
            except KeyError:
                raise ValidationError(ugettext(u"Invalid value"))
        except ValueError:
            raise ValidationError(ugettext(u"Invalid data"))
        return option
        
    def clean_entity(self):
        option = self.cleaned_data.get("option", 0)
        if option != self.OPTION_ADD_TO_EXISTING_ENTITY:
            return None
        else:
            entity_id = self.cleaned_data["entity"]
            try:
                return models.Entity.objects.get(id=entity_id)
            except models.Entity.DoesNotExist:
                raise ValidationError(ugettext(u"Please select an existing entity"))
            
    def _add_to_existing_entity(self):
        old_entity = self.contact.entity
        self.contact.entity = self.cleaned_data["entity"]
        self.contact.save()
        old_entity.save()
    
    def _create_new_entity(self):
        old_entity = self.contact.entity
        self.contact.entity = models.Entity.objects.create()
        self.contact.save()
        old_entity.save()
        #old_entity.default_contact.delete()
    
    def _switch_single_contact(self):
        old_entity = self.contact.entity
        self.contact.entity = models.Entity.objects.create(
            is_single_contact=True,
            name=u"{0.lastname} {0.firstname}".format(self.contact).lower()
        )
        self.contact.save()
        self.contact.entity.default_contact.delete()
        self.contact.entity.save()
        old_entity.save()
        
    def _switch_entity_contact(self):
        self.contact.entity.is_single_contact = False
        self.contact.entity.save()
        
    def change_entity(self):
        option = self.cleaned_data["option"]
        meth = self.meth_map[option]
        meth()
        
class ConfirmForm(forms.Form):
    confirm = forms.BooleanField(initial=True, widget=forms.HiddenInput(), required=False)
    