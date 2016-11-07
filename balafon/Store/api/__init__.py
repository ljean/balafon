# -*- coding: utf-8 -*-

"""a simple store"""

from rest_framework import permissions


def get_staff_api_permissions():
    """get public api permissions"""
    return [permissions.IsAdminUser]
