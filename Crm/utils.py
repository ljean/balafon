# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

def get_users(self):
    return User.objects.exclude(firstame="", lastname="")