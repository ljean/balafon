# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from registration import get_version as get_registration_version
try:
    from registration.backends.default.views import RegistrationView, ActivationView
except ImportError:
    from registration.backends.model_activation.views import RegistrationView, ActivationView

from balafon.Crm.models import Action, ActionType
from balafon.Profile.forms import MessageForm
from balafon.Profile.models import ContactProfile
from balafon.Profile.settings import is_registration_enabled
from balafon.Profile.utils import create_profile_contact, notify_registration
from balafon.settings import get_profile_form, get_registration_form
from balafon.utils import now_rounded


@login_required 
def edit_profile(request):
    try:
        profile = request.user.contactprofile
    except ContactProfile.DoesNotExist:
        raise Http404

    profile_form_class = get_profile_form()
    
    if request.method == "POST":
        form = profile_form_class(request.POST, request.FILES, instance=profile.contact)
        if form.is_valid():
            #save contact
            form.save()
            messages.add_message(request, messages.SUCCESS, _("Your profile has been updated."))
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = profile_form_class(instance=profile.contact)
        
    return render(
        request,
        'Profile/edit_profile.html',
        {
            'contact': profile.contact,
            'form': form,
        }
    )


@login_required 
def post_message(request):
    try:
        profile = request.user.contactprofile
    except ContactProfile.DoesNotExist:
        raise Http404

    if not profile.contact:
        raise Http404
    
    if request.method == "POST":
        
        form = MessageForm(request.POST)
        if form.is_valid():
            
            message = form.cleaned_data['message']
            
            # send message by email
            notification_email = getattr(settings, 'BALAFON_NOTIFICATION_EMAIL', '')
            if notification_email:
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
                
                data = {
                    'contact': profile.contact,
                    'message': message,
                    'site': settings.COOP_CMS_SITE_PREFIX,
                }
                template_ = get_template('Emailing/subscribe_notification_email.txt')
                content = template_.render(data)
                email = EmailMessage(
                    _("Message from web site"), content, from_email,
                    [notification_email], headers = {'Reply-To': profile.contact.email})
                try:
                    email.send()
                    messages.add_message(request, messages.SUCCESS, _("The message have been sent"))
                except Exception:
                    messages.add_message(request, messages.ERROR, _("The message couldn't be send."))
                    
            # add an action
            message_action, _is_new = ActionType.objects.get_or_create(name=_('Message'))
            Action.objects.create(
                subject=_("New message on web site"), planned_date=now_rounded(),
                type=message_action, detail=message, contact=profile.contact, display_on_board=True
            )
        
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = MessageForm()
        
    return render(
        request,
        'Profile/post_message.html',
        {
            'contact': profile.contact,
            'form': form,
        }
    )


class AcceptNewsletterRegistrationView(RegistrationView):
    
    def get_form_class(self, request=None):
        return get_registration_form()

    def dispatch(self, request, *args, **kwargs):
        """make possible to disable this view from settings"""
        if not is_registration_enabled():
            raise Http404
        return super(AcceptNewsletterRegistrationView, self).dispatch(request, *args, **kwargs)
    
    def register(self, request_or_form, **kwargs):

        if get_registration_version() >= '2.0.0':
            data = request_or_form.cleaned_data
        else:
            data = kwargs
            kwargs["username"] = kwargs["email"][:30]

        user = super(AcceptNewsletterRegistrationView, self).register(request_or_form, **kwargs)

        user.first_name = data.get('firstname', "")
        user.last_name = data.get('lastname', "")

        user.contactprofile.firstname = data.get('firstname', "")
        user.contactprofile.lastname = data.get('lastname', "")

        user.contactprofile.entity_type = data.get('entity_type', None)
        user.contactprofile.entity_name = data.get('entity', "")

        user.contactprofile.phone = data.get('phone', "")
        user.contactprofile.mobile = data.get('mobile', "")

        user.contactprofile.city = data.get('city', None)
        user.contactprofile.zip_code = data.get('zip_code', None)
        user.contactprofile.gender = data.get('gender', 0) or 0

        user.contactprofile.address = data.get('address', "")
        user.contactprofile.address2 = data.get('address2', "")
        user.contactprofile.address3 = data.get('address3', "")
        user.contactprofile.cedex = data.get('cedex', "")
        user.contactprofile.birth_date = data.get('birth_date', None)

        user.contactprofile.groups_ids = data.get('groups_ids', '')

        user.save()
        user.contactprofile.save()

        subscription_types = data.get('subscription_types', None)

        user.contactprofile.subscriptions_ids = ",".join([str(s.id) for s in subscription_types])
        user.contactprofile.save()

        return user


class AcceptNewsletterActivationView(ActivationView):

    def activate(self, request, *args, **kwargs):
        activated_user = super(AcceptNewsletterActivationView, self).activate(request, *args, **kwargs)
        # The account has been activated: We can create the corresponding contact in Balafon
        if activated_user:
            profile = create_profile_contact(activated_user)
            notify_registration(profile)
        return activated_user
