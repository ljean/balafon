# -*- coding: utf-8 -*-
"""Crm is the main module"""

import django.dispatch

action_cloned = django.dispatch.Signal(providing_args=["original_action", "new_action"])

new_subscription = django.dispatch.Signal(providing_args=["instance", "contact"])
