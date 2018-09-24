# -*- coding: utf-8 -*-
"""unit testing"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from __future__ import unicode_literals

from decimal import Decimal
from datetime import datetime, timedelta, date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.unit_tests import response_as_json
from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


def get_dt(diff=0):
    """get datetiel from now"""
    now = datetime.now()
    if diff > 0:
        return now + timedelta(days=diff)
    elif diff < 0:
        return now - timedelta(days=-diff)
    return now


class EditActionTest(BaseTestCase):
    """Edit an action"""

    def test_edit_action(self):
        """edit"""
        contact = mommy.make(models.Contact)
        action = mommy.make(models.Action)
        action.contacts.add(contact)
        action.save()
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {
            'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status': "", 'status2': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False
        }

        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "tested")

    def test_allowed_status(self):
        """get allowed status"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        url = reverse("crm_get_action_status")+"?t="+str(action_type.id)+"&timestamp=777"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([action_status1.id, action_status2.id], data['allowed_status'])
        self.assertEqual(0, data['default_status'])

    def test_allowed_status2(self):
        """get allowed status"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        mommy.make(models.ActionStatus)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        url = reverse("crm_get_action_status2")+"?t="+str(action_type.id)+"&timestamp=777"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([action_status1.id, action_status2.id], data['allowed_status2'])
        self.assertEqual(0, data['default_status2'])

    def test_allowed_status_default_value(self):
        """allowed status with default value"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.default_status = action_status2
        action_type.save()

        url = reverse("crm_get_action_status")+"?t="+str(action_type.id)+"&timestamp=777"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([action_status1.id, action_status2.id], data['allowed_status'])
        self.assertEqual(action_status2.id, data['default_status'])

    def test_allowed_status_default_value2(self):
        """allowed status with default value"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        mommy.make(models.ActionStatus)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.default_status2 = action_status2
        action_type.save()

        url = reverse("crm_get_action_status2")+"?t="+str(action_type.id)+"&timestamp=777"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([action_status1.id, action_status2.id], data['allowed_status2'])
        self.assertEqual(action_status2.id, data['default_status2'])

    def test_no_allowed_status(self):
        """test no allowed status"""
        action_type = mommy.make(models.ActionType)

        url = reverse("crm_get_action_status")+"?t="+str(action_type.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([], data['allowed_status'])
        self.assertEqual(0, data['default_status'])

    def test_no_allowed_status2(self):
        """test no allowed status"""
        action_type = mommy.make(models.ActionType)

        url = reverse("crm_get_action_status2")+"?t="+str(action_type.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([], data['allowed_status2'])
        self.assertEqual(0, data['default_status2'])

    def test_allowed_status_no_type(self):
        """test allowed status no type"""
        url = reverse("crm_get_action_status")+"?t="+str(0)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([], data['allowed_status'])
        self.assertEqual(0, data['default_status'])

    def test_allowed_status2_no_type(self):
        """test allowed status no type"""
        url = reverse("crm_get_action_status2") + "?t=" + str(0)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response_as_json(response)
        self.assertEqual([], data['allowed_status2'])
        self.assertEqual(0, data['default_status2'])

    def test_allowed_status_unknown_type(self):
        """test allowed status unknown type"""
        url = reverse("crm_get_action_status")+"?t=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_allowed_status2_unknown_type(self):
        """test allowed status unknown type"""
        url = reverse("crm_get_action_status2")+"?t=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_allowed_status_invalid_type(self):
        """test allowed status invalid type"""
        url = reverse("crm_get_action_status")+"?t=toto"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_allowed_status2_invalid_type(self):
        """test allowed status invalid type"""
        url = reverse("crm_get_action_status2")+"?t=toto"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_action_on_entity(self):
        """edit action on entity"""
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action)
        action.entities.add(entity)
        action.save()
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {
            'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status': "", 'status2': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False
        }

        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "tested")
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)

    def test_edit_action_status_not_allowed(self):
        """edit action status not allowed"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="not tested", type=action_type, status=action_status1)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "", 'time': "",
            'status': action_status3.id, 'in_charge': "", 'opportunity': "", 'detail': "",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False
        }

        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "not tested")

    def test_edit_action_status2_not_allowed(self):
        """edit action status not allowed"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="not tested", type=action_type, status=action_status1)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "", 'time': "", 'status': '',
            'status2': action_status3.id, 'in_charge': "", 'opportunity': "", 'detail': "",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False
        }

        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "not tested")

    def test_edit_action_status_no_type(self):
        """edit status no type"""
        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="not tested", type=action_type, status=action_status1)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        data = {
            'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status': action_status3.id, 'in_charge': "", 'opportunity': "", 'detail': "",
            'priority': models.Action.PRIORITY_MEDIUM, 'amount': 0, 'number': 0,
            'done': False, 'display_on_board': False, 'planned_date': "", 'archived': False
        }

        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "not tested")

    def test_edit_action_planned_date(self):
        """edit action planned date"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_planned_date_time(self):
        """edit action planned date and time"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "12:25", 'planned_date': "", 'end_date': "", 'end_time': "",
            'end_datetime': "", 'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "",
            'detail': "", 'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 12, 25))
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_planned_time(self):
        """edit action planned time"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "", 'time': "12:25", 'planned_date': "", 'end_date': "", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_start_and_end_date(self):
        """edit action start and end date"""

        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-10", 'end_time': "",
            'end_datetime': "", 'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "",
            'detail': "", 'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 10, 0, 0))

    def test_edit_action_start_and_end_same_date(self):
        """edit action start and end at same date"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "",
            'end_datetime': "", 'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "",
            'detail': "", 'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 9, 0, 0))

    def test_edit_action_start_and_end_different_time(self):
        """edit action start and end at same date different time"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "14:00", 'planned_date': "", 'end_date': "2014-04-09",
            'end_time': "16:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 14, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 9, 16, 0))

    def test_edit_action_start_and_end_different_time2(self):
        """edit action start and end at same date different time"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "16:00",
            'end_datetime': "", 'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "",
            'detail': "",  'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 0, 0))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 9, 16, 0))

    def test_edit_action_start_and_end_different_time3(self):
        """edit action start and end at same date different time"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "16:30", 'planned_date': "", 'end_date': "2014-04-10",
            'end_time': "10:15", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 0)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "BBB")

        self.assertEqual(action.planned_date, datetime(2014, 4, 9, 16, 30))
        self.assertEqual(action.end_datetime, datetime(2014, 4, 10, 10, 15))

    def test_edit_action_no_start_and_end_date(self):
        """edit action no start and end"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "", 'time': "", 'planned_date': "", 'end_date': "2014-04-09", 'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_end_before_start1(self):
        """edit action end before start"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "", 'planned_date': "", 'end_date': "2014-04-08", 'end_time': "",
            'end_datetime': "", 'subject': "BBB", 'type': "", 'status': "", 'in_charge': "",
            'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_end_before_start2(self):
        """edit action end time before start"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09",
            'end_time': "", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_end_before_start3(self):
        """edit action end before start"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "",
            'end_date': "2014-04-09", 'end_time': "11:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_date_not_set(self):
        """edit action start. end not set"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "",
            'end_date': "", 'end_time': "12:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_date_invalid1(self):
        """edit action date invalid"""

        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "AAAA", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09",
            'end_time': "13:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 4)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_date_invalid2(self):
        """edit action date invalid"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "AA", 'planned_date': "", 'end_date': "2014-04-09",
            'end_time': "13:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_date_invalid3(self):
        """edit action date invalid"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "AAA",
            'end_time': "13:00", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 2)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_edit_action_date_invalid4(self):
        """edit action date invalid"""
        action = mommy.make(models.Action, subject="AAA")

        data = {
            'date': "2014-04-09", 'time': "12:00", 'planned_date': "", 'end_date': "2014-04-09",
            'end_time': "AA", 'end_datetime': "",
            'subject': "BBB", 'type': "", 'status': "", 'in_charge': "", 'opportunity': "", 'detail': "",
            'amount': 0, 'number': 0, 'done': False,
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.subject, "AAA")

        self.assertEqual(action.planned_date, None)
        self.assertEqual(action.end_datetime, None)

    def test_view_action_start_and_end(self):
        """view action start and end"""
        action = mommy.make(
            models.Action, subject="AAA",
            planned_date=datetime(2014, 4, 9, 12, 15), end_datetime=datetime(2014, 4, 10, 9, 30)
        )

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        self.assertEqual(soup.select("#id_date")[0]["value"], "2014-04-09")
        self.assertEqual(soup.select("#id_time")[0]["value"], "12:15:00")
        self.assertEqual(soup.select("#id_date")[0].get("disabled"), None)
        self.assertEqual(soup.select("#id_time")[0].get("disabled"), None)

        self.assertEqual(soup.select("#id_end_date")[0]["value"], "2014-04-10")
        self.assertEqual(soup.select("#id_end_time")[0]["value"], "09:30:00")
        self.assertEqual(soup.select("#id_end_date")[0].get("disabled"), None)
        self.assertEqual(soup.select("#id_end_time")[0].get("disabled"), None)

    def test_view_action_start_and_end_frozen(self):
        """view action start and end"""
        action = mommy.make(
            models.Action, subject="AAA", frozen=True,
            planned_date=datetime(2014, 4, 9, 12, 15), end_datetime=datetime(2014, 4, 10, 9, 30)
        )

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        self.assertEqual(soup.select("#id_date")[0]["value"], "2014-04-09")
        self.assertEqual(soup.select("#id_time")[0]["value"], "12:15:00")
        self.assertEqual(soup.select("#id_date")[0]["disabled"], "disabled")
        self.assertEqual(soup.select("#id_time")[0]["disabled"], "disabled")

        self.assertEqual(soup.select("#id_end_date")[0]["value"], "2014-04-10")
        self.assertEqual(soup.select("#id_end_time")[0]["value"], "09:30:00")
        self.assertEqual(soup.select("#id_end_date")[0]["disabled"], "disabled")
        self.assertEqual(soup.select("#id_end_time")[0]["disabled"], "disabled")

    def test_view_action_auto_generated(self):
        """view action start and end"""
        action_type = mommy.make(models.ActionType, number_auto_generated=True)
        action = mommy.make(
            models.Action, subject="AAA", type=action_type, number=1
        )

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        self.assertEqual(soup.select("#id_number")[0]["value"], "1")
        self.assertEqual(soup.select("#id_number")[0]["disabled"], "disabled")

    def test_view_action_auto_generated_generator(self):
        """view action start and end"""
        generator1 = mommy.make(models.ActionNumberGenerator, number=110)
        action_type1 = mommy.make(models.ActionType, number_auto_generated=True, number_generator=generator1)

        action = mommy.make(models.Action, subject="AAA", type=action_type1)

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        self.assertEqual(soup.select("#id_number")[0]["value"], "111")
        self.assertEqual(soup.select("#id_number")[0]["disabled"], "disabled")
        generator1 = models.ActionNumberGenerator.objects.get(id=generator1.id)
        self.assertEqual(generator1.number, 111)

    def test_view_action_existing_number_generator(self):
        """view action start and end"""
        generator1 = mommy.make(models.ActionNumberGenerator, number=110)
        action_type1 = mommy.make(models.ActionType, number_auto_generated=True, number_generator=generator1)

        action = mommy.make(models.Action, subject="AAA", type=action_type1, number=57)

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)

        self.assertEqual(soup.select("#id_number")[0]["value"], "57")
        self.assertEqual(soup.select("#id_number")[0]["disabled"], "disabled")

        generator1 = models.ActionNumberGenerator.objects.get(id=generator1.id)
        self.assertEqual(generator1.number, 110)

    def test_view_action_generator_generator_shared_between_types(self):
        """view action start and end"""
        generator1 = mommy.make(models.ActionNumberGenerator, number=110)
        generator2 = mommy.make(models.ActionNumberGenerator, number=5)
        action_type1 = mommy.make(models.ActionType, number_auto_generated=True, number_generator=generator1)
        action_type2 = mommy.make(models.ActionType, number_auto_generated=True, number_generator=generator1)
        action_type3 = mommy.make(models.ActionType, number_auto_generated=True, number_generator=generator2)

        action1 = mommy.make(models.Action, subject="AAA", type=action_type1, number=0)
        action2 = mommy.make(models.Action, subject="AAA", type=action_type2, number=0)
        action3 = mommy.make(models.Action, subject="AAA", type=action_type3, number=0)

        generator1 = models.ActionNumberGenerator.objects.get(id=generator1.id)
        generator2 = models.ActionNumberGenerator.objects.get(id=generator2.id)
        self.assertEqual(generator1.number, 112)
        self.assertEqual(generator2.number, 6)

        action1 = models.Action.objects.get(id=action1.id)
        action2 = models.Action.objects.get(id=action2.id)
        action3 = models.Action.objects.get(id=action3.id)
        self.assertEqual(action1.number, 111)
        self.assertEqual(action2.number, 112)
        self.assertEqual(action3.number, 6)


class ActionTest(BaseTestCase):
    """View actions"""
    def test_view_add_contact_to_action(self):
        """view add contact"""
        action = mommy.make(models.Action)
        url = reverse('crm_add_contact_to_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_add_entity_to_action(self):
        """view add entity"""
        action = mommy.make(models.Action)
        url = reverse('crm_add_entity_to_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_contact_to_action(self):
        """add contact"""
        action = mommy.make(models.Action)
        contact = mommy.make(models.Contact)
        url = reverse('crm_add_contact_to_action', args=[action.id])
        response = self.client.post(url, data={'contact': contact.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(action.contacts.all()[0], contact)

    def test_add_entity_to_action(self):
        """add entity"""
        action = mommy.make(models.Action)
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_entity_to_action', args=[action.id])
        response = self.client.post(url, data={'entity': entity.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)

    def test_view_entity_actions(self):
        """view entity actions"""
        entity = mommy.make(models.Entity)
        action = mommy.make(models.Action, subject="should be only once", archived=False)
        contact1 = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)
        action.contacts.add(contact1)
        action.contacts.add(contact2)
        action.entities.add(entity)
        action.save()

        url = reverse("crm_view_entity", args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        content = response.content.decode('utf-8')
        self.assertEqual(1, content.count(action.subject))

    def test_view_contact_actions_more_than_five(self):
        """view contact actions if more than five"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        actions = [mommy.make(models.Action, subject="--{0}--".format(i), archived=False) for i in range(10)]
        for action in actions:
            action.contacts.add(contact1)
            action.save()

        url = reverse("crm_view_contact", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        for action in actions[5:]:
            self.assertContains(response, action.subject)

        for action in actions[:5]:
            self.assertNotContains(response, action.subject)

    def test_view_contact_actions_gt_five(self):
        """view contact actions if more than five datetime is set"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        action1 = mommy.make(models.Action, subject="--1--", archived=False, planned_date=get_dt())
        action2 = mommy.make(models.Action, subject="--2--", archived=False, planned_date=get_dt(-1))
        action3 = mommy.make(models.Action, subject="--3--", archived=False, planned_date=get_dt(-2))
        action4 = mommy.make(models.Action, subject="--4--", archived=False, planned_date=get_dt(-3))
        action5 = mommy.make(models.Action, subject="--5--", archived=False, planned_date=get_dt(+1))
        action6 = mommy.make(models.Action, subject="--6--", archived=False, planned_date=get_dt(+2))
        action7 = mommy.make(models.Action, subject="--7--", archived=False, planned_date=get_dt(+3))

        for action in [action1, action2, action3, action4, action5, action6, action7]:
            action.contacts.add(contact1)
            action.save()

        url = reverse("crm_view_contact", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        for action in [action1, action2, action5, action6, action7]:
            self.assertContains(response, action.subject)

        for action in [action3, action4]:
            self.assertNotContains(response, action.subject)

    def test_view_entity_actions_gt_five(self):
        """views more than 5 actions on entity view"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        action1 = mommy.make(models.Action, subject="--1--", archived=False, planned_date=get_dt())
        action2 = mommy.make(models.Action, subject="--2--", archived=False, planned_date=get_dt(-1))
        action3 = mommy.make(models.Action, subject="--3--", archived=False, planned_date=get_dt(-2))
        action4 = mommy.make(models.Action, subject="--4--", archived=False, planned_date=get_dt(-3))
        action5 = mommy.make(models.Action, subject="--5--", archived=False, planned_date=get_dt(+1))
        action6 = mommy.make(models.Action, subject="--6--", archived=False, planned_date=get_dt(+2))
        action7 = mommy.make(models.Action, subject="--7--", archived=False, planned_date=get_dt(+3))

        for action in [action1, action2, action3, action4, action5, action6, action7]:
            action.contacts.add(contact1)
            action.save()

        url = reverse("crm_view_entity", args=[entity.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        for action in [action1, action2, action5, action6, action7]:
            self.assertContains(response, action.subject)

        for action in [action3, action4]:
            self.assertNotContains(response, action.subject)

    def test_view_contact_all_actions_by_set(self):
        """view actions by set"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        action_type1 = mommy.make(models.ActionType)
        action_set1 = mommy.make(models.ActionSet)
        action_type2 = mommy.make(models.ActionType, set=action_set1)
        action_type3 = mommy.make(models.ActionType, set=action_set1)
        action_set2 = mommy.make(models.ActionSet)
        action_type4 = mommy.make(models.ActionType, set=action_set2)

        counter = 0
        visible_actions = []
        hidden_actions = []

        for i in range(2):  # pylint: disable=unused-variable
            action = mommy.make(models.Action, subject="--{0}--".format(counter), archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type1, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type3, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type2, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type4, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        url = reverse("crm_view_contact_actions", args=[contact1.id, action_set1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        for action in visible_actions:
            self.assertContains(response, action.subject)

        for action in hidden_actions:
            self.assertNotContains(response, action.subject)

    def test_view_entity_all_actions_by_set(self):
        """view entity actions by set"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        action_type1 = mommy.make(models.ActionType)
        action_set1 = mommy.make(models.ActionSet)
        action_type2 = mommy.make(models.ActionType, set=action_set1)
        action_type3 = mommy.make(models.ActionType, set=action_set1)
        action_set2 = mommy.make(models.ActionSet)
        action_type4 = mommy.make(models.ActionType, set=action_set2)

        counter = 0
        visible_actions = []
        hidden_actions = []

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type1, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type3, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type2, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type4, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            hidden_actions.append(action)
            counter += 1

        url = reverse("crm_view_entity_actions", args=[entity.id, action_set1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        for action in visible_actions:
            self.assertContains(response, action.subject)

        for action in hidden_actions:
            self.assertNotContains(response, action.subject)

    def test_contact_actions_set_gt5(self):
        """vie more than 5 actions by set"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        action_type1 = mommy.make(models.ActionType)
        action_set1 = mommy.make(models.ActionSet)
        action_type2 = mommy.make(models.ActionType, set=action_set1)
        action_type3 = mommy.make(models.ActionType, set=action_set1)
        action_set2 = mommy.make(models.ActionSet)
        action_type4 = mommy.make(models.ActionType, set=action_set2)

        counter = 0
        visible_actions = []
        hidden_actions = []

        for i in range(2):  # pylint: disable=unused-variable
            action = mommy.make(models.Action, subject="--{0}--".format(counter), archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type1, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type1, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type3, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type2, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type2, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type3, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type4, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(5):
            action = mommy.make(models.Action, subject="--{0}--".format(counter), type=action_type4, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        url = reverse("crm_view_contact", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        for action in visible_actions:
            self.assertContains(response, action.subject)

        for action in hidden_actions:
            self.assertNotContains(response, action.subject)

    def test_view_contact_actions(self):
        """view contact actions"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(contact1)
        action1.contacts.add(contact2)
        action1.entities.add(entity)
        action1.save()

        action2 = mommy.make(models.Action, subject="another action to do", archived=False)
        action2.contacts.add(contact1)
        action2.save()

        action3 = mommy.make(models.Action, subject="i believe i can fly", archived=False)
        action3.entities.add(entity)
        action3.save()

        action4 = mommy.make(models.Action, subject="hard days night", archived=False)
        action4.contacts.add(contact2)
        action4.save()

        url = reverse("crm_view_contact", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        content = response.content.decode('utf-8')
        self.assertEqual(1, content.count(action1.subject))
        self.assertEqual(1, content.count(action2.subject))
        self.assertEqual(0, content.count(action3.subject))
        self.assertEqual(0, content.count(action4.subject))

    def test_view_remove_contact_from_action(self):
        """view remove contact from action"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(contact1)
        action1.contacts.add(contact2)
        action1.entities.add(entity)
        action1.save()

        url = reverse('crm_remove_contact_from_action', args=[action1.id, contact1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 2)
        self.assertEqual(action1.entities.count(), 1)

    def test_remove_contact_from_action(self):
        """remove contact from action"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(contact1)
        action1.contacts.add(contact2)
        action1.entities.add(entity)
        action1.save()

        url = reverse('crm_remove_contact_from_action', args=[action1.id, contact1.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 1)
        self.assertEqual(action1.contacts.all()[0], contact2)
        self.assertEqual(action1.entities.count(), 1)
        self.assertEqual(action1.entities.all()[0], entity)

    def test_view_remove_entity_from_action_no_contacts(self):
        """view remove entity fro action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact.lastname = "AZERTY"
        contact.save()

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.entities.add(entity)
        action1.save()

        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, entity.name)
        self.assertNotContains(response, entity.default_contact.lastname)

        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 0)
        self.assertEqual(action1.entities.count(), 1)

    def test_view_remove_entity_from_action(self):
        """view remove entity fro action"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(contact1)
        action1.contacts.add(contact2)
        action1.entities.add(entity)
        action1.save()

        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(action1.contacts.count(), 2)
        self.assertEqual(action1.entities.count(), 1)

    def test_remove_entity_from_action(self):
        """remove entity from action"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact
        contact2 = mommy.make(models.Contact, entity=entity)

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.contacts.add(contact1)
        action1.contacts.add(contact2)
        action1.entities.add(entity)
        action1.save()

        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 2)
        self.assertEqual(action1.entities.count(), 0)

    def test_remove_entity_from_action2(self):
        """remove entity from action2"""
        entity1 = mommy.make(models.Entity, name="Corp1")
        mommy.make(models.Contact, entity=entity1)
        entity2 = mommy.make(models.Entity, name="Corp2")
        entity3 = mommy.make(models.Entity, name="Corp3")

        action1 = mommy.make(models.Action, subject="should be only once", archived=False)
        action1.entities.add(entity1)
        action1.entities.add(entity2)
        action1.entities.add(entity3)
        action1.save()

        url = reverse('crm_remove_entity_from_action', args=[action1.id, entity2.id])
        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(response.status_code, 200)
        action1 = models.Action.objects.get(id=action1.id)
        self.assertEqual(action1.contacts.count(), 0)
        self.assertEqual(action1.entities.count(), 2)
        sort_key = lambda x: x.id
        self.assertEqual(
            sorted(list(action1.entities.all()), key=sort_key),
            sorted([entity1, entity3], key=sort_key)
        )

    def test_add_entity_to_action(self):
        """add entity to action"""
        action = mommy.make(models.Action)
        entity = mommy.make(models.Entity)
        url = reverse('crm_add_entity_to_action', args=[action.id])
        response = self.client.post(url, data={'entity': entity.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)

    def test_view_add_action_from_board(self):
        """view add action from board"""
        url = reverse('crm_create_action', args=[0, 0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)

    def test_view_add_action_from_opportunity(self):
        """view add action from opportunity"""
        opportunity = mommy.make(models.Opportunity)
        url = reverse('crm_create_action', args=[0, 0])+"?opportunity={0}".format(opportunity.id)
        response = self.client.get(url)
        self.assertEqual(BeautifulSoup(response.content).select('#id_opportunity')[0]["value"], str(opportunity.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)

    def test_add_action_from_opportunity(self):
        """add action from opportunity"""
        opportunity = mommy.make(models.Opportunity)
        url = reverse('crm_create_action', args=[0, 0])+"?opportunity={0}".format(opportunity.id)
        data = {
            'subject': "tested", 'type': "", 'date': "", 'time': "",
            'status': "", 'in_charge': "", 'detail': "ABCDEF", 'opportunity': opportunity.id,
            'amount': 0, 'number': 0
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.subject, data["subject"])
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(action.opportunity, opportunity)

    def test_add_action_from_board(self):
        """add action from board"""
        url = reverse('crm_create_action', args=[0, 0])
        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        for item in data:
            if item in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, item).id, data[item])
            elif item in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, item), data[item])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 0)

    def test_view_add_action_from_contact(self):
        """view create from contact"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_create_action', args=[0, contact.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)

    def test_view_add_action_with_type(self):
        """view create from contact"""
        entity = mommy.make(models.Entity)
        action_type = mommy.make(models.ActionType)
        status1 = mommy.make(models.ActionStatus, ordering=1)
        status2 = mommy.make(models.ActionStatus, ordering=2)
        status3 = mommy.make(models.ActionStatus, ordering=3)
        mommy.make(models.ActionStatus, ordering=4)
        action_type.allowed_status.add(status1, status2)
        action_type.default_status = status1
        action_type.allowed_status2.add(status1, status3)
        action_type.default_status2 = status3
        action_type.save()

        contact = entity.default_contact
        url = reverse('crm_create_action_of_type', args=[0, contact.id, action_type.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(models.Action.objects.count(), 0)

        soup = BeautifulSoup(response.content)

        type_fields = soup.select('input#id_type')
        self.assertEqual(1, len(type_fields))
        type_field = type_fields[0]
        self.assertEqual(type_field['type'], 'hidden')
        self.assertEqual(type_field.get('value'), str(action_type.id))

        status_fields = soup.select('select#id_status')
        self.assertEqual(1, len(status_fields))
        status_field = status_fields[0]
        options = status_field.select('option')
        self.assertEqual(3, len(options))
        self.assertEqual(options[0]['value'], "")
        self.assertEqual(options[0].get('selected'), None)
        self.assertEqual(int(options[1]['value']), status1.id)
        self.assertEqual(options[1]['selected'], "selected")
        self.assertEqual(int(options[2]['value']), status2.id)
        self.assertEqual(options[2].get('selected'), None)

        status_fields = soup.select('select#id_status2')
        self.assertEqual(1, len(status_fields))
        status_field = status_fields[0]
        options = status_field.select('option')
        self.assertEqual(3, len(options))
        self.assertEqual(options[0]['value'], "")
        self.assertEqual(options[0].get('selected'), None)
        self.assertEqual(int(options[1]['value']), status1.id)
        self.assertEqual(options[1].get('selected'), None)
        self.assertEqual(int(options[2]['value']), status3.id)
        self.assertEqual(options[2]['selected'], "selected")

    def test_view_add_action_with_type2(self):
        """view create from contact"""
        entity = mommy.make(models.Entity)
        action_type = mommy.make(models.ActionType)
        status1 = mommy.make(models.ActionStatus, ordering=1)
        status2 = mommy.make(models.ActionStatus, ordering=2)
        status3 = mommy.make(models.ActionStatus, ordering=3)
        mommy.make(models.ActionStatus, ordering=4)
        action_type.allowed_status.add(status1, status2)
        action_type.allowed_status2.add(status1, status3)
        action_type.save()

        contact = entity.default_contact
        url = reverse('crm_create_action_of_type', args=[0, contact.id, action_type.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(models.Action.objects.count(), 0)

        soup = BeautifulSoup(response.content)
        type_fields = soup.select('input#id_type')
        self.assertEqual(1, len(type_fields))
        type_field = type_fields[0]
        self.assertEqual(type_field['type'], 'hidden')
        self.assertEqual(type_field.get('value'), str(action_type.id))

        status_fields = soup.select('select#id_status')
        self.assertEqual(1, len(status_fields))
        status_field = status_fields[0]
        options = status_field.select('option')
        self.assertEqual(3, len(options))
        self.assertEqual(options[0]['value'], "")
        self.assertEqual(options[0].get('selected'), "selected")
        self.assertEqual(int(options[1]['value']), status1.id)
        self.assertEqual(options[1].get('selected'), None)
        self.assertEqual(int(options[2]['value']), status2.id)
        self.assertEqual(options[2].get('selected'), None)

        status_fields = soup.select('select#id_status2')
        self.assertEqual(1, len(status_fields))
        status_field = status_fields[0]
        options = status_field.select('option')
        self.assertEqual(3, len(options))
        self.assertEqual(options[0]['value'], "")
        self.assertEqual(options[0].get('selected'), "selected")
        self.assertEqual(int(options[1]['value']), status1.id)
        self.assertEqual(options[1].get('selected'), None)
        self.assertEqual(int(options[2]['value']), status3.id)
        self.assertEqual(options[2].get('selected'), None)

    def test_view_add_action_without_type2(self):
        """view create from contact"""
        entity = mommy.make(models.Entity)
        action_type = mommy.make(models.ActionType)
        status1 = mommy.make(models.ActionStatus, ordering=1)
        status2 = mommy.make(models.ActionStatus, ordering=2)
        status3 = mommy.make(models.ActionStatus, ordering=3)
        mommy.make(models.ActionStatus, ordering=4)
        action_type.allowed_status.add(status1, status2)
        action_type.save()

        contact = entity.default_contact
        url = reverse('crm_create_action_of_type', args=[0, contact.id, action_type.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(models.Action.objects.count(), 0)

        soup = BeautifulSoup(response.content)
        type_fields = soup.select('input#id_type')
        self.assertEqual(1, len(type_fields))
        type_field = type_fields[0]
        self.assertEqual(type_field['type'], 'hidden')
        self.assertEqual(type_field.get('value'), str(action_type.id))

        status_fields = soup.select('select#id_status')
        self.assertEqual(1, len(status_fields))
        status_field = status_fields[0]
        options = status_field.select('option')
        self.assertEqual(3, len(options))
        self.assertEqual(options[0]['value'], "")
        self.assertEqual(options[0].get('selected'), "selected")
        self.assertEqual(int(options[1]['value']), status1.id)
        self.assertEqual(options[1].get('selected'), None)
        self.assertEqual(int(options[2]['value']), status2.id)
        self.assertEqual(options[2].get('selected'), None)

        status_fields = soup.select('select#id_status2')
        self.assertEqual(0, len(status_fields))
        status_fields = soup.select('input#id_status2')
        self.assertEqual(1, len(status_fields))
        status_field = status_fields[0]
        self.assertEqual(status_field['type'], 'hidden')
        self.assertEqual(status_field.get('value', ''), '')

    def test_add_action_from_contact(self):
        """create from contact"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        url = reverse('crm_create_action', args=[0, contact.id])

        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        for item in data:
            if item in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, item).id, data[item])
            elif item in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, item), data[item])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.contacts.all()[0], contact)

        self.assertEqual(action.entities.count(), 0)

    def test_view_add_action_from_entity(self):
        """view create from entity"""
        entity = mommy.make(models.Entity)
        url = reverse('crm_create_action', args=[entity.id, 0])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 0)

    def test_add_action_from_entity(self):
        """create from entity"""
        entity = mommy.make(models.Entity)
        url = reverse('crm_create_action', args=[entity.id, 0])

        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=False)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])

        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        for item in data:
            if item in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, item).id, data[item])
            elif item in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, item), data[item])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(action.entities.all()[0], entity)

    def test_view_edit_action(self):
        """view edit action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        planned_datetime = datetime(2014, 1, 31, 11, 34, 00)
        action = mommy.make(models.Action, display_on_board=True, done=True, planned_date=planned_datetime)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()

        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)
        self.assertEqual(soup.select("input#id_date")[0]["value"], "2014-01-31")
        self.assertEqual(soup.select("input#id_time")[0]["value"], "11:34:00")

    def test_view_edit_action_frozen(self):
        """view edit action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        planned_datetime = datetime(2014, 1, 31, 11, 34, 00)

        action_type = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus, name="status1")
        action_status2 = mommy.make(models.ActionStatus, name="status2", allowed_on_frozen=False)
        action_type.allowed_status.add(action_status1, action_status2)
        action_type.save()
        mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)

        action = mommy.make(models.Action, planned_date=planned_datetime, frozen=True, type=action_type)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("select#id_status option")), 2)
        self.assertEqual(soup.select("select#id_status option")[0]["value"], '')
        self.assertEqual(soup.select("select#id_status option")[1]["value"], str(action_status1.id))

    def test_edit_action(self):
        """edit action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        action = mommy.make(models.Action, display_on_board=True, done=True)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()
        act_id = action.id

        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.id, act_id)

        self.assertEqual(action.display_on_board, True)
        self.assertEqual(action.done, True)
        for item in data:
            if item in ("type", "status", "in_charge"):
                self.assertEqual(getattr(action, item).id, data[item])
            elif item in ("date", "time"):
                pass
            else:
                self.assertEqual(getattr(action, item), data[item])
        self.assertEqual(action.planned_date, datetime(2014, 1, 31, 11, 34, 00))
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 1)

    def test_edit_calculated_amount(self):
        """edit action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        action = mommy.make(models.Action, display_on_board=True, done=True, amount=Decimal("12.5"))
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()
        act_id = action.id

        action_type = mommy.make(models.ActionType, is_amount_calculated=True)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': None, 'number': 5
        }

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.id, act_id)

        self.assertEqual(action.amount, Decimal("12.5"))

    def test_edit_action_anonymous(self):
        """edit action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        action = mommy.make(models.Action, display_on_board=True, done=True)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()
        act_id = action.id

        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }

        self.client.logout()
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.id, act_id)

        self.assertNotEqual(action.subject, data["subject"])

    def test_view_edit_action_anonymous(self):
        """edit action"""
        action = mommy.make(models.Action)

        self.client.logout()
        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_view_edit_action_non_staff(self):
        """edit action"""
        action = mommy.make(models.Action)

        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_edit_action_non_staff(self):
        """edit action"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        action = mommy.make(models.Action, display_on_board=True, done=True)
        action.contacts.add(contact)
        action.entities.add(entity)
        action.save()
        act_id = action.id

        action_type = mommy.make(models.ActionType)
        action_status = mommy.make(models.ActionStatus)
        action_type.allowed_status.add(action_status)
        action_type.save()
        user = mommy.make(User, last_name="Dupond", first_name="Pierre", is_staff=True)
        team_member = mommy.make(models.TeamMember, user=user)

        data = {
            'subject': "tested", 'type': action_type.id, 'date': "2014-01-31", 'time': "11:34",
            'status': action_status.id, 'in_charge': team_member.id, 'detail': "ABCDEF",
            'amount': 200, 'number': 5
        }

        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_edit_action', args=[action.id])
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.id, act_id)

        self.assertNotEqual(action.subject, data["subject"])


class UpdateActionStatusTest(BaseTestCase):
    """Can update status"""

    def test_view_update_action_status(self):
        """it should display form"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        url = reverse('crm_update_action_status', args=[action.id])

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("#id_status option")))
        self.assertContains(response, action_status1.name)
        self.assertContains(response, action_status2.name)
        self.assertNotContains(response, action_status3.name)

        self.assertEqual(0, len(soup.select("#id_status option[selected=selected]")))

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, None)

    def test_view_update_action_status_existing(self):
        """it should display form"""

        action_status1 = mommy.make(models.ActionStatus, name="status1")
        action_status2 = mommy.make(models.ActionStatus, name="status2")
        action_status3 = mommy.make(models.ActionStatus, name="status3")
        action_status4 = mommy.make(models.ActionStatus, name="status4", allowed_on_frozen=False)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.allowed_status.add(action_status4)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status=action_status1, frozen=False)

        url = reverse('crm_update_action_status', args=[action.id])

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(3, len(soup.select("#id_status option")))
        self.assertContains(response, action_status1.name)
        self.assertContains(response, action_status2.name)
        self.assertNotContains(response, action_status3.name)
        self.assertContains(response, action_status4.name)

        self.assertEqual(1, len(soup.select("#id_status option[selected=selected]")))
        self.assertEqual(action_status1.name, soup.select("#id_status option[selected=selected]")[0].text)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, action_status1)

    def test_view_update_action_status_frozen(self):
        """it should display form"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)
        action_status4 = mommy.make(models.ActionStatus, allowed_on_frozen=False)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.allowed_status.add(action_status4)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status=action_status1, frozen=True)

        url = reverse('crm_update_action_status', args=[action.id])

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("#id_status option")))
        self.assertContains(response, action_status1.name)
        self.assertContains(response, action_status2.name)
        self.assertNotContains(response, action_status3.name)
        self.assertNotContains(response, action_status4.name)

        self.assertEqual(1, len(soup.select("#id_status option[selected=selected]")))
        self.assertEqual(action_status1.name, soup.select("#id_status option[selected=selected]")[0].text)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, action_status1)

    def test_view_update_action_status_on_done(self):
        """it should display form"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus, is_final=True)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status=action_status1)

        url = reverse('crm_update_action_status', args=[action.id]) + "?done=1"

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("#id_status option")))
        self.assertContains(response, action_status1.name)
        self.assertContains(response, action_status2.name)
        self.assertNotContains(response, action_status3.name)

        # show a final status has selected item
        self.assertEqual(1, len(soup.select("#id_status option[selected=selected]")))
        self.assertEqual(action_status2.name, soup.select("#id_status option[selected=selected]")[0].text)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, action_status1)

    def test_update_action_status(self):
        """it should change status"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        url = reverse('crm_update_action_status', args=[action.id])

        data = {
            'status': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>'
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, action_status2)

    def test_update_action_status_invalid(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        url = reverse('crm_update_action_status', args=[action.id])

        data = {
            'status': action_status3.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertNotContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>'
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, None)

    def test_update_action_status_existing(self):
        """it should change status"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status=action_status1)

        url = reverse('crm_update_action_status', args=[action.id])

        data = {
            'status': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>'
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, action_status2)

    def test_update_action_status_existing_invalid(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status=action_status1)

        url = reverse('crm_update_action_status', args=[action.id])

        data = {
            'status': action_status3.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertNotContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>',
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, action_status1)

    def test_update_action_status_anonymous(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        self.client.logout()

        url = reverse('crm_update_action_status', args=[action.id])

        data = {
            'status': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, None)

    def test_update_action_status_denied(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_update_action_status', args=[action.id])

        data = {
            'status': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, None)

    def test_save_final_status(self):
        """It should change the done flag"""

        action_status1 = mommy.make(models.ActionStatus, is_final=True)
        action_status2 = mommy.make(models.ActionStatus, is_final=False)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status.add(action_status1)
        action_type.allowed_status.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, done=False)

        action.status = action_status1
        action.save()
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, True)

        action.status = action_status2
        action.save()
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, False)


