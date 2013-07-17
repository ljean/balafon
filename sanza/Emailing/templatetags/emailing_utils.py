# -*- coding: utf-8 -*-

from django import template
register = template.Library()
#from djaloha.templatetags.djaloha_utils import DjalohaEditNode
#from sanza.Emailing.models import HtmlFragment
#
#class HtmlFragmentEditNode(DjalohaEditNode):
#    def render(self, context):
#        context.dicts[0]['can_edit_template'] = True
#        for (k, v) in self._lookup.items():
#            new_v = v.strip('"').strip("'")
#            if len(v)-2 == len(new_v):
#                self._lookup[k] = new_v
#            else:
#                self._lookup[k] = context[v]
#        return super(HtmlFragmentEditNode, self).render(context)
#
#@register.tag
#def html_edit(parser, token):
#    div_id = token.split_contents()[1]
#    return HtmlFragmentEditNode(HtmlFragment, {'div_id': div_id}, 'content')

@register.filter
def dir_debug(obj):
    return unicode(dir(obj))
