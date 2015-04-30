# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


class ActionArchiveTest(BaseTestCase):

    def test_view_monthly_action_anonymous(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.client.logout()

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_monthly_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.user.is_staff = False
        self.user.save()

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month])
        response = self.client.get(url)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_monthly_action(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=31))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=31))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        n = datetime.now()
        url = reverse('crm_actions_of_month', args=[n.year, n.month])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

    def test_view_monthly_action_end_dt(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 29), end_datetime=datetime(2014, 5, 2))
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 4, 2))
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 3, 30))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime(2014, 5, 1), end_datetime=datetime(2014, 5, 2))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        a6 = mommy.make(models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 8))
        a7 = mommy.make(models.Action, subject="#ACT7#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 5, 2))
        a8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 29))

        url = reverse('crm_actions_of_month', args=[2014, 4])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        self.assertContains(response, a6.subject)
        self.assertContains(response, a7.subject)
        self.assertContains(response, a8.subject)

    def test_view_weekly_action_anonymous(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.client.logout()

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%U")])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_weekly_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.user.is_staff = False
        self.user.save()

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%U")])
        response = self.client.get(url)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_weekly_action(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=7))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=7))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%U")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

    def test_view_weekly_action_end_dt(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 15))
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime(2014, 4, 1), end_datetime=datetime(2014, 4, 9))
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime(2014, 4, 1), end_datetime=datetime(2014, 4, 2))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime(2014, 4, 15), end_datetime=datetime(2014, 4, 16))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        a6 = mommy.make(models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 8))
        a7 = mommy.make(models.Action, subject="#ACT7#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 5, 2))
        a8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 9))

        url = reverse('crm_actions_of_week', args=[2014, 14])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        self.assertContains(response, a6.subject)
        self.assertContains(response, a7.subject)
        self.assertContains(response, a8.subject)

    def test_view_daily_action_anonymous(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.client.logout()

        now = datetime.now()
        url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_dailly_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.user.is_staff = False
        self.user.save()

        now = datetime.now()
        url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day])
        response = self.client.get(url)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_daily_action(self):
        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=1))
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=1))
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        now = datetime.now()
        url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

    def test_view_daily_action_end_dt(self):
        a1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 9)
        )
        a2 = mommy.make(
            models.Action, subject="#ACT2#", planned_date=datetime(2014, 4, 8), end_datetime=datetime(2014, 4, 12)
        )
        a3 = mommy.make(
            models.Action, subject="#ACT3#", planned_date=datetime(2014, 4, 8), end_datetime=datetime(2014, 4, 8)
        )
        a4 = mommy.make(
            models.Action, subject="#ACT4#", planned_date=datetime(2014, 4, 10), end_datetime=datetime(2014, 4, 10)
        )
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        a6 = mommy.make(
            models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 9)
        )
        a7 = mommy.make(
            models.Action, subject="#ACT7#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 10)
        )
        a8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 9))

        url = reverse('crm_actions_of_day', args=[2014, 4, 9])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)
        self.assertContains(response, a6.subject)
        self.assertContains(response, a7.subject)
        self.assertContains(response, a8.subject)

    def test_view_monthly_action_in_charge_filter(self):
        user_joe = mommy.make(User, first_name="Joe", is_staff=True)
        user_jack = mommy.make(User, first_name="Jack", is_staff=True)
        user_will = mommy.make(User, first_name="William", is_staff=True)

        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), in_charge=user_joe)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), in_charge=user_joe)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), in_charge=user_jack)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), in_charge=user_will)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        n = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[n.year, n.month]
        ) + "?filter=u{0},u{1}".format(user_joe.id, user_jack.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"u{0}".format(y.id) for y in [user_joe, user_jack]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_monthly_action_type_filter(self):
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)
        action_type3 = mommy.make(models.ActionType)

        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type1)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type2)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type3)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=t{0},t{1}".format(action_type1.id, action_type2.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(y.id) for y in [action_type1, action_type2]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_monthly_action_type_none(self):
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)
        action_type3 = mommy.make(models.ActionType)

        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type1)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type2)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type3)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=t0"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(["t0"], [x["value"] for x in soup.select("select option[selected=selected]")])

    def test_view_monthly_action_type_none_and_defined(self):
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)
        action_type3 = mommy.make(models.ActionType)

        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type1)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type2)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type3)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=t0,t{0}".format(action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t0"] + [u"t{0}".format(y.id) for y in [action_type1,]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_monthly_action_filter_invalid(self):
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=abc"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_view_monthly_action_filter_invalid_user(self):
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=u2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_monthly_action_filter_invalid_type(self):
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=t2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_monthly_action_type_in_charge_filter(self):
        user_joe = mommy.make(User, first_name="Joe", is_staff=True)
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)

        a1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime.now(), in_charge=user_joe, type=action_type1
        )
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), in_charge=user_joe)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type1)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type2)
        a5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=u{0},t{1}".format(user_joe.id, action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(action_type1.id)] + [u"u{0}".format(user_joe.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_not_planned_action_anonymous(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#")
        self.client.logout()

        url = reverse('crm_actions_not_planned')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_not_planned_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#")
        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_actions_not_planned')
        response = self.client.get(url)
        login_url = reverse('django.contrib.auth.views.login')[3:]
        self.assertTrue(response['Location'].find(login_url) > 0)

    def test_view_not_planned_action(self):
        user_joe = mommy.make(User, first_name="Joe", is_staff=True)
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)

        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=None, in_charge=user_joe, type=action_type1)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=None, in_charge=user_joe)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=None, type=action_type1)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=None, type=action_type2)
        a5 = mommy.make(
            models.Action, subject="#ACT5#", planned_date=datetime.now(), in_charge=user_joe, type=action_type1
        )

        url = reverse('crm_actions_not_planned')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertContains(response, a2.subject)
        self.assertContains(response, a3.subject)
        self.assertContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_view_not_planned_action_type_in_charge_filter(self):
        user_joe = mommy.make(User, first_name="Joe", is_staff=True)
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)

        a1 = mommy.make(models.Action, subject="#ACT1#", planned_date=None, in_charge=user_joe, type=action_type1)
        a2 = mommy.make(models.Action, subject="#ACT2#", planned_date=None, in_charge=user_joe)
        a3 = mommy.make(models.Action, subject="#ACT3#", planned_date=None, type=action_type1)
        a4 = mommy.make(models.Action, subject="#ACT4#", planned_date=None, type=action_type2)
        a5 = mommy.make(
            models.Action, subject="#ACT5#", planned_date=datetime.now(), in_charge=user_joe, type=action_type1
        )

        url = reverse('crm_actions_not_planned') + "?filter=u{0},t{1}".format(user_joe.id, action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, a1.subject)
        self.assertNotContains(response, a2.subject)
        self.assertNotContains(response, a3.subject)
        self.assertNotContains(response, a4.subject)
        self.assertNotContains(response, a5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(action_type1.id)] + [u"u{0}".format(user_joe.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
