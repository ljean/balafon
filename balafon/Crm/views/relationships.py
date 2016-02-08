# -*- coding: utf-8 -*-
"""relationships between contacts"""

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_redirect

from balafon.Crm import models, forms
from balafon.permissions import can_access


@user_passes_test(can_access)
@popup_redirect
def add_relationship(request, contact_id):
    """view"""
    contact1 = get_object_or_404(models.Contact, id=contact_id)
    if request.method == "POST":
        form = forms.AddRelationshipForm(contact1, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact1.id]))
    else:
        form = forms.AddRelationshipForm(contact1)

    return render_to_response(
        'Crm/add_relationship.html',
        {'contact': contact1, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def delete_relationship(request, contact_id, relationship_id):
    """view"""
    err_msg = ""
    try:
        contact = models.Contact.objects.get(id=contact_id)
    except models.Contact.DoesNotExist:
        contact = None
        err_msg = _(u"The contact doesn't exist anymore")

    try:
        relationship = models.Relationship.objects.get(id=relationship_id)
    except models.Relationship.DoesNotExist:
        err_msg = _(u"The relationship doesn't exist anymore")

    if err_msg:
        if contact:
            next_url = reverse("crm_view_contact", args=[contact.id])
        else:
            next_url = reverse('crm_board_panel')
        return render_to_response(
            'balafon/message_dialog.html',
            {
                'message': err_msg,
                'next_url':  next_url,
            },
            context_instance=RequestContext(request)
        )
    else:
        if request.method == 'POST':
            form = forms.ConfirmForm(request.POST)
            if form.is_valid():
                if form.cleaned_data["confirm"]:
                    relationship.delete()
                return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
        else:
            form = forms.ConfirmForm()
        return render_to_response(
            'balafon/confirmation_dialog.html',
            {
                'form': form,
                'message': _(u'Are you sure to delete the relationship "{0}"?').format(relationship),
                'action_url': reverse("crm_delete_relationship", args=[contact_id, relationship_id]),
            },
            context_instance=RequestContext(request)
        )


@user_passes_test(can_access)
@popup_redirect
def same_as(request, contact_id):
    """mark 2 contacts to be the same person"""
    contact = get_object_or_404(models.Contact, id=contact_id)
    if request.method == "POST":
        form = forms.SameAsForm(contact, request.POST)
        if form.is_valid():
            if not contact.same_as:
                contact.same_as = models.SameAs.objects.create()
                contact.same_as_priority = 1
                contact.save()
            same_as_contact = form.cleaned_data['contact']
            same_as_contact.same_as_priority = contact.same_as.contact_set.count() + 1
            same_as_contact.same_as = contact.same_as
            same_as_contact.save()
            return HttpResponseRedirect(reverse('crm_view_contact', args=[contact.id]))
    else:
        form = forms.SameAsForm(contact)
        if not form.has_choices():
            return render_to_response(
                'balafon/message_dialog.html',
                {
                    'title': _(u'SameAs contacts'),
                    'message': _(u"No homonymous for {0}").format(contact),
                    'next_url': reverse('crm_view_contact', args=[contact.id]),
                },
                context_instance=RequestContext(request)
            )

    return render_to_response(
        'Crm/same_as.html',
        {'contact': contact, 'form': form},
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
def get_same_as_suggestions(request):
    """JSON API for getting same as contacts"""
    if request.method == "POST":
        form = forms.SameAsSuggestionForm(request.POST)
        if form.is_valid():
            suggestion_list = []
            for contact in form.get_suggested_contacts():
                suggestion_list.append({'id': contact.id, 'fullname': unicode(contact)})

            return HttpResponse(json.dumps(suggestion_list), content_type='application/json')
    else:
        raise Http404


@user_passes_test(can_access)
@popup_redirect
def remove_same_as(request, current_contact_id, contact_id):
    """remove the mark for 2 contacts being the same person"""

    current_contact = get_object_or_404(models.Contact, id=current_contact_id)
    contact = get_object_or_404(models.Contact, id=contact_id)
    if (not contact.same_as) or (not current_contact.same_as):
        raise Http404

    the_same_as = contact.same_as

    if request.method == 'POST':
        form = forms.ConfirmForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["confirm"]:
                if the_same_as.contact_set.count() <= 2:
                    for same_as_contact in the_same_as.contact_set.all():
                        same_as_contact.same_as = None
                        same_as_contact.same_as_priority = 0
                        same_as_contact.save()
                    # refresh
                    the_same_as = models.SameAs.objects.get(id=the_same_as.id)
                    the_same_as.delete()
                else:
                    # Recalculate priority order
                    priority_order = 0
                    for same_as_contact in the_same_as.contact_set.order_by('same_as_priority'):
                        if same_as_contact.id != contact.id:
                            priority_order += 1
                            if same_as_contact.same_as_priority != priority_order:
                                same_as_contact.same_as_priority = priority_order
                                same_as_contact.save()

                    # Remove the same-as link for the selected contact
                    contact.same_as = None
                    contact.same_as_priority = 0
                    contact.save()

            return HttpResponseRedirect(reverse('crm_view_contact', args=[current_contact_id]))
    else:
        form = forms.ConfirmForm()
    confirm_message = _(u'Are you sure that "{0}" and "{1}" are not identical?').format(contact, current_contact)
    if the_same_as.contact_set.count() > 2 and the_same_as.main_contact == contact:
        confirm_message += _(u"\n\nNote: {0} is the main contact. This role will be transfered to {1}.").format(
            contact, current_contact
        )

    return render_to_response(
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': confirm_message,
            'action_url': reverse("crm_remove_same_as", args=[current_contact_id, contact_id]),
        },
        context_instance=RequestContext(request)
    )


@user_passes_test(can_access)
@popup_redirect
def make_main_contact(request, current_contact_id, contact_id):
    """when a single person has several contacts: define the priority rules"""
    contact = get_object_or_404(models.Contact, id=contact_id)
    if not contact.same_as:
        raise Http404

    if request.method == 'POST':
        form = forms.SameAsPriorityForm(contact, request.POST)
        if form.is_valid():
            priority = form.cleaned_data["priority"]

            if priority != contact.same_as_priority:

                other_contact_queryset = contact.same_as.contact_set.exclude(id=contact.id)

                if priority > contact.same_as_priority:
                    # A1 --> 3  ->  B1
                    # B2        ->  C2
                    # C3        ->  A3
                    # D4

                    queryset = other_contact_queryset.filter(
                        same_as_priority__gt=contact.same_as_priority, same_as_priority__lte=priority
                    ).order_by('same_as_priority')

                    for index, other_contact in enumerate(queryset):
                        other_contact.same_as_priority = index + contact.same_as_priority
                        other_contact.save()

                elif priority < contact.same_as_priority:
                    # A1        ->  C1
                    # B2        ->  A2
                    # C3 --> 1      B3
                    # D4

                    queryset = other_contact_queryset.filter(
                        same_as_priority__gte=priority, same_as_priority__lt=contact.same_as_priority
                    ).order_by('same_as_priority')

                    for index, other_contact in enumerate(queryset):
                        other_contact.same_as_priority = index + priority + 1
                        other_contact.save()

                contact.same_as_priority = priority
                contact.save()

            return HttpResponseRedirect(reverse('crm_view_contact', args=[current_contact_id]))

    else:
        form = forms.SameAsPriorityForm(contact)

    return render_to_response(
        'balafon/confirmation_dialog.html',
        {
            'form': form,
            'message': _(
                u'{0}: Do you want to change the priority order of contacts for this person? (1 is higher priority)'
            ).format(
                contact
            ),
            'action_url': reverse("crm_make_main_contact", args=[current_contact_id, contact_id]),
        },
        context_instance=RequestContext(request)
    )
