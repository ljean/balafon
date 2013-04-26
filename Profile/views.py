# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.conf import settings
from forms import ProfileForm, MessageForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sanza.Crm.models import Action, ActionType
from datetime import datetime
from django.core.mail import send_mail, EmailMessage

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
    
@login_required 
def post_message(request):
    profile = request.user.get_profile()
    if not profile.contact:
        raise Http404
    
    if request.method == "POST":
        
        form = MessageForm(request.POST)
        if form.is_valid():
            
            message = form.cleaned_data['message']
            
            #send message by email
            notification_email = getattr(settings, 'SANZA_NOTIFY_SUBSCRIPTIONS', '')
            if notification_email:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
                
                email = EmailMessage(
                    _(u"Message from web site"), message, from_email,
                    [notification_email], headers = {'Reply-To': profile.contact.email})
                try:
                    email.send()
                    messages.add_message(request, messages.SUCCESS,
                        _(u"The message have been sent"))
                except Exception, msg:
                    messages.add_message(request, messages.ERROR,
                        _(u"The message couldn't be send."))
                    
            #add an action
            message_action, _is_new = ActionType.objects.get_or_create(name=_(u'Message'))
            action = Action.objects.create(
                subject=_(u"New message on web site"), planned_date=datetime.now(),
                type = message_action, detail=message, contact=profile.contact, display_on_board=True
            )
        
            return HttpResponseRedirect(reverse('profile_post_message'))
    else:
        form = MessageForm()
        
    return render_to_response(
        'Profile/post_message.html',
        {
            'contact': profile.contact,
            'form': form,
        },
        context_instance=RequestContext(request)
    )