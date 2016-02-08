# -*- coding: utf-8 -*-
"""forms"""

from datetime import date, datetime, time
from itertools import chain
import importlib
import json

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
if DJANGO_VERSION >= (1, 8, 0):
    from django.forms.utils import flatatt
else:
    from django.forms.util import flatatt
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.translation import ugettext as _

import floppyforms as forms
from coop_cms.bs_forms import Form as BsForm

from balafon.fields import HidableModelMultipleChoiceField
from balafon.Crm.models import Contact, Action, Group, Subscription, SubscriptionType
from balafon.Crm.widgets import OpportunityAutoComplete
from balafon.Search import models
from balafon.Search.widgets import DatespanInput
from balafon.Search.utils import get_date_bounds

SEARCH_FORMS = None


def load_from_name(constant_full_name):
    """load module dynamically"""
    constant_full_path = constant_full_name.split('.')
    constant_path, constant_name = '.'.join(constant_full_path[:-1]), constant_full_path[-1]
    module = importlib.import_module(constant_path)
    return getattr(module, constant_name)


class QuickSearchForm(BsForm):
    """Quick search form which is included in the menu"""
    text = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _(u'Quick search')})
    )


def get_search_forms():
    """cache the configured forms"""
    global SEARCH_FORMS #pylint: disable=global-statement
    if not SEARCH_FORMS:
        SEARCH_FORMS = load_from_name(settings.SEARCH_FORM_LIST)
    return SEARCH_FORMS


def get_field_form(field):
    """get field form"""
    _forms = []
    for cat_and_form in get_search_forms():
        _forms.extend(cat_and_form[1])
    field_dict = dict([(_form.name, _form) for _form in _forms if _form])
    return field_dict[field]


class GroupedSelect(forms.Select):
    """Buld select with all forms"""
    def render(self, name, value, attrs=None, choices=(), *args, **kwargs):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select {0}>'.format(flatatt(final_attrs))] 
        str_value = smart_unicode(value)
        for group_label, group in self.choices: 
            if group_label:
                # should belong to an optgroup
                group_label = smart_unicode(group_label) 
                output.append(u'<optgroup label="%s">' % escape(group_label)) 
            for key, value in group:
                #build option html
                option_value = smart_unicode(key)
                output.append(
                    u'<option value="{0}"{1}>{2}</option>'.format(
                        escape(option_value),
                        (option_value == str_value) and u' selected="selected"' or '',
                        escape(smart_unicode(value))
                    )
                )
            if group_label:
                output.append(u'</optgroup>')
        output.append(u'</select>') 
        return u'\n'.join(output)


class GroupedChoiceField(forms.ChoiceField):
    """GroupedChoiceField"""

    def __init__(self, choices=None, *args, **kwargs):

        kwargs.setdefault('required', True)
        kwargs.setdefault('widget', None)
        kwargs.setdefault('label', None)
        kwargs.setdefault('initial', None)
        kwargs.setdefault('help_text', None)

        super(GroupedChoiceField, self).__init__(*args, **kwargs)
        self.choices = choices or ()
        
    def clean(self, value):
        """
        Validates that the input is in self.choices.
        """
        value = super(GroupedChoiceField, self).clean(value)
        if value in (None, ''):
            value = u''
        value = forms.util.smart_unicode(value)
        if value == u'':
            return value
        valid_values = []
        for choice in self.choices:
            group = choice[1]
            valid_values += [str(key) for key, value in group]
        if value not in valid_values:
            raise ValidationError(_(u'Select a valid choice. That choice is not one of the available choices.'))
        return value


class FieldChoiceForm(forms.Form):
    """The form for dynamically adding new filter"""
    
    def __init__(self, *args, **kwargs):
        super(FieldChoiceForm, self).__init__(*args, **kwargs)
        choices = [('', [('', '')])]
        for (cat, forms_) in get_search_forms():
            choices.append(
                (
                    cat,
                    [
                        (reverse('search_get_field', args=[form.name]), form.label)
                        for form in forms_ if form
                    ]
                )
            )
        widget = GroupedSelect(attrs={
            'class': 'form-control half-width',
            'data-placeholder': _(u'Please select a filter'),
        })
        self.fields['field_choice'] = GroupedChoiceField(choices, widget=widget)

    def as_it_is(self):
        """Returns this form rendered as HTML <p>s."""
        return self._html_output(
            normal_row=u'%(field)s<span>%(help_text)s</span>',
            error_row=u'%s',
            row_ender=u'',
            help_text_html=u' <span class="helptext">%s</span>',
            errors_on_separate_row=False
        )


