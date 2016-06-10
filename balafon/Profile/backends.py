# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from coop_cms.perms_backends import ArticlePermissionBackend

from balafon.Profile.utils import check_category_permission


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
            for _user in User.objects.filter(email=email.strip()):
                if _user.check_password(password):
                    return _user
            return None


class ArticleCategoryPermissionBackend(ArticlePermissionBackend):
    
    def has_perm(self, user_obj, perm, obj=None):
        if obj:
            if check_category_permission(obj, perm, user_obj):
                return super(ArticleCategoryPermissionBackend, self).has_perm(user_obj, perm, obj)
        return False
