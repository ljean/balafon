# -*- coding: utf-8 -*-

from django import template
register = template.Library()
from django.core.urlresolvers import reverse
from django.conf import settings

class EmailTrackingEditNode(template.Node):
    
    def render(self, context):
        emailing = context.get('emailing', None)
        contact = context.get('contact', None)
        if emailing and contact:
            tracking_url = reverse("emailing_email_tracking", args=[emailing.id, contact.uuid])
            return u'<img src="{0}" />'.format(tracking_url)
        return u"<!-- tracking -->"

@register.tag
def email_tracking(parser, token):
    return EmailTrackingEditNode()


@register.filter
def dir_debug(obj):
    return unicode(dir(obj))
