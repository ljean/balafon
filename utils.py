# -*- coding: utf-8 -*-

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
