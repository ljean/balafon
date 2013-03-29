# -*- coding: utf-8 -*-

from registration.backends.default import DefaultBackend
from forms import UserRegistrationForm
from utils import create_profile_contact
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class AcceptNewsletterRegistrationBackend(DefaultBackend):
    
    def register(self, request, **kwargs):
        print kwargs
        kwargs["username"] = kwargs["email"] 
        user = super(AcceptNewsletterRegistrationBackend, self).register(request, **kwargs)
        
        #Store if 
        user.contactprofile.accept_newsletter = kwargs.get('accept_newsletter', False)
        user.contactprofile.accept_3rdparty = kwargs.get('accept_3rdparty', False)
        user.contactprofile.save()
        
        return user
    
    def get_form_class(self, request):
        return UserRegistrationForm
    
    def activate(self, request, activation_key):
        activated = super(AcceptNewsletterRegistrationBackend, self).activate(request, activation_key)
        
        #The account has been activated: We can create the corresponding contact in Sanza
        if activated:
            create_profile_contact(activated)
        
        return activated

class EmailModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username.strip())
            
            if not user.is_active:
                return None
            
            if user.check_password(password):
                return user
            
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            for u in User.objects.filter(email=username.strip()):
                if u.check_password(password):
                    return u
            return None