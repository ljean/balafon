# -*- coding: utf-8 -*-
"""search views and actions"""

import json
import xlwt

from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect, popup_close
from coop_cms.models import Newsletter
from wkhtmltopdf.views import PDFTemplateView

from sanza.permissions import can_access
from sanza.utils import logger, log_error, HttpResponseRedirectMailtoAllowed
from sanza.Crm.models import Entity, Contact, Group, Action, Opportunity, City, CustomField
from sanza.Crm import settings as crm_settings
from sanza.Emailing.models import Emailing
from sanza.Emailing.forms import NewEmailingForm
from sanza.Search.models import Search
from sanza.Search.forms import (
    ActionForContactsForm, FieldChoiceForm, GroupForContactsForm, QuickSearchForm, PdfTemplateForm, SearchForm,
    SearchNameForm, get_field_form, ContactsAdminForm
)


#@transaction.commit_manually
def filter_icontains_unaccent(qs, field, text):
    if crm_settings.is_unaccent_filter_supported():
        qs = qs.extra(
            where=[u"UPPER(unaccent("+field+")) LIKE UPPER(unaccent(%s))"],
            params=[u"%{0}%".format(text)]
        )
        return list(qs)    
    return list(qs.filter(**{field+"__icontains": text}))


@user_passes_test(can_access)
def quick_search(request):
    if request.method == "POST":
        form = QuickSearchForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            
            qs = Entity.objects.filter(is_single_contact=False)
            entities_by_name = filter_icontains_unaccent(qs, 'name', text)    
            
            qs = Contact.objects.all()#.filter(has_left=False)
            contacts_by_name = filter_icontains_unaccent(qs, 'lastname', text)
            
            for e in entities_by_name:
                setattr(e, 'is_entity', True)
                for c in e.contact_set.all():
                    try:
                        # avoid duplicates
                        contacts_by_name.remove(c)
                    except ValueError:
                        pass
            contacts = entities_by_name + contacts_by_name
            contacts.sort(key=lambda x: getattr(x, 'name', getattr(x, 'lastname', '')))
            
            qs = Group.objects.all()
            groups_by_name = filter_icontains_unaccent(qs, 'name', text)
            
            contacts_by_email = Contact.objects.filter(
                Q(email__icontains=text) | (Q(email="") & Q(entity__email__icontains=text)))
            
            cities_by_name = []
            for city in City.objects.filter(name__icontains=text):
                entities_count, contacts_count = city.contact_set.count(), city.entity_set.count()
                if entities_count + contacts_count:
                    cities_by_name.append((city, entities_count, contacts_count))
            
            contacts_by_phone = list(Contact.objects.filter(Q(mobile__icontains=text) | Q(phone__icontains=text)))
            contacts_by_phone += list(Entity.objects.filter(phone__icontains=text))
            
            context_dict = {
                'contacts_by_phone': contacts_by_phone,
                'cities_by_name': cities_by_name,
                'text': text,
                'contacts_by_email': contacts_by_email,
                'contacts': contacts,
                'groups_by_name': groups_by_name,
            }
                
            return render_to_response(
                'Search/quicksearch_results.html',
                context_dict,
                context_instance=RequestContext(request)
            )
    else:
        raise Http404


