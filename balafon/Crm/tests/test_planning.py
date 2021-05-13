# -*- coding: utf-8 -*-
"""unit testing"""

from datetime import datetime, timedelta

from django.urls import reverse
from django.test.utils import override_settings

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.unit_tests import response_as_json
from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


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
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_view_monthly_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.user.is_staff = False
        self.user.save()

        now = datetime.now()
        url = reverse('crm_actions_of_month', args=[now.year, now.month])
        response = self.client.get(url)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

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
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_view_weekly_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.user.is_staff = False
        self.user.save()

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_view_weekly_action(self):
        """view actions of the week"""

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=datetime.now())
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=datetime.now()+timedelta(days=7))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=datetime.now()-timedelta(days=7))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=None)

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
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
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_view_dailly_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now())
        self.user.is_staff = False
        self.user.save()

        now = datetime.now()
        url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day])
        response = self.client.get(url)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

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

        user_joe = mommy.make(models.TeamMember, name="Joe", ordering=1)
        user_jack = mommy.make(models.TeamMember, name="Jack", ordering=2)
        user_will = mommy.make(models.TeamMember, name="Will", ordering=3)

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
            ["u{0}".format(y.id) for y in [user_joe, user_jack]],
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
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
            sorted(["t{0}".format(y.id) for y in [action_type1, action_type2]]),
            sorted([x["value"] for x in soup.select("select.action-filter option[selected=selected]")])
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
        self.assertEqual(["t0"], [x["value"] for x in soup.select("select.action-filter option[selected=selected]")])

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
            ["t0"] + ["t{0}".format(y.id) for y in [action_type1,]],
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
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
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
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
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
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
            ["t{0}".format(action_type1.id)] + ["u{0}".format(user_joe.id)],
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
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
            ["t{0}".format(action_type1.id)] + ["s{0}".format(action_status2.id)],
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
        )
        self.assertEqual(
            [
                "t0",
                "t{0}".format(action_type2.id), "t{0}".format(action_type1.id),
                "s{0}".format(action_status2.id), "s{0}".format(action_status1.id)
            ],
            [x["value"] for x in soup.select("select.action-filter option")]
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
            ["t{0}".format(action_type1.id)],
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
        )
        self.assertEqual(
            ["t0", "t{0}".format(action_type1.id), "t{0}".format(action_type2.id)],
            [x["value"] for x in soup.select("select.action-filter option")]
        )

    def test_action_type_ordering_asc(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o1"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [
            action4, action3, action5, action1, action2
        ]

        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    @override_settings(BALAFON_PLANNING_ORDERING=[(5, 'Custom', (('subject', )))])
    def test_action_type_ordering_custom(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o5"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [
            action1, action2, action3, action4, action5
        ]

        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    def test_action_type_ordering_desc(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o0"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [
            action2, action1, action5, action3, action4
        ]

        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    def test_action_type_ordering_name(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        contact1 = mommy.make(models.Contact, lastname="Dupond")
        contact2 = mommy.make(models.Contact, lastname="Alain")
        contact3 = contact2
        contact4 = mommy.make(models.Contact, lastname="Bernard")
        contact5 = mommy.make(models.Contact, lastname="Chausson")

        actions = [action1, action2, action3, action4, action5]
        contacts = [contact1, contact2, contact3, contact4, contact5]

        for action, contact in zip(actions, contacts):
            action.contacts.add(contact)
            action.save()

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o2"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [
            action3, action2, action4, action5, action1
        ]

        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    def test_action_type_ordering_entity_name(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        entity1 = mommy.make(models.Entity, name="Dupond")
        entity2 = mommy.make(models.Entity, name="Alain")
        entity3 = entity2
        entity4 = mommy.make(models.Entity, name="Bernard")
        entity5 = mommy.make(models.Entity, name="Chausson")

        actions = [action1, action2, action3, action4, action5]
        entities = [entity1, entity2, entity3, entity4, entity5]

        for action, entity in zip(actions, entities):
            action.entities.add(entity)
            action.save()

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o3"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [
            action3, action2, action4, action5, action1
        ]

        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    def test_action_filter_name(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        entity1 = mommy.make(models.Entity, name="Dupond")
        entity2 = mommy.make(models.Entity, name="Dupal")
        entity3 = entity2
        entity4 = mommy.make(models.Entity, name="Bernard")
        entity5 = mommy.make(models.Entity, name="Chausson")

        actions = [action1, action2, action3, action4, action5]
        entities = [entity1, entity2, entity3, entity4, entity5]

        for action, entity in zip(actions, entities):
            action.entities.add(entity)
            action.save()

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o3&name=Dup"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [action3, action2, action1]
        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    def test_action_filter_name_entity_and_contacts(self):
        """view actions of the month incharge filter"""
        now = datetime(2016, 10, 10, 12, 0)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=now + timedelta(days=1))
        action2 = mommy.make(models.Action, subject="#ACT2#", planned_date=now + timedelta(days=2))
        action3 = mommy.make(models.Action, subject="#ACT3#", planned_date=now - timedelta(days=1))
        action4 = mommy.make(models.Action, subject="#ACT4#", planned_date=now - timedelta(days=3))
        action5 = mommy.make(models.Action, subject="#ACT5#", planned_date=now)

        entity1 = mommy.make(models.Entity, name="Dupond")
        entity2 = mommy.make(models.Entity, name="Alain")
        contact = mommy.make(models.Contact, lastname='Dupal', entity=entity2)
        entity3 = entity2
        entity4 = mommy.make(models.Entity, name="Bernard")
        entity5 = mommy.make(models.Entity, name="Chausson")

        actions = [action1, action3, action4, action5]
        entities = [entity1, entity3, entity4, entity5]

        action2.contacts.add(contact)
        for action, entity in zip(actions, entities):
            action.entities.add(entity)
            action.save()

        url = reverse(
            'crm_actions_of_month', args=[now.year, now.month]
        ) + "?filter=o3&name=Dup"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        actions = [action1, action2]
        subjects = [action.subject for action in actions]
        for subject in subjects:
            self.assertContains(response, subject)
        content = response.content.decode('utf-8')
        pos = [content.find(subject) for subject in subjects]
        self.assertEqual(pos, list(sorted(pos)))

    def test_view_not_planned_action_anonymous(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#")
        self.client.logout()

        url = reverse('crm_actions_not_planned')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

    def test_view_not_planned_action_non_staff(self):
        """make sure not display for anonymous users"""
        mommy.make(models.Action, subject="#ACT1#")
        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_actions_not_planned')
        response = self.client.get(url)
        login_url = reverse('login')[3:]
        self.assertTrue(response['Location'].find(login_url) >= 0)

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
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
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
            ["t{0}".format(action_type1.id)] + ["u{0}".format(user_joe.id)],
            [x["value"] for x in soup.select("select.action-filter option[selected=selected]")]
        )

    def test_view_action_final_status(self):
        """It should show change status when clicking on done button"""

        status1 = mommy.make(models.ActionStatus, is_final=True)
        status2 = mommy.make(models.ActionStatus, is_final=False)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(status1)
        action_type.allowed_status.add(status2)
        action_type.save()

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type)

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".action")), 1)
        self.assertContains(response, reverse('crm_update_action_status', args=[action1.id])+"?done=1")
        self.assertNotContains(response, reverse('crm_do_action', args=[action1.id]))

    def test_view_action_no_final_status(self):
        """It should show change done flag when clicking on done button"""

        status1 = mommy.make(models.ActionStatus, is_final=False)
        status2 = mommy.make(models.ActionStatus, is_final=False)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(status1)
        action_type.allowed_status.add(status2)
        action_type.save()

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type)

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".action")), 1)
        self.assertNotContains(response, reverse('crm_update_action_status', args=[action1.id])+"?done=1")
        self.assertContains(response, reverse('crm_do_action', args=[action1.id]))

    def test_view_action_status_style(self):
        """It should show status color correctly"""

        status1 = mommy.make(models.ActionStatus, fore_color="#fff;", background_color="#000")

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), status=status1)

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".action")), 1)
        self.assertContains(response, "background: #000;")
        self.assertContains(response, "color: #fff;")

    def test_show_action_contacts_buttons(self):
        """It should show add/remove contacts/entities buttons"""

        action_type = mommy.make(models.ActionType)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type)

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)

        action1.contacts.add(contact)
        action1.entities.add(entity)
        action1.save()

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, action1.subject)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".action")), 1)

        urls = (
            reverse('crm_add_contact_to_action', args=[action1.id]),
            reverse('crm_add_entity_to_action', args=[action1.id]),
            reverse('crm_remove_contact_from_action', args=[action1.id, contact.id]),
            reverse('crm_remove_entity_from_action', args=[action1.id, entity.id]),
        )

        for link_url in urls:
            self.assertContains(response, link_url)

    def test_hide_action_contacts_buttons(self):
        """It should hide add/remove contacts/entities buttons"""

        action_type = mommy.make(models.ActionType, hide_contacts_buttons=True)

        action1 = mommy.make(models.Action, subject="#ACT1#", planned_date=datetime.now(), type=action_type)

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)

        action1.contacts.add(contact)
        action1.entities.add(entity)
        action1.save()

        now = datetime.now()
        url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".action")), 1)

        self.assertContains(response, action1.subject)

        urls = (
            reverse('crm_add_contact_to_action', args=[action1.id]),
            reverse('crm_add_entity_to_action', args=[action1.id]),
            reverse('crm_remove_contact_from_action', args=[action1.id, contact.id]),
            reverse('crm_remove_entity_from_action', args=[action1.id, entity.id]),
        )

        for link_url in urls:
            self.assertNotContains(response, link_url)


