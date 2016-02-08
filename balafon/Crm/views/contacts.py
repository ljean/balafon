# -*- coding: utf-8 -*-
"""contacts"""

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect

from balafon.Crm import models, forms
from balafon.Crm.utils import get_actions_by_set
from balafon.permissions import can_access
from balafon.utils import log_error


@user_passes_test(can_access)
def get_contact_name(request, contact_id):
    """view"""
    try:
        contact = models.Contact.objects.get(id=contact_id)
        return HttpResponse(json.dumps({'name': contact.get_name_and_entity()}), 'application/json')
    except models.Contact.DoesNotExist:
        return HttpResponse(json.dumps({'name': contact_id}), 'application/json')


def get_contacts_from_term(term):
    """view"""
    terms = [word.strip('()') for word in term.split(' ')]

    contacts = []
    contact_set = set()
    for i, term in enumerate(terms):
        matching_contacts = list(models.Contact.objects.filter(
            Q(firstname__icontains=term) |
            Q(lastname__icontains=term) |
            Q(entity__name__icontains=term, entity__is_single_contact=False)
        ))
        if not matching_contacts:
            contact_set = set()
            break
        if i == 0:
            contact_set = set(matching_contacts)
        else:
            contact_set = contact_set.intersection(matching_contacts)

    if not contact_set:
        for term in terms:
            queryset = models.Contact.objects.filter(
                Q(firstname__icontains=term) |
                Q(lastname__icontains=term) |
                Q(entity__name__icontains=term, entity__is_single_contact=False)
            )
            contacts += list(queryset)

    contacts = list(contact_set or set(contacts))
    contacts = [
        {'id': matching_contacts.id, 'name': matching_contacts.get_name_and_entity()}
        for matching_contacts in contacts
    ]
    return sorted(contacts, key=lambda contact: contact['name'])


@user_passes_test(can_access)
@log_error
def get_contact_id(request):
    """view"""
    name = request.GET.get('name')
    contacts = get_contacts_from_term(name)
    if len(contacts) != 1:
        raise Http404
    return HttpResponse(json.dumps({'id': contacts[0]['id']}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_contacts(request):
    """view"""
    term = request.GET.get('term')
    contacts = get_contacts_from_term(term)
    return HttpResponse(json.dumps(contacts), 'application/json')


@user_passes_test(can_access)
@popup_redirect
def edit_contact(request, contact_id, mini=True, go_to_entity=False):
    """view"""
    contact = get_object_or_404(models.Contact, id=contact_id)

    entity = contact.entity

    if request.method == 'POST':
        form = forms.ContactForm(request.POST, request.FILES, instance=contact)
        if form.is_valid():
            contact = form.save()

            if go_to_entity:
                return HttpResponseRedirect(reverse('crm_view_entity', args=[contact.entity.id]))
            else:
                return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.ContactForm(instance=contact)

    return render_to_response(
        'Crm/edit_contact.html',
        {
            'form': form,
            'contact': contact,
            'entity': entity,
            'go_to_entity': go_to_entity,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def view_contact(request, contact_id):
    """view"""
    contact = get_object_or_404(models.Contact, id=contact_id)
    same_as_contact = None

    try:
        preview = bool(request.GET.get('preview', False))
    except ValueError:
        preview = False

    actions = contact.action_set.filter(archived=False)
    actions_by_set = get_actions_by_set(actions, 5)

    request.session["redirect_url"] = reverse('crm_view_contact', args=[contact_id])

    if contact.same_as:
        same_as_contact = models.Contact.objects.filter(
            same_as=contact.same_as
        ).exclude(id=contact.id).order_by('same_as_priority')

    return render_to_response(
        'Crm/view_contact.html',
        {
            'contact': contact,
            'actions_by_set': actions_by_set,
            'same_as': same_as_contact,
            'entity': contact.entity,
            'preview': preview,
            'template_base': "balafon/bs_base.html" if not preview else "balafon/bs_base_raw.html"
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def add_contact(request, entity_id):
    """view"""
    entity = get_object_or_404(models.Entity, id=entity_id)
    contact = models.Contact(entity=entity)

    if request.method == 'POST':
        contact_form = forms.ContactForm(request.POST, request.FILES, instance=contact)
        if contact_form.is_valid():
            contact = contact_form.save()
            photo = contact_form.cleaned_data['photo']
            if photo is not None:
                if type(photo) == bool:
                    contact.photo = None
                    contact.save()
                else:
                    contact.photo.save(photo.name, photo)

            return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
    else:
        contact_form = forms.ContactForm(instance=contact)

    return render_to_response(
        'Crm/edit_contact.html',
        {
            "entity": entity,
            "form": contact_form,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
@log_error
def add_single_contact(request):
    """view"""
    if request.method == 'POST':
        contact = models.Contact()
        contact_form = forms.ContactForm(request.POST, request.FILES, instance=contact)
        if contact_form.is_valid():

            entity = models.Entity(
                name=contact.fullname,
                is_single_contact=True
            )
            entity.save()
            # This create a default contact
            default_contact = entity.default_contact

            contact.entity = entity
            contact = contact_form.save()

            # contact = contact_form.save(commit=False)
            # contact.entity = entity
            # contact.save()

            default_contact.delete()
            # change name of the entity
            contact.save()

            contact_form.save_contact_subscriptions(contact)

            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
        else:
            contact = None
    else:
        contact = None
        contact_form = forms.ContactForm()

    return render_to_response(
        'Crm/edit_contact.html',
        {
            'contact': contact,
            'form': contact_form,
            'is_single_contact': True,
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_contact(request, contact_id):
    """view"""

    contact = get_object_or_404(models.Contact, id=contact_id)
    entity = contact.entity

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if contact.entity.is_single_contact:
                    contact.entity.delete()
                    return HttpResponseRedirect(reverse('crm_board_panel'))
                else:
                    contact.delete()
                    return HttpResponseRedirect(reverse('crm_view_entity', args=[entity.id]))
            else:
                return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.ConfirmForm()

    return render_to_response(
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(u'Are you sure to delete the contact "{0}"?').format(contact),
            'action_url': reverse("crm_delete_contact", args=[contact_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def select_contact_and_redirect(request, view_name, template_name, choices=None):
    """utility view"""
    opportunity_id = request.GET.get('opp_id', 0)
    url_args = "?opp_id={0}".format(opportunity_id) if opportunity_id else ""

    if request.method == 'POST':
        form = forms.SelectContactForm(request.POST)
        if form.is_valid():
            contact = form.cleaned_data["contact"]
            args = [contact.id]
            url = reverse(view_name, args=args)+url_args
            return HttpResponseRedirect(url)
    else:
        form = forms.SelectContactForm(choices=choices)

    post_url = reverse("crm_add_action")+url_args

    return render_to_response(
        template_name,
        {'form': form, 'post_url': post_url},
        context_instance=RequestContext(request)
    )
