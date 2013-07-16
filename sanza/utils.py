# -*- coding: utf-8 -*-

from datetime import datetime
import logging
logger = logging.getLogger("sanza_crm")

def log_error(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except:
            logger.exception("exception")
            raise
    return wrapper

def now_rounded():
    now = datetime.now()
    return datetime(now.year, now.month, now.day, now.hour, now.minute, 0, 0)
