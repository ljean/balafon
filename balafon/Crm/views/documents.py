# -*- coding: utf-8 -*-
"""documents"""

from __future__ import unicode_literals

from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.contrib.messages import api as user_message
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from coop_cms.generic_views import EditableObjectView
from wkhtmltopdf.views import PDFTemplateView

from balafon.Crm import models, forms
from balafon.utils import logger


class ActionDocumentDetailView(EditableObjectView):
    """view"""
    model = models.ActionDocument
    edit_mode = False
    form_class = forms.ActionDocumentForm
    #varname = "action_doc"

    def get_object(self):
        """get action"""
        action = get_object_or_404(models.Action, pk=self.kwargs['pk'])
        try:
            return action.actiondocument
        except self.model.DoesNotExist:
            warning_text = ""
            if not action.type:
                warning_text = _("The action has no type set: Unable to create the corresponding document")
            elif not action.type.default_template:
                warning_text = _(
                    "The action type has no document template defined: Unable to create the corresponding document"
                )
            if warning_text:
                logger.warning(warning_text)
                user_message.warning(self.request, warning_text)
                raise Http404
            else:
                return self.model.objects.create(action=action, template=action.type.default_template)

    def get_template(self):
        """get template"""
        return self.object.template


class ActionDocumentEditView(ActionDocumentDetailView):
    """view"""
    edit_mode = True


class ActionDocumentPdfView(PDFTemplateView):
    """view"""

    def find_template(self, template_type, action_type):
        """look for template"""
        potential_templates = []
        if action_type:
            action_type = slugify(action_type.name)
            potential_templates += [
                "documents/_{0}_{1}.html".format(action_type, template_type),
            ]

        potential_templates += [
            "documents/_{0}.html".format(template_type),
        ]

        for template_name in potential_templates:
            try:
                get_template(template_name)
                return template_name
            except TemplateDoesNotExist:
                pass

        return None

    def render_to_response(self, context, **response_kwargs):
        """render"""
        try:
            action = get_object_or_404(models.Action, pk=self.kwargs['pk'])
        except models.Action.DoesNotExist:
            raise Http404
        try:
            doc = action.actiondocument
        except models.ActionDocument.DoesNotExist:
            raise Http404

        if not self.request.user.has_perm('can_view_object', doc):
            raise PermissionDenied
        context['to_pdf'] = True
        context['object'] = doc
        self.template_name = doc.template

        pdf_options_dict = getattr(settings, 'BALAFON_PDF_OPTIONS', None)
        if pdf_options_dict is None:
            pdf_options = {'margin-top': 0, 'margin-bottom': 0, 'margin-right': 0, 'margin-left': 0, }
        else:
            pdf_options = pdf_options_dict.get(self.template_name, {})
        if self.cmd_options:
            self.cmd_options.update(pdf_options)
        else:
            self.cmd_options = pdf_options
        self.header_template = self.find_template("header", action.type)
        self.footer_template = self.find_template("footer", action.type)
        self.filename = slugify("{0}.contact - {0}.subject".format(action))+".pdf"
        return super(ActionDocumentPdfView, self).render_to_response(context, **response_kwargs)
