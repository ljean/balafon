# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
from django.utils.html import escape

import floppyforms.__future__ as forms


class VerboseManyToManyRawIdWidget(ManyToManyRawIdWidget):
    """
    A Widget for displaying ManyToMany ids in the "raw_id" interface rather than
    in a <select multiple> box. Display user-friendly value like the ForeignKeyRawId widget
    """
    def __init__(self, rel, attrs=None, *args, **kwargs):
        super(VerboseManyToManyRawIdWidget, self).__init__(rel, attrs, *args, **kwargs)
        
    def label_for_value(self, value):
        values = value.split(',')
        str_values = []
        key = self.rel.get_related_field().name
        app_label = self.rel.to._meta.app_label
        class_name = self.rel.to._meta.object_name.lower()
        for v in values:
            try:
                obj = self.rel.to._default_manager.using(self.db).get(**{key: v})
                url = reverse('admin:{0}_{1}_change'.format(app_label, class_name), args=[obj.id])
                label = escape(smart_text(obj))
                
                x = '<a href="{0}" {1}>{2}</a>'.format(
                    url,
                    'onclick="return showAddAnotherPopup(this);" target="_blank"',
                    label
                )
                
                str_values += [x]
            except self.rel.to.DoesNotExist:
                str_values += ['???']
        return '&nbsp;<strong>{0}</strong>'.format(',&nbsp;'.join(str_values))


class CalcHiddenInput(forms.HiddenInput):
    """This field is calculated and hidden. It is not in POST data"""

    def value_omitted_from_data(self, data, files, name):
        # Tell django that this is field value doesn't come from POST data
        return False
