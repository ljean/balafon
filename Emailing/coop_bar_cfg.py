# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_bar.utils import make_link

def back_to_newsletters(request, context):
    if request.user.is_authenticated:
        return make_link(reverse("emailing_newsletter_list"), _(u'Back to newsletters'), 'fugue/table--arrow.png',
            classes=['icon', 'alert_on_click'])

def load_commands(coop_bar):
    coop_bar.register([
        [back_to_newsletters]
    ])
