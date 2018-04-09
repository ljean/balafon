# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

import json
import logging
import os.path
import shutil

from django.conf import settings
from django.test import TestCase as DjangoTestCase
from django.test.utils import override_settings

from coop_cms.utils import RequestManager


default_media_root = settings.MEDIA_ROOT


@override_settings(MEDIA_ROOT=os.path.join(default_media_root, '_unit_tests'))
class TestCase(DjangoTestCase):
    """Base class for tests"""

    def _clean_files(self):
        if default_media_root != settings.MEDIA_ROOT:
            try:
                shutil.rmtree(settings.MEDIA_ROOT)
            except OSError:
                pass
        else:
            raise Exception("Warning! wrong media root for unittesting")

    def setUp(self):
        """before each test"""
        RequestManager().clean()
        logging.disable(logging.CRITICAL)
        self._clean_files()

    def tearDown(self):
        """after each test"""
        logging.disable(logging.NOTSET)
        self._clean_files()


def response_as_json(response):
    return json.loads(response.content.decode('utf-8'))
