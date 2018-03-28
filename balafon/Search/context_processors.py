# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.utils.safestring import mark_safe

from balafon.Search.forms import QuickSearchForm


def quick_search_form(request):
    return {'quick_search_form': QuickSearchForm()}
        

def jhouston(request):
    if 'jhouston' in settings.INSTALLED_APPS:
        return {'jhouston': 
            mark_safe('<script src="{0}jhouston/js/jhouston.js" type="text/javascript"></script>\n'.format(settings.STATIC_URL))
        }
    return {}
