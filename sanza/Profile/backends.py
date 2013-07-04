# -*- coding: utf-8 -*-

from registration.backends.default import DefaultBackend
from forms import UserRegistrationForm
from utils import create_profile_contact, check_category_permission, notify_registration
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from models import CategoryPermission
from coop_cms.perms_backends import ArticlePermissionBackend

class AcceptNewsletterRegistrationBackend(DefaultBackend):
    
    def register(self, request, **kwargs):
        kwargs["username"] = kwargs["email"][:30]
        user = super(AcceptNewsletterRegistrationBackend, self).register(request, **kwargs)
        
        #Store if 
        user.contactprofile.accept_newsletter = kwargs.get('accept_newsletter', False)
        user.contactprofile.accept_3rdparty = kwargs.get('accept_3rdparty', False)
        
        user.first_name = kwargs.get('firstname', "")
        user.last_name = kwargs.get('lastname', "")
        user.contactprofile.entity_type = kwargs.get('entity_type', None)
        user.contactprofile.entity_name = kwargs.get('entity', "")
        user.contactprofile.city = kwargs.get('city', None)
        user.contactprofile.zip_code = kwargs.get('zip_code', None)
        user.contactprofile.gender = kwargs.get('gender', 0)
        
        user.save()
        user.contactprofile.save()
        
        return user
    
    def get_form_class(self, request):
        return UserRegistrationForm
    
    def activate(self, request, activation_key):
        activated_user = super(AcceptNewsletterRegistrationBackend, self).activate(request, activation_key)
        #The account has been activated: We can create the corresponding contact in Sanza
        if activated_user:
            profile = create_profile_contact(activated_user)
            notify_registration(profile)
        return activated_user

class EmailModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None, email=None):
        try:
            email = email or username
            user = User.objects.get(email=email.strip())
            
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
        
class ArticleCategoryPermissionBackend(ArticlePermissionBackend):
    
    def has_perm(self, user_obj, perm, obj=None):
        if obj:
            if check_category_permission(obj, perm, user_obj):
                return super(ArticleCategoryPermissionBackend, self).has_perm(user_obj, perm, obj)
        return False