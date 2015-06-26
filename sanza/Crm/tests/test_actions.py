# -*- coding: utf-8 -*-
"""unit testing"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


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
            'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
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
        data = json.loads(response.content)
        self.assertEqual([action_status1.id, action_status2.id], data['allowed_status'])
        self.assertEqual(0, data['default_status'])

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
        data = json.loads(response.content)
        self.assertEqual([action_status1.id, action_status2.id], data['allowed_status'])
        self.assertEqual(action_status2.id, data['default_status'])

    def test_no_allowed_status(self):
        """test no allowed status"""
        action_type = mommy.make(models.ActionType)

        url = reverse("crm_get_action_status")+"?t="+str(action_type.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([], data['allowed_status'])
        self.assertEqual(0, data['default_status'])

    def test_allowed_status_no_type(self):
        """test allowed status no type"""
        url = reverse("crm_get_action_status")+"?t="+str(0)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual([], data['allowed_status'])
        self.assertEqual(0, data['default_status'])

    def test_allowed_status_unknown_type(self):
        """test allowed status unknown type"""
        url = reverse("crm_get_action_status")+"?t=100"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_allowed_status_invalid_type(self):
        """test allowed status invalid type"""
        url = reverse("crm_get_action_status")+"?t=toto"
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
            'status': "", 'in_charge': "", 'opportunity': "", 'detail':"",
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
        errors = BeautifulSoup(response.content).select('#id_time .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_end_date .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_end_date .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_end_time .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_end_time .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_end_time .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_date .field-error')
        self.assertEqual(len(errors), 1)

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

        errors = BeautifulSoup(response.content).select('#id_time .field-error')
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

        errors = BeautifulSoup(response.content).select('#id_end_date .field-error')
        self.assertEqual(len(errors), 1)

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

        errors = BeautifulSoup(response.content).select('#id_end_time .field-error')
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

        self.assertEqual(soup.select("#id_end_date")[0]["value"], "2014-04-10")
        self.assertEqual(soup.select("#id_end_time")[0]["value"], "09:30:00")


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
        self.assertEqual(1, response.content.count(action.subject))

    def test_view_contact_actions_more_than_five(self):
        """view contact actions if more than five"""
        entity = mommy.make(models.Entity)
        contact1 = entity.default_contact

        actions = [mommy.make(models.Action, subject=u"--{0}--".format(i), archived=False) for i in range(10)]
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

        action1 = mommy.make(models.Action, subject=u"--1--", archived=False, planned_date=get_dt())
        action2 = mommy.make(models.Action, subject=u"--2--", archived=False, planned_date=get_dt(-1))
        action3 = mommy.make(models.Action, subject=u"--3--", archived=False, planned_date=get_dt(-2))
        action4 = mommy.make(models.Action, subject=u"--4--", archived=False, planned_date=get_dt(-3))
        action5 = mommy.make(models.Action, subject=u"--5--", archived=False, planned_date=get_dt(+1))
        action6 = mommy.make(models.Action, subject=u"--6--", archived=False, planned_date=get_dt(+2))
        action7 = mommy.make(models.Action, subject=u"--7--", archived=False, planned_date=get_dt(+3))

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

        action1 = mommy.make(models.Action, subject=u"--1--", archived=False, planned_date=get_dt())
        action2 = mommy.make(models.Action, subject=u"--2--", archived=False, planned_date=get_dt(-1))
        action3 = mommy.make(models.Action, subject=u"--3--", archived=False, planned_date=get_dt(-2))
        action4 = mommy.make(models.Action, subject=u"--4--", archived=False, planned_date=get_dt(-3))
        action5 = mommy.make(models.Action, subject=u"--5--", archived=False, planned_date=get_dt(+1))
        action6 = mommy.make(models.Action, subject=u"--6--", archived=False, planned_date=get_dt(+2))
        action7 = mommy.make(models.Action, subject=u"--7--", archived=False, planned_date=get_dt(+3))

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
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type1, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type3, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type2, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type4, archived=False)
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
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type1, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type3, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(10):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type2, archived=False)
            if i % 2:
                action.contacts.add(contact1)
            else:
                action.entities.add(entity)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type4, archived=False)
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
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type1, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type1, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type3, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type2, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(2):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type2, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type3, archived=False)
            action.contacts.add(contact1)
            action.save()
            visible_actions.append(action)
            counter += 1

        for i in range(3):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type4, archived=False)
            action.contacts.add(contact1)
            action.save()
            hidden_actions.append(action)
            counter += 1

        for i in range(5):
            action = mommy.make(models.Action, subject=u"--{0}--".format(counter), type=action_type4, archived=False)
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
        self.assertEqual(1, response.content.count(action1.subject))
        self.assertEqual(1, response.content.count(action2.subject))
        self.assertEqual(0, response.content.count(action3.subject))
        self.assertEqual(0, response.content.count(action4.subject))

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


class DoActionTest(BaseTestCase):
    """Do action"""

    def test_do_action(self):
        """do it"""
        action = mommy.make(models.Action, done=False)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(action.done, False)

        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'done': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, True)

    def test_undo_action(self):
        """undo it"""
        action = mommy.make(models.Action, done=True)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(action.done, True)

        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'done': False})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, False)

    def test_view_action_warning_not_in_charge(self):
        """warning if not in charge"""
        user = mommy.make(User, is_active=True, is_staff=True, last_name="L", first_name="F")
        team_member = mommy.make(models.TeamMember, user=user)
        action = mommy.make(models.Action, done=True, in_charge=team_member)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "warning")


class ActionAutoGenerateNumberTestCase(TestCase):
    """test number can be autogenerated"""

    def test_create_auto_number(self):
        """create auto number"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)

    def test_create_several_auto_number(self):
        """create several numbers"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 2)
        no_gen_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=False)
        action = models.Action.objects.create(type=no_gen_type, subject="a")
        self.assertEqual(action.number, 0)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 3)

    def test_save_several_auto_number(self):
        """save : number is not changed"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)
        action.save()
        self.assertEqual(action.number, 1)

    def test_create_several_auto_types(self):
        """number generated by type"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 2)
        no_gen_type = mommy.make(models.ActionType, last_number=27, number_auto_generated=True)
        action = models.Action.objects.create(type=no_gen_type, subject="a")
        self.assertEqual(action.number, 28)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 3)

    def test_create_no_number_generation(self):
        """create action with no auto generation"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=False)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 0)


