# -*- coding: utf-8 -*-
"""templatetags library"""

from __future__ import unicode_literals

from datetime import date, datetime

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

from balafon.Crm.models import ActionStatusTrack
from balafon.utils import logger

register = template.Library()


@register.filter
def seq_to_br(seq):
    """return sequence items separated by br html tags"""
    if seq:
        return mark_safe("<br>".join(['{0}'.format(x) for x in seq]))
    return mark_safe("&nbsp;")


@register.filter
def seq_to_dash(seq):
    """return sequence items separated by dashes"""
    if seq:
        return mark_safe(" - ".join(seq))
    return mark_safe("&nbsp;")


@register.filter
def is_today(date_time):
    """True if is today"""
    if date_time:
        date_val = date(date_time.year, date_time.month, date_time.day)
        return date_val == date.today()
    return False


@register.filter
def cut_null_hour(value):
    """remove the hour if 00:00"""
    try:
        date_and_hour = value.split(" ")
        date_, hour_ = ' '.join(date_and_hour[:-1]), date_and_hour[-1]
        if hour_ == "00:00":
            return date_
    except ValueError:
        pass
    return value


@register.filter
def get_action_date_label(action):
    """get label level (warning, danger) if date is raised"""
    if not action.planned_date:
        return "label-warning"
    if (not action.done) and action.planned_date < datetime.now():
        return "label-danger"
    return "label-not-yet"


@register.filter
def custom_field(instance, field_name):
    """access a custom field value"""
    return getattr(instance, 'custom_field_' + field_name)
    

class IncludeNode(template.Node):
    """
    try to load a template
    #Thanks http://djangosnippets.org/snippets/2058/
    """
    def __init__(self, template_name):
        self.template_name = template_name

    def render(self, context):
        try:
            # Loading the template and rendering it
            included_template = template.loader.get_template(self.template_name).render(context)
        except template.TemplateDoesNotExist:
            included_template = ''
        return included_template


@register.tag
def try_to_include(parser, token):
    """
    Usage: {% try_to_include "head.html" %}
    This will fail silently if the template doesn't exist. If it does, it will
    be rendered with the current context.
    """
    try:
        tag_name, template_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("{0} tag requires a single argument".format(token.contents.split()[0]))

    return IncludeNode(template_name[1:-1])


@register.filter
def split_lines(lines, nb=1):
    """split in lines"""
    try:
        return "\n".join(lines.splitlines()[:nb])
    except Exception:
        return ""


class MenuActionUrlNode(template.Node):
    """try to return a reverse without breaking app if invalid"""
    def __init__(self, view_name, action_id):
        self.view_name_var = view_name
        self.action_id_var = action_id

    def render(self, context):
        """return text"""
        try:
            obj, attr = self.view_name_var.split('.')
            view_name = getattr(context[obj], attr)

            obj, attr = self.action_id_var.split('.')
            action_id = getattr(context[obj], attr)

        except (ValueError, KeyError, AttributeError) as exc:
            logger.error('MenuActionUrl: {0}', exc)
            return ''

        try:
            action_id = int(action_id)
        except ValueError:
            logger.error("menu_action_url tag: action_id must be an integer")
            return ''

        try:
            return reverse(view_name, args=[action_id])
        except NoReverseMatch:
            logger.error(
                'MenuActionUrl: NoReverseMatch for reverse("{0}", args=[{1}])', self.view_name_var, self.action_id_var
            )
            return ''


@register.tag
def menu_action_url(parser, token):
    """return a reverse for action menu without breaking app if invalid """
    try:
        tag_name, view_name_var, action_id_var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("menu_action_url tag requires view_name and action_id")
    return MenuActionUrlNode(view_name_var, action_id_var)


@register.filter
def action_status_date(action, status):
    """return date"""
    queryset = ActionStatusTrack.objects.filter(action=action, status=status).order_by('-datetime')
    if queryset.count():
        return queryset[0].datetime
