# -*- coding: utf-8 -*-

import floppyforms as forms
from django.forms import ChoiceField
from django.utils.html import escape
from django.forms.util import flatatt
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from sanza.Search import models
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from sanza.Search.widgets import DatespanInput
from sanza.Crm.models import Contact
from django.conf import settings
SEARCH_FORMS = None
from django.utils import importlib
from itertools import chain

def load_from_name(constant_full_name):
    x = constant_full_name.split('.')
    constant_path, constant_name = '.'.join(x[:-1]), x[-1]
    module = importlib.import_module(constant_path)
    return getattr(module, constant_name)

class QuickSearchForm(forms.Form):
    """Quick search form which is included in the menu"""
    text = forms.CharField(required=True,
        widget=forms.TextInput(attrs={'placeholder': _(u'Quick search')}))

def get_search_forms():
    global SEARCH_FORMS
    if not SEARCH_FORMS:
        SEARCH_FORMS = load_from_name(settings.SEARCH_FORM_LIST)
    return SEARCH_FORMS

def get_field_form(field):
    _forms = []
    for (cat, fs) in get_search_forms():
        _forms.extend(fs)
    x = dict([(f._name, f) for f in _forms])
    return x[field]


class GroupedSelect(forms.Select): 
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = '' 
        final_attrs = self.build_attrs(attrs, name=name) 
        output = [u'<select%s>' % flatatt(final_attrs)] 
        str_value = smart_unicode(value)
        for group_label, group in self.choices: 
            if group_label: # should belong to an optgroup
                group_label = smart_unicode(group_label) 
                output.append(u'<optgroup label="%s">' % escape(group_label)) 
            for k, v in group:
                option_value = smart_unicode(k)
                option_label = smart_unicode(v) 
                selected_html = (option_value == str_value) and u' selected="selected"' or ''
                output.append(u'<option value="%s"%s>%s</option>' % (escape(option_value), selected_html, escape(option_label))) 
            if group_label:
                output.append(u'</optgroup>') 
        output.append(u'</select>') 
        return u'\n'.join(output)

class GroupedChoiceField(ChoiceField):
    def __init__(self, choices=(), required=True, widget=GroupedSelect, label=None, initial=None, help_text=None):
        super(ChoiceField, self).__init__(required, widget, label, initial, help_text)
        self.choices = choices
        
    def clean(self, value):
        """
        Validates that the input is in self.choices.
        """
        value = super(forms.ChoiceField, self).clean(value)
        if value in (None, ''):
            value = u''
        value = forms.util.smart_unicode(value)
        if value == u'':
            return value
        valid_values = []
        for group_label, group in self.choices:
            valid_values += [str(k) for k, v in group]
        if value not in valid_values:
            raise ValidationError(gettext(u'Select a valid choice. That choice is not one of the available choices.'))
        return value

class FieldChoiceForm(forms.Form):
    """The form for dynamicalling adding new filter"""
    
    def __init__(self, *args, **kwargs):
        super(FieldChoiceForm, self).__init__(*args, **kwargs)
        choices = []
        for (cat, fs) in get_search_forms():
            choices.append(
                (cat, [(reverse('search_get_field', args=[f._name]), f._label) for f in fs])
            )
        self.fields['field_choice'] = GroupedChoiceField(choices)
        
    def as_it_is(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row = u'%(field)s<span>%(help_text)s</span>',
            error_row = u'%s',
            row_ender = u'',
            help_text_html = u' <span class="helptext">%s</span>',
            errors_on_separate_row = False)