@user_passes_test(can_access)
def search(request, search_id=0, group_id=0, opportunity_id=0, city_id=0):
    message = ''
    results = []
    search_obj = None
    field_choice_form = FieldChoiceForm()
    contains_refuse_newsletter = False
    data = None
    contacts_count = 0
    has_empty_entities = False
    group = opportunity = city = None
    contacts_display = False

    if request.method == "POST":
        data = request.POST
    elif group_id:
        group = get_object_or_404(Group, id=group_id)
        data = {"gr0-_-group-_-0": group_id}
    elif opportunity_id:
        opportunity = get_object_or_404(Opportunity, id=opportunity_id)
        data = {"gr0-_-opportunity-_-0": opportunity_id}
    elif city_id:
        city = get_object_or_404(City, id=city_id)
        data = {"gr0-_-city-_-0": city_id}
            
    if data:
        search_form = SearchForm(data)
        if search_form.is_valid():
            contacts_display = search_form.contacts_display
            
            if not contacts_display:
                results, contacts_count, has_empty_entities = search_form.get_contacts_by_entity()
                contains_refuse_newsletter = search_form.contains_refuse_newsletter
            else:
                results = search_form.get_contacts()
                contacts_count, has_empty_entities = len(results), False
                contains_refuse_newsletter = search_form.contains_refuse_newsletter
            
            if not results:
                message = _(u'Sorry, no results found')
    else:
        search_obj = get_object_or_404(Search, id=search_id) if search_id else None
        search_form = SearchForm(instance=search_obj)
    
    entities_count = 0 if contacts_display else len(results)
    return render_to_response(
        'Search/search.html',
        {
            'request': request,
            'results': results,
            'nb_results_by_page': getattr(settings, 'SANZA_SEARCH_NB_IN_PAGE', 50),
            'field_choice_form': field_choice_form,
            'message': message,
            'has_empty_entities': has_empty_entities,
            'search_form': search_form,
            'search': search_obj,
            'contacts_count': contacts_count,
            'entities_count': entities_count,
            'contains_refuse_newsletter': contains_refuse_newsletter,
            'group': group,
            'opportunity': opportunity,
            'city': city,
            'contacts_display': contacts_display,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def save_search(request, search_id):
    try:
        search_id = int(search_id)
        if search_id:
            get_object_or_404(Search, id=search_id)
    except ValueError:
        raise Http404
    
    if request.method == "POST":
        form = SearchNameForm(request.POST)
        if form.is_valid():
            search_obj = form.cleaned_data['name']
            search_fields = form.cleaned_data['search_fields']
            search_fields['name'] = search_obj.name
            search_form = SearchForm(search_fields, instance=search_obj, save=True)
            if search_form.is_valid():
                search_form.save_search()
                return HttpResponseRedirect(reverse('search', args=[search_obj.id]))
    else:
        if search_id:
            search_obj = get_object_or_404(Search, id=search_id)
            initial = {'name': search_obj.name, 'search_id': search_id}
        else:
            initial = {'search_id': 0}
        form = SearchNameForm(initial=initial)
    
    return render_to_response(
        'Search/search_name.html',
        {
            'form': form,
            'search_id': search_id,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def get_field(request, name):
    block = request.GET.get('block')
    count = request.GET.get('count')
    if not (block and count):
        raise Http404
    try:
        form_class = get_field_form(name)
        t = Template('{{form.as_it_is}}')
        c = Context({'form': form_class(block, count)})
        return HttpResponse(json.dumps({'form': t.render(c)}), content_type="application/json")
    except KeyError:
        raise Http404
    except Exception, msg:
        logger.exception("get_field")
        raise


@user_passes_test(can_access)
def mailto_contacts(request, bcc):
    """Open the mail client in order to send email to contacts"""
    if request.method == "POST":
        nb_limit = getattr(settings, 'SANZA_MAILTO_LIMIT', 25)
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            emails = search_form.get_contacts_emails()
            if emails:
                if len(emails)>nb_limit:
                    if getattr(settings, 'SANZA_MAILTO_LIMIT_AS_TEXT', False):
                        #conf49 : La poste required only ' ' as separator
                        #return HttpResponse(',\r\n'.join(emails), mimetype='text/plain')
                        return HttpResponse(', '.join(emails), content_type='text/plain')
                    else:
                        index_from, email_groups = 0, []
                        nb_emails = len(emails)
                        while True:
                            index_to = index_from + nb_limit
                            if index_to < nb_emails:
                                email_groups.append(emails[index_from:index_to])
                            else:
                                email_groups.append(emails[index_from:])
                                break
                            index_from = index_to
                        return render_to_response(
                            'Search/mailto_groups.html',
                            {'bcc': int(bcc), 'email_groups': email_groups, 'nb_limit': nb_limit},
                            context_instance=RequestContext(request)
                        )
                else:
                    mailto = u'mailto:'
                    if int(bcc): mailto += '?bcc='
                    mailto += ','.join(emails)
                    return HttpResponseRedirectMailtoAllowed(mailto)
            else:
                return HttpResponse(_(u'Mailto: Error, no emails defined'), content_type='text/plain')
    raise Http404


@user_passes_test(can_access)
def view_search_list(request):
    searches = Search.objects.all()#.order_by("-created")
    return render_to_response(
        'Search/search_list.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def create_emailing(request):
    try:
        if request.method == "POST":
            if "create_emailing" in request.POST:
                #called by the colorbox
                form = NewEmailingForm(request.POST)
                if form.is_valid():
                    newsletter_id = form.cleaned_data['newsletter']
                    if newsletter_id:
                        newsletter = Newsletter.objects.get(id=newsletter_id)
                    else:
                        newsletter = Newsletter.objects.create(subject=form.cleaned_data['subject'])

                    subscription_type = form.cleaned_data['subscription_type']

                    contacts = form.get_contacts()

                    emailing = Emailing.objects.create(
                        newsletter=newsletter,
                        subscription_type=subscription_type,
                        lang=form.cleaned_data['lang']
                    )
                    for c in contacts:
                        emailing.send_to.add(c)

                    emailing.from_email = form.cleaned_data['from_email']

                    emailing.save()
                    
                    return HttpResponseRedirect(newsletter.get_absolute_url())
                else:
                    return render_to_response(
                        'Search/create_action_for_contacts.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    form = NewEmailingForm(initial={'contacts': contacts})
                    return render_to_response(
                        'Search/new_emailing.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
    except Exception, msg:
        logger.exception("create_emailing")
        raise
    raise Http404


@user_passes_test(can_access)
def export_contacts_as_excel(request):
    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            contacts = search_form.get_contacts()
            if not search_form.contacts_display:
                #if the form alread has a sort criteria: don't sort again
                contacts.sort(key=lambda x: u"{0}-{1}-{2}".format(x.entity, x.lastname, x.firstname))
            
            #create the excel document
            wb = xlwt.Workbook()
            ws = wb.add_sheet('sanza')

            fields = ['id', 'get_gender_display', 'lastname', 'firstname', 'title', 'get_entity_name', 'job', 'role',
                'get_address', 'get_address2', 'get_address3', 'get_zip_code', 'get_cedex', 'get_city',
                'get_foreign_country', 'mobile', 'get_phone', 'get_email', 'birth_date']
            
            #header
            header_style = xlwt.easyxf('font: bold 1; pattern: pattern solid, fore-colour gray25;')
            #create a map of verbose name for each field
            field_dict = dict([(f.name, _(f.verbose_name).capitalize()) for f in Contact._meta.fields])
            field_dict['foreign_country'] = _(u"Country")
            field_dict['entity_name'] = _(u"Entity")
            
            #Add custom fields
            for cf in CustomField.objects.filter(export_order__gt=0).order_by('export_order'):
                if cf.model == CustomField.MODEL_CONTACT:
                    fields.append('custom_field_'+cf.name)
                    field_dict['custom_field_'+cf.name] = cf.label
                elif cf.model == CustomField.MODEL_ENTITY:
                    fields.append('entity_custom_field_'+cf.name)
                    field_dict['entity_custom_field_'+cf.name] = cf.label
            
            for i, f in enumerate(fields):
                if f[:4] == 'get_':
                    f = f[4:]
                    if f[-8:] == '_display':
                        f = f[:-8]
                #print the verbose name if exists, the field name if not
                value = field_dict.get(f, f)
                ws.write(0, i, value, header_style)
            
            style = xlwt.Style.default_style
            for i, c in enumerate(contacts):
                for j, fn in enumerate(fields):
                    f = getattr(c, fn)
                    if callable(f):
                        f = f()
                    if fn == 'role':
                        f = u", ".join([r.name for r in f.all()])
                    if f:
                        ws.write(i+1, j, unicode(f), style)

            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename={0}.xls'.format('sanza')
            wb.save(response)
            return response
        else:
            logger.error(unicode(search_form.errors))
    raise Http404


@user_passes_test(can_access)
@popup_redirect
def create_action_for_contacts(request):
    if request.method == "POST":
        if "create_actions" in request.POST:
            form = ActionForContactsForm(request.POST)
            if form.is_valid():
                contacts = form.get_contacts()
                for contact in contacts:
                    #create actions
                    kwargs = dict(form.cleaned_data)
                    for k in ('date', 'time', 'contacts'): del kwargs[k]
                    action = Action.objects.create(**kwargs)
                    action.contacts.add(contact)
                    action.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    _(u"{0} actions have been created".format(len(contacts)))
                )
                return HttpResponseRedirect(reverse('crm_board_panel'))
            else:
                return render_to_response(
                    'Search/create_action_for_contacts.html',
                    {'form': form},
                    context_instance=RequestContext(request)
                )
        else:
            search_form = SearchForm(request.POST)
            if search_form.is_valid():
                contacts = search_form.get_contacts()
                if contacts:
                    form = ActionForContactsForm(initial={'contacts': contacts})
                    return render_to_response(
                        'Search/create_action_for_contacts.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
                else:
                    return render_to_response(
                        'sanza/message_dialog.html',
                        {
                            'title': _('Create action for contacts'),
                            'message': _(u'The search results contains no contacts')
                        },
                        context_instance=RequestContext(request)
                    )
    raise Http404


@user_passes_test(can_access)
@popup_redirect
def add_contacts_to_group(request):
    try:
        if request.method == "POST":
            if "add_to_group" in request.POST:
                form = GroupForContactsForm(request.POST)
                if form.is_valid():
                    contacts = form.get_contacts()
                    groups = form.cleaned_data['groups']
                    
                    if form.cleaned_data["on_contact"]:
                        for g in groups:
                            for c in contacts:
                                g.contacts.add(c)
                            g.save()
                        messages.add_message(request, messages.SUCCESS, _(u"{0} contacts have been added to groups".format(len(contacts))))
                    else:
                        entities = set([c.entity for c in contacts])
                        for g in groups:
                            for entity in entities:
                                g.entities.add(entity)
                            g.save()
                        messages.add_message(request, messages.SUCCESS, _(u"{0} entities have been added to groups".format(len(entities))))
                    return HttpResponseRedirect(reverse('crm_board_panel'))
                else:
                    return render_to_response(
                        'Search/add_contacts_to_group.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    if contacts:
                        form = GroupForContactsForm(initial={'contacts': contacts})
                        return render_to_response(
                            'Search/add_contacts_to_group.html',
                            {'form': form},
                            context_instance=RequestContext(request)
                        )
                    else:
                        return render_to_response(
                            'sanza/message_dialog.html',
                            {
                                'title': _('Add contacts to group'),
                                'message': _(u'The search results contains no contacts')
                            },
                            context_instance=RequestContext(request)
                        )
    except Exception, msg:
        logger.exception("add_contacts_to_group")
        raise
    raise Http404


@user_passes_test(can_access)
@popup_close
def contacts_admin(request):
    
    if not request.user.is_superuser:
        raise PermissionDenied
    
    try:
        if request.method == "POST":
            if "contacts_admin" in request.POST:
                form = ContactsAdminForm(request.POST)
                if form.is_valid():
                    nb_contacts = 0
                    contacts = form.get_contacts()
                    subscribe = form.cleaned_data['subscribe_newsletter']
                    for c in contacts:
                        if c.accept_newsletter != subscribe:
                            c.accept_newsletter = subscribe
                            c.save()
                            nb_contacts += 1
                    if subscribe:
                        messages.add_message(request, messages.SUCCESS,
                            _(u"{0} contacts have subscribe to the newsletter".format(nb_contacts)))
                    else:
                        messages.add_message(request, messages.SUCCESS,
                            _(u"{0} contacts have unsubscribe to the newsletter".format(nb_contacts)))
                    return None #popup_close will return js code to close the popup
                else:
                    return render_to_response(
                        'Search/contacts_admin_form.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    if contacts:
                        form = ContactsAdminForm(initial={'contacts': contacts})
                        return render_to_response(
                            'Search/contacts_admin_form.html',
                            {'form': form},
                            context_instance=RequestContext(request)
                        )
                    else:
                        return render_to_response(
                            'sanza/message_dialog.html',
                            {
                                'title': _('Contacts admin'),
                                'message': _(u'The search results contains no contacts')
                            },
                            context_instance=RequestContext(request)
                        )
    except Exception, msg:
        logger.exception("contacts_admin")
        raise
    raise Http404


@user_passes_test(can_access)
@popup_redirect
@log_error
def export_to_pdf(request):
    try:
        if request.method == "POST":
            if "export_to_pdf" in request.POST:
                #called by the colorbox
                form = PdfTemplateForm(request.POST)
                if form.is_valid():
                    template_name = form.cleaned_data['template']
                    contacts = form.get_contacts()
                    context = {
                        "contacts": contacts,
                        "search_dict": json.loads(form.cleaned_data['search_dict']),
                    }
                    
                    context = form.patch_context(context)
                    
                    pdf_options = getattr(settings, 'SANZA_PDF_OPTIONS', None)
                    if pdf_options is None:
                        cmd_options = {'margin-top': 0, 'margin-bottom': 0, 'margin-right': 0, 'margin-left': 0, }
                    else:
                        cmd_options = pdf_options.get(template_name, {})
                    
                    pdf_view = PDFTemplateView(
                        filename='sanza.pdf',
                        template_name=template_name,
                        request=request,
                        cmd_options=cmd_options)
                    return pdf_view.render_to_response(context)

                else:
                    return render_to_response(
                        'Search/export_to_pdf.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    search_dict = json.dumps(search_form.serialize())
                    form = PdfTemplateForm(initial={'contacts': contacts, 'search_dict': search_dict})
                    return render_to_response(
                        'Search/export_to_pdf.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
    except Exception, msg:
        logger.exception("export_to_pdf")
        raise
    raise Http404
