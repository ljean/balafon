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
from django.template.loader import get_template
from models import ContactProfile
from sanza.utils import now_rounded
from registration.backends.default.views import RegistrationView, ActivationView
from forms import UserRegistrationForm
from utils import create_profile_contact, notify_registration

@login_required 
def edit_profile(request):
    try:
        profile = request.user.get_profile()
    except ContactProfile.DoesNotExist:
        raise Http404
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile.contact)
        if form.is_valid():
            contact = form.save()
            messages.add_message(request, messages.SUCCESS, _(u"Your profile has been updated."))
            return HttpResponseRedirect(reverse('homepage'))
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
            notification_email = getattr(settings, 'SANZA_NOTIFICATION_EMAIL', '')
            if notification_email:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
                
                data = {
                    'contact': profile.contact,
                    'message': message,
                    'site': settings.COOP_CMS_SITE_PREFIX,
                }
                t = get_template('Emailing/subscribe_notification_email.txt')
                content = t.render(Context(data))
                
                email = EmailMessage(
                    _(u"Message from web site"), content, from_email,
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
                subject=_(u"New message on web site"), planned_date=now_rounded(),
                type = message_action, detail=message, contact=profile.contact, display_on_board=True
            )
        
            return HttpResponseRedirect(reverse('homepage'))
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

class AcceptNewsletterRegistrationView(RegistrationView):
    
    def get_form_class(self, request):
        return UserRegistrationForm
    
    def register(self, request, **kwargs):
        kwargs["username"] = kwargs["email"][:30]
        user = super(AcceptNewsletterRegistrationView, self).register(request, **kwargs)
        
        #Store if 
        user.contactprofile.accept_newsletter = kwargs.get('accept_newsletter', False)
        user.contactprofile.accept_3rdparty = kwargs.get('accept_3rdparty', False)
        
        user.first_name = kwargs.get('firstname', "")
        user.last_name = kwargs.get('lastname', "")
        user.contactprofile.entity_type = kwargs.get('entity_type', None)
        user.contactprofile.entity_name = kwargs.get('entity', "")
        user.contactprofile.city = kwargs.get('city', None)
        user.contactprofile.zip_code = kwargs.get('zip_code', None)
        user.contactprofile.gender = kwargs.get('gender', 0) or 0
        
        user.save()
        user.contactprofile.save()
        
        return user

class AcceptNewsletterActivationView(ActivationView):
    def activate(self, request, *args, **kwargs):
        activated_user = super(AcceptNewsletterActivationView, self).activate(request, *args, **kwargs)
        #The account has been activated: We can create the corresponding contact in Sanza
        if activated_user:
            profile = create_profile_contact(activated_user)
            notify_registration(profile)
        return activated_user