class SearchForm(forms.Form):
    """Main search form"""
    name = forms.CharField(required=False, help_text=_('Enter a name and click save.'))
    excluded = forms.CharField(required=False, widget=forms.HiddenInput())

    class Media:
        """media files"""
        css = {
            'all': ('chosen/chosen.css', 'chosen/chosen-bootstrap.css')
        }
        js = (
            'chosen/chosen.jquery.js',
        )

    def __init__(self, data=None, instance=None, save=False, *args, **kwargs):
        super(SearchForm, self).__init__(data=data, *args, **kwargs)
        self._forms = {}
        self._instance = instance
        self._save = save
        self.contacts_display = False
        self.contains_refuse_newsletter = False
        if instance:
            self.fields['name'].initial = instance.name
        if not data and instance:
            data = {}
            for group in instance.searchgroup_set.all():
                for search_field in group.searchfield_set.all():
                    key = '-_-'.join((group.name, search_field.field, str(search_field.count or len(data))))
                    if search_field.is_list:
                        #data[key] = json.loads(f.value) # doesn't work :(
                        data[key] = self._str_to_list(search_field.value)
                    else:
                        data[key] = search_field.value
        if data:
            for key in data:
                if hasattr(data, 'getlist'):
                    value = data.getlist(key)
                    if len(value) == 1:
                        value = data.get(key)
                else:
                    value = data.get(key)
                try:
                    #extract search fields
                    group, field, fid = key.split('-_-')
                    #will raise an except for city visible field --> ignore this field
                    fid = int(fid)
                    if group not in self._forms:
                        self._forms[group] = []
                    form_class = get_field_form(field)
                    form = form_class(group, fid, {field: value})
                    self.contacts_display = self.contacts_display or form.contacts_display
                    self._forms[group].append(form)
                except ValueError:
                    pass
            #sort forms of a group according to their id
            for form in self._forms.values():
                form.sort(key=lambda field_: field_.count)
    
    def block_count(self):
        """number of block"""
        return len(self._forms)
    
    def field_count(self):
        """number of fields"""
        return sum([len(f) for f in self._forms])
    
    def _str_to_list(self, str_value):
        """convert string to list"""
        def _split_unicode(unicode_str):
            """remove trailing ' " from string"""
            unicode_str0 = unicode_str
            try:
                if unicode_str[:2] in ("u'", 'u"'):
                    unicode_str = unicode_str[2:]
                elif unicode_str[0] in ("'", '"'):
                    unicode_str = unicode_str[1:]
                
                if unicode_str[-1] in ("'", '"'):
                    unicode_str = unicode_str[:-1]
            except IndexError:
                return unicode_str0
            return unicode_str
            
        if str_value[0] == '[' and str_value[-1] == ']':
            #remove [ and ]
            values = str_value[1:-1]
            # get things separated by ', '
            values = values.split(", ")
            values = [value for value in values]
            values = [_split_unicode(value) for value in values]
            return values
        return []
    
    def serialize(self):
        """serialize the form for json"""
        data = {}
        for group, the_forms in self._forms.items():
            for form in the_forms:
                if group in data:
                    data[group] += [form.serialize()]
                else:
                    data[group] = [form.serialize()]
        return data
    
    def clean_name(self):
        """validate name"""
        name = self.cleaned_data['name']
        if len(name) >= 100:
            raise ValidationError(_(u"Too long"))
        if self._save:
            if name:
                queryset = models.Search.objects.filter(name=name)
                if self._instance and self._instance.id:
                    queryset = queryset.exclude(id=self._instance.id)
                if queryset.count() > 0:
                    raise ValidationError("This search name is already used")
            else:
                if self._instance:
                    raise ValidationError("A name is required for saving the search")
        return name
    
    def clean(self):
        """validate form"""
        keys = self._forms.keys()
        keys.sort()
        cleaned_data = super(SearchForm, self).clean()
        for key in keys:
            for form in self._forms[key]:
                cleaned_data.update(form.clean())
        return cleaned_data
    
    def save_search(self):
        """save search"""
        self._instance.searchgroup_set.all().delete()
        self._instance.name = self.cleaned_data['name']
        self._instance.save()
        keys = self._forms.keys()
        for key in keys:
            group = models.SearchGroup.objects.create(name=key, search=self._instance)
            for form in self._forms[key]:
                field = models.SearchField.objects.create(
                    search_group=group, field=form.name, value=form.value, count=form.count)
                if form.multi_values:
                    field.is_list = True
                    field.save()
        return self._instance
    
    def clean_excluded(self):
        """validate"""
        excluded = self.cleaned_data['excluded']
        if excluded:
            return [int(x) for x in excluded.strip("#").split("##")]
        return []

    def is_valid(self):
        """is full form valid?"""
        if not super(SearchForm, self).is_valid():
            return False
        keys = self._forms.keys()
        keys.sort()
        for key in keys:
            for form in self._forms[key]:
                if not form.is_valid():
                    return False
        return True
    
    def _get_contacts(self):
        """get contacts"""
        keys = self._forms.keys()
        keys.sort()
        contacts = set([])
        global_post_processors = []
        self.contains_refuse_newsletter = False
        
        for key in keys:
            post_processors = []
            contacts_set = Contact.objects.all()
            
            if not ('secondary_contact' in [form.name for form in self._forms[key]]):
                contacts_set = contacts_set.filter(main_contact=True)
            
            for form in self._forms[key]:
                
                contacts_set = form.get_queryset(contacts_set)
                
                if hasattr(form, 'post_process'):
                    post_processors.append(form.post_process)
                    
                if hasattr(form, 'global_post_process'):
                    global_post_processors.append(form.global_post_process)

            for post_processor in post_processors:
                contacts_set = post_processor(contacts_set)
                
            contacts = contacts.union(set(contacts_set))
        
        for global_post_processor in global_post_processors:
            contacts = global_post_processor(contacts)

        #Just for compatibility
        queryset = SubscriptionType.objects.filter(site=Site.objects.get_current(), name=u'Newsletter')
        if queryset.count():
            for contact in contacts:
                for subscription_type in queryset:
                    try:
                        if not contact.subscription_set.get(subscription_type=subscription_type).accept_subscription:
                            self.contains_refuse_newsletter = True
                            break
                    except Subscription.DoesNotExist:
                        self.contains_refuse_newsletter = True
                        break
                
        return list(contacts)
    
    def _get_filter_func(self):
        """filter function"""
        form_names = [form.name for form in chain.from_iterable(self._forms.values())]
        if 'contact_has_left' in form_names:
            return lambda contact: contact
        return lambda contact: contact and (not contact.has_left)

    def get_contacts_by_entity(self):
        """get contacts by entities"""
        contacts = self._get_contacts()
        contacts_count = 0
        entities = {}
        filter_func = self._get_filter_func()
        empty_entities = {}
        for contact in contacts:
            pass_filter = filter_func(contact)
            entity = contact.entity if contact else None
            if entity and not entities.has_key(entity.id):
                entities[entity.id] = (entity, [])
                empty_entities[entity.id] = entity
            if pass_filter:
                entities[entity.id][1].append(contact)
                entities[entity.id][1].sort(key=lambda c: c.lastname.lower())
                empty_entities.pop(entity.id, None)
                contacts_count += 1
            
        results = []
        for entity, contacts in entities.values():
            entity.search_contacts = contacts
            if entity.id in empty_entities:
                setattr(entity, 'is_empty', True)
            results.append(entity)
        results.sort(key=lambda x: x.name)
        return results, contacts_count, len(empty_entities) > 0
    
    def get_contacts(self):
        """get contacts"""
        filter_func = self._get_filter_func()
        contacts = self._get_contacts()
        contact_ids = self.cleaned_data['excluded']
        return [contact for contact in contacts if contact.id not in contact_ids and filter_func(contact)]
        
    def get_contacts_emails(self):
        """get contact emails"""
        filter_func = self._get_filter_func()
        contacts = self._get_contacts()
        excluded_ids = self.cleaned_data['excluded']
        emails = []
        for contact in contacts:
            if contact.get_email and (contact.id not in excluded_ids) and filter_func(contact):
                if contact.firstname or contact.lastname:
                    emails.append(u'"{1}" <{0}>'.format(contact.get_email, contact.fullname))
                else:
                    emails.append(contact.get_email)
        return emails
    
    def actions(self):
        """allowed actions"""
        form = FieldChoiceForm()
        html_tpl = u"""{0}
            <a class="btn btn-xs btn-default btn-yellow add-field" href="">
            <span class="glyphicon glyphicon-filter"></span> {1}</a>
            <a class="btn btn-xs btn-default add-block" href="">
            <span class="glyphicon glyphicon-th-list"></span> {2}</a>
            <a class="btn btn-xs btn-default duplicate-block" href="">
            <span class="glyphicon glyphicon-share"></span> {5}</a>
            <a class="btn btn-xs btn-danger clear-block" href="">
            <span class="glyphicon glyphicon-remove"></span> {3}</a>
            <a class="btn btn-xs btn-danger remove-block" href="">
            <span class="glyphicon glyphicon-trash"></span> {4}</a>"""

        return html_tpl.format(
            form.as_it_is(), _(u'Add filter'), _(u'Add block'), _(u'Clear'), _(u'Remove'), _(u'Duplicate')
        )
    
    def as_html(self):
        """as html"""
        keys = self._forms.keys()
        keys.sort()
        html = u'<div>{0}</div>'.format(self.as_p())
        if keys:
            for key in keys:
                html_tpl = u'<div class="search-block" rel="{0}"><div class="actions">{1}</div><div class="fields">'
                html += html_tpl.format(key, self.actions())
                for form in self._forms[key]:
                    html += form.as_it_is()
                html += '</div></div>'
        return html


