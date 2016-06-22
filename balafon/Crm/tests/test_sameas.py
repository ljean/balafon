# -*- coding: utf-8 -*-
"""unit testing"""

from cStringIO import StringIO
import json
import sys

from django.core import management
from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class AddSameAsTest(BaseTestCase):
    """Test add same as contact : several contact for a same person"""

    def test_add_same_as(self):
        """add a same as: only 1"""
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 2)

    def test_add_same_as_list(self):
        """add a same as several people"""
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, entity=entity2, firstname="Ringo", lastname="Star")

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertNotContains(response, entity1)
        self.assertContains(response, contact2.lastname)
        self.assertContains(response, entity2)

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact3.id})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, None)


class SameAsSuggestionTest(BaseTestCase):
    """Test add same as contact : several contact for a same person"""

    def test_suggestion_list(self):
        """check that contact with same name are suggested"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(1, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertTrue(contact2.id in ids)
        self.assertFalse(contact3.id in ids)

    def test_suggestion_emails(self):
        """check that contact with same email are suggested"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon", email="contact@beatles.com")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star", email="contact@beatles.com")
        contact4 = mommy.make(models.Contact, firstname="Gallagher", lastname="Noel")

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(2, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertTrue(contact2.id in ids)
        self.assertTrue(contact3.id in ids)
        self.assertFalse(contact4.id in ids)

    def test_suggestion_entity_emails(self):
        """check that contact inside an entity with same email are suggested"""
        beatles = mommy.make(models.Entity, email="contact@beatles.com")
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon", email="contact@beatles.com")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star", email="contact@beatles.com")
        contact4 = mommy.make(models.Contact, firstname="Gallagher", lastname="Noel")
        contact5 = mommy.make(models.Contact, entity=beatles, firstname="Georges", lastname="Harrison")
        contact6 = beatles.default_contact

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(4, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertTrue(contact2.id in ids)
        self.assertTrue(contact3.id in ids)
        self.assertFalse(contact4.id in ids)
        self.assertTrue(contact5.id in ids)
        self.assertTrue(contact6.id in ids)

    def test_suggestion_list_two_choices(self):
        """test suggestion several choices"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(2, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertTrue(contact2.id in ids)
        self.assertFalse(contact3.id in ids)
        self.assertTrue(contact4.id in ids)

    def test_suggestion_list_two_choices_existing_same_as(self):
        """test suggestions with existing same as"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for contact in [contact1, contact2]:
            contact.same_as = same_as
            contact.save()

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        ids = [int(x["value"]) for x in soup.select("select option")]
        self.assertEqual(1, len(ids))
        self.assertFalse(contact1.id in ids)
        self.assertFalse(contact2.id in ids)
        self.assertFalse(contact3.id in ids)
        self.assertTrue(contact4.id in ids)

    def test_suggestion_list_two_choices_existing_same_as_with_all(self):
        """suggestions when all are already set as same_as"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for contact in [contact1, contact2, contact4]:
            contact.same_as = same_as
            contact.save()

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('select')))

    def test_suggestion_list_no_homonymous(self):
        """test suggestion without hononymous"""
        mommy.make(models.Contact, firstname="John", lastname="Lennon")
        mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="Ringo", lastname="Star")
        mommy.make(models.Contact, firstname="John", lastname="Lennon")

        url = reverse("crm_same_as", args=[contact3.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('select')))


class SameAsPriorityTest(BaseTestCase):
    """Test change the priority between contacts"""

    def test_make_main_view(self):
        """view make main contact"""
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")

        url = reverse("crm_same_as", args=[contact1.id])
        response = self.client.post(url, data={'contact': contact2.id})
        self.assertEqual(200, response.status_code)

        url = reverse("crm_make_main_contact", args=[contact1.id, contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 2)

    def test_make_main_post(self):
        """make main contact"""
        entity1 = mommy.make(models.Entity, name="Toto")
        entity2 = mommy.make(models.Entity, name="Titi")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_make_main_contact", args=[contact2.id, contact1.id])

        response = self.client.post(url, data={'priority': 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(contact2.get_absolute_url()),
        )

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 2)
        self.assertEqual(contact2.same_as_priority, 1)

    def test_make_main_post_several_lower(self):
        """make main contact"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2, contact3, contact4]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_make_main_contact", args=[contact2.id, contact3.id])

        response = self.client.post(url, data={'priority': 1})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(contact2.get_absolute_url()),
        )

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        contact4 = models.Contact.objects.get(id=contact4.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact3.same_as, contact1.same_as)
        self.assertEqual(contact4.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 2)
        self.assertEqual(contact2.same_as_priority, 3)
        self.assertEqual(contact3.same_as_priority, 1)
        self.assertEqual(contact4.same_as_priority, 4)

    def test_make_main_post_several_lower2(self):
        """make main contact"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact5 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2, contact3, contact4, contact5]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_make_main_contact", args=[contact1.id, contact4.id])

        response = self.client.post(url, data={'priority': 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(contact1.get_absolute_url()),
        )

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        contact4 = models.Contact.objects.get(id=contact4.id)
        contact5 = models.Contact.objects.get(id=contact5.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact3.same_as, contact1.same_as)
        self.assertEqual(contact4.same_as, contact1.same_as)
        self.assertEqual(contact5.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 3)
        self.assertEqual(contact3.same_as_priority, 4)
        self.assertEqual(contact4.same_as_priority, 2)
        self.assertEqual(contact5.same_as_priority, 5)

    def test_make_main_post_several_higher(self):
        """make main contact"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2, contact3, contact4]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_make_main_contact", args=[contact2.id, contact1.id])

        response = self.client.post(url, data={'priority': 3})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(contact2.get_absolute_url()),
        )

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        contact4 = models.Contact.objects.get(id=contact4.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact3.same_as, contact1.same_as)
        self.assertEqual(contact4.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 3)
        self.assertEqual(contact2.same_as_priority, 1)
        self.assertEqual(contact3.same_as_priority, 2)
        self.assertEqual(contact4.same_as_priority, 4)

    def test_make_main_post_several_higher2(self):
        """make main contact"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact4 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact5 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2, contact3, contact4, contact5]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_make_main_contact", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'priority': 4})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.content,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(contact1.get_absolute_url()),
        )

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)
        contact4 = models.Contact.objects.get(id=contact4.id)
        contact5 = models.Contact.objects.get(id=contact5.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact3.same_as, contact1.same_as)
        self.assertEqual(contact4.same_as, contact1.same_as)
        self.assertEqual(contact5.same_as, contact1.same_as)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 4)
        self.assertEqual(contact3.same_as_priority, 2)
        self.assertEqual(contact4.same_as_priority, 3)
        self.assertEqual(contact5.same_as_priority, 5)

    def test_make_main_invalid(self):
        """make main contact : invalid priority value"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact2, contact3, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_make_main_contact", args=[contact2.id, contact1.id])

        response = self.client.post(url, data={'priority': 10})
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select(".field-error")))

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, models.SameAs.objects.all()[0])
        self.assertEqual(contact2.same_as, contact1.same_as)
        self.assertEqual(contact3.same_as, contact1.same_as)
        self.assertEqual(contact2.same_as_priority, 1)
        self.assertEqual(contact3.same_as_priority, 2)
        self.assertEqual(contact1.same_as_priority, 3)


