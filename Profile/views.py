# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings
from forms import ProfileForm
from django.contrib.auth.decorators import login_required

@login_required 
def edit_profile(request):
    profile = request.user.get_profile()
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile.contact)
        if form.is_valid():
            contact = form.save()
            return HttpResponseRedirect(reverse('profile_edit'))
    else:
        form = ProfileForm(instance=profile.contact)
        
    return render_to_response(
        'Profile/edit_profile.html',
        {
            'contact': profile.contact,
            'form': form,
        },
        context_instance=RequestContext(request)
    )