class UpdateActionStatus2Test(BaseTestCase):
    """Can update status2"""

    def test_view_update_action_status2(self):
        """it should display form"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        url = reverse('crm_update_action_status2', args=[action.id])

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("#id_status2 option")))
        self.assertContains(response, action_status1.name)
        self.assertContains(response, action_status2.name)
        self.assertNotContains(response, action_status3.name)

        self.assertEqual(0, len(soup.select("#id_status2 option[selected=selected]")))

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, None)

    def test_view_update_action_status2_existing(self):
        """it should display form"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status2=action_status1)

        url = reverse('crm_update_action_status2', args=[action.id])

        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)

        self.assertEqual(2, len(soup.select("#id_status2 option")))
        self.assertContains(response, action_status1.name)
        self.assertContains(response, action_status2.name)
        self.assertNotContains(response, action_status3.name)

        self.assertEqual(1, len(soup.select("#id_status2 option[selected=selected]")))
        self.assertEqual(action_status1.name, soup.select("#id_status2 option[selected=selected]")[0].text)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, action_status1)

    def test_update_action_status2(self):
        """it should change status"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        url = reverse('crm_update_action_status2', args=[action.id])

        data = {
            'status2': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>',
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, action_status2)

    def test_update_action_status2_invalid(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        url = reverse('crm_update_action_status2', args=[action.id])

        data = {
            'status2': action_status3.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertNotContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>',
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, None)

    def test_update_action_status2_existing(self):
        """it should change status"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status=action_status1)

        url = reverse('crm_update_action_status2', args=[action.id])

        data = {
            'status2': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>'
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, action_status2)

    def test_update_action_status2_existing_invalid(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, status2=action_status1)

        url = reverse('crm_update_action_status2', args=[action.id])

        data = {
            'status2': action_status3.id
        }
        response = self.client.post(url, data)

        self.assertEqual(200, response.status_code)
        self.assertNotContains(
            response,
            '<script>$.colorbox.close(); window.location=window.location;</script>'
        )

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, action_status1)

    def test_update_action_status2_anonymous(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        self.client.logout()

        url = reverse('crm_update_action_status2', args=[action.id])

        data = {
            'status2': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, None)

    def test_update_action_status2_denied(self):
        """it should show error"""

        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_status3 = mommy.make(models.ActionStatus)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type)

        self.user.is_staff = False
        self.user.save()

        url = reverse('crm_update_action_status2', args=[action.id])

        data = {
            'status2': action_status2.id
        }
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status2, None)

    def test_save_final_status2(self):
        """status2 don't change the done flag"""

        action_status1 = mommy.make(models.ActionStatus, is_final=True)
        action_status2 = mommy.make(models.ActionStatus, is_final=False)

        action_type = mommy.make(models.ActionType)
        action_type.allowed_status2.add(action_status1)
        action_type.allowed_status2.add(action_status2)
        action_type.save()

        action = mommy.make(models.Action, type=action_type, done=False)

        action.status2 = action_status1
        action.save()
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, False)

        action.status2 = action_status2
        action.save()
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, False)