class SearchFieldForm(BsForm):
    """Base class for search forms"""
    contacts_display = False
    multi_values = False
    
    def __init__(self, block, count, data=None, *args, **kwargs):
        self.block = block
        self.count = count
        form_data = None
        if data:
            if self.multi_values:
                val = data[self.name]
                self.value = val if type(val) is list else [val]
            else:
                self.value = data[self.name]
            form_data = {self._get_field_name(): self.value}
        super(SearchFieldForm, self).__init__(form_data, *args, **kwargs)
        
    def _get_field_name(self):
        """return field name"""
        return self.block+'-_-'+self.name+'-_-'+unicode(self.count)
        
    def _add_field(self, field):
        """adda field"""
        field.required = True
        if not field.widget.attrs.get('class', None):
            field.widget.attrs['class'] = "form-control"
        else:
            field.widget.attrs['class'] += " form-control"
        self.fields[self._get_field_name()] = field
        
    def clean(self):
        """return cleaned data"""
        return {self._get_field_name(): self.value}
        
    def serialize(self):
        """serialize"""
        return {self.name: self.value}
        
    def as_it_is(self):
        """return form html without any wrapper tag"""
        template = get_template("Search/_search_field_form.html")
        return template.render(Context({"form": self}))
    
    def get_queryset(self, queryset):
        """
        returns a queryset for filtering contacts corresponding to searches
        it can be overriden in subclassses
        A subclass may also define a get_lookup or get_exclude_lookup method for building the queryset more easily
        (and for compatibility reasons)
        """
        if hasattr(self, 'get_lookup'):
            lookup = self.get_lookup()
            if lookup:
                if type(lookup) is dict:
                    queryset = queryset.filter(**lookup)
                elif type(lookup) is list:
                    queryset = queryset.filter(*lookup)
                else:
                    queryset = queryset.filter(lookup)
                    
        if hasattr(self, 'get_exclude_lookup'):
            lookup = self.get_exclude_lookup()
            if lookup:
                if type(lookup) is dict:
                    queryset = queryset.exclude(**lookup)
                elif type(lookup) is list:
                    queryset = queryset.exclude(*lookup)
                else:
                    queryset = queryset.exclude(lookup)

        return queryset


