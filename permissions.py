# -*- coding: utf-8 -*-

def can_access(user):
    return user.is_authenticated() and user.is_staff