class ActionMenuTest(BaseTestCase):
    """Custom menu action"""

    def test_action_menu(self):
        """test custom menus are displayed"""
        action_type1 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_do_action', a_attrs='class="colorbox-form"', order_index=2
        )

        menu2 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="remove", label="DELETE ME", view_name='crm_delete_action', a_attrs='target="_blank"', order_index=1
        )

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 2)

        self.assertEqual(li_tags[0].text.strip(), menu2.label)
        self.assertEqual(li_tags[0].a['target'], '"_blank"')
        self.assertEqual(li_tags[0].a['href'], reverse('crm_delete_action', args=[action.id]))
        self.assertEqual(li_tags[0].a.span['class'], ['glyphicon', 'glyphicon-{0}'.format(menu2.icon)])

        self.assertEqual(li_tags[1].text.strip(), menu1.label)
        self.assertEqual(li_tags[1].a['class'], ['"colorbox-form"'])
        self.assertEqual(li_tags[1].a['href'], reverse('crm_do_action', args=[action.id]))
        self.assertEqual(li_tags[1].a.span['class'], ['glyphicon', 'glyphicon-{0}'.format(menu1.icon)])

    def test_action_menu_one_not_set(self):
        """test custom menus are displayed only for associated types"""
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_do_action', a_attrs='class="colorbox-form"', order_index=2
        )

        mommy.make(
            models.ActionMenu, action_type=action_type2,
            icon="remove", label="DELETE ME", view_name='crm_delete_action', a_attrs='target="_blank"', order_index=1
        )

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 1)

        self.assertEqual(li_tags[0].text.strip(), menu1.label)
        self.assertEqual(li_tags[0].a['class'], ['"colorbox-form"'])
        self.assertEqual(li_tags[0].a['href'], reverse('crm_do_action', args=[action.id]))
        self.assertEqual(li_tags[0].a.span['class'], ['glyphicon', 'glyphicon-{0}'.format(menu1.icon)])

    def test_action_menu_no_type(self):
        """test action is displayed if no type defined"""
        action = mommy.make(models.Action, type=None)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 0)

    def test_action_no_menu(self):
        """test action is displayed if no custom menu"""
        action_type1 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 0)

    def test_action_inavlid_view_name(self):
        """test custom menus are displayed only for associated types"""
        action_type1 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_blabla_dummy', a_attrs='class="colorbox-form"', order_index=2
        )

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 1)

        self.assertEqual(li_tags[0].text.strip(), menu1.label)
        self.assertEqual(li_tags[0].a['class'], ['"colorbox-form"'])
        self.assertEqual(li_tags[0].a['href'], '')
        self.assertEqual(li_tags[0].a.span['class'], ['glyphicon', 'glyphicon-{0}'.format(menu1.icon)])


