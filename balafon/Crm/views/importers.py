# -*- coding: utf-8 -*-
"""import data from files"""

from datetime import datetime
import os.path
import re

from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.messages import success, error
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from balafon.Crm import models, forms
from balafon.Crm import settings as crm_settings
from balafon.Crm.utils import unicode_csv_reader, resolve_city, check_city_exists
from balafon.permissions import can_access


@user_passes_test(can_access)
def new_contacts_import(request):
    """view"""
    if request.method == 'POST':
        instance = models.ContactsImport(imported_by=request.user)
        form = forms.ContactsImportForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            import_file = form.cleaned_data['import_file']
            contact_import = form.save()
            if not contact_import.name:
                contact_import.name = os.path.splitext(import_file.name)[0]
                contact_import.save()
            return HttpResponseRedirect(reverse('crm_confirm_contacts_import', args=[contact_import.id]))
    else:
        form = forms.ContactsImportForm()

    return render_to_response(
        'Crm/new_contacts_import.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


def _fill_contact_data(fields, row):
    """fill the contact data from file"""
    contact_data = {}
    for i, field in enumerate(fields):
        try:
            contact_data[field] = row[i]
        except IndexError:
            contact_data[field] = ''
        if field == 'gender':
            if contact_data[field]:
                if contact_data[field] in ('M', 'M.', 'Mr', 'Mr.'):
                    contact_data[field] = models.Contact.GENDER_MALE
                elif crm_settings.ALLOW_COUPLE_GENDER and contact_data[field] in ('Mrs and Mr', 'Mme et M.'):
                    contact_data[field] = models.Contact.GENDER_COUPLE
                else:
                    contact_data[field] = models.Contact.GENDER_FEMALE

        #Copy value of entity fields with _ rather than . for using it in template
        if field.find('.') > 0:
            contact_data[field.replace('.', '_')] = contact_data[field]

        if field.find('city') >= 0 and contact_data[field]:
            field = field.replace('.', '_')

        if field.find("accept_") == 0:
            contact_data[field] = True if contact_data[field] else False

    return contact_data


def _get_subcription_field_name(subscription_type):
    return 'accept_' + slugify(subscription_type.name).replace('-', '_')


def _set_contact_and_entity(contact_data, entity_dict, extract_from_email):
    """format properly name and entity"""
    name = u"< {0} >".format(_(u"Unknown"))
    email_providers = (
        'free', 'gmail', 'yahoo', 'yahoo.co', 'wanadoo', 'orange', 'sfr', 'laposte',
        'hotmail', 'neuf', 'club-internet', 'voila', 'aol', 'live', 'ymail',
    )
    if not contact_data['entity']:
        entity = u''
        if extract_from_email:
            res = re.match(r'(?P<name>.+)@(?P<cpn>.+)\.(?P<ext>.+)', contact_data['email'])
            if res:
                regex_value = res.groups(0)
                name, entity = regex_value[0], regex_value[1]
                #email = u'{0}@{1}.{2}'.format(name, entity, ext)
                if entity in email_providers:
                    entity = ""
        contact_data['entity'] = entity
    if not (contact_data['lastname'] or contact_data['firstname']):
        try:
            contact_data['firstname'], contact_data['lastname'] = [x.capitalize() for x in name.split('.')]
        except ValueError:
            contact_data['lastname'] = name.capitalize()

    if contact_data['entity']:
        entity_exist = models.Entity.objects.filter(name__iexact=contact_data['entity']).count() != 0
        contact_data['entity_exists'] = entity_exist or (contact_data['entity'] in entity_dict)
        entity_dict[contact_data['entity']] = True
    else:
        contact_data['entity_exists'] = False

    if contact_data['entity']:
        contact_queryset = models.Contact.objects.filter(entity__name=contact_data['entity'])
    else:
        contact_queryset = models.Contact.objects.filter(entity__is_single_contact=True)
    contact_count = contact_queryset.filter(
        lastname=contact_data['lastname'], firstname=contact_data['firstname']
    ).count()
    contact_data['contact_exists'] = contact_count != 0

    if contact_data['entity_type']:
        entity_type_exists = models.EntityType.objects.filter(name=contact_data['entity_type']).count() != 0
        contact_data['entity_type_exists'] = entity_type_exists


def _set_contact_roles(contact_data, role_dict):
    """set the contact role properly"""

    split_roles = lambda text, sep: [elt.strip() for elt in text.split(sep) if elt.strip()]
    roles = contact_data['role']
    if ';' in roles:
        roles = split_roles(roles, ";")
    elif ',' in roles:
        roles = split_roles(roles, ",")
    else:
        roles = [roles.strip()]

    contact_data['role'] = roles
    contact_data['role_exists'] = []
    for role in roles:
        contact_data['role_exists'].append(
            (models.EntityRole.objects.filter(name__iexact=role).count() != 0) or (role.lower() in role_dict)
        )
        role_dict[role.lower()] = True

    contact_data['roles'] = [
        {'name': role, 'exists': role_exists}
        for (role, role_exists) in zip(contact_data['role'], contact_data['role_exists'])
    ]


def _set_contact_groups(contact_data, groups_dict):
    """set the groups properly"""
    entity_groups = [
        group_name.strip() for group_name in contact_data['entity.groups'].strip().split(";") if group_name
    ]
    contact_data['entity_groups'] = []
    for group in entity_groups:
        exists = (models.Group.objects.filter(name__iexact=group).count() != 0) or (group in groups_dict)
        groups_dict[group] = True
        contact_data['entity_groups'].append({'name': group, 'exists': exists})

    contact_groups = [
        group_name.strip() for group_name in contact_data['groups'].strip().split(";") if group_name
    ]
    contact_data['contact_groups'] = []
    for group in contact_groups:
        exists = (models.Group.objects.filter(name__iexact=group).count() != 0) or (group in groups_dict)
        groups_dict[group] = True
        contact_data['contact_groups'].append({'name': group, 'exists': exists})


def read_contacts(reader, fields, extract_from_email):
    """read contacts data from csv file"""
    contacts = []
    entity_dict = {}
    role_dict = {}
    groups_dict = {}

    counter = 0
    for key, row in enumerate(reader):
        counter += 1

        if key == 0:
            #remove the header row
            continue

        contact_data = _fill_contact_data(fields, row)

        contact_data["entity_city_exists"] = check_city_exists(
            contact_data["entity_city"], contact_data["entity_zip_code"], contact_data["entity_country"]
        )
        contact_data["city_exists"] = check_city_exists(
            contact_data["city"], contact_data["zip_code"], contact_data["country"]
        )

        if not any(contact_data.values()):
            continue

        _set_contact_and_entity(contact_data, entity_dict, extract_from_email)

        _set_contact_roles(contact_data, role_dict)

        _set_contact_groups(contact_data, groups_dict)

        contacts.append(contact_data)

    total_contacts = counter
    return contacts, total_contacts


def get_imports_fields():
    """get the list of fields to import"""
    fields = [
        'gender', 'firstname', 'lastname', 'email', 'phone', 'mobile', 'job',
        'notes', 'role',
    ]

    for subscription_type in models.SubscriptionType.objects.all():
        fields += [
            _get_subcription_field_name(subscription_type)
        ]

    fields += [    'entity', 'entity.type', 'entity.description', 'entity.website', 'entity.email',
        'entity.phone', 'entity.fax', 'entity.notes',
        'entity.address', 'entity.address2', 'entity.address3',
        'entity.city', 'entity.cedex', 'entity.zip_code', 'entity.country',
        'address', 'address2', 'address3', 'city', 'cedex', 'zip_code', 'country',
        'entity.groups', 'groups', 'favorite_language', 'title', 'birth_date'
    ]

    #custom fields
    custom_fields_count = models.CustomField.objects.all().aggregate(Max('import_order'))['import_order__max']
    if not custom_fields_count:
        custom_fields_count = 0
    for i in xrange(custom_fields_count):
        fields.append('cf_{0}'.format(i+1))

    custom_fields = []
    for index_ in xrange(1, custom_fields_count+1):
        try:
            custom_field = models.CustomField.objects.get(import_order=index_)
            custom_fields.append(custom_field)
        except models.CustomField.DoesNotExist:
            custom_fields.append(None)
        except models.CustomField.MultipleObjectsReturned:
            raise Exception(_(u"There are several custom fields with index {0}").format(index_))

    return fields, custom_fields


@user_passes_test(can_access)
def contacts_import_template(request):
    """download the contacts import template"""

    fields, custom_fields = get_imports_fields()

    cols = fields[:len(fields) - len(custom_fields)] + custom_fields

    template_file = u";".join([u'"{0}"'.format(unicode(col)) for col in cols])+u"\n"

    return HttpResponse(template_file, content_type="text/csv", )


def _create_contact(contact_data, contacts_import, entity_dict):
    """create a contact from import file"""
    #Entity
    if settings.DEBUG:
        try:
            print contact_data['entity'], contact_data['lastname']
        except UnicodeError:
            print '##!'

    if not contact_data['entity.type']:
        entity_type = contacts_import.entity_type
    else:
        entity_type = models.EntityType.objects.get_or_create(name=contact_data['entity.type'])[0]

    if contact_data['entity_exists']:
        entity = models.Entity.objects.filter(name__iexact=contact_data['entity'])[0]
    else:
        if contact_data['entity']:
            entity = models.Entity.objects.create(
                name=contact_data['entity'], type=entity_type, imported_by=contacts_import)
        else:
            entity = models.Entity.objects.get_or_create(
                contact__lastname=contact_data['lastname'],
                contact__firstname=contact_data['firstname'],
                is_single_contact=True
            )[0]
            entity.name = u"{0} {1}".format(contact_data['firstname'], contact_data['lastname'])
            entity.imported_by = contacts_import
            entity.save()

    if entity.is_single_contact:
        is_first_for_entity = True
    else:
        is_first_for_entity = entity.name not in entity_dict
        entity_dict[entity.name] = True

    #Contact
    contact = models.Contact.objects.get_or_create(
        entity=entity, firstname=contact_data['firstname'], lastname=contact_data['lastname']
    )[0]
    contact.imported_by = contacts_import

    for group in contacts_import.groups.all():
        group.contacts.add(contact)
        group.save()

    return contact, is_first_for_entity


def _set_contact_fields(contact, contact_data, fields, complex_fields, default_department):
    """set the contact fields"""

    for field_name in fields:
        if field_name in complex_fields:
            continue
        obj = contact
        try:
            pre_field, field = field_name.split('.')
            obj = getattr(obj, pre_field)
        except ValueError:
            field = field_name
        if contact_data[field_name] and field != 'city':
            setattr(obj, field, contact_data[field_name])

    if contact_data['city']:
        contact.city = resolve_city(
            contact_data['city'],
            contact_data['zip_code'],
            contact_data['country'],
            default_department
        )

    if contact_data['entity.city']:
        contact.entity.city = resolve_city(
            contact_data['entity.city'],
            contact_data['entity.zip_code'],
            contact_data['entity.country'],
            default_department
        )

    if contact_data['role']:
        for role_exists, role in zip(contact_data['role_exists'], contact_data['role']):
            if role_exists:
                contact.role.add(models.EntityRole.objects.filter(name__iexact=role)[0])
            else:
                contact.role.add(models.EntityRole.objects.create(name=role))

    if contact_data['birth_date']:
        value = contact_data['birth_date']
        date_value = None
        date_formats = ["%Y-%m-%d", "%d/%m/%Y"]
        for date_format in date_formats:
            try:
                date_value = datetime.strptime(value, date_format).date()
                break
            except ValueError:
                date_value = None
        contact.birth_date = date_value

    for (is_entity, key) in ((True, 'entity_groups'), (False, 'contact_groups')):
        for group_data in contact_data[key]:
            group, group_exists = group_data['name'], group_data['exists']
            if group_exists:
                group = models.Group.objects.filter(name__iexact=group)[0]
            else:
                group = models.Group.objects.get_or_create(name=group)[0]
            if is_entity:
                if contact.entity.is_single_contact:
                    group.contacts.add(contact)
                else:
                    group.entities.add(contact.entity)
            else:
                group.contacts.add(contact)
            group.save()

    contact.entity.save()
    contact.save()
    contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()


def _set_custom_fields(contact, contact_data, cf_names, custom_fields, is_first_for_entity):
    """set the contacts custom fields"""
    for name, custom_field in zip(cf_names, custom_fields):
        value = contact_data[name]
        if custom_field and value:
            if custom_field.model == models.CustomField.MODEL_ENTITY and is_first_for_entity:
                custom_field_value = models.EntityCustomFieldValue.objects.get_or_create(
                    custom_field=custom_field, entity=contact.entity
                )[0]
                custom_field_value.value = value
                custom_field_value.save()

            if custom_field.model == models.CustomField.MODEL_CONTACT:
                custom_field_value = models.ContactCustomFieldValue.objects.get_or_create(
                    custom_field=custom_field, contact=contact
                )[0]
                custom_field_value.value = value
                custom_field_value.save()


def _set_subscriptions(contact, contact_data):
    """set the contacts subscriptions (newsletters, ...)"""
    for subscription_type in models.SubscriptionType.objects.all():

        try:
            # if the subscription exist : keep it as it is
            models.Subscription.objects.get(contact=contact, subscription_type=subscription_type)

        except models.Subscription.DoesNotExist:
            # if it doesn't exist and that the corresponding cell is True in file, create it
            field_name = _get_subcription_field_name(subscription_type)
            if contact_data[field_name]:
                models.Subscription.objects.create(
                    contact=contact,
                    subscription_type=subscription_type,
                    accept_subscription=True,
                    subscription_date=datetime.now()
                )


@user_passes_test(can_access)
def confirm_contacts_import(request, import_id):
    """confirm contacts import: do it really"""
    fields, custom_fields = get_imports_fields()

    custom_fields_count = len(custom_fields)
    cf_names = ['cf_{0}'.format(idx) for idx in xrange(1, custom_fields_count+1)]

    contacts_import = get_object_or_404(models.ContactsImport, id=import_id)
    try:
        if request.method == 'POST':
            form = forms.ContactsImportConfirmForm(request.POST, instance=contacts_import)

            if form.is_valid():

                reader = unicode_csv_reader(
                    contacts_import.import_file, form.cleaned_data['encoding'], delimiter=form.cleaned_data['separator']
                )
                contacts, total_contacts = read_contacts(reader, fields, form.cleaned_data['entity_name_from_email'])
                default_department = form.cleaned_data['default_department']
                contacts_import = form.save()

                complex_fields = (
                    'entity', 'city', 'entity.city', 'role', 'entity.groups',
                    'contacts.groups', 'country', 'entity.country', 'entity.type',
                )

                if 'create_contacts' in request.POST:
                    #create entities
                    entity_dict = {}
                    for contact_data in contacts:
                        contact, is_first_for_entity = _create_contact(contact_data, contacts_import, entity_dict)
                        _set_contact_fields(contact, contact_data, fields, complex_fields, default_department)
                        _set_custom_fields(contact, contact_data, cf_names, custom_fields, is_first_for_entity)
                        _set_subscriptions(contact, contact_data)
                    return HttpResponseRedirect(reverse("balafon_homepage"))
                else:
                    form = forms.ContactsImportConfirmForm(instance=contacts_import)
            else:

                reader = unicode_csv_reader(
                    contacts_import.import_file, contacts_import.encoding, delimiter=contacts_import.separator
                )
                contacts, total_contacts = read_contacts(reader, fields, contacts_import.entity_name_from_email)
        else:
            form = forms.ContactsImportConfirmForm(instance=contacts_import)
            reader = unicode_csv_reader(
                contacts_import.import_file, contacts_import.encoding, delimiter=contacts_import.separator
            )
            contacts, total_contacts = read_contacts(reader, fields, contacts_import.entity_name_from_email)

        return render_to_response(
            'Crm/confirm_contacts_import.html',
            {'form': form, 'contacts': contacts, 'nb_contacts': len(contacts), 'total_contacts': total_contacts},
            context_instance=RequestContext(request)
        )

    except UnicodeDecodeError:
        error(
            request,
            _(u"An error occurred while reading the csv file. You should check that the file encoding is correct.")
        )
    except Exception, msg:  # pylint: disable broad-except
        error(
            request,
            u'{0}: {1}'.format(
                _(u"An error occurred. You should check that the file is a valid csv file."),
                msg
            )
        )

    return HttpResponseRedirect(reverse("crm_new_contacts_import"))



@user_passes_test(can_access)
def unsubscribe_contacts_import(request):
    """view"""
    if request.method == 'POST':
        form = forms.UnsubscribeContactsImportForm(request.POST, request.FILES)
        if form.is_valid():
            input_file = request.FILES['input_file']

            reader = unicode_csv_reader(input_file, "utf-8", delimiter=";")

            contacts_count = 0
            try:
                for line in reader:
                    email = line[0]
                    contacts = models.Contact.objects.filter(email=email)
                    for contact in contacts:
                        for index_, subscription in enumerate(contact.subscription_set.all()):
                            if index_ == 0:
                                contacts_count += 1
                            subscription.accept_subscription = False
                            subscription.unsubscription_date = datetime.now()
                            subscription.save()
                success(request, _(u"{0} contacts have been unsubscribed").format(contacts_count))

            except UnicodeDecodeError:
                error(request, _(u"Unicode error while reading the file"))

            return HttpResponseRedirect(reverse('balafon_homepage'))
    else:
        form = forms.UnsubscribeContactsImportForm()

    return render_to_response(
        'Crm/unsubscribe_contacts_import.html',
        {'form': form},
        context_instance=RequestContext(request)
    )
