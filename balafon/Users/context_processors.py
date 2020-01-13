# -*- coding: utf-8 -*-
"""context processor"""

from balafon.Users.models import CustomMenu


def user_config(request):
    """add constant to context"""

    return {
        'users_custom_menus': [
            menu for menu in CustomMenu.objects.filter(position=CustomMenu.POSITION_MENU) if menu.get_children()
        ],
    }
