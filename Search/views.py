# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponse, HttpResponseRedirect
from sanza.Search.forms import QuickSearchForm
from sanza.Crm.models import Entity, Contact, Group, Action
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
from colorbox.decorators import popup_redirect
from coop_cms.models import Newsletter
from sanza.Emailing.forms import NewEmailingForm
from sanza.Crm.forms import ActionForContactsForm
from django.contrib import messages

@login_required
def quick_search(request):
    if request.method == "POST":
        form = QuickSearchForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            
            entities_by_name = Entity.objects.filter(name__icontains=text)
            
            contacts_by_name = Contact.objects.filter(lastname__icontains=text)
            
            entities_title = _(u'Entities')
            contacts_title = _(u'Contacts')
            
            return render_to_response(
                'Search/quicksearch_results.html',
                locals(),
                context_instance=RequestContext(request)
            )
    else:
        raise Http404
    
@login_required
def search(request, search_id=0):
    message = ''
    entities = []
    search=None
    field_choice_form = forms.FieldChoiceForm()
    contains_refuse_newsletter = False
    if request.method == "POST":
        search_form = forms.SearchForm(request.POST)
        if search_form.is_valid():
            entities = search_form.get_contacts_by_entity()
            contains_refuse_newsletter = search_form.contains_refuse_newsletter
            if not entities:
                message = _(u'Sorry, no results found')
    else:
        search = get_object_or_404(models.Search, id=search_id) if search_id else None
        search_form = forms.SearchForm(instance=search)
        
    return render_to_response(
        'Search/search.html',
        {
            'request': request, 'entities': entities,
            'field_choice_form': field_choice_form, 'message': message,
            'search_form': search_form, 'search': search,
            'contains_refuse_newsletter': contains_refuse_newsletter,
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
def mailto_contacts(request):
    """Open the mail client in order to send email to contacts"""
    if request.method == "POST":
        search_form = forms.SearchForm(request.POST)
        if search_form.is_valid():
            emails = search_form.get_contacts_emails()
            if len(emails)>50:
                return HttpResponse(',\r\n'.join(emails), mimetype='text/plain')
            else:
                mailto = u'mailto:'+','.join(emails)
                return HttpResponseRedirect(mailto)
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
            
            #create the excel document
            wb = xlwt.Workbook()
            ws = wb.add_sheet('sanza')
            
            #fields = ('get_gender', 'lastname', 'firstname', 'title', 'entity', 'role',
            #    'get_address', 'get_zipcode', 'get_cedex', 'get_city', 'get_mobile', 'get_phone', 'get_email')
            
            fields = ('get_gender_display', 'lastname', 'firstname', 'title', 'entity', 'role',
                'get_address', 'get_zip_code', 'get_cedex', 'get_city', 'mobile', 'get_phone', 'get_email')
            
            #header
            header_style = xlwt.easyxf('font: bold 1; pattern: pattern solid, fore-colour gray25;')
            #create a map of verbose name for each field
            field_dict = dict([(f.name, _(f.verbose_name).capitalize()) for f in Contact._meta.fields])
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
                    form = ActionForContactsForm(initial={'contacts': contacts})
                    return render_to_response(
                        'Search/create_action_for_contacts.html',
                        {'form': form},
                        context_instance=RequestContext(request)
                    )
    except Exception, msg:
        print msg
        raise
    raise Http404