# -*- coding: utf-8 -*-
"""common utils"""

from bs4 import BeautifulSoup
from datetime import datetime
import logging
from urllib.parse import urlparse
from importlib import import_module

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.urls import resolve, Resolver404
from django.utils.translation import ugettext as _

from coop_cms.utils.requests import RequestManager
from coop_cms.utils import dehtml
from rest_framework.renderers import JSONRenderer

from balafon.settings import get_allowed_homepages


logger = logging.getLogger("balafon_crm")


def log_error(view_func):
    """log error decorator"""
    def wrapper(request, *args, **kwargs):
        """wrapper"""
        try:
            return view_func(request, *args, **kwargs)
        except Http404:
            raise
        except:
            logger.exception("exception")
            raise
    return wrapper


def now_rounded():
    """datetime rounded to the minute"""
    now = datetime.now()
    return datetime(now.year, now.month, now.day, now.hour, now.minute, 0, 0)


class HttpResponseRedirectMailtoAllowed(HttpResponseRedirect):
    """Mailto redirect"""
    allowed_schemes = ['http', 'https', 'ftp', 'mailto']


def get_form_errors(response):
    """get form errors"""
    soup = BeautifulSoup(response.content, "html.parser")
    errors = soup.select('.field-error .label')
    return errors


def is_allowed_homepage(url_string):
    """return True is the current page can be set as homepage"""
    url = urlparse(url_string)
    try:
        safe_url = url.path
        resolved = resolve(safe_url)
    except Resolver404:
        return False
    if resolved.url_name in get_allowed_homepages():
        return True
    return False


def validate_rgb(value):
    """"check rgb"""
    wrong = False
    if not (len(value) == 7 or len(value) == 4):
        wrong = True
    else:
        if value[0] != "#":
            wrong = True
        else:
            try:
                int(value[1:], 16)
            except ValueError:
                wrong = True
    if wrong:
        raise ValidationError(_('RGB format (e.g. #123456) expected'))
    return False


class Utf8JSONRenderer(JSONRenderer):
    """Utf-8 support"""
    def render(self, *args, **kwargs):
        content = super(Utf8JSONRenderer, self).render(*args, **kwargs)
        return content.decode('utf-8')


def load_from_module(settings_key, default_value):
    """returns the form to be used for creating a new article"""
    full_class_name = getattr(settings, settings_key, '') or default_value
    if full_class_name:
        try:
            module_name, obj_name = full_class_name.rsplit('.', 1)
        except ValueError:
            raise ImportError("Unable to import {0}: full path is required".format(full_class_name))
        module = import_module(module_name)
        obj = getattr(module, obj_name)
        return obj
    return None


def send_email(subject, template_name, context, recipients, sender=None, cc_list=None):
    """Send an HTML email"""
    emails = []
    connection = get_connection()
    from_email = sender if sender else settings.DEFAULT_FROM_EMAIL
    for address in recipients:
        context['email_address'] = address
        context['subject'] = subject
        the_template = get_template(template_name)
        html_text = the_template.render(context)
        text = dehtml(html_text)
        email = EmailMultiAlternatives(subject, text, from_email, [address], cc=cc_list if cc_list else [])
        email.attach_alternative(html_text, "text/html")
        emails.append(email)
    return connection.send_messages(emails)


def full_path_url(url):
    request = RequestManager().get_request()
    is_secured = not settings.DEBUG
    if request:
        is_secured = request.is_secure()
    site = Site.objects.get_current(request)
    if url is None:
        url = ''
    full_url = site.domain + url
    if is_secured:
        return 'https://' + full_url
    else:
        return 'http://' + full_url
