# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Max
from sanza.Crm import models, forms
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
import json, re
from colorbox.decorators import popup_redirect
from sanza.Crm.settings import get_default_country
from django.conf import settings
import os.path, re
from sanza.Crm.utils import unicode_csv_reader, resolve_city
    
@login_required
def view_entity(request, entity_id):
    last_week = date.today() - timedelta(7)
    entity = get_object_or_404(models.Entity, id=entity_id)
    contacts = models.Contact.objects.filter(entity=entity).order_by("-main_contact")
    actions = models.Action.objects.filter(Q(entity=entity),
        Q(done=False) | Q(done_date__gte=last_week)).order_by("done", "planned_date", "priority")
    opportunities = models.Opportunity.objects.filter(Q(entity=entity),
        Q(ended=False) | Q(end_date__gte=last_week)).order_by("status__ordering", "ended")
    multi_user = True
    entity.save() #update last access
    request.session["redirect_url"] = reverse('crm_view_entity', args=[entity_id])
    return render_to_response(
        'Crm/entity.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_entities_list(request):
    entities = models.Entity.objects.all().order_by('name')
    
    return render_to_response(
        'Crm/all_entities.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def add_entity_to_group(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    
    if request.method == "POST":
        form = forms.AddEntityToGroupForm(entity, request.POST)
        if form.is_valid():
            name = form.cleaned_data["group_name"]
            
            group, is_new = models.Group.objects.get_or_create(name=name)
            group.entities.add(entity)
            group.save()
            next_url = reverse('crm_view_entity', args=[entity_id])
            #if is_new:
            #    request.session["next_url"] = next_url
            #    return HttpResponseRedirect(reverse('crm_edit_group', args=[group.id]))
            #else:
            return HttpResponseRedirect(next_url)
    else:
        form = forms.AddEntityToGroupForm(entity)
    
    context_dict = {
        'entity': entity,
        'form': form,
        'request': request,
    }

    return render_to_response(
        'Crm/add_entity_to_group.html',
        context_dict,
        context_instance=RequestContext(request)
    )

@login_required
def get_group_suggest_list(request):
    try:
        suggestions = []
        term = request.GET["term"]#the 1st chars entered in the autocomplete
        for group in models.Group.objects.filter(name__istartswith=term):
            suggestions.append(group.name)
        return HttpResponse(json.dumps(suggestions), mimetype='application/json')
    except Exception, msg:
        print '###', msg
        
@login_required
@popup_redirect
def remove_entity_from_group(request, group_id, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    group = get_object_or_404(models.Group, id=group_id)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            group.entities.remove(entity)
        return HttpResponseRedirect(reverse('crm_view_entity', args=[entity_id]))
    
    return render_to_response(
        'confirmation_dialog.html',
        {
            'message': _(u'Do you want to remove {0.name} from the {1.name} group?').format(entity, group),
            'action_url': reverse("crm_remove_entity_from_group", args=[group_id, entity_id]),
        },
        context_instance=RequestContext(request)
    )
    
@login_required
def get_group_members(request, group_id):
    group = get_object_or_404(models.Group, id=group_id)
    group.save() #update last access
    return render_to_response(
        'Crm/group_members.html',
        {'group': group, 'entities': group.entities.all().order_by('name')},
        context_instance=RequestContext(request)
    )
    
@login_required
def edit_group(request, group_id):
    group = models.Group.objects.get(id=group_id)
    next_url = request.session.get('next_url', reverse('crm_see_my_groups'))
    if request.method == "POST":
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
        next_url = request.session.pop('next_url', reverse('crm_see_my_groups'))
        return HttpResponseRedirect(next_url)
    else:
        form = forms.EditGroupForm(instance=group)
    
    context_dict = {
        'form': form,
        'group': group,
        'request': request,
        'next_url': next_url,
    }

    return render_to_response(
        'Crm/edit_group.html',
        context_dict,
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def delete_group(request, group_id):
    group = models.Group.objects.get(id=group_id)
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            group.delete()
            return HttpResponseRedirect(reverse("crm_see_my_groups"))
        else:
            return HttpResponseRedirect(reverse('crm_edit_group', args=[group.id]))
    
    return render_to_response(
        'confirmation_dialog.html',
        {
            'message': _(u'Are you sure to delete the group {0.name}?').format(group),
            'action_url': reverse("crm_delete_group", args=[group_id]),
        },
        context_instance=RequestContext(request)
    )


@login_required
def add_group(request):
    
    if request.method == "POST":
        group = models.Group()
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm_see_my_groups'))
        group = None
    else:
        form = forms.EditGroupForm()
    
    return render_to_response(
        'Crm/edit_group.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def see_my_groups(request):
    
    ordering = request.GET.get('ordering', 'name')
    
    groups = models.Group.objects.all()
    
    if ordering == 'name':
        try:
            #may fail for some databases
            groups = groups.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        except:
            groups = list(models.Group.objects.all())
            groups.sort(key=lambda g: g.name.lower()) #order groups with case-independant name
    else:
        groups = groups.order_by('-modified')
        
    return render_to_response(
        'Crm/my_groups.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def edit_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    entity.save() #update last access
    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            logo = form.cleaned_data['logo']
            if logo:
                if type(logo)==bool:
                    entity.logo = None
                    entity.save()
                else:
                    entity.logo.save(logo.name, logo)
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity)

    return render_to_response(
        'Crm/edit_entity.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def create_entity(request):
    if request.method == "POST":
        entity = models.Entity()
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            logo = form.cleaned_data['logo']
            if logo:
                if type(logo)==bool:
                    entity.logo = None
                    entity.save()
                else:
                    entity.logo.save(logo.name, logo)
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
        else:
            entity = None
    else:
        form = forms.EntityForm()

    return render_to_response(
        'Crm/edit_entity.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def delete_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            entity.delete()
            return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect(reverse('crm_edit_entity', args=[entity.id]))
    
    return render_to_response(
        'confirmation_dialog.html',
        {
            'message': _(u'Are you sure to delete {0.name}?').format(entity),
            'action_url': reverse("crm_delete_entity", args=[entity_id]),
        },
        context_instance=RequestContext(request)
    )

@login_required
def get_city_name(request, city):
    try:
        city_id = int(city)
        city = models.City.objects.get(id=city_id)
        return HttpResponse(json.dumps({'name': city.name}), 'application/json')
    except ValueError:
        return HttpResponse(json.dumps({'name': city}), 'application/json')

@login_required
def get_cities(request):
    term = request.GET.get('term')
    country_id = int(request.GET.get('country', 0))
    default_country = models.Zone.objects.get(name=get_default_country(), parent__isnull=True)
    if country_id == 0 or country_id == default_country.id:
        cities = [{'id': x.id, 'name': x.name}
            for x in models.City.objects.filter(name__istartswith=term).exclude(parent__code='')]
    else:
        cities = [{'id': x.id, 'name': x.name}
            for x in models.City.objects.filter(name__istartswith=term, parent__id=country_id)]
    return HttpResponse(json.dumps(cities), 'application/json')

@login_required
def get_opportunity_name(request, opp_id):
    try:
        opp = models.Opportunity.objects.get(id=opp_id)
        return HttpResponse(json.dumps({'name': opp.name}), 'application/json')
    except models.Opportunity.DoesNotExist:
        return HttpResponse(json.dumps({'name': opp_id}), 'application/json')

@login_required
def get_opportunities(request):
    term = request.GET.get('term')
    opps = [{'id': x.id, 'name': u'{0} -  {1}'.format(x.name, x.entity.name)}
        for x in models.Opportunity.objects.filter(Q(name__istartswith=term) | Q(entity__name__istartswith=term))]
    return HttpResponse(json.dumps(opps), 'application/json')

@login_required
def get_entity_name(request, entity_id):
    try:
        entity = models.Entity.objects.get(id=entity_id)
        return HttpResponse(json.dumps({'name': entity.name}), 'application/json')
    except models.Entity.DoesNotExist:
        return HttpResponse(json.dumps({'name': entity_id}), 'application/json')

@login_required
def get_entities(request):
    term = request.GET.get('term')
    entities = [{'id': x.id, 'name': x.name}
        for x in models.Entity.objects.filter(name__istartswith=term)]
    return HttpResponse(json.dumps(entities), 'application/json')

@login_required
def edit_contact(request, contact_id, mini=True):
    contact = get_object_or_404(models.Contact, id=contact_id)
    
    entity = contact.entity
    
    if request.method == 'POST':
        if mini:
            contact_form = forms.MiniContactForm(request.POST, instance=contact)
        else:
            contact_form = forms.ContactForm(request.POST, instance=contact)
        
        if contact_form.is_valid():
            contact_form.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        if mini:
            contact_form = forms.MiniContactForm(instance=contact)
        else:
            contact_form = forms.ContactForm(instance=contact)
        
    return render_to_response(
        'Crm/edit_contact.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_contact(request, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    actions = contact.action_set.all()
    same_as = None
    if contact.same_as:
        same_as = models.Contact.objects.filter(same_as=contact.same_as).exclude(id=contact.id)
    
    return render_to_response(
        'Crm/view_contact.html',
        {'contact': contact, 'actions': actions, 'same_as': same_as, 'entity': contact.entity},
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def same_as(request, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    if request.method == "POST":
        form = forms.SameAsForm(contact, request.POST)
        if form.is_valid():
            if not contact.same_as:
                contact.same_as = models.SameAs.objects.create()
                contact.save()
            same_as_contact = form.cleaned_data['contact']
            same_as_contact.same_as = contact.same_as
            same_as_contact.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.SameAsForm(contact)
    
    return render_to_response(
        'Crm/same_as.html',
        {'contact': contact, 'form': form},
        context_instance=RequestContext(request)
    )


@login_required
def add_contact(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    
    if request.method == 'POST':
        contact = models.Contact(entity=entity)
        contact_form = forms.MiniContactForm(request.POST, instance=contact)
        if contact_form.is_valid():
            contact_form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        contact_form = forms.MiniContactForm()
        
    return render_to_response(
        'Crm/edit_contact.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def delete_contact(request, contact_id):
    contact = get_object_or_404(models.Contact, id=contact_id)
    entity = contact.entity
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            contact.delete()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
        else:
            return HttpResponseRedirect(reverse('crm_edit_contact', args=[contact.id]))
    
    return render_to_response(
        'confirmation_dialog.html',
        {
            'message': _(u'Are you sure to delete the contact "{0}"?').format(contact),
            'action_url': reverse("crm_delete_contact", args=[contact_id]),
        },
        context_instance=RequestContext(request)
    )

@login_required
def add_action_for_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    
    if request.method == 'POST':
        action = models.Action(entity=entity)
        form = forms.ActionForm(entity, request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_entity', args=[entity.id])    
            return HttpResponseRedirect(next_url)
        action = None
    else:
        form = forms.ActionForm(entity)
    
    return render_to_response(
        'Crm/edit_action.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_entity_actions(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    actions = models.Action.objects.filter(entity=entity).order_by('done', '-done_date')
    all_actions = True
    request.session["redirect_url"] = reverse('crm_entity_actions', args=[entity_id])
    return render_to_response(
        'Crm/entity_actions.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def edit_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    entity = get_object_or_404(models.Entity, id=action.entity.id)
    
    if request.method == 'POST':
        form = forms.ActionForm(entity, request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_entity', args=[entity.id])    
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ActionForm(entity, instance=action)
    
    return render_to_response(
        'Crm/edit_action.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def delete_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    entity = get_object_or_404(models.Entity, id=action.entity.id)
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            action.delete()
            next_url = request.session.get('redirect_url') or reverse('crm_view_entity', args=[entity.id])    
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('crm_edit_action', args=[action.id]))
    
    return render_to_response(
        'confirmation_dialog.html',
        {
            'message': _(u'Are you sure to delete the action "{0}"?').format(action),
            'action_url': reverse("crm_delete_action", args=[action_id]),
        },
        context_instance=RequestContext(request)
    )

@login_required
def add_opportunity_for_entity(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    
    if request.method == 'POST':
        opportunity = models.Opportunity(entity=entity)
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_entity', args=[entity.id])    
            return HttpResponseRedirect(next_url)
        opportunity = None
    else:
        form = forms.OpportunityForm()
    
    return render_to_response(
        'Crm/edit_opportunity.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_entity_opportunities(request, entity_id):
    entity = get_object_or_404(models.Entity, id=entity_id)
    opportunities = models.Opportunity.objects.filter(entity=entity)
    all_opportunities = True
    request.session["redirect_url"] = reverse('crm_entity_opportunities', args=[entity_id])
    return render_to_response(
        'Crm/entity_opportunities.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_all_opportunities(request, ordering=None):
    opportunities = models.Opportunity.objects.all()
    if ordering == 'name':
        opportunities = opportunities.order_by('name')
    elif ordering == 'entity':
        opportunities = opportunities.order_by('entity__name')
    elif ordering == 'date':
        opportunities = opportunities.order_by('-end_date')
    else:
        opportunities = opportunities.order_by('ended', '-end_date')
        
    all_opportunities = True
    request.session["redirect_url"] = reverse('crm_all_opportunities')
    return render_to_response(
        'Crm/all_opportunities.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def edit_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    entity = get_object_or_404(models.Entity, id=opportunity.entity.id)
    
    if request.method == 'POST':
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.OpportunityForm(instance=opportunity)
    
    return render_to_response(
        'Crm/edit_opportunity.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    actions = opportunity.action_set.all()
    contacts = set([a.contact for a in actions if a.contact])
    return render_to_response(
        'Crm/view_opportunity.html',
        {'opportunity': opportunity, 'actions': actions, 'contacts': contacts, 'mailto': True},
        context_instance=RequestContext(request)
    )

@login_required
def mailto_opportunity_contacts(request, opportunity_id):
    """Open the mail client in order to send email to contacts"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    actions = opportunity.action_set.all()
    emails = set([a.contact.get_email for a in actions if a.contact and a.contact.get_email])
    if len(emails)>50:
        return HttpResponse(',\r\n'.join(emails), mimetype='text/plain')
    else:
        mailto = u'mailto:'+','.join(emails)
        return HttpResponseRedirect(mailto)

@login_required
@popup_redirect
def delete_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    entity = get_object_or_404(models.Entity, id=opportunity.entity.id)
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            opportunity.delete()
            next_url = request.session.get('redirect_url') or reverse('crm_view_entity', args=[entity.id])    
            return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('crm_edit_opportunity', args=[opportunity.id]))
    
    return render_to_response(
        'confirmation_dialog.html',
        {
            'message': _(u'Are you sure to delete the opportunity "{0}"?').format(opportunity),
            'action_url': reverse("crm_delete_opportunity", args=[opportunity_id]),
        },
        context_instance=RequestContext(request)
    )

@login_required
def view_board_panel(request):
    days = getattr(settings, 'SANZA_DAYS_OF_ACTIONS_ON_PANEL', 30)
    until_date = date.today() + timedelta(days)
    actions = models.Action.objects.filter(Q(done=False),
        Q(display_on_board=True), Q(planned_date__lte=until_date) | Q(planned_date__isnull=True)).order_by(
        "priority", "planned_date")
    opportunities = models.Opportunity.objects.filter(display_on_board=True, ended=False).order_by("status__ordering")
    partial = True
    multi_user = True
    default_my_actions = True
    request.session["redirect_url"] = reverse('crm_board_panel')
    return render_to_response(
        'Crm/board_panel.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
def view_all_actions(request):
    actions = models.Action.objects.all().order_by("-planned_date")
    partial = False
    multi_user = True
    default_my_actions = False
    all_actions = True
    request.session["redirect_url"] = reverse('crm_all_actions')
    return render_to_response(
        'Crm/all_actions.html',
        locals(),
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def do_action(request, action_id):
    action = get_object_or_404(models.Action, id=action_id)
    if request.method =="POST":
        form = forms.ActionDoneForm(request.POST, instance=action)
        if form.is_valid:
            action.done = True
            action = form.save()
            
            if 'done_and_new' in request.POST:
                return HttpResponseRedirect(reverse('crm_add_action_for_entity', args=[action.entity.id]))
            else:
                next_url = request.session.get('redirect_url') or reverse('crm_board_panel')    
                return HttpResponseRedirect(next_url)
    else:
        form = forms.ActionDoneForm(instance=action)
    return render_to_response(
        'Crm/do_action.html',
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )

def select_entity_and_redirect(request, view_name, template_name):
    if request.method == 'POST':
        form = forms.SelectEntityForm(request.POST)
        if form.is_valid():
            entity = form.cleaned_data["entity"]
            args = [entity.id]
            url = reverse(view_name, args=args)
            return HttpResponseRedirect(url)
    else:
        form = forms.SelectEntityForm()
    
    return render_to_response(
        template_name,
        {'form': form},
        context_instance=RequestContext(request)
    )

@login_required
@popup_redirect
def add_opportunity(request):
    try:
        return select_entity_and_redirect(
            request,
            'crm_add_opportunity_for_entity',
            'Crm/add_opportunity.html'
        )
    except Exception, msg:
        print "##", msg
        raise

@login_required
@popup_redirect
def add_action(request):
    try:
        return select_entity_and_redirect(
            request,
            'crm_add_action_for_entity',
            'Crm/add_action.html',
        )
    except Exception, msg:
        print "##", msg
        raise

@login_required
def edit_custom_fields(request, model_name, instance_id):
    try:
        form_class = {
            'entity': forms.EntityCustomFieldForm,
            'contact': forms.ContactCustomFieldForm,
        }[model_name]
    except KeyError:
        raise Http404
    
    instance = get_object_or_404(form_class.model(), id=instance_id)
    
    if request.method == 'POST':
        form = form_class(instance, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = form_class(instance)
    
    return render_to_response(
        'Crm/edit_custom_fields.html',
        {'form': form, 'instance': instance},
        context_instance=RequestContext(request)
    )
    
@login_required
def new_contacts_import(request):
    if request.method == 'POST':
        instance = models.ContactsImport(imported_by=request.user)
        form = forms.ContactsImportForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            src = form.cleaned_data['import_file']
            ipt = form.save()
            if not ipt.name:
                ipt.name = os.path.splitext(src.name)[0]
                ipt.save()
            return HttpResponseRedirect(reverse('crm_confirm_contacts_import', args=[ipt.id]))
    else:
        form = forms.ContactsImportForm()
    
    return render_to_response(
        'Crm/new_contacts_import.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

@login_required
def confirm_contacts_import(request, import_id):
    
    contacts_import = get_object_or_404(models.ContactsImport, id=import_id)
    reader = unicode_csv_reader(contacts_import.import_file)
    
    fields = ['entity', 'gender', 'firstname', 'lastname', 'email', 'entity.phone',
        'phone', 'entity.fax', 'mobile', 'entity.address', 'entity.address2', 'entity.address3',
        'entity.city', 'entity.cedex', 'entity.zip_code', 'address', 'address2',
        'address3', 'city', 'cedex', 'zip_code', 'job', 'entity.website', 'notes', 'role', 'entity.email', 'groups',
    ]
    
    #custom fields
    custom_fields_count = models.CustomField.objects.all().aggregate(Max('import_order'))['import_order__max']
    for i in xrange(custom_fields_count):
        fields.append('cf_{0}'.format(i+1))
        
    custom_fields = []
    for idx in xrange(1, custom_fields_count+1):
        try:
            cf = models.CustomField.objects.get(import_order=idx)
            custom_fields.append(cf)
        except models.CustomField.DoesNotExist:
            custom_fields.append(None)
    
    cf_names = ['cf_{0}'.format(idx) for idx in xrange(1, custom_fields_count+1)]
        
    contacts = []
    entity_dict = {}
    role_dict = {}
    groups_dict = {}
    for k, row in enumerate(reader):
        if k==0: continue #remove the header row
        c = {}
        for i, field in enumerate(fields):
            c[field] = row[i]
            if field == 'gender':
                if c[field]:
                    if c[field] in ('M', 'M.', 'Mr', 'Mr.'):
                        c[field] = models.Contact.GENDER_MALE
                    else:
                        c[field] = models.Contact.GENDER_FEMALE
            #Copy value of entity fields with _ rather than . for using it in template
            if field.find('.')>0:
                c[field.replace('.', '_')] = c[field]
            if field.find('city')>=0 and c[field]:
                field = field.replace('.', '_')
                c[field+'_exists'] = (models.City.objects.filter(name__iexact=c[field]).count()>0)
                
        if not c['entity']:
            entity = u''
            res = re.match('(?P<name>.+)@(?P<cpn>.+)\.(?P<ext>.+)', c['email'])
            if res:
                name, entity, ext = res.groups(0)
                #email = u'{0}@{1}.{2}'.format(name, entity, ext)
            if entity in ('free', 'gmail', 'yahoo', 'wanadoo', 'orange', 'sfr', 'laposte'):
                entity = name
            if not c['entity']:
                c['entity'] = entity
        else:
            name = c['entity']
        if not (c['lastname'] or c['firstname']):
            try:
                c['firstname'], c['lastname'] = [x.capitalize() for x in name.split('.')]
            except ValueError:
                c['lastname'] = name.capitalize()
        
        c['entity_exists'] = (models.Entity.objects.filter(name__iexact=c['entity']).count()!=0) or \
            (c['entity'] in entity_dict)
        entity_dict[c['entity']] = True
        
        c['role'] = c['role'].split(";")
        c['role_exists'] = []
        for r in c['role']:
            c['role_exists'].append(
                (models.EntityRole.objects.filter(name__iexact=r).count()!=0) or (r.lower() in role_dict)
            )
            role_dict[r.lower()] = True
        c['roles'] = [{'name': r, 'exists': e} for (r, e) in zip(c['role'], c['role_exists'])]
        
        groups = [x for x in c['groups'].strip().split(";") if x]
        c['groups_exists'] = []
        for g in groups:
            c['groups_exists'].append(
                (models.Group.objects.filter(name__iexact=g).count()!=0) or (g in groups_dict)
            )
            groups_dict[g] = True
        c['entity_groups'] = [{'name': g, 'exists': e} for (g, e) in zip(groups, c['groups_exists'])]
        
        #if c['email']:
        #    if models.Contact.objects.filter(email=c['email']).count()==0:
        #        contacts.append(c)
        #    else:
        #        print '## DO NOT ADD', c['entity'], c['lastname']
        #else:
        #    contacts.append(c)
        contacts.append(c)
    total_contacts = k
    
    if request.method == 'POST':
        form = forms.ContactsImportConfirmForm(request.POST, instance=contacts_import)
        
        if form.is_valid():
            #create entities
            default_department = form.cleaned_data['default_department']
            contacts_import = form.save()
            entity_dict = {}
            for c in contacts:
                #Entity
                if settings.DEBUG:
                    try:
                        print c['entity'], c['lastname']
                    except UnicodeError:
                        print '##!'
                if c['entity_exists']:
                    entity = models.Entity.objects.filter(name__iexact=c['entity'])[0]
                else:
                    entity = models.Entity.objects.create(
                        name=c['entity'], type=contacts_import.entity_type, imported_by=contacts_import,
                        relationship=contacts_import.relationship, activity_sector=contacts_import.activity_sector)
                
                is_first_for_entity = entity_dict.has_key(entity.name)
                entity_dict[entity.name] = True
                
                for g in contacts_import.groups.all():
                    g.entities.add(entity)
                    g.save()
                    
                #Contact
                contact = models.Contact.objects.create(entity=entity, firstname=c['firstname'],
                    lastname=c['lastname'], imported_by=contacts_import)
                
                for field_name in fields:
                    if field_name in ('entity', 'city', 'entity.city', 'role', 'groups'):
                        continue
                    obj = contact
                    try:
                        x, field = field_name.split('.')
                        obj = getattr(obj, x)
                    except ValueError:
                        field = field_name
                    if c[field_name] and field!='city':
                        setattr(obj, field, c[field_name])

                if c['city']:
                    contact.city = resolve_city(c['city'], c['zip_code'], default_department)
                if c['entity.city']:
                    contact.entity.city = resolve_city(c['entity.city'], c['entity.zip_code'], default_department)
                if c['role']:
                    for role_exists, role in zip(c['role_exists'], c['role']):
                        if role_exists:
                            contact.role.add(models.EntityRole.objects.filter(name__iexact=role)[0])
                        else:
                            contact.role.add(models.EntityRole.objects.create(name=role))
                if c['groups']:
                    for group_exists, group in zip(c['groups_exists'], c['groups']):
                        if group_exists:
                            group = models.Group.objects.filter(name__iexact=group)[0]
                        else:
                            group, _x = models.Group.objects.get_or_create(name=group)
                        group.entities.add(contact.entity)
                        group.save()
                
                contact.entity.save()
                contact.save()
                
                for name, cf in zip(cf_names, custom_fields):
                    value = c[name]
                    if cf and value:
                        if cf.model == models.CustomField.MODEL_ENTITY and is_first_for_entity:
                            cfv, _x = models.EntityCustomFieldValue.objects.get_or_create(custom_field=cf, entity=contact.entity)
                            cfv.value = value
                            cfv.save()
                        if cf.model == models.CustomField.MODEL_CONTACT:
                            cfv, _x = models.ContactCustomFieldValue.objects.get_or_create(custom_field=cf, contact=contact)
                            cfv.value = value 
                            cfv.save()
            return HttpResponseRedirect("/")
    else:
        form = forms.ContactsImportConfirmForm(instance=contacts_import)
    
    return render_to_response(
        'Crm/confirm_contacts_import.html',
        {'form': form, 'contacts': contacts, 'nb_contacts': len(contacts), 'total_contacts': total_contacts},
        context_instance=RequestContext(request)
    )
