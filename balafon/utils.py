# -*- coding: utf-8 -*-
"""common utils"""

from bs4 import BeautifulSoup
from datetime import datetime
import logging
import urlparse

from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve, Resolver404
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _

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
    url = urlparse.urlparse(url_string)
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
        raise ValidationError(_(u'RGB format (e.g. #123456) expected'))
    return False


class Utf8JSONRenderer(JSONRenderer):
    """Utf-8 support"""
    ensure_ascii = False
