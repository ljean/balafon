# -*- coding: utf-8 -*-
"""view and edit entities"""

from datetime import date
import json
import re

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect

from sanza.Crm import models, forms
from sanza.Crm.utils import get_actions_by_set
from sanza.Crm.settings import is_unaccent_filter_supported
from sanza.permissions import can_access
from sanza.utils import log_error


@user_passes_test(can_access)
def get_entity_name(request, entity_id):
    """view"""
    try:
        entity = models.Entity.objects.get(id=entity_id)
        return HttpResponse(json.dumps({'name': entity.name}), 'application/json')
    except models.Entity.DoesNotExist:
        return HttpResponse(json.dumps({'name': entity_id}), 'application/json')


@user_passes_test(can_access)
def get_entities(request):
    """view"""
    term = request.GET.get('term')
    entities = [
        {'id': x.id, 'name': x.name}
        for x in models.Entity.objects.filter(name__icontains=term)
    ]
    return HttpResponse(json.dumps(entities), 'application/json')


@user_passes_test(can_access)
@log_error
def get_entity_id(request):
    """view"""
    name = request.GET.get('name', '')
    if name:
        entity = get_object_or_404(models.Entity, name=name)
        return HttpResponse(json.dumps({'id': entity.id}), 'application/json')
    raise Http404


@user_passes_test(can_access)
def view_entity(request, entity_id):
    """view"""

    entity = get_object_or_404(models.Entity, id=entity_id)
    contacts = entity.contact_set.all().order_by("has_left", "-main_contact", "lastname", "firstname")

    actions = models.Action.objects.filter(
        Q(entities=entity) | Q(contacts__entity=entity), Q(archived=False)
    ).distinct().order_by("planned_date", "priority")

    actions_by_set = get_actions_by_set(actions, 5)

    multi_user = True
    request.session["redirect_url"] = reverse('crm_view_entity', args=[entity_id])

    context = {
        "entity": entity,
        'contacts': contacts,
        'actions_by_set': actions_by_set,
        'multi_user': multi_user,
    }

    return render_to_response(
        'Crm/entity.html',
        context,
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_entities_list(request):
    """view"""
    letter_filter = request.GET.get("filter", "*")

    queryset = models.Entity.objects.all()
    if re.search(r"\w+", letter_filter):
        if is_unaccent_filter_supported():
            queryset = queryset.extra(
                where=[u"UPPER(unaccent(name)) LIKE UPPER(unaccent(%s))"],
                params=[u"{0}%".format(letter_filter)]
            )
        else:
            queryset = queryset.filter(name__istartswith=letter_filter)
    elif letter_filter == "~":
        queryset = queryset.filter(name__regex=r'^\W|^\d')
    entities = list(queryset)

    return render_to_response(
        'Crm/all_entities.html',
        {'entities': entities, "letter_filter": letter_filter},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def change_contact_entity(request, contact_id):
    """view"""
    try:
        contact = get_object_or_404(models.Contact, id=contact_id)

        if request.method == "POST":
            form = forms.ChangeContactEntityForm(contact, request.POST)
            if form.is_valid():
                form.change_entity()
                next_url = reverse('crm_view_contact', args=[contact_id])
                return HttpResponseRedirect(next_url)
        else:
            form = forms.ChangeContactEntityForm(contact)

        context_dict = {
            'contact': contact,
            'form': form,
        }

        return render_to_response(
            'Crm/change_contact_entity.html',
            context_dict,
            context_instance=RequestContext(request)
        )
    except Exception, msg:
        print "#ERR", msg
        raise



@user_passes_test(can_access)
@popup_redirect
def edit_entity(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    #update last access
    entity.save()
    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity)

    return render_to_response(
        'Crm/edit_entity.html',
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def create_entity(request, entity_type_id):
    """view"""
    try:
        entity_type_id = int(entity_type_id)
    except ValueError:
        raise Http404
    if entity_type_id:
        entity_type = get_object_or_404(models.EntityType, id=entity_type_id)
        entity = models.Entity(type=entity_type)
    else:
        entity = models.Entity()

    if request.method == "POST":
        form = forms.EntityForm(request.POST, request.FILES, instance=entity)
        if form.is_valid():
            entity = form.save()
            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        form = forms.EntityForm(instance=entity, initial={'relationship_date': date.today()})

    return render_to_response(
        'Crm/edit_entity.html',
        {
            'entity': entity,
            'form': form,
            'create_entity': True,
            'entity_type_id': entity_type_id,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_entity(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                entity.delete()
                return HttpResponseRedirect(reverse('sanza_homepage'))
            else:
                return HttpResponseRedirect(reverse('crm_edit_entity', args=[entity.id]))
    else:
        form = forms.ConfirmForm()
    return render_to_response(
        'sanza/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete {0.name}?').format(entity),
            'action_url': reverse("crm_delete_entity", args=[entity_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def select_entity_and_redirect(request, view_name, template_name):
    """view"""
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
