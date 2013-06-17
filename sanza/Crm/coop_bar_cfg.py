# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_bar.utils import make_link
from coop_cms.coop_bar_cfg import can_edit_object

@can_edit_object
def doc_to_pdf(request, context):
    if request.user.is_authenticated() and request.user.is_staff:
        object = context["object"]
        if not context.get('edit_mode') and hasattr(object, 'get_pdf_url'):
            return make_link(object.get_pdf_url(), _(u'Pdf'), 'fugue/document-pdf.png',
                classes=['icon', 'alert_on_click'])

def load_commands(coop_bar):
    
    coop_bar.register([
        [doc_to_pdf],
    ])
    