class SearchForm(forms.Form):
    name = forms.CharField(max_length=100, required=False,
        help_text=_('Enter a name and click save.'))
    
    excluded = forms.CharField(max_length=1000, required=False, widget=forms.HiddenInput())
    #subject = forms.CharField(max_length=1000, required=False, widget=forms.HiddenInput())
    
    def __init__(self, data=None, instance=None, save=False, *args, **kwargs):
        super(SearchForm, self).__init__(data=data, *args, **kwargs)
        self._forms = {}
        self._instance = instance
        self._save = save
        if instance: self.fields['name'].initial = instance.name
        if not data and instance:
            data = {}
            for gr in instance.searchgroup_set.all():
                for f in gr.searchfield_set.all():
                    key = '-_-'.join((gr.name, f.field, str(len(data))))
                    data[key] = f.value
        if data:
            for key, value in data.items():
                try:
                    #extract search fields
                    gr, field, id = key.split('-_-')
                    int(id) #will raise an except for city visible field --> ignore this field
                    if not self._forms.has_key(gr):
                        self._forms[gr] = []
                    form_class = get_field_form(field)
                    self._forms[gr].append(form_class(gr, id, {field: value}))
                except ValueError:
                    pass
            #sort forms of a group according to their id
            for fs in self._forms.values(): 
                fs.sort(key=lambda f: f._count)
    
    def block_count(self):
        return len(self._forms)
    
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if self._save:
            if name:
                qs = models.Search.objects.filter(name=name)
                if self._instance and self._instance.id:
                    qs = qs.exclude(id=self._instance.id)
                if qs.count()>0:
                    raise ValidationError("This search name is already used")
            else:
                if self._instance:
                    raise ValidationError("A name is required for saving the search")
        return name
    
    def clean(self):
        keys = self._forms.keys()
        keys.sort()
        cleaned_data = super(SearchForm, self).clean()
        for key in keys:
            for form in self._forms[key]:
                cleaned_data.update(form.clean())
        return cleaned_data
    
    def save_search(self):
        self._instance.searchgroup_set.all().delete()
        self._instance.name = self.cleaned_data['name']
        self._instance.save()
        keys = self._forms.keys()
        for key in keys:
            gr = models.SearchGroup.objects.create(name=key, search=self._instance)
            for form in self._forms[key]:
                field = models.SearchField.objects.create(search_group=gr, field=form._name, value=form._value)
        return self._instance
    
    def clean_excluded(self):
        excluded = self.cleaned_data['excluded']
        if excluded:
            return [int(x) for x in excluded.strip("#").split("##")]
        return []
        
    
    def is_valid(self):
        if not super(SearchForm, self).is_valid():
            return False
        keys = self._forms.keys()
        keys.sort()
        results = []
        for key in keys:
            lookup = {}
            for form in self._forms[key]:
                if not form.is_valid():
                    return False
        return True
    
    def _get_contacts(self):
        keys = self._forms.keys()
        keys.sort()
        contacts = set([])
        post_processors = []
        for key in keys:
            q_objs = []
            exclude_q_objs = []
            if 'secondary_contact' in [f._name for f in self._forms[key]]:
                filter_lookup = {}
            else:
                filter_lookup = {'main_contact': True}
            exclude_lookup = {}
            for form in self._forms[key]:
                lookup = form.get_lookup()
                if lookup:
                    if type(lookup) is dict:
                        filter_lookup.update(lookup)
                    elif type(lookup) is list:
                        q_objs.extend(lookup)
                    else:
                        q_objs.append(lookup)

                if hasattr(form, 'get_exclude_lookup'):
                    xcl_lkp = form.get_exclude_lookup()
                    if xcl_lkp:
                        if type(xcl_lkp) is dict:
                            exclude_lookup.update(xcl_lkp)
                        elif type(xcl_lkp) is list:
                            exclude_q_objs.extend(xcl_lkp)
                        else:
                            exclude_q_objs.append(xcl_lkp)
                
                if hasattr(form, 'post_process'):
                    post_processors.append(form.post_process)

            contacts_set = Contact.objects.filter(**filter_lookup)
            for q_obj in q_objs:
                contacts_set = contacts_set.filter(q_obj)
            if exclude_lookup:
                contacts_set = contacts_set.exclude(**exclude_lookup)
            for q_obj in exclude_q_objs:
                contacts_set = contacts_set.exclude(q_obj)
            contacts = contacts.union(set(contacts_set))
            for pp in post_processors:
                contacts = pp(contacts)
        return list(contacts)
    
    def _get_filter_func(self):
        #form_names = [f._name for f in chain.from_iterable(self._forms.values())]
        #if 'main_contact' in form_names:
        #    return lambda c: (not c.has_left)
        #return lambda c: (not c.has_left) and c.main_contact
        return lambda c: (not c.has_left)

    def get_contacts_by_entity(self):
        self.contains_refuse_newsletter = False
        contacts = self._get_contacts()
        contacts_count = 0
        entities = {}
        filter_func = self._get_filter_func()
        empty_entities = {}
        for contact in contacts:
            pass_filter = filter_func(contact)
            entity = contact.entity
            if not entities.has_key(entity.id):
                entities[entity.id] = (entity, [])
                empty_entities[entity.id] = entity
            if pass_filter:
                if not contact.accept_newsletter:
                    self.contains_refuse_newsletter = True
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
        return results, contacts_count, (len(empty_entities)>0)
    
    def get_contacts(self):
        filter_func = self._get_filter_func()
        contacts = self._get_contacts()
        ids = self.cleaned_data['excluded']
        return [c for c in contacts if (c.id not in ids and filter_func(c))]
        
    def get_contacts_emails(self):
        filter_func = self._get_filter_func()
        contacts = self._get_contacts()
        excluded_ids = self.cleaned_data['excluded']
        emails = []
        for c in contacts:
            if c.get_email and (c.id not in excluded_ids) and filter_func(c):
                if c.firstname or c.lastname:
                    emails.append(u'"{1}" <{0}>'.format(c.get_email, c.fullname))    
                else:
                    emails.append(c.get_email)
        return emails
    
    def actions(self):
        f = FieldChoiceForm()
        return u"""
            {0}
            <a class="add-field" href="">{1}</a>
            <a class="add-block" href="">{2}</a>
            <a class="duplicate-block" href="">{5}</a>
            <a class="clear-block" href="">{3}</a>
            <a class="remove-block" href="">{4}</a>""".format(
                f.as_it_is(), _(u'Add filter'), _(u'Add block'), _(u'Clear'), _(u'Remove'), _(u'Duplicate'))
    
    def as_html(self):
        keys = self._forms.keys()
        keys.sort()
        html = u'<div>{0}</div>'.format(self.as_p())
        if keys:
            for key in keys:
                html += u'<div class="search-block" rel="{0}"><div class="actions">{1}</div><div class="fields">'.format(key, self.actions())
                for form in self._forms[key]:
                    html += form.as_it_is()
                html += '</div></div>'
        return html

