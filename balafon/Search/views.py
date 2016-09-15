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
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext, Context, Template
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect, popup_close
from coop_cms.models import Newsletter
from coop_cms.utils import paginate
from wkhtmltopdf.views import PDFTemplateView

from balafon.permissions import can_access, is_admin
from balafon.utils import logger, log_error, HttpResponseRedirectMailtoAllowed
from balafon.Crm.models import Entity, Contact, Group, Action, Opportunity, City, CustomField, Subscription
from balafon.Crm import settings as crm_settings
from balafon.Emailing.models import Emailing
from balafon.Emailing.forms import NewEmailingForm
from balafon.Search.models import Search
from balafon.Search.forms import (
    ActionForContactsForm, FieldChoiceForm, GroupForContactsForm, QuickSearchForm, PdfTemplateForm, SearchForm,
    SearchNameForm, get_field_form, SubscribeContactsAdminForm
)


def filter_icontains_unaccent(queryset, field, text):
    if crm_settings.is_unaccent_filter_supported():
        queryset = queryset.extra(
            where=[u"UPPER(unaccent("+field+")) LIKE UPPER(unaccent(%s))"],
            params=[u"%{0}%".format(text)]
        )
        return list(queryset)
    return list(queryset.filter(**{field+"__icontains": text}))


