# -*- coding: utf-8 -*-
"""about groups"""

from __future__ import unicode_literals, print_function

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect
from coop_cms.utils import paginate

from balafon.Crm import models, forms
from balafon.permissions import can_access
from balafon.utils import log_error


@user_passes_test(can_access)
@popup_redirect
def add_entity_to_group(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)

    if request.method == "POST":
        form = forms.AddEntityToGroupForm(entity, request.POST)
        if form.is_valid():
            name = form.cleaned_data["group_name"]
            group = models.Group.objects.get_or_create(name=name)[0]
            group.entities.add(entity)
            group.save()
            next_url = reverse('crm_view_entity', args=[entity_id])
            return HttpResponseRedirect(next_url)
    else:
        form = forms.AddEntityToGroupForm(entity)

    context_dict = {
        'entity': entity,
        'form': form,
        'request': request,
    }

    return render(
        request,
        'Crm/add_entity_to_group.html',
        context_dict
    )


@user_passes_test(can_access)
@popup_redirect
def add_contact_to_group(request, contact_id):
    """view"""
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)

        if request.method == "POST":
            form = forms.AddContactToGroupForm(contact, request.POST)
            if form.is_valid():
                name = form.cleaned_data["group_name"]
                group = models.Group.objects.get_or_create(name=name)[0]
                if contact not in group.contacts.all():
                    group.contacts.add(contact)
                    group.save()
                next_url = reverse('crm_view_contact', args=[contact_id])
                return HttpResponseRedirect(next_url)
        else:
            form = forms.AddContactToGroupForm(contact)

        context_dict = {
            'contact': contact,
            'form': form,
        }

        return render(
            request,
            'Crm/add_contact_to_group.html',
            context_dict
        )

    # pylint: disable=broad-except
    except Exception as msg:
        print("#ERR", msg)
        raise


@user_passes_test(can_access)
def get_group_suggest_list(request):
    """view"""
    try:
        suggestions = []
        #the 1st chars entered in the autocomplete
        term = request.GET["term"]
        for group in models.Group.objects.filter(name__icontains=term):
            suggestions.append(group.name)
        return HttpResponse(json.dumps(suggestions), content_type='application/json')

    # pylint: disable=broad-except
    except Exception as msg:
        print('###', msg)


@user_passes_test(can_access)
@popup_redirect
def remove_entity_from_group(request, group_id, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    group = get_object_or_404(models.Group, id=group_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                group.entities.remove(entity)
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity_id]))
    else:
        form = forms.ConfirmForm()
    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _('Do you want to remove {0.name} from the {1.name} group?').format(entity, group),
            'action_url': reverse("crm_remove_entity_from_group", args=[group_id, entity_id]),
        }
    )


@user_passes_test(can_access)
@popup_redirect
def remove_contact_from_group(request, group_id, contact_id):
    """view"""
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)
        group = get_object_or_404(models.Group, id=group_id)
        if request.method == 'POST':
            form = forms.ConfirmForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["confirm"]:
                    group.contacts.remove(contact)
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact_id]))
        else:
            form = forms.ConfirmForm()
        return render(
            request,
            'balafon/confirmation_dialog.html',
            {
                'form': form,
                'message': _('Do you want to remove {0.fullname} from the {1.name} group?').format(contact, group),
                'action_url': reverse("crm_remove_contact_from_group", args=[group_id, contact_id]),
            }
        )

    # pylint: disable=broad-except
    except Exception as msg:
        print("#ERR", msg)
        raise


@user_passes_test(can_access)
def edit_group(request, group_id):
    """view"""

    groups = models.Group.objects.filter(id=group_id).prefetch_related('contacts', 'entities')

    if groups.count() == 0:
        raise Http404

    group = groups[0]

    next_url = request.session.get('next_url', reverse('crm_see_my_groups'))
    if request.method == "POST":
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            next_url = request.session.pop('next_url', reverse('crm_see_my_groups'))
            return HttpResponseRedirect(next_url)
    else:
        form = forms.EditGroupForm(instance=group)

    members = list(group.contacts.all()) + list(group.entities.all())
    members = [
        {
            'id': member.id,
            'type': 'entity' if isinstance(member, models.Entity) else 'contact',
            'name': member.name if isinstance(member, models.Entity) else member.fullname,
            'url': member.get_preview_url(),
            'raw': member.name if isinstance(member, models.Entity) else member.lastname,
        }
        for member in members
    ]
    members = sorted(members, key=lambda member: member['raw'])

    context_dict = {
        'form': form,
        'group': group,
        'members': members,
        'members_count': len(members),
        'request': request,
        'next_url': next_url,
    }

    return render(
        request,
        'Crm/edit_group.html',
        context_dict
    )