class SearchFieldForm(forms.Form):
    def __init__(self, block, count, data=None, *args, **kwargs):
        self._block = block
        self._count = count
        form_data = None
        if data:
            self._value = data[self._name]
            form_data = {self._get_field_name(): self._value}
        super(SearchFieldForm, self).__init__(form_data, *args, **kwargs)
        
    def _get_field_name(self):
        return self._block+'-_-'+self._name+'-_-'+self._count
        
    def _add_field(self, field):
        field.required = True
        self.fields[self._get_field_name()] = field
        
    def clean(self):
        return {self._get_field_name(): self._value}
        
    def as_it_is(self):
        "Returns this form rendered as HTML <p>s."
        return self._html_output(
            normal_row = u'<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s <a href="" class="remove-field">{0}</a></p>'.format(_(u'Remove')),
            error_row = u'%s',
            row_ender = '</p>',
            help_text_html = u' <span class="helptext">%s</span>',
            errors_on_separate_row = True)
        
class TwoDatesForm(SearchFieldForm):
    
    def __init__(self, *args, **kwargs):
        super(TwoDatesForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
            label=self._label, initial='{0} {0}'.format(date.today().strftime("%d/%m/%Y")),
            widget=DatespanInput())
        self._add_field(field)
        
    def __getattr__(self, name):
        if name == 'clean_'+self._get_field_name():
            return self._clean_field
        return super(TwoDatesForm, self).__getattr__(name)
    
    def _clean_field(self):
        try:
            self._get_dates()
        except ValueError:
            raise ValidationError(_(u"Two valid dates are required"))
        return self._value
    
    def _get_dates(self):
        d1, d2 = self._value.split(' ')
        d1, d2 = [int(x) for x in d1.split('/')], [int(x) for x in d2.split('/')]
        d1.reverse(), d2.reverse()
        return date(*d1), date(*d2)

class YesNoSearchFieldForm(SearchFieldForm):
    def __init__(self, *args, **kwargs):
        super(YesNoSearchFieldForm, self).__init__(*args, **kwargs)
        choices = ((1, _('Yes')), (0, _('No')),)
        field = forms.ChoiceField(choices=choices, label=self._label)
        self._add_field(field)
    
    def is_yes(self):
        return True if int(self._value) else False

class SearchActionBaseForm:
    def _pre_init(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        return initial_contacts
        
    def _post_init(self, initial_contacts):
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts

    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        return Contact.objects.filter(id__in=ids)


class SearchActionForm(forms.Form, SearchActionBaseForm):
    contacts = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        initial_contacts = self._pre_init(*args, **kwargs)
        super(SearchActionForm, self).__init__(*args, **kwargs)
        self._post_init(initial_contacts)

class ContactsAdminForm(SearchActionForm):
    subscribe_newsletter = forms.BooleanField(required=False)
    

