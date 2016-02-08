# -*- coding: utf-8 -*-
"""unit testing"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from datetime import datetime

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from balafon.Crm import models


class ListActionsTest(APITestCase):
    """It should return actions"""

    def setUp(self):
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()
        self.user = user
        self.client = APIClient()
        self.client.login(username=user.username, password='pass')

    def _get_actions_in(self, prefix='in-', **kwargs):
        """actions in the test period"""
        return [
            mommy.make(
                models.Action,
                subject=prefix + 'A',
                planned_date=datetime(2015, 6, 30, 12, 0),
                end_datetime=datetime(2015, 6, 30, 15, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'B',
                planned_date=datetime(2015, 7, 1, 9, 0),
                end_datetime=datetime(2015, 7, 2, 10, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'C',
                planned_date=datetime(2015, 6, 30, 12, 0),
                end_datetime=None,
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'D',
                planned_date=datetime(2015, 6, 28, 12, 0),
                end_datetime=datetime(2015, 6, 29, 12, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'E',
                planned_date=datetime(2015, 6, 28, 12, 0),
                end_datetime=datetime(2015, 7, 10, 12, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'F',
                planned_date=datetime(2015, 7, 1, 12, 0),
                end_datetime=datetime(2015, 7, 10, 12, 0),
                **kwargs
            ),
        ]

    def _get_daily_actions_in(self, prefix='in-', **kwargs):
        """actions in the test period"""
        return [
            mommy.make(
                models.Action,
                subject=prefix + 'A',
                planned_date=datetime(2015, 6, 30, 12, 0),
                end_datetime=datetime(2015, 6, 30, 15, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'B',
                planned_date=datetime(2015, 6, 30, 0, 0, 0),
                end_datetime=None,
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'C',
                planned_date=datetime(2015, 6, 30, 23, 59, 59),
                end_datetime=None,
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'D',
                planned_date=datetime(2015, 6, 29, 23, 0),
                end_datetime=datetime(2015, 6, 30, 2, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'E',
                planned_date=datetime(2015, 6, 30, 23, 0),
                end_datetime=datetime(2015, 7, 1, 1, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'F',
                planned_date=datetime(2015, 6, 28, 12, 0),
                end_datetime=datetime(2015, 7, 2, 12, 0),
                **kwargs
            ),
        ]

    def _get_actions_out(self, prefix="out-", **kwargs):
        """action out of the test period"""
        return [
            mommy.make(
                models.Action,
                subject=prefix + 'A',
                planned_date=datetime(2015, 6, 28, 12, 0),
                end_datetime=datetime(2015, 6, 28, 15, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'B',
                planned_date=datetime(2015, 6, 28, 12, 0),
                end_datetime=None,
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'C',
                planned_date=datetime(2015, 7, 12, 12, 0),
                end_datetime=None,
                **kwargs
            ),
        ]

    def _get_daily_actions_out(self, prefix="out-", **kwargs):
        """action out of the test period"""
        return [
            mommy.make(
                models.Action,
                subject=prefix + 'A',
                planned_date=datetime(2015, 6, 29, 12, 0),
                end_datetime=datetime(2015, 6, 29, 15, 0),
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'B',
                planned_date=datetime(2015, 6, 29, 23, 59, 59),
                end_datetime=None,
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'C',
                planned_date=datetime(2015, 7, 1, 0, 0, 0),
                end_datetime=None,
                **kwargs
            ),
            mommy.make(
                models.Action,
                subject=prefix + 'D',
                planned_date=datetime(2015, 7, 1, 8, 0, 0),
                end_datetime=datetime(2015, 7, 1, 10, 0, 0),
                **kwargs
            ),
        ]

    def test_read_actions_in_range(self):
        """It should return action in range"""
        actions_in = self._get_actions_in()
        actions_out = self._get_actions_out()

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_read_daily_actions(self):
        """It should return action of the day"""
        actions_in = self._get_daily_actions_in()
        actions_out = self._get_daily_actions_out()

        url = reverse('crm_api_list_actions') + "?start=2015-06-30&end=2015-06-30"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_read_actions_end_before_start(self):
        """It should return no actions"""
        self._get_actions_in()
        self._get_actions_out()
        url = reverse('crm_api_list_actions') + "?start=2015-07-06&end=2015-06-29"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))

    def test_read_actions_empty(self):
        """It should return no actions"""
        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))

    def test_read_actions_anonymous(self):
        """It should return error"""
        self.client.logout()
        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06"
        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_read_actions_non_staff(self):
        """It should return error"""
        self.user.is_staff = False
        self.user.save()
        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_read_actions_no_start(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions') + "?end=2015-07-06"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_no_end(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions') + "?start=2015-06-29"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_no_period(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_invalid_start(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions') + "?start=2015-06-32&end=2015-07-06"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_dummy_start(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions') + "?start=blabla&end=2015-07-06"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_invalid_end(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions') + "?start=2015-06-30&end=2015-15-06"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_dummy_end(self):
        """It should returns an error"""
        url = reverse('crm_api_list_actions') + "?start=2015-06-30&end=dummy"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_type_filter(self):
        """It should return action in range with right action type"""
        type_in = mommy.make(models.ActionType)
        type_out = mommy.make(models.ActionType)

        actions_in = self._get_actions_in(type=type_in, prefix="type-in-")

        actions_out = self._get_actions_out(type=type_in, prefix="out-")
        actions_out += self._get_actions_in(type=type_out, prefix="type-out-")
        actions_out += self._get_actions_in(type=None, prefix="type-none-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&action_type={0}".format(
            type_in.id
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_read_actions_type_filter_not_exists(self):
        """It should returns an error"""
        type_in = mommy.make(models.ActionType)

        self._get_actions_in(type=type_in, prefix="type-in-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&action_type={0}".format(
            type_in.id + 1
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_actions_type_filter_invalid(self):
        """It should returns an error"""
        type_in = mommy.make(models.ActionType)

        self._get_actions_in(type=type_in, prefix="type-in-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&action_type=blabla"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_in_charge_filter(self):
        """It should return action in range with right user in charge"""
        member_in = mommy.make(models.TeamMember)
        member_out = mommy.make(models.TeamMember)

        actions_in = self._get_actions_in(in_charge=member_in, prefix="in-")

        actions_out = self._get_actions_out(in_charge=member_in, prefix="out-")
        actions_out += self._get_actions_in(in_charge=member_out, prefix="in_charge-out-")
        actions_out += self._get_actions_in(in_charge=None, prefix="in_charge-none-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&in_charge={0}".format(
            member_in.id
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_read_two_in_charge_filter(self):
        """It should return action in range with right user in charge"""
        member_1 = mommy.make(models.TeamMember)
        member_2 = mommy.make(models.TeamMember)

        actions_in = self._get_actions_in(in_charge=member_1, prefix="in1-")
        actions_in += self._get_actions_in(in_charge=member_2, prefix="in2-")

        actions_out = self._get_actions_out(in_charge=member_1, prefix="out1-")
        actions_out += self._get_actions_in(in_charge=None, prefix="in_charge-none-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&in_charge={0},{1}".format(
            member_1.id, member_2.id
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_read_in_charge_not_exists(self):
        """It should returns an error"""
        member_in = mommy.make(models.TeamMember)

        self._get_actions_in(in_charge=member_in, prefix="in-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&in_charge={0}".format(
            member_in.id + 1
        )

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(response.data))

    def test_read_in_charge_invalid(self):
        """It should returns an error"""
        member_in = mommy.make(models.TeamMember)

        self._get_actions_in(in_charge=member_in, prefix="in-")

        url = reverse('crm_api_list_actions') + "?start=2015-06-29&end=2015-07-06&in_charge=blabla"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_member_action(self):
        """It should returns team member actions"""
        user = mommy.make(User, username='bill', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()
        self.client.logout()
        self.client.login(username=user.username, password='pass')

        member_1 = mommy.make(models.TeamMember, user=user)
        member_2 = mommy.make(models.TeamMember)

        actions_in = self._get_actions_in(in_charge=member_1, prefix="in1-")

        actions_out = self._get_actions_in(in_charge=member_2, prefix="in2-")
        actions_out += self._get_actions_out(in_charge=member_1, prefix="out1-")
        actions_out += self._get_actions_in(in_charge=None, prefix="in_charge-none-")

        url = reverse('crm_api_list_team_member_actions') + "?start=2015-06-29&end=2015-07-06"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_team_daily_actions(self):
        """It should returns team member actions"""
        user = mommy.make(User, username='bill', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()
        self.client.logout()
        self.client.login(username=user.username, password='pass')

        member_1 = mommy.make(models.TeamMember, user=user)
        member_2 = mommy.make(models.TeamMember)

        actions_in = self._get_daily_actions_in(in_charge=member_1, prefix="in1-")

        actions_out = self._get_daily_actions_in(in_charge=member_2, prefix="in2-")
        actions_out += self._get_daily_actions_out(in_charge=member_1, prefix="out1-")
        actions_out += self._get_daily_actions_in(in_charge=None, prefix="in_charge-none-")

        url = reverse('crm_api_list_team_member_actions') + "?start=2015-06-30&end=2015-06-30"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(actions_in), len(response.data))
        for action in actions_in:
            self.assertTrue(action.subject in [act['subject'] for act in response.data])
        for action in actions_out:
            self.assertFalse(action.subject in [act['subject'] for act in response.data])

    def test_team_member_action_inactive(self):
        """It should returns returns an error"""
        user = mommy.make(User, username='bill', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()
        self.client.logout()
        self.client.login(username=user.username, password='pass')

        user.is_active = False
        user.save()

        member_1 = mommy.make(models.TeamMember, user=user)

        actions_out = self._get_actions_in(in_charge=member_1, prefix="in1-")

        url = reverse('crm_api_list_team_member_actions') + "?start=2015-06-29&end=2015-07-06"

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


    def test_team_member_action_not_member(self):
        """It should returns returns an error"""
        user = mommy.make(User, username='bill', is_active=True, is_staff=False)
        user.set_password('pass')
        user.save()
        self.client.logout()
        self.client.login(username=user.username, password='pass')

        url = reverse('crm_api_list_team_member_actions') + "?start=2015-06-29&end=2015-07-06"

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_member_action_anonymous(self):
        """It should returns returns an error"""
        self.client.logout()

        url = reverse('crm_api_list_team_member_actions') + "?start=2015-06-29&end=2015-07-06"

        response = self.client.get(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


class DeleteActionTest(APITestCase):
    """It should delete an action"""

    def setUp(self):
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()
        self.user = user
        self.client = APIClient()
        self.client.login(username=user.username, password='pass')

    def test_delete_action(self):
        """It should delete action"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        action.contacts.add(contact)
        action.save()

        action2 = mommy.make(models.Action)

        url = reverse('crm_api_delete_action', args=[action.id])

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(models.Action.objects.filter(id=action.id).count(), 0)
        self.assertEqual(models.Action.objects.filter(id=action2.id).count(), 1)
        self.assertEqual(models.Contact.objects.filter(id=contact.id).count(), 1)

    def test_delete_action_anonymous(self):
        """It should not delete and returns an error"""
        self.client.logout()
        action = mommy.make(models.Action)

        url = reverse('crm_api_delete_action', args=[action.id])

        response = self.client.delete(url, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        self.assertEqual(models.Action.objects.filter(id=action.id).count(), 1)

    def test_delete_action_non_staff(self):
        """It should not delete and returns an error"""
        self.user.is_staff = False
        self.user.save()

        action = mommy.make(models.Action)

        url = reverse('crm_api_delete_action', args=[action.id])

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(models.Action.objects.filter(id=action.id).count(), 1)


class UpdateActionDateTest(APITestCase):
    """It should update the date of the action"""

    def setUp(self):
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()
        self.user = user
        self.client = APIClient()
        self.client.login(username=user.username, password='pass')

    def test_update_action_date(self):
        """It should update action date"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        action.contacts.add(contact)
        action.save()

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))

    def test_update_action_date_anonymous(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)

        self.client.logout()

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_update_action_date_missing_start(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': '',
            'end_datetime': '2015-06-30T17:00:00Z',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_update_action_date_missing_end(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_update_action_date_invalid_start(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': 'jkhjk',
            'end_datetime': '2015-06-30T12:00:00Z',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_update_action_date_invalid_end(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': 'eeee',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_update_action_date_non_staff(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_api_update_action_date', args=[action.id])

        data = {
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)


class UpdateActionTest(APITestCase):
    """It should update an action"""

    def setUp(self):
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()
        self.user = user
        self.client = APIClient()
        self.client.login(username=user.username, password='pass')

    def test_update_action(self):
        """It should update action"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, member)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))
        self.assertEqual(list(action.contacts.all()), [contact])

    def test_update_action_type(self):
        """It should update action"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_type = mommy.make(models.ActionType)

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, member)
        self.assertEqual(action.type, action_type)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))
        self.assertEqual(list(action.contacts.all()), [contact])

    def test_update_action_type_and_status(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status)
        action_type.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': action_status.id,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, member)
        self.assertEqual(action.type, action_type)
        self.assertEqual(action.status, action_status)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))
        self.assertEqual(list(action.contacts.all()), [contact])

    def test_update_action_type_and_status_not_allowed(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': action_status.id,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.type, None)
        self.assertEqual(action.status, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_type_not_found(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_type = mommy.make(models.ActionType)

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id+1,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.type, None)
        self.assertEqual(action.status, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_type_invalid(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': "xxx",
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.type, None)
        self.assertEqual(action.status, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_status_not_found(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status)
        action_type.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': action_status.id + 1,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.type, None)
        self.assertEqual(action.status, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_status_invalid(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status)
        action_type.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': "xxx",
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.type, None)
        self.assertEqual(action.status, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_date_anonymous(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        self.client.logout()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_date_non_staff(self):
        """It should not update and returns error"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, '')
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.detail, '')
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_empty(self):
        """It should update action"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        action = mommy.make(
            models.Action,
            subject='ABC',
            detail='DEF',
            planned_date=datetime.now(),
            end_datetime=datetime.now(),
            in_charge=member
        )
        action.contacts.add(contact)
        action.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': None,
            'end_datetime': None,
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_update_action_invalid_start(self):
        """It should not update action and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        action = mommy.make(
            models.Action,
            subject='ABC',
            detail='DEF',
            planned_date=datetime.now(),
            end_datetime=datetime.now(),
            in_charge=member
        )
        action.contacts.add(contact)
        action.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': 'ab',
            'end_datetime': None,
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action_x = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, action_x.subject)
        self.assertEqual(action.in_charge, action_x.in_charge)
        self.assertEqual(action.detail, action_x.detail)
        self.assertEqual(action.planned_date, action_x.planned_date)
        self.assertEqual(action.end_datetime, action_x.end_datetime)
        self.assertEqual(list(action_x.contacts.all()), [contact])

    def test_update_action_invalid_end(self):
        """It should not update action and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        action = mommy.make(
            models.Action,
            subject='ABC',
            detail='DEF',
            planned_date=datetime.now(),
            end_datetime=datetime.now(),
            in_charge=member
        )
        action.contacts.add(contact)
        action.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': [],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': None,
            'end_datetime': 'cd',
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action_x = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, action_x.subject)
        self.assertEqual(action.in_charge, action_x.in_charge)
        self.assertEqual(action.detail, action_x.detail)
        self.assertEqual(action.planned_date, action_x.planned_date)
        self.assertEqual(action.end_datetime, action_x.end_datetime)
        self.assertEqual(list(action_x.contacts.all()), [contact])

    def test_update_action_invalid_contact(self):
        """It should not update action and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        action = mommy.make(
            models.Action,
            subject='ABC',
            detail='DEF',
            planned_date=datetime.now(),
            end_datetime=datetime.now(),
            in_charge=member
        )
        action.contacts.add(contact)
        action.save()

        url = reverse('crm_api_update_action', args=[action.id])

        data = {
            'contacts': ['aee'],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': None,
            'end_datetime': None,
            'type': None,
            'status': None,
        }

        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        action_x = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, action_x.subject)
        self.assertEqual(action.in_charge, action_x.in_charge)
        self.assertEqual(action.detail, action_x.detail)
        self.assertEqual(action.planned_date, action_x.planned_date)
        self.assertEqual(action.end_datetime, action_x.end_datetime)
        self.assertEqual(list(action_x.contacts.all()), [contact])


