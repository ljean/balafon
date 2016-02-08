# -*- coding: utf-8 -*-
"""test emailing actions"""

from django.contrib.auth.models import User
from django.utils.translation import ugettext

from model_mommy import mommy

from balafon.Crm import models
from balafon.Emailing.tests import BaseTestCase
from balafon.Users.models import UserPreferences


class ActionInFavoriteTestCase(BaseTestCase):

    def test_create_action_in_favorite(self):
        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        mommy.make(UserPreferences, user=user, message_in_favorites=True)

        action_type = mommy.make(models.ActionType, name=ugettext(u"Message"))
        action = mommy.make(models.Action, type=action_type)

        self.assertEqual(1, user.user_favorite_set.count())
        fav = user.user_favorite_set.all()[0]
        self.assertEqual(action, fav.content_object)

    def test_create_action_not_in_favorite(self):
        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=user, message_in_favorites=False)

        action_type = mommy.make(models.ActionType, name=ugettext(u"Message"))
        mommy.make(models.Action, type=action_type)

        self.assertEqual(0, user.user_favorite_set.count())