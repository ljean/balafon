# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from coop_cms.perms_backends import ArticlePermissionBackend

from balafon.Profile.utils import check_category_permission


class EmailModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None, email=None):
        email = email or username
        kwargs = {
            'is_active': True,
            'email': email.strip(),
        }

        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
            
        except User.DoesNotExist:
            return None

        except User.MultipleObjectsReturned:
            for next_user in User.objects.filter(**kwargs):
                if next_user.check_password(password):
                    return next_user
            return None


class ArticleCategoryPermissionBackend(ArticlePermissionBackend):
    
    def has_perm(self, user_obj, perm, obj=None):
        if obj:
            if check_category_permission(obj, perm, user_obj):
                return super(ArticleCategoryPermissionBackend, self).has_perm(user_obj, perm, obj)
        return False