class ReassignActionTest(BaseTestCase):
    """Change the action contacts and entities"""

    def test_view_reassign_action_to_contact(self):
        """view reassign contact popup"""
        action = mommy.make(models.Action)
        contact1 = mommy.make(models.Contact)
        action.contacts.add(contact1)
        action.save()

        url = reverse('crm_reassign_action', args=[action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reassign_action_to_contact(self):
        """reassign action to another contact"""

        action = mommy.make(models.Action)
        contact1 = mommy.make(models.Contact)
        action.contacts.add(contact1)
        action.save()

        contact2 = mommy.make(models.Contact)

        data = {
            'object_id': contact2.id,
            'object_type': 'contact',
            'name': contact2.fullname
        }

        url = reverse('crm_reassign_action', args=[action.id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        js_script = '<script>$.colorbox.close(); window.location="{0}";</script>'.format(contact2.get_absolute_url())
        self.assertContains(response, js_script)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(list(action.contacts.all()), [contact2])

    def test_reassign_action_to_entity(self):
        """reassign action to another entity"""

        action = mommy.make(models.Action)
        contact1 = mommy.make(models.Contact)
        action.contacts.add(contact1)
        action.save()

        data = {
            'object_id': contact1.entity.id,
            'object_type': 'entity',
            'name': contact1.entity.name
        }

        url = reverse('crm_reassign_action', args=[action.id])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        js_script = '<script>$.colorbox.close(); window.location="{0}";</script>'.format(
            contact1.entity.get_absolute_url()
        )
        self.assertContains(response, js_script)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 0)
        self.assertEqual(action.entities.count(), 1)
        self.assertEqual(list(action.entities.all()), [contact1.entity])

    def test_reassign_action_anonymous(self):
        """reassign action to another entity : anonymous"""
        action = mommy.make(models.Action)
        contact1 = mommy.make(models.Contact)
        action.contacts.add(contact1)
        action.save()

        self.client.logout()

        data = {
            'object_id': contact1.entity.id,
            'object_type': 'entity',
            'name': contact1.entity.name
        }

        url = reverse('crm_reassign_action', args=[action.id])
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(list(action.contacts.all()), [contact1])

    def test_reassign_action_user_not_allowed(self):
        """reassign action to another entity : non staff"""
        action = mommy.make(models.Action)
        contact1 = mommy.make(models.Contact)
        action.contacts.add(contact1)
        action.save()

        self.user.is_staff = False
        self.user.save()

        data = {
            'object_id': contact1.entity.id,
            'object_type': 'entity',
            'name': contact1.entity.name
        }

        url = reverse('crm_reassign_action', args=[action.id])
        response = self.client.post(url, data)

        self.assertEqual(302, response.status_code)

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.contacts.count(), 1)
        self.assertEqual(action.entities.count(), 0)
        self.assertEqual(list(action.contacts.all()), [contact1])


class ActionDurationTest(BaseTestCase):
    """calculate duration test"""

    def test_action_duration_same_day(self):
        """return the duration of an action"""
        action = mommy.make(
            models.Action,
            planned_date=datetime(2016, 2, 4, 14, 0),
            end_datetime=datetime(2016, 2, 4, 16, 0)
        )
        self.assertEqual(action.duration(), "2:00")

    def test_action_duration_same_day2(self):
        """return the duration of an action"""
        action = mommy.make(
            models.Action,
            planned_date=datetime(2016, 2, 4, 13, 48),
            end_datetime=datetime(2016, 2, 4, 16, 15)
        )
        self.assertEqual(action.duration(), "2:27")

    def test_action_duration_several_days(self):
        """return the duration of an action"""
        action = mommy.make(
            models.Action,
            planned_date=datetime(2016, 2, 2, 13, 48),
            end_datetime=datetime(2016, 2, 4, 16, 15)
        )
        self.assertEqual(action.duration(), _("2 days 2:27"))


class ActionStatusTrackTest(BaseTestCase):
    """calculate duration test"""

    def test_action_no_type(self):
        """no track is created"""
        action = mommy.make(models.Action)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 0)

    def test_action_dont_track(self):
        """no track is created"""
        action_type = mommy.make(models.ActionType, track_status=False)
        action = mommy.make(models.Action, type=action_type)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 0)

    def test_action_track_default_status(self):
        """a track is created"""
        status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType, track_status=True, default_status=status)
        action = mommy.make(models.Action, type=action_type)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 0)

    def test_action_track_no_default_status(self):
        """a track is created"""
        status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType, track_status=True)
        action = mommy.make(models.Action, type=action_type)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 0)

    def test_action_track_set_status(self):
        """a track is created"""
        status = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType, track_status=True)
        action = mommy.make(models.Action, type=action_type, status=status)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 1)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status)
        self.assertEqual(track.datetime.date(), date.today())

    def test_action_track(self):
        """a track is created for each status changed"""
        status1 = mommy.make(models.ActionStatus)
        status2 = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType, track_status=True)
        #
        action = mommy.make(models.Action, type=action_type, status=status1)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 1)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status1)
        self.assertEqual(track.datetime.date(), date.today())
        action.status = status2
        action.save()
        #
        self.assertEqual(models.ActionStatusTrack.objects.count(), 2)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status2)
        self.assertEqual(track.datetime.date(), date.today())

    def test_action_track_none(self):
        """a track is created for each status changed"""
        status1 = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType, track_status=True)
        #
        action = mommy.make(models.Action, type=action_type, status=status1)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 1)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status1)
        self.assertEqual(track.datetime.date(), date.today())
        action.status = None
        action.save()
        #
        self.assertEqual(models.ActionStatusTrack.objects.count(), 1)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status1)
        self.assertEqual(track.datetime.date(), date.today())

    def test_action_track_no_status_changed(self):
        """a track is created for each status changed"""
        status1 = mommy.make(models.ActionStatus)
        action_type = mommy.make(models.ActionType, track_status=True)
        #
        action = mommy.make(models.Action, type=action_type, status=status1)
        self.assertEqual(models.ActionStatusTrack.objects.count(), 1)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status1)
        self.assertEqual(track.datetime.date(), date.today())
        action.subject = "Test"
        action.save()
        #
        self.assertEqual(models.ActionStatusTrack.objects.count(), 1)
        track = models.ActionStatusTrack.objects.all()[0]
        self.assertEqual(track.action, action)
        self.assertEqual(track.status, status1)
        self.assertEqual(track.datetime.date(), date.today())
