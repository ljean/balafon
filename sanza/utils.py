# -*- coding: utf-8 -*-
"""common utils"""

from bs4 import BeautifulSoup
from datetime import datetime
import logging

from django.http import HttpResponseRedirect, Http404

logger = logging.getLogger("sanza_crm")


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
    soup = BeautifulSoup(response.content)
    errors = soup.select('.field-error .label')
    return errors
