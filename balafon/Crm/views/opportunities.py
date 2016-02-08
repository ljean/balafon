# -*- coding: utf-8 -*-
"""opportunities : certainly a bad name :-) this is a group of actions"""

from datetime import datetime
import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect
from coop_cms.utils import paginate

from balafon.Crm import models, forms
from balafon.Crm.utils import get_actions_by_set
from balafon.permissions import can_access
from balafon.utils import log_error


@user_passes_test(can_access)
@log_error
def get_opportunity_name(request, opp_id):
    """view"""
    try:
        opp = models.Opportunity.objects.get(id=opp_id)
        return HttpResponse(json.dumps({'name': opp.name}), 'application/json')
    except (models.Opportunity.DoesNotExist, ValueError):
        return HttpResponse(json.dumps({'name': opp_id}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunities(request):
    """view"""
    term = request.GET.get('term')
    queryset = models.Opportunity.objects.filter(ended=False, name__icontains=term)
    opportunities = [{'id': x.id, 'name': u'{0}'.format(x.name)} for x in queryset]
    return HttpResponse(json.dumps(opportunities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_opportunity_id(request):
    """view"""
    name = request.GET.get('name')
    opportunity = get_object_or_404(models.Opportunity, name=name)
    return HttpResponse(json.dumps({'id': opportunity.id}), 'application/json')


@user_passes_test(can_access)
def view_entity_opportunities(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    opportunities = models.Opportunity.objects.filter(entity=entity)

    request.session["redirect_url"] = reverse('crm_entity_opportunities', args=[entity_id])

    return render_to_response(
        'Crm/entity_opportunities.html',
        {
            'entity': entity,
            'opportunities': opportunities,
            'all_opportunities': True,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_all_opportunities(request, ordering=None):
    """view"""
    opportunities = models.Opportunity.objects.all()
    if not ordering:
        ordering = 'date'
    if ordering == 'name':
        opportunities = opportunities.order_by('name')
    elif ordering == 'status':
        opportunities = opportunities.order_by('status__ordering', 'status')
    elif ordering == 'type':
        opportunities = opportunities.order_by('type')
    elif ordering == 'date':
        opportunities = list(opportunities)
        opportunities.sort(key=lambda o: o.get_start_date() or datetime(1970, 1, 1))
        opportunities.reverse()

    request.session["redirect_url"] = reverse('crm_all_opportunities')
    page_obj = paginate(request, opportunities, 50)

    return render_to_response(
        'Crm/all_opportunities.html',
        {
            "opportunities": list(page_obj),
            'page_obj': page_obj,
            "ordering": ordering,
            "all_opportunities": True,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def edit_opportunity(request, opportunity_id):
    """view"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == 'POST':
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.OpportunityForm(instance=opportunity)

    return render_to_response(
        'Crm/edit_opportunity.html',
        {'opportunity': opportunity, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_opportunity(request, opportunity_id):
    """view"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)
    actions = opportunity.action_set.filter(archived=False)
    actions_by_set = get_actions_by_set(actions)

    contacts = []
    for action in actions:
        contacts += [contact for contact in action.contacts.all()]
        for entity in action.entities.all():
            contacts += [contact for contact in entity.contact_set.filter(has_left=False)]
    contacts = list(set(contacts))
    contacts.sort(key=lambda contact_elt: contact_elt.lastname.lower())

    request.session["redirect_url"] = reverse('crm_view_opportunity', args=[opportunity.id])

    context = {
        'opportunity': opportunity,
        'actions_by_set': actions_by_set,
        'contacts': contacts,
    }

    return render_to_response(
        'Crm/view_opportunity.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_opportunity(request, opportunity_id):
    """view"""
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                for action in opportunity.action_set.all():
                    action.opportunity = None
                    action.save()
                opportunity.delete()
                next_url = reverse('crm_board_panel')
                return HttpResponseRedirect(next_url)
        else:
            return HttpResponseRedirect(reverse('crm_view_opportunity', args=[opportunity.id]))
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the opportunity "{0}"?').format(opportunity),
            'action_url': reverse("crm_delete_opportunity", args=[opportunity_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_action_to_opportunity(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)

    if request.method == "POST":
        form = forms.SelectOpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.cleaned_data["opportunity"]
            action.opportunity = opportunity
            action.save()
            next_url = request.session.get('redirect_url')
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectOpportunityForm()

    return render_to_response(
        'Crm/add_action_to_opportunity.html',
        {'action': action, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_action_from_opportunity(request, action_id, opportunity_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    opportunity = get_object_or_404(models.Opportunity, id=opportunity_id)

    if request.method == "POST":
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if action.opportunity == opportunity:
                    action.opportunity = None
                    action.save()
            next_url = request.session.get('redirect_url')
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you want to remove the action {0} from opportunity {1}?').format(
                action.subject, opportunity.name
            ),
            'action_url': reverse("crm_remove_action_from_opportunity", args=[action.id, opportunity.id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_opportunity(request):
    """view"""
    next_url = request.session.get('redirect_url')
    if request.method == 'POST':
        opportunity = models.Opportunity()
        form = forms.OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save()
            next_url = next_url or reverse('crm_view_opportunity', args=[opportunity.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.OpportunityForm()

    next_url = next_url or reverse('crm_board_panel')
    return render_to_response(
        'Crm/edit_opportunity.html',
        {'next_url': next_url, 'form': form},
        context_instance=RequestContext(request)
    )
