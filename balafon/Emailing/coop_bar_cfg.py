# -*- coding: utf-8 -*-
"""coop_bar configuration: add links to balafon"""

from django.urls import reverse
from django.utils.translation import ugettext as _

from coop_bar.utils import make_link


def balafon_homepage(request, context):
    """back to balafon homepage"""
    if request and request.user.is_authenticated and request.user.is_staff:
        return make_link(
            reverse("balafon_homepage"),
            _('Balafon'),
            'address-book',
            classes=['icon', 'alert_on_click']
        )


def back_to_newsletters(request, context):
    """back to balafon newsletters"""
    if request and request.user.is_authenticated and request.user.is_staff:
        return make_link(
            reverse("emailing_newsletter_list"),
            _('Back to newsletters'),
            'arrow-left',
            classes=['icon', 'alert_on_click']
        )


def load_commands(coop_bar):
    """load commands"""
    coop_bar.register([
        [balafon_homepage, back_to_newsletters],
    ])