@user_passes_test(can_access)
def quick_search(request):
    if request.method == "POST":
        form = QuickSearchForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            
            queryset = Entity.objects.filter(is_single_contact=False)
            entities_by_name = filter_icontains_unaccent(queryset, 'name', text)
            
            queryset = Contact.objects.all()#.filter(has_left=False)
            contacts_by_name = filter_icontains_unaccent(queryset, 'lastname', text)
            
            for entity in entities_by_name:
                setattr(entity, 'is_entity', True)
                for contact in entity.contact_set.all():
                    try:
                        # avoid duplicates
                        contacts_by_name.remove(contact)
                    except ValueError:
                        pass
            contacts = entities_by_name + contacts_by_name
            contacts.sort(key=lambda x: getattr(x, 'name', getattr(x, 'lastname', '')))
            
            queryset = Group.objects.all()
            groups_by_name = filter_icontains_unaccent(queryset, 'name', text)
            
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

    page_obj = paginate(request, results, getattr(settings, 'BALAFON_SEARCH_NB_IN_PAGE', None) or 50)

    return render_to_response(
        'Search/search.html',
        {
            'page_obj': page_obj,
            'results': list(page_obj),
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
        the_template = Template('{{form.as_it_is}}')
        the_context = Context({'form': form_class(block, count)})
        return HttpResponse(json.dumps({'form': the_template.render(the_context)}), content_type="application/json")
    except KeyError:
        raise Http404
    except Exception as msg:
        logger.exception("get_field")
        raise


@user_passes_test(can_access)
def mailto_contacts(request, bcc):
    """Open the mail client in order to send email to contacts"""
    if request.method == "POST":
        nb_limit = getattr(settings, 'BALAFON_MAILTO_LIMIT', 25) or 25
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            emails = search_form.get_contacts_emails()
            if emails:
                if len(emails) > nb_limit:
                    if getattr(settings, 'BALAFON_MAILTO_LIMIT_AS_TEXT', False):
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
    searches = Search.objects.all()
    page_obj = paginate(request, searches, 50)

    return render_to_response(
        'Search/search_list.html',
        {
            'searches': list(page_obj),
            'page_obj': page_obj,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def create_emailing(request):
    try:
        if request.method == "POST":
            if "create_emailing" in request.POST:
                # called by the colorbox
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
                    for contact in contacts:
                        emailing.send_to.add(contact)

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
    except Exception as msg:
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
                # if the form already has a sort criteria: don't sort again
                contacts.sort(key=lambda x: u"{0}-{1}-{2}".format(x.entity, x.lastname, x.firstname))
            
            # create the excel document
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('balafon')

            fields = [
                'id', 'get_gender_display', 'lastname', 'firstname', 'title', 'get_entity_name', 'job', 'role',
                'get_address', 'get_address2', 'get_address3', 'get_zip_code', 'get_cedex', 'get_city',
                'get_foreign_country', 'mobile', 'get_phone', 'get_email', 'birth_date'
            ]
            
            # header
            header_style = xlwt.easyxf('font: bold 1; pattern: pattern solid, fore-colour gray25;')
            # create a map of verbose name for each field
            field_dict = dict([(field.name, _(field.verbose_name).capitalize()) for field in Contact._meta.fields])
            field_dict['foreign_country'] = _(u"Country")
            field_dict['entity_name'] = _(u"Entity")
            
            # Add custom fields
            for cf in CustomField.objects.filter(export_order__gt=0).order_by('export_order'):
                if cf.model == CustomField.MODEL_CONTACT:
                    fields.append('custom_field_'+cf.name)
                    field_dict['custom_field_'+cf.name] = cf.label
                elif cf.model == CustomField.MODEL_ENTITY:
                    fields.append('entity_custom_field_'+cf.name)
                    field_dict['entity_custom_field_'+cf.name] = cf.label
            
            for index, field in enumerate(fields):
                if field[:4] == 'get_':
                    field = field[4:]
                    if field[-8:] == '_display':
                        field = field[:-8]
                # print the verbose name if exists, the field name if not
                value = field_dict.get(field, field)
                worksheet.write(0, index, value, header_style)
            
            style = xlwt.Style.default_style
            for index, contact in enumerate(contacts):
                for index2, field_name in enumerate(fields):
                    field = getattr(contact, field_name)

                    if field_name == 'role':
                        field = u", ".join([r.name for r in field.all()])

                    elif callable(field):
                        field = field()

                    if field:
                        worksheet.write(index+1, index2, unicode(field), style)

            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename={0}.xls'.format('balafon')
            workbook.save(response)
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
                    # create actions for each contact
                    kwargs = dict(form.cleaned_data)
                    for key in ('date', 'time', 'contacts'):
                        del kwargs[key]
                    action = Action.objects.create(**kwargs)
                    if action.type and action.type.default_status:
                        action.status = action.type.default_status
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
                        'balafon/message_dialog.html',
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
                            'balafon/message_dialog.html',
                            {
                                'title': _('Add contacts to group'),
                                'message': _(u'The search results contains no contacts')
                            },
                            context_instance=RequestContext(request)
                        )
    except Exception as msg:
        logger.exception("add_contacts_to_group")
        raise
    raise Http404


@user_passes_test(is_admin)
@popup_close
def subscribe_contacts_admin(request):
    
    if not request.user.is_superuser:
        raise PermissionDenied
    
    try:
        if request.method == "POST":
            if "subscribe_contacts_admin" in request.POST:
                form = SubscribeContactsAdminForm(request.POST)
                if form.is_valid():
                    nb_contacts = 0
                    contacts = form.get_contacts()
                    subscription_type = form.cleaned_data['subscription_type']
                    subscribe = form.cleaned_data['subscribe']

                    for contact in contacts:

                        if subscribe:
                            subscription, created = Subscription.objects.get_or_create(
                                contact=contact, subscription_type=subscription_type
                            )
                        else:
                            created = False
                            try:
                                subscription = Subscription.objects.get(
                                    contact=contact, subscription_type=subscription_type
                                )
                            except Subscription.DoesNotExist:
                                subscription = None

                        if created or (subscription and subscribe != subscription.accept_subscription):
                            subscription.accept_subscription = subscribe
                            subscription.save()
                            nb_contacts += 1

                    if subscribe:
                        messages.add_message(
                            request,
                            messages.SUCCESS,
                            _(u"{0} contacts have subscribe to the newsletter".format(nb_contacts))
                        )
                    else:
                        messages.add_message(
                            request,
                            messages.SUCCESS,
                            _(u"{0} contacts have unsubscribe to the newsletter".format(nb_contacts))
                        )

                    return None  # popup_close will return js code to close the popup
                else:
                    return render(
                        request,
                        'Search/subscribe_contacts_admin_form.html',
                        {'form': form}
                    )
            else:
                search_form = SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    if contacts:
                        form = SubscribeContactsAdminForm(initial={'contacts': contacts})
                        return render(
                            request,
                            'Search/subscribe_contacts_admin_form.html',
                            {'form': form}
                        )
                    else:
                        return render(
                            request,
                            'balafon/message_dialog.html',
                            {
                                'title': _('Subscribe contacts admin'),
                                'message': _(u'The search results contains no contacts')
                            }
                        )
    except Exception:
        logger.exception("search_subscribe_contacts_admin")
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
                    
                    pdf_options = getattr(settings, 'BALAFON_PDF_OPTIONS', None)
                    if pdf_options is None:
                        cmd_options = {'margin-top': 0, 'margin-bottom': 0, 'margin-right': 0, 'margin-left': 0, }
                    else:
                        cmd_options = pdf_options.get(template_name, {})
                    
                    pdf_view = PDFTemplateView(
                        filename='balafon.pdf',
                        template_name=template_name,
                        request=request,
                        cmd_options=cmd_options
                    )
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
    except Exception as msg:
        logger.exception("export_to_pdf")
        raise
    raise Http404
