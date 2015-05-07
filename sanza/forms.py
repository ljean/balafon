# -*- coding: utf-8 -*-
"""Sanza : your django CRM"""

from django.contrib.auth.forms import AuthenticationForm

from coop_cms.bs_forms import BootstrapableMixin


class BsAuthenticationForm(BootstrapableMixin, AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(BsAuthenticationForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()
