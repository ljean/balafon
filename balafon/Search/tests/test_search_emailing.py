# -*- coding: utf-8 -*-
"""test search forms of the emailing module"""

from datetime import datetime
import json

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Emailing.models import Emailing
from balafon.Emailing.tests import BaseTestCase
from balafon.utils import get_form_errors


class EmailingSearchTest(BaseTestCase):
    """test emailing searches"""

    def _new_contact(self, name):
        """create a new contact"""
        entity = mommy.make(models.Entity)
        contact = entity.default_contact
        contact.lastname = name
        contact.main_contact = True
        contact.has_left = False
        contact.save()
        return contact

    def test_view_emailing_empty(self):
        """view form no emailing defined"""
        url = reverse('search_get_field', args=['emailing_sent'])
        url += "?block=gr0&count=0"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        soup = BeautifulSoup(data['form'])
        selector = soup.select("select#id_gr0-_-emailing_sent-_-0 option")
        self.assertEqual(1, len(selector))
        self.assertEqual("", selector[0]["value"])

    def test_view_emailing_sent(self):
        """view form no emailing sent"""
        mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        emailing2 = mommy.make(Emailing, status=Emailing.STATUS_SENDING, scheduling_dt=datetime.now())
        emailing3 = mommy.make(
            Emailing, status=Emailing.STATUS_SENT, scheduling_dt=datetime.now(), sending_dt=datetime.now()
        )
        mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=datetime.now())

        url = reverse('search_get_field', args=['emailing_sent'])
        url += "?block=gr0&count=0"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        soup = BeautifulSoup(data['form'])
        selector = soup.select("select#id_gr0-_-emailing_sent-_-0 option")
        self.assertEqual(3, len(selector))
        self.assertEqual("", selector[0]["value"])
        self.assertEqual(emailing3.id, int(selector[1]["value"]))
        self.assertEqual(emailing2.id, int(selector[2]["value"]))

    def test_view_emailing_opened(self):
        """view form no emailing opened"""

        mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        emailing2 = mommy.make(Emailing, status=Emailing.STATUS_SENDING, scheduling_dt=datetime.now())
        emailing3 = mommy.make(
            Emailing, status=Emailing.STATUS_SENT, scheduling_dt=datetime.now(), sending_dt=datetime.now()
        )
        mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=datetime.now())

        url = reverse('search_get_field', args=['emailing_opened'])
        url += "?block=gr0&count=0"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        soup = BeautifulSoup(data['form'])
        selector = soup.select("select#id_gr0-_-emailing_opened-_-0 option")
        self.assertEqual(3, len(selector))
        self.assertEqual("", selector[0]["value"])
        self.assertEqual(emailing3.id, int(selector[1]["value"]))
        self.assertEqual(emailing2.id, int(selector[2]["value"]))

    def test_view_emailing_to_send(self):
        """view form no emailing to be send"""

        emailing1 = mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        emailing2 = mommy.make(Emailing, status=Emailing.STATUS_SENDING, scheduling_dt=datetime.now())
        mommy.make(
            Emailing, status=Emailing.STATUS_SENT, scheduling_dt=datetime.now(), sending_dt=datetime.now()
        )
        emailing4 = mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=datetime.now())

        url = reverse('search_get_field', args=['emailing_send'])
        url += "?block=gr0&count=0"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        soup = BeautifulSoup(data['form'])
        selector = soup.select("select#id_gr0-_-emailing_send-_-0 option")
        self.assertEqual(4, len(selector))
        self.assertEqual("", selector[0]["value"])
        self.assertEqual(emailing4.id, int(selector[1]["value"]))
        self.assertEqual(emailing2.id, int(selector[2]["value"]))
        self.assertEqual(emailing1.id, int(selector[3]["value"]))

    def test_view_emailing_bounce(self):
        """view form no emailing bounce"""

        mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        emailing2 = mommy.make(Emailing, status=Emailing.STATUS_SENDING, scheduling_dt=datetime.now())
        emailing3 = mommy.make(
            Emailing, status=Emailing.STATUS_SENT, scheduling_dt=datetime.now(), sending_dt=datetime.now()
        )
        mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=datetime.now())

        url = reverse('search_get_field', args=['emailing_bounce'])
        url += "?block=gr0&count=0"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        soup = BeautifulSoup(data['form'])
        selector = soup.select("select#id_gr0-_-emailing_bounce-_-0 option")
        self.assertEqual(3, len(selector))
        self.assertEqual("", selector[0]["value"])
        self.assertEqual(emailing3.id, int(selector[1]["value"]))
        self.assertEqual(emailing2.id, int(selector[2]["value"]))

    def test_view_emailing_contacts(self):
        """view form no emailing all contacts"""

        emailing1 = mommy.make(Emailing, status=Emailing.STATUS_EDITING)
        emailing2 = mommy.make(Emailing, status=Emailing.STATUS_SENDING, scheduling_dt=datetime.now())
        emailing3 = mommy.make(
            Emailing, status=Emailing.STATUS_SENT, scheduling_dt=datetime.now(), sending_dt=datetime.now()
        )
        emailing4 = mommy.make(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=datetime.now())

        url = reverse('search_get_field', args=['emailing_contacts'])
        url += "?block=gr0&count=0"

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        soup = BeautifulSoup(data['form'])
        selector = soup.select("select#id_gr0-_-emailing_contacts-_-0 option")
        self.assertEqual(5, len(selector))
        self.assertEqual("", selector[0]["value"])
        self.assertEqual(emailing4.id, int(selector[1]["value"]))
        self.assertEqual(emailing3.id, int(selector[2]["value"]))
        self.assertEqual(emailing2.id, int(selector[3]["value"]))
        self.assertEqual(emailing1.id, int(selector[4]["value"]))

    def test_search_sent_to(self):
        """search contacts who received the emailing"""

        emailing = mommy.make(Emailing, status=Emailing.STATUS_SENDING)
        emailing2 = mommy.make(Emailing, status=Emailing.STATUS_SENDING)

        contact1 = self._new_contact(u"ABCDabcd")
        contact2 = self._new_contact(u"EFGHefg")
        contact3 = self._new_contact(u"IJKLijkl")
        contact4 = self._new_contact(u"MNOPmnop")

        emailing.sent_to.add(contact1)
        emailing.send_to.add(contact2)
        emailing.save()

        emailing2.sent_to.add(contact3)
        emailing2.save()

        url = reverse('search')

        data = {"gr0-_-emailing_sent-_-0": emailing.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], get_form_errors(response))

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)
        self.assertNotContains(response, contact4.lastname)

    def test_search_opened(self):
        """search contacts who opened the emailing"""
        emailing = mommy.make(Emailing, status=Emailing.STATUS_SENDING)

        contact1 = self._new_contact(u"ABCDabcd")
        contact2 = self._new_contact(u"EFGHefg")
        contact3 = self._new_contact(u"IJKLijkl")

        emailing.sent_to.add(contact1)
        emailing.send_to.add(contact2)
        emailing.opened_emails.add(contact1)
        emailing.save()

        url = reverse('search')

        data = {"gr0-_-emailing_opened-_-0": emailing.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], get_form_errors(response))

        self.assertContains(response, contact1.lastname)
        self.assertNotContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_search_send_to(self):
        """search contacts who will receive the emailing"""

        emailing = mommy.make(Emailing, status=Emailing.STATUS_SENDING)

        contact1 = self._new_contact(u"ABCDabcd")
        contact2 = self._new_contact(u"EFGHefg")
        contact3 = self._new_contact(u"IJKLijkl")

        emailing.sent_to.add(contact1)
        emailing.send_to.add(contact2)
        emailing.save()

        url = reverse('search')

        data = {"gr0-_-emailing_send-_-0": emailing.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], get_form_errors(response))

        self.assertNotContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_search_contacts(self):
        """search all contacts in the emailing"""
        emailing = mommy.make(Emailing, status=Emailing.STATUS_SENDING)

        contact1 = self._new_contact(u"ABCDabcd")
        contact2 = self._new_contact(u"EFGHefg")
        contact3 = self._new_contact(u"IJKLijkl")

        emailing.sent_to.add(contact1)
        emailing.send_to.add(contact2)
        emailing.save()

        url = reverse('search')

        data = {"gr0-_-emailing_contacts-_-0": emailing.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], get_form_errors(response))

        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_search_bounce(self):
        """search contacts with bounce"""
        emailing = mommy.make(Emailing, status=Emailing.STATUS_SENDING)

        contact1 = self._new_contact(u"ABCDabcd")
        contact2 = self._new_contact(u"EFGHefg")
        contact3 = self._new_contact(u"IJKLijkl")
        contact4 = self._new_contact(u"MNOPmnop")
        contact5 = self._new_contact(u"QRSTqrst")
        contact6 = self._new_contact(u"UVWXuvwx")

        for contact in (contact1, contact2, contact3, contact4, contact5, contact6):
            emailing.sent_to.add(contact)

        emailing.hard_bounce.add(contact1)
        emailing.soft_bounce.add(contact2)
        emailing.spam.add(contact3)
        emailing.unsub.add(contact4)
        emailing.rejected.add(contact5)

        emailing.save()

        url = reverse('search')

        data = {"gr0-_-emailing_bounce-_-0": emailing.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], get_form_errors(response))

        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, contact3.lastname)
        self.assertContains(response, contact4.lastname)
        self.assertContains(response, contact5.lastname)
        self.assertNotContains(response, contact6.lastname)

    def test_search_bounce_several(self):
        """search contacts with several bounces"""
        emailing = mommy.make(Emailing, status=Emailing.STATUS_SENDING)

        contact1 = self._new_contact(u"ABCDabcd")
        contact2 = self._new_contact(u"EFGHefg")
        contact3 = self._new_contact(u"IJKLijkl")

        for contact in (contact1, contact2, contact3, ):
            emailing.sent_to.add(contact)

        emailing.hard_bounce.add(contact1)
        emailing.soft_bounce.add(contact2)
        emailing.hard_bounce.add(contact2)

        emailing.save()

        url = reverse('search')

        data = {"gr0-_-emailing_bounce-_-0": emailing.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual([], get_form_errors(response))

        self.assertContains(response, contact1.lastname)
        self.assertContains(response, contact2.lastname)
        self.assertNotContains(response, contact3.lastname)

    def test_contact_by_emailing_error(self):
        """check behavior if emailing id is wrong"""
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Doe", lastname="John")

        url = reverse('search')

        data = {"gr0-_-emailing_opened-_-0": 333}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, obi.lastname)
        self.assertNotContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)

        self.assertEqual(1, len(get_form_errors(response)))
