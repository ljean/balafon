# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from coop_bar.utils import make_link


def can_view(perm, object_names):
    def inner_decorator(func):
        def wrapper(request, context):
            for object_name in object_names:
                obj = context.get(object_name)
                if obj and request and request.user.has_perm(perm+"_"+object_name, obj):
                    yes_we_can = func(request, context)
                    if yes_we_can:
                        return yes_we_can
            return
        return wrapper
    return inner_decorator

can_view_object = can_view('can_view', ['object'])


@can_view_object
def doc_to_pdf(request, context):
    obj = context.get("object", None)
    if obj:
        if not context.get('edit_mode') and hasattr(obj, 'get_pdf_url'):
            return make_link(obj.get_pdf_url(), _('Pdf'), 'fugue/document-pdf.png',
                classes=['icon', 'alert_on_click'])


def load_commands(coop_bar):
    
    coop_bar.register([
        [doc_to_pdf],
    ])
