# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponse, HttpResponseRedirect
from sanza.Search.forms import QuickSearchForm
from sanza.Crm.models import Entity, Contact, Group, Action, Opportunity, City, CustomField
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, Template
from sanza.Search import forms, models
import json
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from datetime import datetime
from sanza.Emailing.models import Emailing
import xlwt
from django.contrib.auth.decorators import login_required
from colorbox.decorators import popup_redirect, popup_close
from coop_cms.models import Newsletter
from sanza.Emailing.forms import NewEmailingForm
from sanza.Crm.forms import ActionForContactsForm, OpportunityForContactsForm, GroupForContactsForm
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q

@login_required
def quick_search(request):
    if request.method == "POST":
        form = QuickSearchForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            
            entities_by_name = Entity.objects.filter(name__icontains=text).order_by('name')
            
            contacts_by_name = Contact.objects.filter(lastname__icontains=text).order_by('lastname', 'firstname')
            
            groups_by_name = Group.objects.filter(name__icontains=text)
            
            cities_by_name = []
            for city in City.objects.filter(name__icontains=text):
                contacts_and_entities = list(city.contact_set.all()) + list(city.entity_set.all())
                if contacts_and_entities:
                    setattr(city, 'contacts_and_entities', contacts_and_entities)
                    cities_by_name.append(city)
            
            
            contacts_by_phone = list(Contact.objects.filter(Q(mobile__icontains=text) | Q(phone__icontains=text)))
            contacts_by_phone += list(Entity.objects.filter(phone__icontains=text))
            
            entities_title = _(u'Entities')
            contacts_title = _(u'Contacts')
            groups_title = _(u'Groups')
            cities_title = _(u'Contacts and entities by city')
            phones_title = _(u'Contacts and entities by phone number')
            
            return render_to_response(
                'Search/quicksearch_results.html',
                locals(),
                context_instance=RequestContext(request)
            )
    else:
        raise Http404
      
@login_required
def search(request, search_id=0, group_id=0):
    message = ''
    entities = []
    search=None
    field_choice_form = forms.FieldChoiceForm()
    contains_refuse_newsletter = False
    data = None
    contacts_count = 0
    has_empty_entities = False
    
    if request.method == "POST":
        data = request.POST
    elif group_id:
        data = {"gr0-_-group-_-0": group_id}
            
    if data:
        search_form = forms.SearchForm(data)
        if search_form.is_valid():
            entities, contacts_count, has_empty_entities = search_form.get_contacts_by_entity()
            contains_refuse_newsletter = search_form.contains_refuse_newsletter
            if not entities:
                message = _(u'Sorry, no results found')
    else:
        search = get_object_or_404(models.Search, id=search_id) if search_id else None
        search_form = forms.SearchForm(instance=search)
        
        
    return render_to_response(
        'Search/search.html',
        {
            'request': request, 'entities': entities, 'nb_entities_by_page': getattr(settings, 'SANZA_SEARCH_NB_IN_PAGE', 50),
            'field_choice_form': field_choice_form, 'message': message, 'has_empty_entities': has_empty_entities,
            'search_form': search_form, 'search': search, 'contacts_count': contacts_count,
            'contains_refuse_newsletter': contains_refuse_newsletter, 'group_id': group_id,
        },
        context_instance=RequestContext(request)
    )
    
@login_required
def save_search(request, search_id=0):
    if search_id:
        search = get_object_or_404(models.Search, id=search_id)
    else:
        search = models.Search()
    
    if request.method == "POST":
        search_form = forms.SearchForm(request.POST, instance=search, save=True)
        if search_form.is_valid():
            search_form.save_search()
            return HttpResponseRedirect(reverse('search', args=[search.id]))    
    return HttpResponseRedirect(reverse('search'))
    
@login_required
def get_field(request, name):
    block = request.GET.get('block')
    count = request.GET.get('count')
    if not (block and count):
        raise Http404
    try:
        form_class = forms.get_field_form(name)
        t = Template('{{form.as_it_is}}')
        c = Context({'form': form_class(block, count)})
        return HttpResponse(json.dumps({'form': t.render(c)}), mimetype="application/json")
    except KeyError:
        raise Http404
    except Exception, msg:
        print 'Search.views.get_field ERROR', msg
        raise
    
@login_required
def mailto_contacts(request, bcc):
    """Open the mail client in order to send email to contacts"""
    if request.method == "POST":
        nb_limit = getattr(settings, 'SANZA_MAILTO_LIMIT', 50)
        search_form = forms.SearchForm(request.POST)
        if search_form.is_valid():
            emails = search_form.get_contacts_emails()
            if emails:
                if len(emails)>nb_limit:
                    return HttpResponse(',\r\n'.join(emails), mimetype='text/plain')
                else:
                    mailto = u'mailto:'
                    if int(bcc): mailto += '?bcc='
                    mailto += ','.join(emails)
                    return HttpResponseRedirect(mailto)
            else:
                return HttpResponse(_(u'Mailto: Error, no emails defined'), mimetype='text/plain')
    raise Http404

@login_required
def view_search_list(request):
    searches = models.Search.objects.all()#.order_by("-created")
    return render_to_response(
        'Search/search_list.html',
        locals(),
        context_instance=RequestContext(request)
    )
    
