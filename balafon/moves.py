# -*- coding: utf-8 -*-
"""
coop_cms manage compatibilty with django and python versions
"""

import json
import sys

from django import VERSION
from django.conf import settings


if sys.version_info[0] < 3:
    # Python 2
    import urllib2

    def urlopen(url):
        return urllib2.urlopen(url).read()
else:
    # Python 3
    from urllib.request import urlopen
