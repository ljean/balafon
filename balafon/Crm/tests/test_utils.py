# -*- coding: utf-8 -*-
"""unit testing"""

from django.core.exceptions import ValidationError

from balafon.utils import validate_rgb
from balafon.Crm.tests import BaseTestCase


class CheckRgbTest(BaseTestCase):
    """check validate_rgb utility"""

    def test_validate_rgb_6_chars(self):
        """it should not raise an error"""
        validate_rgb("#123456")

    def test_validate_rgb_6_hexa(self):
        """it should not raise an error"""
        validate_rgb("#abcdef")

    def test_validate_rgb_3_chars(self):
        """it should not raise an error"""
        validate_rgb("#123")

    def test_validate_rgb_3_hexa(self):
        """it should not raise an error"""
        validate_rgb("#fff")

    def test_validate_rgb_mix(self):
        """it should not raise an error"""
        validate_rgb("#f1b2c3")

    def test_validate_rgb_invalid_char(self):
        """it should raise an error"""
        self.assertRaises(ValidationError, validate_rgb, '#hello')
        self.assertRaises(ValidationError, validate_rgb, 'cool')

    def test_validate_rgb_missing_chars(self):
        """it should raise an error"""
        self.assertRaises(ValidationError, validate_rgb, '#1')
        self.assertRaises(ValidationError, validate_rgb, '#12')
        self.assertRaises(ValidationError, validate_rgb, '#1234')
        self.assertRaises(ValidationError, validate_rgb, '#12345')

    def test_validate_rgb_missing_sharp(self):
        """it should raise an error"""
        self.assertRaises(ValidationError, validate_rgb, '123')
        self.assertRaises(ValidationError, validate_rgb, '123456')

    def test_validate_rgb_too_many_chars(self):
        """it should raise an error"""
        self.assertRaises(ValidationError, validate_rgb, '#1234567')
        self.assertRaises(ValidationError, validate_rgb, '#12345678')
