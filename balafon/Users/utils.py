# -*- coding: utf-8 -*-

from balafon.permissions import can_access

from .models import UserPermissions


def can_create_group(user):
    """define who can access"""
    if can_access(user):
        try:
            preferences = UserPermissions.objects.get(user=user)
            return preferences.can_create_group
        except UserPermissions.DoesNotExist:
            return True  # allowed by default
    return False
