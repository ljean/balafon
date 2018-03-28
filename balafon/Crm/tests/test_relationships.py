# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class RelationshipTest(BaseTestCase):

    def test_view_add_relationship(self):
        entity1 = mommy.make(models.Entity, name="The Beatles")
        entity2 = mommy.make(models.Entity, name="Apple Records")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="Paul", lastname="McCartney")

        relation_type = mommy.make(models.RelationshipType, name="Partners")

        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, relation_type.name)

    def test_add_relationship(self):
        entity1 = mommy.make(models.Entity, name="The Beatles")
        entity2 = mommy.make(models.Entity, name="Apple Records")
        contact1 = mommy.make(models.Contact, entity=entity1, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, entity=entity2, firstname="Paul", lastname="McCartney")

        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")

        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': contact2.id, 'relationship_type': relation_type.id})
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])

        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        r = models.Relationship.objects.get(contact1=contact1, contact2=contact2)
        self.assertEqual(r.relationship_type, relation_type)

    def test_add_reversed_relationship(self):
        contact1 = mommy.make(models.Contact, firstname="Alex", lastname="Ferguson")
        contact2 = mommy.make(models.Contact, firstname="Eric", lastname="Cantona")

        relation_type = mommy.make(models.RelationshipType, name="Coach of", reverse="Player of")

        url = reverse("crm_add_relationship", args=[contact2.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, relation_type.name)
        self.assertContains(response, relation_type.reverse)

        response = self.client.post(url, data={'contact2': contact1.id, 'relationship_type': -relation_type.id})
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(list(errors), [])

        #refresh
        contact1 = models.Contact.objects.get(id=contact1.id)
        contact2 = models.Contact.objects.get(id=contact2.id)

        r = models.Relationship.objects.get(contact1=contact1, contact2=contact2)
        self.assertEqual(r.relationship_type, relation_type)

    def test_add_relationship_no_contact(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")

        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")

        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': '', 'relationship_type': relation_type.id})
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        self.assertEqual(0, models.Relationship.objects.filter(contact1=contact1, contact2=contact2).count())

    def test_add_relationship_no_type(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")

        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")

        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': contact2.id, 'relationship_type': ''})
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 1)

        self.assertEqual(0, models.Relationship.objects.filter(contact1=contact1, contact2=contact2).count())

    def test_add_relationship_invaliddata(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")

        relation_type = mommy.make(models.RelationshipType, name="Partners")
        mommy.make(models.RelationshipType, name="Friends")
        mommy.make(models.RelationshipType, name="Enemies")

        url = reverse("crm_add_relationship", args=[contact1.id])
        response = self.client.post(url, data={'contact2': "AAAA", 'relationship_type': 'ZZZZZ'})
        self.assertEqual(200, response.status_code)

        errors = BeautifulSoup(response.content).select('.field-error')
        self.assertEqual(len(errors), 2)

        self.assertEqual(0, models.Relationship.objects.filter(contact1=contact1, contact2=contact2).count())

    def test_get_relationship(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        relationship_type = mommy.make(models.RelationshipType, name="Partenaires")

        models.Relationship.objects.create(contact1=contact1, contact2=contact2, relationship_type=relationship_type)

        for r in contact1.get_relationships():
            self.assertEqual(r.contact, contact2)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.name)

        for r in contact2.get_relationships():
            self.assertEqual(r.contact, contact1)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.name)

    def test_get_relationship_with_reverse(self):
        contact1 = mommy.make(models.Contact, firstname="John", lastname="Lennon")
        contact2 = mommy.make(models.Contact, firstname="Paul", lastname="McCartney")
        relationship_type = mommy.make(models.RelationshipType, name="Parain", reverse="Filleul")

        models.Relationship.objects.create(contact1=contact1, contact2=contact2, relationship_type=relationship_type)

        for r in contact1.get_relationships():
            self.assertEqual(r.contact, contact2)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.name)

        for r in contact2.get_relationships():
            self.assertEqual(r.contact, contact1)
            self.assertEqual(r.type, relationship_type)
            self.assertEqual(r.type_name, relationship_type.reverse)

    def test_view_relationships(self):
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker")
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")
        leia = mommy.make(models.Contact, firstname="Leia", lastname="Princess")
        ian = mommy.make(models.Contact, firstname="Ian", lastname="Solo")
        chewe = mommy.make(models.Contact, firstname="Chewbacca")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")
        father = mommy.make(models.RelationshipType, name="Father", reverse="Child")
        friends = mommy.make(models.RelationshipType, name="Friend")

        models.Relationship.objects.create(contact1=anakin, contact2=luke, relationship_type=father)
        models.Relationship.objects.create(contact1=anakin, contact2=leia, relationship_type=father)
        models.Relationship.objects.create(contact1=obi, contact2=luke, relationship_type=master)
        models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)
        models.Relationship.objects.create(contact1=luke, contact2=ian, relationship_type=friends)
        models.Relationship.objects.create(contact1=chewe, contact2=luke, relationship_type=friends)

        response = self.client.get(reverse("crm_view_contact", args=[luke.id]))
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select("table tr.relationship")), 4)# 4 + title
        self.assertEqual(len(soup.select(".add-relation")), 1) # add button is enabled

        self.assertContains(response, anakin.fullname)
        self.assertContains(response, obi.fullname)
        self.assertContains(response, ian.fullname)
        self.assertContains(response, chewe.fullname)
        self.assertNotContains(response, leia.fullname)

    def test_view_relations_disabeld(self):
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker")

        response = self.client.get(reverse("crm_view_contact", args=[luke.id]))
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select("table.contact-relationships")), 0)
        self.assertEqual(len(soup.select(".add-relation")), 0)# add button is disabled

    def test_view_no_relations(self):
        luke = mommy.make(models.Contact, firstname="Luke", lastname="Skywalker")
        friends = mommy.make(models.RelationshipType, name="Friend")

        response = self.client.get(reverse("crm_view_contact", args=[luke.id]))
        soup = BeautifulSoup(response.content)

        self.assertEqual(len(soup.select("table.contact-relationships")), 0)
        self.assertEqual(len(soup.select(".add-relation")), 1)# add button is disabled

    def test_view_delete_relationship(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")

        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)

        response = self.client.get(reverse("crm_delete_relationship", args=[obi.id, r.id]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(1, models.Relationship.objects.filter(id=r.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=obi.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=anakin.id).count())

    def test_cancel_delete_relationship(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")

        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)

        response = self.client.post(
            reverse("crm_delete_relationship", args=[obi.id, r.id]), {})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(1, models.Relationship.objects.filter(id=r.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=obi.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=anakin.id).count())


    def test_delete_relationship(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")

        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)

        response = self.client.post(
            reverse("crm_delete_relationship", args=[obi.id, r.id]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(0, models.Relationship.objects.filter(id=r.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=obi.id).count())
        self.assertEqual(1, models.Contact.objects.filter(id=anakin.id).count())

    def test_delete_unknown_relationship(self):
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")

        response = self.client.get(
            reverse("crm_delete_relationship", args=[obi.id, 100]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("crm_delete_relationship", args=[obi.id, 100]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)

    def test_delete_relationship_unknown_contact(self):
        anakin = mommy.make(models.Contact, firstname="Anakin", lastname="Skywalker")
        obi = mommy.make(models.Contact, firstname="Obi-Wan", lastname="Kenobi")

        master = mommy.make(models.RelationshipType, name="Master", reverse="Padawan")

        r = models.Relationship.objects.create(contact1=obi, contact2=anakin, relationship_type=master)

        response = self.client.post(
            reverse("crm_delete_relationship", args=[8765, r.id]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("crm_delete_relationship", args=[8755, r.id]), {'confirm': 1})
        self.assertEqual(response.status_code, 200)