@user_passes_test(can_access)
@popup_redirect
def delete_group(request, group_id):
    """view"""
    group = get_object_or_404(models.Group, id=group_id)

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                group.delete()
                return HttpResponseRedirect(reverse("crm_see_my_groups"))
            else:
                return HttpResponseRedirect(reverse('crm_edit_group', args=[group.id]))
    else:
        form = forms.ConfirmForm()

    return render(
        request,
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _('Are you sure to delete the group {0.name}?').format(group),
            'action_url': reverse("crm_delete_group", args=[group_id]),
        }
    )


@user_passes_test(can_access)
def add_group(request):
    """view"""
    group = None

    if request.method == "POST":
        group = models.Group()
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm_see_my_groups'))
    else:
        form = forms.EditGroupForm()

    return render(
        request,
        'Crm/edit_group.html',
        {
            'group': group,
            'form': form,
        }
    )


@user_passes_test(can_access)
def see_my_groups(request):
    """view"""
    ordering = request.GET.get('ordering', 'name')

    groups = models.Group.objects.all()

    if ordering == 'name':
        try:
            # may fail for some databases
            groups = groups.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

        # pylint: disable=broad-except
        except Exception:
            groups = list(models.Group.objects.all())
            #order groups with case-independant name
            groups.sort(key=lambda group: group.name.lower())
    else:
        groups = groups.order_by('-modified')

    page_obj = paginate(request, groups, 50)

    return render(
        request,
        'Crm/my_groups.html',
        {
            'groups': list(page_obj),
            'page_obj': page_obj,
            'ordering': ordering,
        }
    )


@user_passes_test(can_access)
def get_group_name(request, gr_id):
    """view"""
    try:
        group = models.Group.objects.get(id=gr_id)
        return HttpResponse(json.dumps({'name': group.name}), 'application/json')

    except models.Group.DoesNotExist:
        return HttpResponse(json.dumps({'name': gr_id}), 'application/json')


@user_passes_test(can_access)
def get_groups(request):
    """view"""
    term = request.GET.get('term')
    queryset = models.Group.objects.filter(name__icontains=term)[:10]
    groups = [{'id': group.id, 'name': group.name} for group in queryset]
    return HttpResponse(json.dumps(groups), 'application/json')


@user_passes_test(can_access)
@log_error
def get_group_id(request):
    """view"""
    name = request.GET.get('name')
    try:
        group = get_object_or_404(models.Group, name__iexact=name)

    except models.Group.MultipleObjectsReturned:
        group = get_object_or_404(models.Group, name=name)
    return HttpResponse(json.dumps({'id': group.id}), 'application/json')


@user_passes_test(can_access)
@popup_redirect
def select_contact_or_entity(request):
    """view"""

    if request.method == 'POST':
        form = forms.SelectContactOrEntityForm(request.POST)
        if form.is_valid():
            obj = form.cleaned_data['name']
            dict_obj = {
                'id': form.cleaned_data['object_id'],
                'type': form.cleaned_data['object_type'],
                'name': obj.name if isinstance(obj, models.Entity) else obj.fullname,
                'url': obj.get_preview_url(),
            }
            json_data = json.dumps(dict_obj)
            return HttpResponse(
                '<script>$.colorbox.close(); if (addMember("{1}", {2})) {{addMemberToList({0});}};</script>'.format(
                    json_data, dict_obj['type'], dict_obj['id']
                )
            )
    else:
        form = forms.SelectContactOrEntityForm()

    return render(
        request,
        'Crm/popup_select_contact_or_entity.html',
        {
            'form': form,
        }
    )

@user_passes_test(can_access)
def get_contact_or_entity(request):
    """view"""
    try:
        suggestions = []
        #the 1st chars entered in the autocomplete
        term = request.GET.get("term", '')

        if len(term):

            for contact in models.Contact.objects.filter(lastname__istartswith=term)[:20]:
                suggestions.append(
                    {
                        'name': contact.fullname,
                        'type_and_id': 'contact#{0}'.format(contact.id),
                        'raw': contact.lastname
                    }
                )

            for entity in models.Entity.objects.filter(name__istartswith=term, is_single_contact=False)[:20]:
                suggestions.append(
                    {
                        'name': entity.name,
                        'type_and_id': 'entity#{0}'.format(entity.id),
                        'raw': entity.name
                    }
                )

        suggestions = sorted(
            suggestions, key=lambda obj_dict: obj_dict['raw'].lower()
        )[:20]

        return HttpResponse(json.dumps(suggestions), content_type='application/json')

    # pylint: disable=broad-except
    except Exception as msg:
        print('###', msg)