@login_required
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
                    
                    contacts = form.get_contacts()
                    
                    emailing = Emailing.objects.create(newsletter=newsletter)
                    for c in contacts:
                        emailing.send_to.add(c)
                    emailing.save()
                    return HttpResponseRedirect(newsletter.get_edit_url())
                else:
                    return render_to_response(
                        'Search/create_action_for_contacts.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = forms.SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    form = NewEmailingForm(initial={'contacts': contacts})
                    return render_to_response(
                        'Search/new_emailing.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
    except Exception, msg:
        print "ERROR", msg
        raise
    raise Http404
    
@login_required
def export_contacts_as_excel(request):
    search_form = forms.SearchForm(request.POST)
    if request.method == "POST":
        search_form = forms.SearchForm(request.POST)
        if search_form.is_valid():
            contacts = search_form.get_contacts()
            contacts.sort(key=lambda x: u"{0}-{1}-{2}".format(x.entity, x.lastname, x.firstname))
            
            #create the excel document
            wb = xlwt.Workbook()
            ws = wb.add_sheet('sanza')

            fields = ['id', 'get_gender_display', 'lastname', 'firstname', 'title', 'entity', 'role',
                'get_address', 'get_address2', 'get_address3', 'get_zip_code', 'get_cedex', 'get_city', 'mobile', 'get_phone', 'get_email']
            
            #header
            header_style = xlwt.easyxf('font: bold 1; pattern: pattern solid, fore-colour gray25;')
            #create a map of verbose name for each field
            field_dict = dict([(f.name, _(f.verbose_name).capitalize()) for f in Contact._meta.fields])
            
            #Add custom fields
            for cf in CustomField.objects.filter(export_order__gt=0).order_by('export_order'):
                fields.append('get_custom_field_'+cf.name)
                field_dict['custom_field_'+cf.name] = cf.label
            
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

        response = HttpResponse(mimetype='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename={0}.xls'.format('sanza')
        wb.save(response)
        return response
    raise Http404

@login_required
@popup_redirect
def create_action_for_contacts(request):
    try:
        search_form = forms.SearchForm(request.POST)
        if request.method == "POST":
            if "create_actions" in request.POST:
                form = ActionForContactsForm(request.POST)
                if form.is_valid():
                    contacts = form.get_contacts()
                    for contact in contacts:
                        #create actions
                        kwargs = dict(form.cleaned_data)
                        for k in ('date', 'time', 'contacts'): del kwargs[k]
                        action = Action.objects.create(
                            entity = contact.entity,
                            contact = contact,
                            **kwargs
                        )
                    messages.add_message(request, messages.SUCCESS, _(u"{0} actions have been created".format(len(contacts))))
                    return HttpResponseRedirect(reverse('crm_board_panel'))
                else:
                    return render_to_response(
                        'Search/create_action_for_contacts.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = forms.SearchForm(request.POST)
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
    except Exception, msg:
        print msg
        raise
    raise Http404


@login_required
@popup_redirect
def create_opportunity_for_contacts(request):
    try:
        search_form = forms.SearchForm(request.POST)
        if request.method == "POST":
            if "create_opportunities" in request.POST:
                form = OpportunityForContactsForm(request.POST)
                if form.is_valid():
                    contacts = form.get_contacts()
                    entities = set([c.entity for c in contacts])
                    for entity in entities:
                        #create opportunity
                        kwargs = dict(form.cleaned_data)
                        for k in ('contacts', ): del kwargs[k]
                        opportunity = Opportunity.objects.create(
                            entity = entity, **kwargs
                        )
                    messages.add_message(request, messages.SUCCESS, _(u"{0} opportunities have been created".format(len(entities))))
                    return HttpResponseRedirect(reverse('crm_board_panel'))
                else:
                    return render_to_response(
                        'Search/create_opportunity_for_contacts.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
            else:
                search_form = forms.SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    if contacts:
                        form = OpportunityForContactsForm(initial={'contacts': contacts})
                        return render_to_response(
                            'Search/create_opportunity_for_contacts.html',
                            {'form': form},
                            context_instance=RequestContext(request)
                        )
                    else:
                        return render_to_response(
                            'sanza/message_dialog.html',
                            {
                                'title': _('Create opportunity for contacts'),
                                'message': _(u'The search results contains no contacts')
                            },
                            context_instance=RequestContext(request)
                        )
    except Exception, msg:
        print msg
        raise
    raise Http404

@login_required
@popup_redirect
def add_contacts_to_group(request):
    try:
        search_form = forms.SearchForm(request.POST)
        if request.method == "POST":
            if "add_to_group" in request.POST:
                form = GroupForContactsForm(request.POST)
                if form.is_valid():
                    contacts = form.get_contacts()
                    entities = set([c.entity for c in contacts])
                    groups = form.cleaned_data['groups']
                    for g in groups:
                        for entity in entities:
                        #create opportunity
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
                search_form = forms.SearchForm(request.POST)
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
        print msg
        raise
    raise Http404

@login_required
@popup_close
def contacts_admin(request):
    
    if not request.user.is_superuser:
        raise PermissionDenied
    
    try:
        search_form = forms.SearchForm(request.POST)
        if request.method == "POST":
            if "contacts_admin" in request.POST:
                form = forms.ContactsAdminForm(request.POST)
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
                search_form = forms.SearchForm(request.POST)
                if search_form.is_valid():
                    contacts = search_form.get_contacts()
                    if contacts:
                        form = forms.ContactsAdminForm(initial={'contacts': contacts})
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
        print msg
        raise
    raise Http404
