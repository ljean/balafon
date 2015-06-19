# -*- coding: utf-8 -*-
"""coop_bar configuration: add links to action document"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from coop_bar.utils import make_link

from sanza.Crm.models import Action, ActionDocument
from sanza.Store.models import StoreManagementActionType


def store_edit_sales_items(request, context):
    """add a link to action document """
    if request and request.user.is_authenticated() and request.user.is_staff:
        obj = context.get('object', None)
        if obj and isinstance(obj, ActionDocument) and obj.action.type:
            try:
                obj.action.type.storemanagementactiontype
            except StoreManagementActionType.DoesNotExist:
                return

            print "$", obj.action.type

        # return make_link(reverse("emailing_newsletter_list"), _(u'Back to newsletters'), 'fugue/table--arrow.png',
        #     classes=['icon', 'alert_on_click'])


def load_commands(coop_bar):
    """load commands"""
    coop_bar.register([
        [store_edit_sales_items],
    ])