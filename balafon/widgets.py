# -*- coding: utf-8 -*-

from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.urls import reverse
from django.utils.encoding import smart_text
from django.utils.html import escape, mark_safe

import floppyforms.__future__ as forms


class VerboseManyToManyRawIdWidget(ManyToManyRawIdWidget):
    """
    A Widget for displaying ManyToMany ids in the "raw_id" interface rather than
    in a <select multiple> box. Display user-friendly value like the ForeignKeyRawId widget
    """

    def __init__(self, rel, attrs=None, *args, **kwargs):
        super().__init__(rel, attrs, *args, **kwargs)

    def label_and_url_for_value(self, value):
        values = value
        str_values = []
        key = self.rel.field.name
        app_label = self.rel.model._meta.app_label
        class_name = self.rel.model._meta.model_name.lower()
        for elt in values:
            try:
                obj = self.rel.related_model.objects.using(self.db).get(**{key: elt})
                url = reverse('admin:{0}_{1}_change'.format(app_label, class_name), args=[obj.id])
                label = escape(smart_text(obj))
                link = '<a href="{0}" {1}>{2}</a>'.format(
                    url,
                    'onclick="return showAddAnotherPopup(this);" target="_blank"',
                    label
                )
                str_values += [link]
            except self.rel.related_model.DoesNotExist:
                str_values += ['???']
        return mark_safe('&nbsp;<strong>{0}</strong>'.format(',&nbsp;'.join(str_values))), ''


class CalcHiddenInput(forms.HiddenInput):
    """This field is calculated and hidden. It is not in POST data"""

    def value_omitted_from_data(self, data, files, name):
        # Tell django that this is field value doesn't come from POST data
        return False