class TwoDatesForm(SearchFieldForm):
    """Base class for any SerachForm providing a 'TwoDate' field"""
    
    def __init__(self, *args, **kwargs):
        super(TwoDatesForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self.label, initial='{0} {0}'.format(date.today().strftime("%d/%m/%Y")),
            widget=DatespanInput()
        )
        self._add_field(field)
        
    def __getattr__(self, name):
        """get attribute dynamically"""
        if name == 'clean_'+self._get_field_name():
            return self._clean_field
        return super(TwoDatesForm, self).__getattr__(name)
    
    def _clean_field(self):
        """validate"""
        try:
            self._get_dates()
        except ValueError:
            raise ValidationError(_(u"Two valid dates are required"))
        return self.value
    
    def _get_dates(self):
        """return selected dates"""
        return get_date_bounds(self.value)

    def _get_datetimes(self):
        """return selected date times"""
        start_date, end_date = get_date_bounds(self.value)
        return datetime.combine(start_date, time.min), datetime.combine(end_date, time.max)


class YesNoSearchFieldForm(SearchFieldForm):
    """Base class for ny SearchForm providing a Yes/No field"""

    def __init__(self, *args, **kwargs):
        super(YesNoSearchFieldForm, self).__init__(*args, **kwargs)
        choices = ((1, _('Yes')), (0, _('No')),)
        field = forms.ChoiceField(choices=choices, label=self.label)
        self._add_field(field)
    
    def is_yes(self):
        """Is yes selected?"""
        return True if int(self.value) else False


