# -*- coding: utf-8 -*-
"""coop_bar configuration: add links to sanza"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from coop_bar.utils import make_link


def sanza_homepage(request, context):
    """back to sanza homepage"""
    if request and request.user.is_authenticated() and request.user.is_staff:
        return make_link(reverse("sanza_homepage"), _(u'Sanza'), 'fugue/table--arrow.png',
            classes=['icon', 'alert_on_click'])


def back_to_newsletters(request, context):
    """back to sanza newsletters"""
    if request and request.user.is_authenticated() and request.user.is_staff:
        return make_link(reverse("emailing_newsletter_list"), _(u'Back to newsletters'), 'fugue/table--arrow.png',
            classes=['icon', 'alert_on_click'])


def load_commands(coop_bar):
    """load commands"""
    coop_bar.register([
        [sanza_homepage, back_to_newsletters],
    ])