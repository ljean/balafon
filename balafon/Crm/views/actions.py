# -*- coding: utf-8 -*-
"""about actions : something you do with a contact or an entity"""

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext, Template, Context
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect, popup_reload, popup_close
from coop_cms.utils import paginate

from balafon.Crm import models, forms
from balafon.Crm.signals import action_cloned
from balafon.Crm.views.contacts import select_contact_and_redirect
from balafon.Crm.utils import get_actions_by_set
from balafon.permissions import can_access
from balafon.utils import HttpResponseRedirectMailtoAllowed


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
    request.session["redirect_url"] = reverse('crm_entity_actions', args=[entity_id, set_id])
    page_obj = paginate(request, actions, 50)

    return render_to_response(
        'Crm/entity_actions.html',
        {
            'title': title,
            'entity': entity,
            'action_set': action_set,
            'all_actions': True,
            'actions': list(page_obj),
            'page_obj': page_obj,
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
    page_obj = paginate(request, actions, 50)
    request.session["redirect_url"] = reverse('crm_contact_actions', args=[contact_id, set_id])

    return render_to_response(
        'Crm/entity_actions.html',
        {
            'contact': contact,
            'action_set': action_set,
            'actions': list(page_obj),
            'page_obj': page_obj,
            'all_actions': True,
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
        try:
            team_member = models.TeamMember.objects.get(user=request.user)
            initial['in_charge'] = team_member
        except models.TeamMember.DoesNotExist:
            pass

        try:
            opp_id = int(request.GET.get('opportunity', 0))
            initial['opportunity'] = models.Opportunity.objects.get(id=opp_id)
        except (ValueError, models.Opportunity.DoesNotExist):
            pass

        try:
            type_id = int(request.GET.get('type', 0))
            initial['type'] = models.ActionType.objects.get(id=type_id)
        except (ValueError, models.ActionType.DoesNotExist):
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

            return HttpResponseRedirect(next_url or reverse('balafon_homepage'))
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'balafon/confirmation_dialog.html',
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
def reassign_action(request, action_id):
    """view"""
    action = get_object_or_404(models.Action, id=action_id)
    if request.method == 'POST':
        form = forms.SelectContactOrEntityForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['name']
            action.contacts.clear()
            action.entities.clear()
            if isinstance(obj, models.Entity):
                action.entities.add(obj)
            else:
                action.contacts.add(obj)
            action.save()
            return HttpResponseRedirect(obj.get_absolute_url())

    else:
        form = forms.SelectContactOrEntityForm()

    title = _(u'Reassign {0}'.format(action.type.name.lower()) if action.type else _(u'action'))
    return render_to_response(
        'Crm/popup_reassign_action.html',
        {'form': form, 'action': action, 'title': title},
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
        'balafon/confirmation_dialog.html',
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
        'balafon/confirmation_dialog.html',
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


@user_passes_test(can_access)
@popup_reload
def clone_action(request, action_id):
    """clone an action with different type"""

    action = get_object_or_404(models.Action, id=action_id, type__isnull=False)

    if request.method == 'POST':
        form = forms.CloneActionForm(action.type, request.POST)
        if form.is_valid():
            action_type = form.cleaned_data['action_type']
            new_action = action.clone(action_type)
            action_cloned.send(sender=models.Action, original_action=action, new_action=new_action)

            next_url = reverse('crm_edit_action', args=[new_action.id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.CloneActionForm(action.type)

    context = {
        'form': form,
        'action': action,
        'action_type_name': form.action_type_name,
    }

    return render(
        request,
        'Crm/popup_clone_action.html',
        context,
    )

@user_passes_test(can_access)
@popup_close
def update_action_status(request, action_id):
    """change the action status"""

    action = get_object_or_404(models.Action, id=action_id)

    if request.method == 'POST':
        form = forms.UpdateActionStatusForm(request.POST, instance=action)
        if form.is_valid():
            action.status = form.cleaned_data['status']
            action.save()

            return None
    else:

        # When the popup is shown after clicking on "done" button
        # show a final status has default value
        on_do = request.GET.get('done', None)
        if on_do and action.type:
            final_status = action.type.allowed_status.filter(is_final=True)
            if final_status.count():
                action.status = final_status[0]

        form = forms.UpdateActionStatusForm(instance=action)

    context = {
        'form': form,
        'action': action,
    }

    return render(
        request,
        'Crm/popup_update_action_status.html',
        context,
    )


@user_passes_test(can_access)
def mailto_action(request, action_id):
    """Open the mail client in order to send email to action contacts"""

    action = get_object_or_404(models.Action, id=action_id)
    mailto_settings = get_object_or_404(models.MailtoSettings, action_type=action.type)

    emails = [contact.get_email for contact in action.contacts.all()]
    emails += [entity.email for entity in action.entities.all()]

    template_text = Template(mailto_settings.body_template)
    body = template_text.render(Context({'action': action, 'settings': mailto_settings}))

    # Remove duplicates and empty and soty in alphabetical order
    emails = list(sorted(set([email for email in emails if email])))

    mailto = u'mailto:'
    if mailto_settings.bcc:
        mailto += '?bcc='
    mailto += ','.join(emails)
    mailto += "&" if mailto_settings.bcc else "?"
    mailto += 'subject={0}'.format(mailto_settings.subject or action.subject)
    mailto += '&body={0}'.format(body)
    return HttpResponseRedirectMailtoAllowed(mailto)