class PlanningRedirectView(BaseTestCase):
    """Test redirections"""

    def test_view_this_month_actions(self):
        """It should redirect and keep query string args"""
        action_type = mommy.make(models.ActionType)
        query_string = "?t={0}".format(action_type.id)
        url = reverse('crm_this_month_actions') + query_string
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        now = datetime.now()
        redirect_url = reverse('crm_actions_of_month', args=[now.year, now.month]) + query_string
        self.assertTrue(response['Location'].find(redirect_url) >= 0)

    def test_view_this_week_actions(self):
        """It should redirect and keep query string args"""
        action_type = mommy.make(models.ActionType)
        query_string = "?t={0}".format(action_type.id)
        url = reverse('crm_this_week_actions') + query_string
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        now = datetime.now()
        redirect_url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")]) + query_string
        self.assertTrue(response['Location'].find(redirect_url) >= 0)

    def test_view_today_actions(self):
        """It should redirect and keep query string args"""
        action_type = mommy.make(models.ActionType)
        query_string = "?t={0}".format(action_type.id)
        url = reverse('crm_today_actions') + query_string
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        now = datetime.now()
        redirect_url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day]) + query_string
        self.assertTrue(response['Location'].find(redirect_url) >= 0)


class GoToPlanningDateTest(BaseTestCase):
    """It should return the url of given parameters"""

    def test_404_on_get(self):
        """It should return 404"""
        url = reverse('crm_go_to_planning_date')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_go_to_day(self):
        """It should return url"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'day',
            'planning_date': '2016-02-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)

        resp_data = response_as_json(response)

        self.assertEqual(resp_data['url'], reverse('crm_actions_of_day', args=[2016, 2, 14]) + '?filter=t2')

    def test_go_to_day_september(self):
        """It should return url"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'day',
            'planning_date': '2016-09-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)

        resp_data = response_as_json(response)

        self.assertEqual(resp_data['url'], reverse('crm_actions_of_day', args=[2016, 9, 14]) + '?filter=t2')

    def test_go_to_day_december(self):
        """It should return url"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'day',
            'planning_date': '2016-12-09',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)

        resp_data = response_as_json(response)

        self.assertEqual(resp_data['url'], reverse('crm_actions_of_day', args=[2016, 12, 9]) + '?filter=t2')

    def test_go_to_month(self):
        """It should return url"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'month',
            'planning_date': '2016-02-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)

        resp_data = response_as_json(response)

        self.assertEqual(resp_data['url'], reverse('crm_actions_of_month', args=[2016, 2]) + '?filter=t2')

    def test_go_to_week(self):
        """It should return url"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'week',
            'planning_date': '2016-02-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)

        resp_data = response_as_json(response)

        self.assertEqual(resp_data['url'], reverse('crm_actions_of_week', args=[2016, 6]) + '?filter=t2')

    def test_go_to_week_no_filters(self):
        """It should return url"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'week',
            'planning_date': '2016-02-14',
            'filters': '',
        }

        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)

        resp_data = response_as_json(response)

        self.assertEqual(resp_data['url'], reverse('crm_actions_of_week', args=[2016, 6]))

    def test_go_to_invalid_type(self):
        """It should return 404 error"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'blabla',
            'planning_date': '2016-02-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(404, response.status_code)

    def test_go_to_invalid_date(self):
        """It should return 404 error"""
        url = reverse('crm_go_to_planning_date')

        data = {
            'planning_type': 'month',
            'planning_date': 'blabla',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(404, response.status_code)

    def test_go_to_anonymous(self):
        """It should not be allowed"""
        url = reverse('crm_go_to_planning_date')
        self.client.logout()
        data = {
            'planning_type': 'month',
            'planning_date': '2016-02-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)

    def test_go_to_not_allowed(self):
        """It should not be allowed"""
        url = reverse('crm_go_to_planning_date')
        self.user.is_staff = False
        self.user.save()

        data = {
            'planning_type': 'month',
            'planning_date': '2016-02-14',
            'filters': 't2',
        }

        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)
