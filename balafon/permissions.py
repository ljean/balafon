# -*- coding: utf-8 -*-
"""permission rules and utilities"""


def can_access(user):
    """define who can access"""
    return user.is_authenticated() and user.is_staff


def is_admin(user):
    """define who can access"""
    return user.is_authenticated() and user.is_superuser
