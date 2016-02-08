#-*- coding: utf-8 -*-

from django.contrib.admin.widgets import ManyToManyRawIdWidget

from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse
from django.utils.html import escape


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
                label = escape(smart_unicode(obj))
                
                x = u'<a href="{0}" {1}>{2}</a>'.format(url,
                    'onclick="return showAddAnotherPopup(this);" target="_blank"',
                    label
                )
                
                str_values += [x]
            except self.rel.to.DoesNotExist:
                str_values += [u'???']
        return u'&nbsp;<strong>{0}</strong>'.format(u',&nbsp;'.join(str_values))
