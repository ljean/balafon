# -*- coding: utf-8 -*-
from django.utils.safestring import mark_safe
from django import template
register = template.Library()
from datetime import date

@register.filter
def seq_to_br(seq):
    if seq:
        return mark_safe(u"<br>".join([unicode(x) for x in seq]))
    return mark_safe(u"&nbsp;")

@register.filter
def seq_to_dash(seq):
    if seq:
        return mark_safe(u" - ".join(seq))
    return mark_safe(u"&nbsp;")

@register.filter
def is_today(dt):
    if dt:
        d = date(dt.year, dt.month, dt.day)
        return (d == date.today())
    return False
    
@register.filter
def cut_null_hour(value):
    try:
        x = value.split(u" ")    
        d, h = u' '.join(x[:-1]), x[-1]
        if h == "00:00":
            return d
    except:
        pass
    return value
    
@register.filter
def custom_field(instance, field_name):
    return getattr(instance, 'custom_field_'+field_name)
    

#Thanks http://djangosnippets.org/snippets/2058/
class IncludeNode(template.Node):
    def __init__(self, template_name):
        self.template_name = template_name

    def render(self, context):
        try:
            # Loading the template and rendering it
            included_template = template.loader.get_template(
                    self.template_name).render(context)
        except template.TemplateDoesNotExist:
            included_template = ''
        return included_template

@register.tag
def try_to_include(parser, token):
    """Usage: {% try_to_include "head.html" %}

    This will fail silently if the template doesn't exist. If it does, it will
    be rendered with the current context."""
    try:
        tag_name, template_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires a single argument" % token.contents.split()[0]

    return IncludeNode(template_name[1:-1])

@register.filter
def split_lines(lines, nb=1):
    try:
        return u"\n".join(lines.splitlines()[:nb])
    except Exception:
        return u""