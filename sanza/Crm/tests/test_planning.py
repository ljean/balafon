# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


class ActionArchiveTest(BaseTestCase):
    """test view planning"""

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
        """view actions for the month"""
        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=31))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=31))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        date_now = datetime.now()
        url = reverse('crm_actions_of_month', args=[date_now.year, date_now.month])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

    def test_view_monthly_action_end_dt(self):
        """view actions ending in the month"""
        action1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 29), end_datetime=datetime(2014, 5, 2)
        )
        action2 = mommy.make(
            models.Action, subject="#ACT2#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 4, 2)
        )
        action3 = mommy.make(
            models.Action, subject="#ACT3#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 3, 30)
        )
        action4 = mommy.make(
            models.Action, subject="#ACT4#", planned_date=datetime(2014, 5, 1), end_datetime=datetime(2014, 5, 2)
        )
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        action6 = mommy.make(
            models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 8)
        )
        action7 = mommy.make(
            models.Action, subject="#ACT7#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 5, 2)
        )
        action8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 29))

        url = reverse('crm_actions_of_month', args=[2014, 4])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)
        self.assertContains(response, action6.subject)
        self.assertContains(response, action7.subject)
        self.assertContains(response, action8.subject)

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
        """view actions of the week"""

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=7))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=7))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%U")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

    def test_view_weekly_action_end_dt(self):
        """view actions ending in the week"""
        action1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 15)
        )
        action2 = mommy.make(
            models.Action, subject="#ACT2#", planned_date=datetime(2014, 4, 1), end_datetime=datetime(2014, 4, 9)
        )
        action3 = mommy.make(
            models.Action, subject="#ACT3#", planned_date=datetime(2014, 4, 1), end_datetime=datetime(2014, 4, 2)
        )
        action4 = mommy.make(
            models.Action, subject="#ACT4#", planned_date=datetime(2014, 4, 15), end_datetime=datetime(2014, 4, 16)
        )
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        action6 = mommy.make(
            models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 8)
        )
        action7 = mommy.make(
            models.Action, subject="#ACT7#", planned_date=datetime(2014, 3, 29), end_datetime=datetime(2014, 5, 2)
        )
        action8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 9))

        url = reverse('crm_actions_of_week', args=[2014, 14])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)
        self.assertContains(response, action6.subject)
        self.assertContains(response, action7.subject)
        self.assertContains(response, action8.subject)

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
        """view actions of the day"""

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=1))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        now = datetime.now()
        url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

    def test_view_daily_action_end_dt(self):
        """view actions ending in the week"""

        action1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 9)
        )
        action2 = mommy.make(
            models.Action, subject="#ACT2#", planned_date=datetime(2014, 4, 8), end_datetime=datetime(2014, 4, 12)
        )
        action3 = mommy.make(
            models.Action, subject="#ACT3#", planned_date=datetime(2014, 4, 8), end_datetime=datetime(2014, 4, 8)
        )
        action4 = mommy.make(
            models.Action, subject="#ACT4#", planned_date=datetime(2014, 4, 10), end_datetime=datetime(2014, 4, 10)
        )
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)
        action6 = mommy.make(
            models.Action, subject="#ACT6#", planned_date=datetime(2014, 4, 2), end_datetime=datetime(2014, 4, 9)
        )
        action7 = mommy.make(
            models.Action, subject="#ACT7#", planned_date=datetime(2014, 4, 9), end_datetime=datetime(2014, 4, 10)
        )
        action8 = mommy.make(models.Action, subject="#ACT8#", planned_date=datetime(2014, 4, 9))

        url = reverse('crm_actions_of_day', args=[2014, 4, 9])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)
        self.assertContains(response, action6.subject)
        self.assertContains(response, action7.subject)
        self.assertContains(response, action8.subject)

    def test_in_charge_filter(self):
        """view actions of the month in charge filter"""

        user_joe = mommy.make(models.TeamMember, name="Joe")
        user_jack = mommy.make(models.TeamMember, name="Jack")
        user_will = mommy.make(models.TeamMember, name="Will")

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), in_charge=user_joe)
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), in_charge=user_joe)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), in_charge=user_jack)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), in_charge=user_will)
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        date_now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[date_now.year, date_now.month]
        ) + "?filter=u{0},u{1}".format(user_joe.id, user_jack.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"u{0}".format(y.id) for y in [user_joe, user_jack]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_type_filter(self):
        """view actions of the month action type filter"""

        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')
        action_type3 = mommy.make(models.ActionType, name='Abe')

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type1)
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type2)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type3)
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=t{0},t{1}".format(action_type1.id, action_type2.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            sorted([u"t{0}".format(y.id) for y in [action_type1, action_type2]]),
            sorted([x["value"] for x in soup.select("select option[selected=selected]")])
        )

    def test_action_type_none(self):
        """view actions of the month no type"""

        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')
        action_type3 = mommy.make(models.ActionType, name='Abe')

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type1)
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type2)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type3)
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=t0"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, action1.subject)
        self.assertNotContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(["t0"], [x["value"] for x in soup.select("select option[selected=selected]")])

    def test_type_none_and_defined(self):
        """view actions of the month action type some are set"""

        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')
        action_type3 = mommy.make(models.ActionType, name='Abe')

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type1)
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type2)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type3)
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=t0,t{0}".format(action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t0"] + [u"t{0}".format(y.id) for y in [action_type1,]],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_filter_invalid(self):
        """view actions of the month : invalid filter"""

        mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=abc"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_filter_invalid_user(self):
        """view actions of the month filter with invalid user"""

        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=u2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_filter_invalid_type(self):
        """view actions of the month filter with invalid type"""
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month]) + "?filter=t2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_action_type_in_charge_filter(self):
        """view actions of the month incharge filter"""
        user_joe = mommy.make(models.TeamMember, name="Joe")
        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')

        action1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime.now(), in_charge=user_joe, type=action_type1
        )
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), in_charge=user_joe)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now(), type=action_type1)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now(), type=action_type2)
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=u{0},t{1}".format(user_joe.id, action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertNotContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(action_type1.id)] + [u"u{0}".format(user_joe.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_action_type_and_status(self):
        """view actions of the month incharge filter"""
        action_type1 = mommy.make(models.ActionType, name='XYZ')
        action_type2 = mommy.make(models.ActionType, name="UVW")
        action_status1 = mommy.make(models.ActionStatus, name='Def')
        action_status2 = mommy.make(models.ActionStatus, name='Abc')
        action_type1.allowed_status.add(action_status1)
        action_type1.allowed_status.add(action_status2)
        action_type1.save()
        action_type2.allowed_status.add(action_status2)
        action_type2.save()

        action1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime.now(), status=action_status1, type=action_type1
        )
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        action3 = mommy.make(
            models.Action, subject="#ACT3#", planned_date=datetime.now(), status=action_status2, type=action_type1
        )
        action4 = mommy.make(
            models.Action, subject="#ACT4#", planned_date=datetime.now(), status=action_status2, type=action_type2
        )
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=s{0},t{1}".format(action_status2.id, action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, action1.subject)
        self.assertNotContains(response, action2.subject)
        self.assertContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(action_type1.id)] + [u"s{0}".format(action_status2.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        self.assertEqual(
            [
                u"t0",
                u"t{0}".format(action_type2.id), u"t{0}".format(action_type1.id),
                u"s{0}".format(action_status2.id), u"s{0}".format(action_status1.id)
            ],
            [x["value"] for x in soup.select("select option")]
        )

    def test_action_type_and_not_managed_status(self):
        """view actions of the month incharge filter"""
        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)

        action1 = mommy.make(
            models.Action, subject="#ACT1#", planned_date=datetime.now(), status=action_status1, type=action_type1
        )
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now(), type=action_type1)
        action3 = mommy.make(
            models.Action, subject="#ACT3#", planned_date=datetime.now(), status=action_status2, type=action_type1
        )
        action4 = mommy.make(
            models.Action, subject="#ACT4#", planned_date=datetime.now(), status=action_status2, type=action_type2
        )
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=datetime.now())

        now = datetime.now()
        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=s{0},t{1}".format(action_status2.id, action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(action_type1.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
        self.assertEqual(
            [u"t0", u"t{0}".format(action_type1.id), u"t{0}".format(action_type2.id)],
            [x["value"] for x in soup.select("select option")]
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
        """view actions not planned"""
        user_joe = mommy.make(models.TeamMember, name="Joe")
        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=None, in_charge=user_joe, type=action_type1)
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=None, in_charge=user_joe)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=None, type=action_type1)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=None, type=action_type2)
        action5 = mommy.make(
            models.Action, subject="#ACT5#", planned_date=datetime.now(), in_charge=user_joe, type=action_type1
        )

        url = reverse('crm_actions_not_planned')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertContains(response, action2.subject)
        self.assertContains(response, action3.subject)
        self.assertContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )

    def test_not_planned_type_in_charge_filter(self):
        """view actions not planned filtered by in charge"""
        user_joe = mommy.make(models.TeamMember, name="Joe")
        action_type1 = mommy.make(models.ActionType, name='Abc')
        action_type2 = mommy.make(models.ActionType, name='Abd')

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=None, in_charge=user_joe, type=action_type1)
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=None, in_charge=user_joe)
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=None, type=action_type1)
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=None, type=action_type2)
        action5 = mommy.make(
            models.Action, subject="#ACT5#", planned_date=datetime.now(), in_charge=user_joe, type=action_type1
        )

        url = reverse('crm_actions_not_planned') + "?filter=u{0},t{1}".format(user_joe.id, action_type1.id)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)
        self.assertNotContains(response, action2.subject)
        self.assertNotContains(response, action3.subject)
        self.assertNotContains(response, action4.subject)
        self.assertNotContains(response, action5.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(
            [u"t{0}".format(action_type1.id)] + [u"u{0}".format(user_joe.id)],
            [x["value"] for x in soup.select("select option[selected=selected]")]
        )
