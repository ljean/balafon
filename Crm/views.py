# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from sanza.Crm import models, forms
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
import json, re
from colorbox.decorators import popup_redirect
from sanza.Crm.settings import get_default_country

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
    
    if request.method == "POST":
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
        next_url = request.session.pop('next_url', reverse('crm_get_group_members', args=[group.id]))
        return HttpResponseRedirect(next_url)
    else:
        form = forms.EditGroupForm(instance=group)
    
    context_dict = {
        'form': form,
        'group': group,
        'request': request,
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
def view_all_opportunities(request):
    opportunities = models.Opportunity.objects.all().order_by('ended', '-end_date')
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
    last_week = date.today() - timedelta(7)
    actions = models.Action.objects.filter(Q(display_on_board=True),
        Q(done=False) | Q(done_date__gte=last_week)).order_by("done", "planned_date", "-done_date", "priority")
    opportunities = models.Opportunity.objects.filter(Q(display_on_board=True),
        Q(ended=False) | Q(end_date__gte=last_week)).order_by("status__ordering", "ended")
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
