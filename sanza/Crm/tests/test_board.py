# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.core.urlresolvers import reverse


from sanza.Crm.tests import BaseTestCase


class BoardPanelTest(BaseTestCase):
    """board"""
    def test_view_board_panel(self):
        """test view board"""

        response = self.client.get(reverse("crm_board_panel"))
        self.assertRedirects(response, reverse('users_favorites_list'))
