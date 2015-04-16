# -*- coding: utf-8 -*-
"""about groups"""

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect

from sanza.Crm import models, forms
from sanza.permissions import can_access
from sanza.utils import log_error


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

    return render_to_response(
        'Crm/add_entity_to_group.html',
        context_dict,
        context_instance=RequestContext(request)
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

        return render_to_response(
            'Crm/add_contact_to_group.html',
            context_dict,
            context_instance=RequestContext(request)
        )

    # pylint: disable=broad-except
    except Exception, msg:
        print "#ERR", msg
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
    except Exception, msg:
        print '###', msg


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
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Do you want to remove {0.name} from the {1.name} group?').format(entity, group),
            'action_url': reverse("crm_remove_entity_from_group", args=[group_id, entity_id]),
        },
        context_instance=RequestContext(request)
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
        return render_to_response(
            'sanza/confirmation_dialog.html',
            {
                'form': form,
                'message': _(u'Do you want to remove {0.fullname} from the {1.name} group?').format(contact, group),
                'action_url': reverse("crm_remove_contact_from_group", args=[group_id, contact_id]),
            },
            context_instance=RequestContext(request)
        )

    # pylint: disable=broad-except
    except Exception, msg:
        print "#ERR", msg
        raise


@user_passes_test(can_access)
def edit_group(request, group_id):
    """view"""
    group = get_object_or_404(models.Group, id=group_id)
    next_url = request.session.get('next_url', reverse('crm_see_my_groups'))
    if request.method == "POST":
        form = forms.EditGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
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

    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the group {0.name}?').format(group),
            'action_url': reverse("crm_delete_group", args=[group_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def add_group(request):
    """view"""
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


@user_passes_test(can_access)
def see_my_groups(request):
    """view"""
    ordering = request.GET.get('ordering', 'name')

    groups = models.Group.objects.all()

    if ordering == 'name':
        try:
            #may fail for some databases
            groups = groups.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

        # pylint: disable=broad-except
        except Exception:
            groups = list(models.Group.objects.all())
            #order groups with case-independant name
            groups.sort(key=lambda group: group.name.lower())
    else:
        groups = groups.order_by('-modified')

    return render_to_response(
        'Crm/my_groups.html',
        locals(),
        context_instance=RequestContext(request)
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