class CloneActionTest(BaseTestCase):
    """clone an action"""

    def test_view_clone_action_1_type(self):
        """it should display hidden input for the only allowed type"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        html_fields = soup.select("#id_action_type")
        self.assertEqual(1, len(html_fields))
        self.assertEqual(html_fields[0]["type"], "hidden")
        self.assertEqual(html_fields[0]["value"], "{0}".format(action_type_2.id))

    def test_view_clone_action_2_types(self):
        """it should display a select with allowed types"""
        action_type_1 = mommy.make(models.ActionType, order_index=1)
        action_type_2 = mommy.make(models.ActionType, order_index=2)
        action_type_3 = mommy.make(models.ActionType, order_index=3)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.next_action_types.add(action_type_3)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        html_fields = soup.select("#id_action_type")
        self.assertEqual(1, len(html_fields))
        options = html_fields[0].select("option")
        self.assertEqual(len(options), 2)
        self.assertEqual(options[0]["value"], "{0}".format(action_type_2.id))
        self.assertEqual(options[1]["value"], "{0}".format(action_type_3.id))

    def test_view_clone_action_no_types(self):
        """it should display an empty select"""
        action_type_1 = mommy.make(models.ActionType, order_index=1)

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        html_fields = soup.select("#id_action_type")
        self.assertEqual(1, len(html_fields))
        options = html_fields[0].select("option")
        self.assertEqual(len(options), 0)

    def test_view_clone_action_type_is_none(self):
        """it should display 404"""
        action = mommy.make(models.Action, type=None)
        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(404, response.status_code)

    def test_view_clone_anonymous(self):
        """it should display hidden input for the only allowed type"""
        self.client.logout()

        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(302, response.status_code)

    def test_view_clone_non_staff(self):
        """it should display hidden input for the only allowed type"""
        self.user.is_staff = False
        self.user.save()

        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(302, response.status_code)

    def test_post_clone_action(self):
        """it should clone"""
        action_status_1 = mommy.make(models.ActionStatus)
        action_type_1 = mommy.make(models.ActionType)
        action_type_1.allowed_status.add(action_status_1)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)

        action = mommy.make(models.Action, type=action_type_1, done=True, status=action_status_1)

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.content, '<script>$.colorbox.close(); window.location=window.location;</script>')

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.status, None)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)

    def test_post_clone_action_default_status(self):
        """it should clone"""
        action_status = mommy.make(models.ActionStatus)
        action_status_1 = mommy.make(models.ActionStatus)
        action_type_1 = mommy.make(models.ActionType)
        action_type_1.allowed_status.add(action_status_1)
        action_type_2 = mommy.make(models.ActionType, default_status=action_status)
        action_type_2.allowed_status.add(action_status)
        action_type_2.save()
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)

        action = mommy.make(models.Action, type=action_type_1, done=True, status=action_status_1)

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.content, '<script>$.colorbox.close(); window.location=window.location;</script>')

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.status, action_status)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)

    def test_post_clone_action_anonymous(self):
        """it should not clone and redirect to login page"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': action_type_2.id
        }

        self.client.logout()

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_action_non_staff(self):
        """it should not clone and redirect to login page"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': action_type_2.id
        }

        self.user.is_staff = False
        self.user.save()

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_action_invalid(self):
        """it should not clone and show error"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': 'bla'
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".error-msg")), 1)
        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_no_type(self):
        """it should not clone and show error"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': ''
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".error-msg")), 1)
        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_other_type(self):
        """it should not clone and show error"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_3 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': action_type_3.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".error-msg")), 1)
        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_type_is_none(self):
        """it should not clone and 404"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=None)

        data = {
            'action_type': action_type_2,
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(404, response.status_code)
        self.assertEqual(1, models.Action.objects.count())
