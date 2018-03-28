# -*- coding: utf-8 -*-
"""test relationship search"""

from __future__ import unicode_literals

from datetime import date, timedelta

from django.core.urlresolvers import reverse

from model_mommy import mommy

from balafon.Crm import models
from balafon.Search.tests import BaseTestCase


class RelationshipSearchTest(BaseTestCase):
    """search on relationship"""

    def test_relationship_with_reverse(self):
        """contacts by relationship type"""

        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Jack", lastname="Doedoedoe")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")

        models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)

        url = reverse('search')

        data = {"gr0-_-contacts_by_relationship_type-_-0": master.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, obi.lastname)
        self.assertNotContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)

    def test_relationship_reverse(self):
        """contacts by relationship type: reverse"""

        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        doe = mommy.make(models.Contact, firstname="Jack", lastname="Doedoedoe")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")

        models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)

        url = reverse('search')

        data = {"gr0-_-contacts_by_relationship_type-_-0": -master.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, obi.lastname)
        self.assertContains(response, anakin.lastname)
        self.assertNotContains(response, doe.lastname)

    def test_relationship_type(self):
        """contacts by relationship type : no reverse"""
        john = mommy.make(models.Contact, firstname="John", lastname="Lennon#")
        ringo = mommy.make(models.Contact, firstname="Georges", lastname="Harrison")
        doe = mommy.make(models.Contact, firstname="Jack", lastname="Doedoedoe")

        friends = mommy.make(models.RelationshipType, name="Fiends")

        models.Relationship.objects.create(contact1=john, contact2=ringo, relationship_type=friends)

        url = reverse('search')

        data = {"gr0-_-contacts_by_relationship_type-_-0": friends.id}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, john.lastname)
        self.assertContains(response, ringo.lastname)
        self.assertNotContains(response, doe.lastname)

    def test_relationship_date(self):
        """contacts by relationship date"""
        john = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        ringo = mommy.make(models.Contact, firstname="Georges", lastname="Harrison")
        doe = mommy.make(models.Contact, firstname="Jack", lastname="Doedoedoe")

        friends = mommy.make(models.RelationshipType, name="Fiends")

        models.Relationship.objects.create(contact1=john, contact2=ringo, relationship_type=friends)

        url = reverse('search')

        today = date.today()
        data = {"gr0-_-contacts_by_relationship_dates-_-0": '{0} {0}'.format(today.strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, john.lastname)
        self.assertContains(response, ringo.lastname)
        self.assertNotContains(response, doe.lastname)

    def test_relationship_not_in_date(self):
        """contacts by relationship not in date"""
        john = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        ringo = mommy.make(models.Contact, firstname="Georges", lastname="Harrison")
        doe = mommy.make(models.Contact, firstname="Jack", lastname="Doedoedoe")

        friends = mommy.make(models.RelationshipType, name="Fiends")

        models.Relationship.objects.create(contact1=john, contact2=ringo, relationship_type=friends)

        url = reverse('search')

        tomorrow = date.today() + timedelta(1)
        data = {"gr0-_-contacts_by_relationship_dates-_-0": '{0} {0}'.format(tomorrow.strftime("%d/%m/%Y"))}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, john.lastname)
        self.assertNotContains(response, ringo.lastname)
        self.assertNotContains(response, doe.lastname)
