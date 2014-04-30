# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from datetime import datetime
import logging
logger = logging.getLogger("sanza_crm")
from django.http import Http404

def log_error(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except Http404:
            raise
        except:
            logger.exception("exception")
            raise
    return wrapper

def now_rounded():
    now = datetime.now()
    return datetime(now.year, now.month, now.day, now.hour, now.minute, 0, 0)

class HttpResponseRedirectMailtoAllowed(HttpResponseRedirect):
    allowed_schemes = ['http', 'https', 'ftp', 'mailto']