class SearchActionBaseMixin(object):
    """
    Base class for any views which needs to get extra information for handling results
    Example : Pdf, CreateActions...
    """
    def _pre_init(self, *args, **kwargs):
        """at the beginning of __init__"""
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and 'contacts' in initial:
            initial_contacts = u';'.join([unicode(contact.id) for contact in initial['contacts']])
            initial.pop('contacts')
        return initial_contacts
        
    def _post_init(self, initial_contacts):
        """at the end of __init__"""
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts

    def get_contacts(self):
        """get contacts"""
        ids = self.cleaned_data["contacts"].split(";")
        contacts = Contact.objects.filter(id__in=ids)
        contact_by_ids = {}
        for contact in contacts:
            contact_by_ids[unicode(contact.id)] = contact
        ordered_contacts = []
        for contact_id in ids:
            ordered_contacts.append(contact_by_ids[contact_id])
        return ordered_contacts


class SearchActionForm(forms.Form, SearchActionBaseMixin):
    """Base class for any views which needs to get extra information for handling results"""
    contacts = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        initial_contacts = self._pre_init(*args, **kwargs)
        super(SearchActionForm, self).__init__(*args, **kwargs)
        self._post_init(initial_contacts)


class ContactsAdminForm(SearchActionForm):
    """This form is used for superuser forcing newsletter subscription"""
    subscribe_newsletter = forms.BooleanField(required=False)


class PdfTemplateForm(SearchActionForm):
    """Form for Pdf generation"""
    search_dict = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(PdfTemplateForm, self).__init__(*args, **kwargs)
        
        if getattr(settings, 'BALAFON_PDF_TEMPLATES', None):
            choices = settings.BALAFON_PDF_TEMPLATES
        else:
            choices = (
                ('pdf/labels_24.html', _(u'etiquettes 24')),
                ('pdf/labels_21.html', _(u'etiquettes 21')),
                ('pdf/agipa_21.html', _(u'Agipa 21')),
                ('pdf/labels_16.html', _(u'etiquettes 16')),
                ('pdf/address_strip.html', _(u'bande adresse')),
            )
        
        self.fields['template'] = forms.ChoiceField(
            choices=choices,
            required=True,
            label=_(u'template'),
            help_text=_(u'Select the type of document to generate')
        )
        
        extra_fields = getattr(settings, 'BALAFON_PDF_FORM_EXTRA_FIELDS', None)
        if extra_fields:
            for field_name, field_label, initial_value in extra_fields:
                self.fields[field_name] = forms.CharField(label=field_label, initial=initial_value)
       
    def patch_context(self, context):
        """
        add to data from external function in context
        It can be used for example for adding blank labels in labels generation
        """
        template = self.cleaned_data['template']
        extra_data = self._get_extra_data()
        context.update(extra_data)
        hooks = getattr(settings, 'BALAFON_PDF_FORM_CONTEXT_HOOKS', {})
        if hooks and template in hooks:
            context = hooks[template](template, context)
        return context
    
    def _get_extra_data(self):
        """
        This extra_data comes from additional fields defined in BALAFON_PDF_FORM_EXTRA_FIELDS settings
        These values are passed to the template
        """
        extra_data = dict(self.cleaned_data)
        for field in ('template', 'contacts', 'search_dict'):
            extra_data.pop(field)
        return extra_data
        
        