class RemoveSameAsTest(BaseTestCase):
    """Test remove same as contact : several contact for a same person"""

    def test_remove_same_as_two_clones(self):
        """remove same as: no main"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact1.same_as_priority, 0)
        self.assertEqual(contact2.same_as_priority, 0)

    def test_remove_same_as_two_clones_prio1(self):
        """remove same as: main exists"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2]):
            contact.same_as = same_as
            contact.same_as_priority = 2 - priority
            contact.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact1.same_as_priority, 0)
        self.assertEqual(contact2.same_as_priority, 0)

    def test_remove_same_as_three_clones(self):
        """remove same_as when several clones"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2, contact3]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 0)
        self.assertEqual(contact3.same_as_priority, 2)

    def test_remove_same_as_three_clones_prio1(self):
        """remove same_as when several clones with a main one"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact2, contact3, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(contact1.same_as_priority, 2)
        self.assertEqual(contact2.same_as_priority, 0)
        self.assertEqual(contact3.same_as_priority, 1)

    def test_remove_same_as_three_clones_prio2(self):
        """remove same_as when several clones with main, remove other"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact3, contact2, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(contact1.same_as_priority, 2)
        self.assertEqual(contact2.same_as_priority, 0)
        self.assertEqual(contact3.same_as_priority, 1)

    def test_remove_same_as_not_same(self):
        """remove same as. a contact is not member"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(404, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as, None)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact1.same_as_priority, 0)
        self.assertEqual(contact2.same_as_priority, 0)

    def test_remove_same_as_not_in_same_as(self):
        """remove same as. Same name but not in same as"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()
        same_as.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact3.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(404, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact3.same_as, None)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 2)
        self.assertEqual(contact3.same_as_priority, 0)

    def test_remove_same_as_not_in_same_as_2(self):
        """remove same as. Same name but not in same as: reverse link"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact1, contact2]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()
        same_as.save()

        url = reverse("crm_remove_same_as", args=[contact3.id, contact1.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(404, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact3.same_as, None)
        self.assertEqual(contact1.same_as_priority, 1)
        self.assertEqual(contact2.same_as_priority, 2)
        self.assertEqual(contact3.same_as_priority, 0)

    def test_remove_same_as_three_clones_prio3(self):
        """remove same as three clones: main contact is the last one"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact3, contact2, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()
        same_as.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={'confirm': 1})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, None)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(contact1.same_as_priority, 2)
        self.assertEqual(contact2.same_as_priority, 0)
        self.assertEqual(contact3.same_as_priority, 1)

    def test_remove_same_as_cancel(self):
        """cancel removing same_as"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact3, contact2, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()
        same_as.save()

        url = reverse("crm_remove_same_as", args=[contact1.id, contact2.id])

        response = self.client.post(url, data={})
        self.assertEqual(200, response.status_code)

        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)
        contact3 = models.Contact.objects.get(id=contact3.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 3)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact3.same_as, same_as)
        self.assertEqual(contact1.same_as_priority, 3)
        self.assertEqual(contact2.same_as_priority, 2)
        self.assertEqual(contact3.same_as_priority, 1)

    def test_delete_same_as_contact(self):
        """The same as is updated when we delete one of the orther contacts (1 remaining)"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact3 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact3, contact2, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()
        same_as.save()

        contact3.delete()
        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        self.assertEqual(1, models.SameAs.objects.count())
        same_as = models.SameAs.objects.all()[0]
        self.assertEqual(same_as.contact_set.count(), 2)
        self.assertEqual(contact1.same_as, same_as)
        self.assertEqual(contact2.same_as, same_as)
        self.assertEqual(contact1.same_as_priority, 2)
        self.assertEqual(contact2.same_as_priority, 1)

    def test_delete_same_as_contact_last_one(self):
        """The same is deleted if we delete the other contact"""
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="John", lastname="Lennon")

        same_as = models.SameAs.objects.create()
        for priority, contact in enumerate([contact2, contact1]):
            contact.same_as = same_as
            contact.same_as_priority = priority + 1
            contact.save()
        same_as.save()

        contact2.delete()
        # refresh
        contact1 = models.Contact.objects.get(id=contact1.id)

        self.assertEqual(0, models.SameAs.objects.count())
        self.assertEqual(contact1.same_as_priority, 0)



class FindSameAsTest(BaseTestCase):

    def test_find_same_as(self):

        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")

        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))

    def test_find_same_as_with_group(self):

        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")

        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', "SameAs", verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))
        qs = models.Group.objects.filter(name="SameAs")
        self.assertEqual(1, qs.count())
        self.assertEqual(qs[0].contacts.count(), 2)
        self.assertFalse(contact1 in qs[0].contacts.all())
        self.assertTrue(contact2 in qs[0].contacts.all())
        self.assertTrue(contact3 in qs[0].contacts.all())

    def test_find_same_as_with_existing_group(self):

        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")

        gr = models.Group.objects.create(name="SameAs")
        gr.contacts.add(contact1)
        gr.save()

        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', "SameAs", verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))

        qs = models.Group.objects.filter(name="SameAs")
        self.assertEqual(1, qs.count())
        self.assertEqual(qs[0].contacts.count(), 3)
        self.assertTrue(contact1 in qs[0].contacts.all())
        self.assertTrue(contact2 in qs[0].contacts.all())
        self.assertTrue(contact3 in qs[0].contacts.all())

    def test_find_same_as_with_no_name(self):

        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact3 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        contact4 = mommy.make(models.Contact, firstname="", lastname="")
        contact5 = mommy.make(models.Contact, firstname="", lastname="")

        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('find_same_as', "SameAs", verbosity=0, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        self.assertEqual(2, len(buf.readlines()))

        qs = models.Group.objects.filter(name="SameAs")
        self.assertEqual(1, qs.count())
        self.assertEqual(qs[0].contacts.count(), 2)
        self.assertFalse(contact1 in qs[0].contacts.all())
        self.assertTrue(contact2 in qs[0].contacts.all())
        self.assertTrue(contact3 in qs[0].contacts.all())
        self.assertFalse(contact4 in qs[0].contacts.all())
        self.assertFalse(contact5 in qs[0].contacts.all())


class SameAsSuggestionApiTest(BaseTestCase):
    """Return json list with Same_as contact"""

    def test_empty(self):
        """it should return empty list"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'lastname': 'Solo'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(0, len(resp_data))

    def test_lastname(self):
        """it should return list with 1 contact"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'lastname': 'Skywalker'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)

        self.assertEqual(1, len(resp_data))
        self.assertEqual(resp_data[0]['id'], contact2.id)
        self.assertNotEqual(resp_data[0]['fullname'], '')

    def test_fullname(self):
        """it should return list with 1 contact"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'lastname': 'Skywalker',
            'firstname': 'Luke'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(1, len(resp_data))
        self.assertEqual(resp_data[0]['id'], contact1.id)
        self.assertNotEqual(resp_data[0]['fullname'], '')

    def test_email(self):
        """it should return list with 2 contacts"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'lastname': 'Skywalker',
            'firstname': '',
            'email': 'luke@starwars.com'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(2, len(resp_data))
        resp_data = sorted(resp_data, key=lambda contact: contact['id'])
        self.assertEqual(resp_data[0]['id'], contact1.id)
        self.assertNotEqual(resp_data[0]['fullname'], '')
        self.assertEqual(resp_data[1]['id'], contact2.id)
        self.assertNotEqual(resp_data[1]['fullname'], '')

    def test_only_email(self):
        """it should return list with 1 contact"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'lastname': '',
            'firstname': '',
            'email': 'luke@starwars.com'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(1, len(resp_data))
        resp_data = sorted(resp_data, key=lambda contact: contact['id'])
        self.assertEqual(resp_data[0]['id'], contact1.id)
        self.assertNotEqual(resp_data[0]['fullname'], '')


    def test_entity_email(self):
        """it should return contact based on entity email"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')
        entity.default_contact.delete()

        url = reverse('crm_same_as_suggestions')
        data = {
            'email': 'contact@starwars.com'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(1, len(resp_data))
        resp_data = sorted(resp_data, key=lambda contact: contact['id'])
        self.assertEqual(resp_data[0]['id'], contact2.id)
        self.assertNotEqual(resp_data[0]['fullname'], '')

    def test_ignore_existing(self):
        """it should not return the contact with the given id"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')
        contact3 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')

        url = reverse('crm_same_as_suggestions')
        data = {
            'id': contact3.id,
            'lastname': 'Skywalker',
            'firstname': '',
            'email': 'luke@starwars.com'
        }

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)
        resp_data = json.loads(response.content)
        self.assertEqual(2, len(resp_data))
        resp_data = sorted(resp_data, key=lambda contact: contact['id'])
        self.assertEqual(resp_data[0]['id'], contact1.id)
        self.assertNotEqual(resp_data[0]['fullname'], '')
        self.assertEqual(resp_data[1]['id'], contact2.id)
        self.assertNotEqual(resp_data[1]['fullname'], '')

    def test_anonymous(self):
        """it should return permission denied"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'id': contact1.id,
            'lastname': 'Skywalker',
            'firstname': '',
            'email': 'luke@starwars.com'
        }

        self.client.logout()

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)

    def test_not_allowed(self):
        """it should return permission denied"""
        entity = mommy.make(models.Entity, name='StarWars', email='contact@starwars.com')
        contact1 = mommy.make(models.Contact, lastname='Skywalker', firstname='Luke', email='luke@starwars.com')
        contact2 = mommy.make(models.Contact, entity=entity, lastname='Skywalker', firstname='', email='')

        url = reverse('crm_same_as_suggestions')
        data = {
            'id': contact1.id,
            'lastname': 'Skywalker',
            'firstname': '',
            'email': 'luke@starwars.com'
        }

        self.user.is_staff = False
        self.user.save()

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)
