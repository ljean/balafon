# -*- coding: utf-8 -*-
"""about actions : something you do with a contact or an entity"""

from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sites.models import Site
from django.db.models import Q, ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import Template, Context
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
def get_action_status2(request):
    """view"""
    try:
        action_type_id = int(request.GET.get("t", 0))
    except ValueError:
        raise Http404

    default_status = 0
    if action_type_id:
        action_type = get_object_or_404(models.ActionType, id=action_type_id)
        allowed_status = [s.id for s in action_type.allowed_status2.all()]
        if action_type.default_status2:
            default_status = action_type.default_status2.id
    else:
        allowed_status = []
    json_response = json.dumps({'allowed_status2': allowed_status, 'default_status2': default_status})
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

    return render(
        request,
        'Crm/view_contact_actions.html',
        {
            'contact': contact,
            'actions_by_set': actions_by_set,
            'entity': contact.entity
        }
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

    return render(
        request,
        'Crm/view_entity_actions.html',
        {
            'actions_by_set': actions_by_set,
            'entity': entity
        }
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

    return render(
        request,
        'Crm/edit_action.html',
        context
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
        title = _("Other kind of actions") if models.ActionSet.objects.count() else _("Actions")

    actions = models.Action.objects.filter(
        Q(entity=entity) | Q(contact__entity=entity) | Q(opportunity__entity=entity), *filters
    ).order_by("planned_date", "priority")
    request.session["redirect_url"] = reverse('crm_entity_actions', args=[entity_id, set_id])
    page_obj = paginate(request, actions, 50)

    return render(
        request,
        'Crm/entity_actions.html',
        {
            'title': title,
            'entity': entity,
            'action_set': action_set,
            'all_actions': True,
            'actions': list(page_obj),
            'page_obj': page_obj,
            'filters': filters,
        }
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
        title = _("Other kind of actions") if models.ActionSet.objects.count() else _("Actions")

    actions = contact.action_set.filter(*filters).order_by("planned_date", "priority")
    page_obj = paginate(request, actions, 50)
    request.session["redirect_url"] = reverse('crm_contact_actions', args=[contact_id, set_id])

    return render(
        request,
        'Crm/entity_actions.html',
        {
            'contact': contact,
            'action_set': action_set,
            'actions': list(page_obj),
            'page_obj': page_obj,
            'all_actions': True,
            'title': title,
        }
    )


@user_passes_test(can_access)
@popup_redirect
def create_action(request, entity_id, contact_id, type_id=None):
    """view"""
    # entity_id or contact_id can be 0
    # add from menu -> both are 0 / add from contact -> entity_id = 0 / add from entity -> contact_id = 0
    contact_id = int(contact_id)
    entity_id = int(entity_id)
    contact = get_object_or_404(models.Contact, id=contact_id) if contact_id else None
    entity = get_object_or_404(models.Entity, id=entity_id) if entity_id else None

    try:
        action_type = models.ActionType.objects.get(id=type_id)
    except (ValueError, models.ActionType.DoesNotExist):
        action_type = None

    if request.method == 'POST':
        form = forms.ActionForm(request.POST, action_type=action_type)
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

        form = forms.ActionForm(initial=initial, action_type=action_type)

    context = {
        'form': form,
        'contact_id': contact_id,
        'entity_id': entity_id,
        'type_id': action_type.id if action_type else 0,
    }

    return render(
        request,
        'Crm/edit_action.html',
        context
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

    return render(
        request,
        'Crm/edit_action.html',
        context
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

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _('Are you sure to delete this action?'),
            'action_url': reverse("crm_delete_action", args=[action_id]),
        }
    )


@user_passes_test(can_access)
def view_all_actions(request):
    """view"""
    actions = models.Action.objects.all().order_by("-planned_date")
    request.session["redirect_url"] = reverse('crm_all_actions')
    return render(
        request,
        'Crm/all_actions.html',
        {
            'actions': actions,
            'partial': False,
            'multi_user': True,
            'default_my_actions': False,
            'all_actions': True,
            'view_name': "crm_all_actions",
        }
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

    return render(
        request,
        'Crm/do_action.html',
        {'form': form, 'action': action}
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

    title = _('Reassign {0}'.format(action.type.name.lower()) if action.type else _('action'))
    return render(
        request,
        'Crm/popup_reassign_action.html',
        {'form': form, 'action': action, 'title': title}
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

    return render(
        request,
        "Crm/add_contact_to_action.html",
        {'form': form, 'action': action}
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

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _('Do you to remove {0} from this action?').format(contact),
            'action_url': reverse("crm_remove_contact_from_action", args=[action_id, contact_id]),
        }
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

    return render(
        request,
        "Crm/add_entity_to_action.html",
        {'form': form, 'action': action}
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

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _('Do you to remove {0} from this action?').format(entity),
            'action_url': reverse("crm_remove_entity_from_action", args=[action_id, entity_id]),
        }
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
def update_action_status(request, action_id, status2=False):
    """change the action status"""

    action = get_object_or_404(models.Action, id=action_id)
    form_class = forms.UpdateActionStatus2Form if status2 else forms.UpdateActionStatusForm

    if request.method == 'POST':

        form = form_class(request.POST, instance=action)
        if form.is_valid():
            if not status2:
                action.status = form.cleaned_data['status']
            action.status2 = form.cleaned_data['status2']
            action.save()
            return None
    else:

        # When the popup is shown after clicking on "done" button
        # show a final status as default value
        on_do = request.GET.get('done', None)
        if on_do and action.type:
            if not status2:
                final_status = action.type.allowed_status.filter(is_final=True)
                if final_status.count():
                    action.status = final_status[0]

        form = form_class(instance=action)

    context = {
        'form': form,
        'action': action,
    }

    return render(
        request,
        'Crm/popup_update_action_status{0}.html'.format('2' if status2 else ''),
        context,
    )


def update_action_status2(request, action_id):
    return update_action_status(request, action_id, True)


@user_passes_test(can_access)
def mailto_action(request, action_id):
    """Open the mail client in order to send email to action contacts"""

    action = get_object_or_404(models.Action, id=action_id)
    try:
        mailto_settings = models.MailtoSettings.objects.get(action_type=action.type)
        body_template = mailto_settings.body_template
        subject = mailto_settings.subject or action.type.mail_to_subject or action.subject
        is_bcc = mailto_settings.bcc
    except models.MailtoSettings.DoesNotExist:
        body_template = ''
        mailto_settings = None
        if action.type:
            subject = action.type.mail_to_subject or action.subject
        else:
            subject = action.subject
        is_bcc = False

    if action.status and action.status.next_on_send:
        action.status = action.status.next_on_send
        action.save()

    emails = [contact.get_email for contact in action.contacts.all()]
    emails += [entity.email for entity in action.entities.all()]

    doc_url = ''
    if action.uuid and hasattr(action, 'sale'):
        try:
            url = reverse('store_view_sales_document_public', args=[action.uuid])
            prefix = "http{0}://".format('s' if request.is_secure else '')
            doc_url = prefix + Site.objects.get_current().domain + url
        except ObjectDoesNotExist:
            pass

    if body_template:
        template_text = Template(body_template)
        body = template_text.render(Context({'action': action, 'settings': mailto_settings, 'doc_url': doc_url}))
    else:
        body = ''

    # Remove duplicates and empty and sort in alphabetical order
    emails = list(sorted(set([email for email in emails if email])))

    mailto = 'mailto:'
    if is_bcc:
        mailto += '?bcc='
    mailto += ','.join(emails)
    mailto += "&" if is_bcc else "?"
    mailto += 'subject={0}'.format(subject)
    mailto += '&body={0}'.format(body)
    return HttpResponseRedirectMailtoAllowed(mailto)


@user_passes_test(can_access)
@popup_close
def view_status_track(request, action_id):
    """change the action status"""

    action = get_object_or_404(models.Action, id=action_id, type__track_status=True)

    if request.method == 'POST':
        return None

    context = {
        'action': action,
    }

    return render(
        request,
        'Crm/popup_status_track.html',
        context,
    )