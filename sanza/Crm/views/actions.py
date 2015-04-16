# -*- coding: utf-8 -*-
"""about actions : something you do with a contact or an entity"""

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect

from sanza.Crm import models, forms
from sanza.Crm.views.contacts import select_contact_and_redirect
from sanza.Crm.utils import get_actions_by_set
from sanza.permissions import can_access


@user_passes_test(can_access)
def get_action_status(request):
    """view"""
    try:
        action_type_id = int(request.GET.get("t", 0))
    except ValueError:
        raise Http404

    default_status = 0
    if action_type_id:
        action_type = get_object_or_404(models.ActionType, id=action_type_id)
        allowed_status = [s.id for s in action_type.allowed_status.all()]
        if action_type.default_status:
            default_status = action_type.default_status.id
    else:
        allowed_status = []
    json_response = json.dumps({'allowed_status': allowed_status, 'default_status': default_status})
    return HttpResponse(json_response, content_type="application/json")


@user_passes_test(can_access)
def view_all_contact_actions(request, contact_id, action_set_id):
    """view"""
    contact = get_object_or_404(models.Contact, id=contact_id)
    if int(action_set_id):
        action_set_list = [get_object_or_404(models.ActionSet, id=action_set_id)]
    else:
        action_set_list = [None]

    request.session["redirect_url"] = reverse('crm_view_contact_actions', args=[contact_id, action_set_id])

    actions = contact.action_set.filter(archived=False).order_by("planned_date", "priority")
    actions_by_set = get_actions_by_set(actions, 0, action_set_list)

    return render_to_response(
        'Crm/view_contact_actions.html',
        {
            'contact': contact,
            'actions_by_set': actions_by_set,
            'entity': contact.entity
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_all_entity_actions(request, entity_id, action_set_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    if int(action_set_id):
        action_set_list = [get_object_or_404(models.ActionSet, id=action_set_id)]
    else:
        action_set_list = [None]

    request.session["redirect_url"] = reverse('crm_view_entity_actions', args=[entity_id, action_set_id])

    actions = models.Action.objects.filter(
        Q(entities=entity) | Q(contacts__entity=entity),
        Q(archived=False)
    ).distinct().order_by("planned_date", "priority")
    actions_by_set = get_actions_by_set(actions, 0, action_set_list)

    return render_to_response(
        'Crm/view_entity_actions.html',
        {
            'actions_by_set': actions_by_set,
            'entity': entity
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def add_action_for_entity(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    return select_contact_and_redirect(
        request,
        'crm_add_action_for_contact',
        'Crm/add_action.html',
        choices=entity.contact_set.filter(has_left=False)
    )


@user_passes_test(can_access)
@popup_redirect
def add_action_for_contact(request, contact_id):
    """view"""
    contact = get_object_or_404(models.Contact, id=contact_id)
    action = models.Action(contact=contact)
    if request.method == 'POST':
        form = forms.ActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_view_contact', args=[contact.id])
            return HttpResponseRedirect(next_url)
    else:
        opportunity_id = request.GET.get('opp_id', 0)
        initial = {}
        if opportunity_id:
            try:
                initial['opportunity'] = models.Opportunity.objects.get(id=opportunity_id)
            except models.Opportunity.DoesNotExist:
                pass
        form = forms.ActionForm(instance=action, initial=initial)

    context = {
        'form': form,
        'contact': contact,
    }

    return render_to_response(
        'Crm/edit_action.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_entity_actions(request, entity_id, set_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)

    filters = []
    if int(set_id):
        action_set = get_object_or_404(models.ActionSet, id=set_id)
        filters.append(Q(type__set=action_set))
        title = action_set.name
    else:
        filters.append(Q(type__set=None))
        title = _(u"Other kind of actions") if models.ActionSet.objects.count() else _(u"Actions")

    actions = models.Action.objects.filter(
        Q(entity=entity) | Q(contact__entity=entity) | Q(opportunity__entity=entity), *filters
    ).order_by("planned_date", "priority")
    all_actions = True
    request.session["redirect_url"] = reverse('crm_entity_actions', args=[entity_id, set_id])
    return render_to_response(
        'Crm/entity_actions.html',
        {
            'title': title,
            'entity': entity,
            'action_set': action_set,
            'all_actions': all_actions,
            'actions': actions,
            'filters': filters,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_contact_actions(request, contact_id, set_id):
    """view"""
    contact = get_object_or_404(models.Contact, id=contact_id)

    filters = []
    if int(set_id):
        action_set = get_object_or_404(models.ActionSet, id=set_id)
        filters.append(Q(type__set=action_set))
        title = action_set.name
    else:
        filters.append(Q(type__set=None))
        title = _(u"Other kind of actions") if models.ActionSet.objects.count() else _(u"Actions")

    actions = contact.action_set.filter(*filters).order_by("planned_date", "priority")
    all_actions = True
    request.session["redirect_url"] = reverse('crm_contact_actions', args=[contact_id, set_id])
    return render_to_response(
        'Crm/entity_actions.html',
        {
            'contact': contact,
            'action_set': action_set,
            'actions': actions,
            'all_actions': all_actions,
            'title': title,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def create_action(request, entity_id, contact_id):
    """view"""
    #entity_id or contact_id can be 0
    #add from menu -> both are 0 / add from contact -> entity_id = 0 / add from entity -> contact_id = 0
    contact_id = int(contact_id)
    entity_id = int(entity_id)
    contact = get_object_or_404(models.Contact, id=contact_id) if contact_id else None
    entity = get_object_or_404(models.Entity, id=entity_id) if entity_id else None

    if request.method == 'POST':
        form = forms.ActionForm(request.POST)
        if form.is_valid():
            next_url = request.session.get('redirect_url')
            action = form.save()
            if entity:
                action.entities.add(entity)
                if not next_url:
                    next_url = reverse("crm_view_entity", args=[entity.id])
            elif contact:
                action.contacts.add(contact)
                if not next_url:
                    next_url = reverse("crm_view_contact", args=[contact.id])
            else:
                action.display_on_board = True
            action.save()

            if not next_url:
                next_url = reverse('crm_board_panel')
            return HttpResponseRedirect(next_url)
    else:
        initial = {}
        if request.user.is_staff and request.user.first_name:
            initial['in_charge'] = request.user
        try:
            opp_id = int(request.GET.get('opportunity', 0))
            initial['opportunity'] = models.Opportunity.objects.get(id=opp_id)
        except (ValueError, models.Opportunity.DoesNotExist):
            pass

        form = forms.ActionForm(initial=initial)

    context = {
        'form': form,
        'contact_id': contact_id,
        'entity_id': entity_id,
    }

    return render_to_response(
        'Crm/edit_action.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def edit_action(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.ActionForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url')
            if not next_url:
                next_url = reverse('crm_board_panel')
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ActionForm(instance=action)

    context = {
        'form': form,
        'action': action,
    }

    return render_to_response(
        'Crm/edit_action.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_action(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                next_url = request.session.get('redirect_url')

                if not next_url and action.entities.count():
                    next_url = reverse('crm_view_entity', args=[action.entities.all()[0].id])

                if not next_url and action.contacts.count():
                    next_url = reverse('crm_view_contact', args=[action.contacts.all()[0].id])

                action.delete()

            return HttpResponseRedirect(next_url or reverse('sanza_homepage'))
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete this action?'),
            'action_url': reverse("crm_delete_action", args=[action_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_all_actions(request):
    """view"""
    actions = models.Action.objects.all().order_by("-planned_date")
    request.session["redirect_url"] = reverse('crm_all_actions')
    return render_to_response(
        'Crm/all_actions.html',
        {
            'actions': actions,
            'partial': False,
            'multi_user': True,
            'default_my_actions': False,
            'all_actions': True,
            'view_name': "crm_all_actions",
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def do_action(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == "POST":
        form = forms.ActionDoneForm(request.POST, instance=action)
        if form.is_valid():
            form.save()
            next_url = request.session.get('redirect_url') or reverse('crm_board_panel')
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ActionDoneForm(instance=action)

    return render_to_response(
        'Crm/do_action.html',
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )



@user_passes_test(can_access)
@popup_redirect
def add_contact_to_action(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.SelectContactForm(request.POST)
        if form.is_valid():
            next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
            contact = form.cleaned_data["contact"]
            action.contacts.add(contact)
            action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectContactForm()

    return render_to_response(
        "Crm/add_contact_to_action.html",
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_contact_from_action(request, action_id, contact_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    contact = get_object_or_404(models.Contact, id=contact_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
                action.contacts.remove(contact)
                action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you to remove {0} from this action?').format(contact),
            'action_url': reverse("crm_remove_contact_from_action", args=[action_id, contact_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_entity_to_action(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.SelectEntityForm(request.POST)
        if form.is_valid():
            next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
            entity = form.cleaned_data["entity"]
            action.entities.add(entity)
            action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.SelectEntityForm()

    return render_to_response(
        "Crm/add_entity_to_action.html",
        {'form': form, 'action': action},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def remove_entity_from_action(request, action_id, entity_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    entity = get_object_or_404(models.Entity, id=entity_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                next_url = request.session.get('redirect_url') or reverse("crm_board_panel")
                action.entities.remove(entity)
                action.save()
            return HttpResponseRedirect(next_url)
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you to remove {0} from this action?').format(entity),
            'action_url': reverse("crm_remove_entity_from_action", args=[action_id, entity_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_action(request):
    """view"""
    return select_contact_and_redirect(
        request,
        'crm_add_action_for_contact',
        'Crm/add_action.html',
    )
