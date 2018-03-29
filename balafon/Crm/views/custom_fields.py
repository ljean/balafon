# -*- coding: utf-8 -*-
"""Crm is the main module"""

from __future__ import unicode_literals

from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from colorbox.decorators import popup_redirect

from balafon.Crm import forms
from balafon.permissions import can_access


@user_passes_test(can_access)
@popup_redirect
def edit_custom_fields(request, model_name, instance_id):
    """view"""
    try:
        form_class = {
            'entity': forms.EntityCustomFieldForm,
            'contact': forms.ContactCustomFieldForm,
        }[model_name]
    except KeyError:
        raise Http404

    instance = get_object_or_404(form_class.model(), id=instance_id)

    if request.method == 'POST':
        form = form_class(instance, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = form_class(instance)

    return render(
        request,
        'Crm/edit_custom_fields.html',
        {'form': form, 'instance': instance, 'model_name': model_name},
    )
