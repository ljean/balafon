# -*- coding: utf-8 -*-
"""context processor"""

from sanza.Users.models import CustomMenu


def user_config(request):
    """add constant to context"""
    return {
        'users_custom_menus': [menu for menu in CustomMenu.objects.all() if menu.get_children()],
    }