class CreateActionTest(APITestCase):
    """It should create an action"""

    def setUp(self):
        user = mommy.make(User, username='joe', is_active=True, is_staff=True)
        user.set_password('pass')
        user.save()
        self.user = user
        self.client = APIClient()
        self.client.login(username=user.username, password='pass')

    def test_create_action(self):
        """It should create action"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(1, models.Action.objects.count())
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, member)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))
        self.assertEqual(list(action.contacts.all()), [contact])

    def test_create_action_anonymous(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        self.client.logout()

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_non_staff(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_empty(self):
        """It should create action"""
        url = reverse('crm_api_create_action')

        data = {
            'contacts': [],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': None,
            'end_datetime': None,
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(1, models.Action.objects.count())
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, None)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)
        self.assertEqual(list(action.contacts.all()), [])

    def test_create_action_invalid_start(self):
        """It should not create action and returns error"""
        url = reverse('crm_api_create_action')

        data = {
            'contacts': [],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': 'ab',
            'end_datetime': None,
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_invalid_end(self):
        """It should not create action and returns error"""
        url = reverse('crm_api_create_action')

        data = {
            'contacts': [],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': None,
            'end_datetime': 'cd',
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_invalid_contact(self):
        """It should not create action and returns error"""
        url = reverse('crm_api_create_action')

        data = {
            'contacts': ['aee'],
            'subject': '',
            'in_charge': '',
            'detail': '',
            'planned_date': None,
            'end_datetime': None,
            'type': None,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_type(self):
        """It should create action"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_type = mommy.make(models.ActionType)

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, member)
        self.assertEqual(action.type, action_type)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))
        self.assertEqual(list(action.contacts.all()), [contact])

    def test_create_action_type_and_status(self):
        """It should create action"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status)
        action_type.save()

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': action_status.id,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(1, models.Action.objects.count())
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data['subject'])
        self.assertEqual(action.in_charge, member)
        self.assertEqual(action.type, action_type)
        self.assertEqual(action.status, action_status)
        self.assertEqual(action.detail, data['detail'])
        self.assertEqual(action.planned_date, datetime(2015, 6, 30, 12, 0))
        self.assertEqual(action.end_datetime, datetime(2015, 6, 30, 17, 0))
        self.assertEqual(list(action.contacts.all()), [contact])

    def test_create_action_type_and_status_not_allowed(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': action_status.id,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_type_not_found(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_type = mommy.make(models.ActionType)

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id+1,
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_type_invalid(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': "xxx",
            'status': None,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_status_not_found(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status)
        action_type.save()

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': action_status.id + 1,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())

    def test_create_action_status_invalid(self):
        """It should not create and returns error"""
        contact = mommy.make(models.Contact)
        member = mommy.make(models.TeamMember)
        action_status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status)
        action_type.save()

        url = reverse('crm_api_create_action')

        data = {
            'contacts': [contact.id],
            'subject': 'Test',
            'in_charge': member.id,
            'detail': 'Blabla',
            'planned_date': '2015-06-30T12:00:00Z',
            'end_datetime': '2015-06-30T17:00:00Z',
            'type': action_type.id,
            'status': "xxx",
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(0, models.Action.objects.count())