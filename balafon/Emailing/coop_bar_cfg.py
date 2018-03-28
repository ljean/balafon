# -*- coding: utf-8 -*-
"""coop_bar configuration: add links to balafon"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from coop_bar.utils import make_link


def balafon_homepage(request, context):
    """back to balafon homepage"""
    if request and request.user.is_authenticated() and request.user.is_staff:
        return make_link(
            reverse("balafon_homepage"),
            _('Balafon'),
            'img/balafon-icon.png',
            classes=['icon', 'alert_on_click']
        )


def back_to_newsletters(request, context):
    """back to balafon newsletters"""
    if request and request.user.is_authenticated() and request.user.is_staff:
        return make_link(
            reverse("emailing_newsletter_list"),
            _('Back to newsletters'),
            'fugue/table--arrow.png',
            classes=['icon', 'alert_on_click']
        )


def load_commands(coop_bar):
    """load commands"""
    coop_bar.register([
        [balafon_homepage, back_to_newsletters],
    ])
