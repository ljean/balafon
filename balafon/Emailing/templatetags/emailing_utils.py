# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.core.urlresolvers import reverse

register = template.Library()


class EmailTrackingEditNode(template.Node):
    
    def render(self, context):
        emailing = context.get('emailing', None)
        contact = context.get('contact', None)
        if emailing and contact:
            tracking_url = reverse("emailing_email_tracking", args=[emailing.id, contact.uuid])
            return '<img src="{0}" />'.format(tracking_url)
        return '<!-- tracking -->'


@register.tag
def email_tracking(parser, token):
    return EmailTrackingEditNode()


@register.filter
def dir_debug(obj):
    return '{0}'.format(dir(obj))
