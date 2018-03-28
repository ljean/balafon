# -*- coding: utf-8 -*-
"""permission rules and utilities"""

from __future__ import unicode_literals


def can_access(user):
    """define who can access"""
    return user.is_authenticated() and user.is_staff


def is_admin(user):
    """define who can access"""
    return user.is_authenticated() and user.is_superuser
