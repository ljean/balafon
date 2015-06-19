# -*- coding: utf-8 -*-
"""a simple store"""

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from colorbox.decorators import popup_close

from coop_cms.generic_views import EditableFormsetView

from sanza.Crm.models import Action
from sanza.Store.models import StoreItemSale
from sanza.Store.forms import StoreItemSaleForm


# @login_required
# @popup_close
# def edit_fragments(request):
#     """edit fragments of the current template"""
#
#     if not request.user.is_staff:
#         raise PermissionDenied
#
#     formset_class = modelformset_factory(StoreItemSale, forms.EditFragmentForm, extra=1)
#
#     if request.method == "POST":
#         formset = formset_class(request.POST, queryset=StoreItemSale)
#         if formset.is_valid():
#             formset.save()
#             #popup_close decorator will close and refresh
#             return None
#     else:
#         formset = formset_class(queryset=models.Fragment.objects.all())
#
#     context_dict = {
#         'form': formset,
#         'title': _(u"Edit store items?"),
#     }
#
#     return render_to_response(
#         'Store/popup_edit_store_items.html',
#         context_dict,
#         context_instance=RequestContext(request)
#     )


from django.forms.models import BaseModelFormSet
class CustomFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self. user = kwargs.pop('user', None)
        super(CustomFormSet, self).__init__(*args, **kwargs)

    def _construct_forms(self):
        self.forms = []
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i, user=self.user))


###########
### Comment passer un attribut au Fomrset?
### http://stackoverflow.com/a/623198/117092


class Callback(object):
    def __init__(self, field_name, value):
        self._field_name = field_name
        self._value = value

    def cb(self, **kwargs):
        print kwargs

class SalesDocumentView(EditableFormsetView):
    """
    Edit a sales document: bill, proposition...
    Make possible to change the StoreItemSale formset
    """
    model = StoreItemSale
    form_class = StoreItemSaleForm
    extra = 1
    action = None

    def get_action(self):
        """get the associated action"""
        if self.action is None:
            action_id = self.kwargs.get('action_id', 0)
            self.action = get_object_or_404(Action, id=action_id)
        return self.action

    def get_edit_url(self):
        """get edit url: where to go for edition"""
        return reverse('store_edit_sales_document', args=[self.get_action().id])

    def get_template(self):
        """get the template to use"""
        return self.get_action().type.default_template

    def get_success_url(self):
        """get success url : where to go after successful edition"""
        return reverse('store_view_sales_document', args=[self.get_action().id])

    def get_formset_class(self):
        """formset class"""
        return modelformset_factory(
            self.model, self.get_form_class(), extra=self.extra,
            form_callback=Callback('action', self.get_action()).cb
        )

    def get_queryset(self):
        """returns objects to edit"""
        queryset = super(SalesDocumentView, self).get_queryset()
        return queryset.filter(sale__action=self.get_action())

    def get_empty_object_kwargs(self):
        """get argument to use for creating an empty object"""
        sale = self.get_action().sale_set.all()[0]
        return {'sale': sale}

    def get_context_data(self, *args, **kwargs):
        """get context"""
        context = super(SalesDocumentView, self).get_context_data(*args, **kwargs)
        context['action'] = self.get_action()
        return context