class ActionForContactsForm(forms.ModelForm):
    """Create action for contacts"""
    date = forms.DateField(label=_(u"planned date"), required=False, widget=forms.TextInput())
    time = forms.TimeField(label=_(u"planned time"), required=False)
    contacts = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        """create form from model"""
        model = Action
        fields = (
            'date', 'time', 'type', 'subject', 'in_charge', 'detail', 'planned_date', 'contacts', 'opportunity'
        )
        
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and 'contacts' in initial:
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        super(ActionForContactsForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
        self.fields['opportunity'].widget = OpportunityAutoComplete(
            attrs={'placeholder': _(u'Enter the name of an opportunity'), 'size': '80', 'class': 'colorbox'}
        )
        
    def get_contacts(self):
        """return contacts"""
        contact_ids = self.cleaned_data["contacts"].split(";")
        return Contact.objects.filter(id__in=contact_ids)
        
    def clean_planned_date(self):
        """validate planned date"""
        the_date = self.cleaned_data["date"]
        the_time = self.cleaned_data.get("time", None)
        if the_date:
            return datetime.combine(the_date, the_time or datetime.min.time())
        return None


class GroupForContactsForm(forms.Form):
    """Add contacts to group"""
    contacts = forms.CharField(widget=forms.HiddenInput())
    groups = HidableModelMultipleChoiceField(queryset=Group.objects.all())
    on_contact = forms.BooleanField(
        label=_(u"Group on contact"),
        required=False,
        initial=True,
        help_text=_(u"Define if the group is added on the contact itself or on his entity")
    )
    
    class Media:
        """media files"""
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )
        
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and 'contacts' in initial:
            initial_contacts = u';'.join([unicode(contact.id) for contact in initial['contacts']])
            initial.pop('contacts')
        super(GroupForContactsForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
    
        self.fields['groups'].widget.attrs = {
            'class': 'chzn-select',
            'data-placeholder': _(u'Select groups'),
            'style': "width:350px;"
        }
        self.fields['groups'].help_text = ''

    def get_contacts(self):
        """get contacts"""
        contact_ids = self.cleaned_data["contacts"].split(";")
        return Contact.objects.filter(id__in=contact_ids)


class SearchNameForm(forms.Form):
    """Save search form"""
    search_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    name = forms.CharField(required=True, label=_(u"Name"))
    search_fields = forms.CharField(required=True, widget=forms.HiddenInput())
    
    def clean_name(self):
        """validate name"""
        search_id = self.cleaned_data["search_id"]
        
        name = self.cleaned_data["name"]
        if not name:
            raise ValidationError(_(u"This field is required"))
        
        queryset = models.Search.objects.filter(name=name)
        if search_id:
            queryset = queryset.exclude(id=search_id)
        if queryset.count() > 0:
            raise ValidationError(_(u"This name is already used"))
        
        if search_id:
            search = models.Search.objects.get(id=search_id)
            if search.name != name:
                search.name = name
                search.save()
        else:
            search = models.Search(name=name)        
        return search
    
    def clean_search_fields(self):
        """validate search fields"""
        search_fields = self.cleaned_data["search_fields"]
        data = json.loads(search_fields)
        for key in ('csrfmiddlewaretoken', 'excluded', 'name', 'field_choice'):
            data.pop(key, None)
        return data
