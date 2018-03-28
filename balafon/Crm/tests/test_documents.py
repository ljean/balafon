# -*- coding: utf-8 -*-
"""unit testing"""

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from coop_cms.settings import is_perm_middleware_installed
from model_mommy import mommy

from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class ActionDocumentTestCase(BaseTestCase):
    """Test action document"""

    def test_new_document_edit(self):
        """edit a new document"""
        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact)
        action.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)
        action = models.Action.objects.get(id=action.id)
        self.assertNotEqual(action.actiondocument, None)

    def test_new_document_view(self):
        """view a new document"""
        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact)
        action.save()

        response = self.client.get(reverse('crm_view_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)
        action = models.Action.objects.get(id=action.id)
        self.assertNotEqual(action.actiondocument, None)

    def test_no_document_view(self):
        """view action document when no document is associated"""
        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact)
        action.save()

        response = self.client.get(reverse('crm_view_action_document', args=[action.id]))
        self.assertEqual(404, response.status_code)
        action = models.Action.objects.get(id=action.id)
        try:
            action.actiondocument  # pylint: disable=pointless-statement
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)

    def test_no_document_edit(self):
        """edit action document when no document is associated"""
        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact)
        action.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(404, response.status_code)
        action = models.Action.objects.get(id=action.id)
        try:
            action.actiondocument  # pylint: disable=pointless-statement
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)

    def test_no_document_pdf(self):
        """pdf of action document when no document is associated"""
        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact)
        action.save()

        response = self.client.get(reverse('crm_pdf_action_document', args=[action.id]))
        self.assertEqual(404, response.status_code)

    def test_no_type_view(self):
        """view action document when no type is associated"""
        contact = mommy.make(models.Contact)
        action = mommy.make(models.Action, type=None)
        action.contacts.add(contact)
        action.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(404, response.status_code)

        response = self.client.get(reverse('crm_view_action_document', args=[action.id]))
        self.assertEqual(404, response.status_code)

        response = self.client.get(reverse('crm_pdf_action_document', args=[action.id]))
        self.assertEqual(404, response.status_code)

        action = models.Action.objects.get(id=action.id)
        try:
            action.actiondocument  # pylint: disable=pointless-statement
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)

    def test_view_document_view(self):
        """view action document"""

        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        action = mommy.make(models.Action, type=action_type)
        action.contacts.add(contact)
        action.save()

        #Create
        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)
        action = models.Action.objects.get(id=action.id)
        action.actiondocument.content = "This is a test for document actions"
        action.actiondocument.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, action.actiondocument.content)

        response = self.client.get(reverse('crm_view_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, action.actiondocument.content)

    def _check_anonymous_not_allowed(self, response, url):
        """helper to check that anonymous user can not access"""
        if is_perm_middleware_installed():
            self.assertEqual(302, response.status_code)
            auth_url = reverse("auth_login")
            self.assertRedirects(response, auth_url+'?next='+url)
        else:
            self.assertEqual(403, response.status_code)

    def test_anonymous_document_view(self):
        """view action document as anonymous user"""

        contact = mommy.make(models.Contact)
        action_ype = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        action = mommy.make(models.Action, type=action_ype)
        action.contacts.add(contact)
        action.save()

        # Make sure that this document is created
        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)

        # logout user
        self.client.logout()

        url = reverse('crm_pdf_action_document', args=[action.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)

        url = reverse('crm_edit_action_document', args=[action.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)

        url = reverse('crm_view_action_document', args=[action.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)

    def test_not_staff_document_view(self):
        """view action document as non-staff user"""

        contact = mommy.make(models.Contact)
        action_type = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        action = mommy.make(models.Action, type=action_type)

        action.contacts.add(contact)
        action.save()

        # Make sure that this document is created
        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(200, response.status_code)

        # change user
        self.client.logout()
        user = User.objects.create(username="titi", is_staff=False, is_active=True)
        user.set_password("abc")
        user.save()
        self.client.login(username="titi", password="abc")

        response = self.client.get(reverse('crm_pdf_action_document', args=[action.id]))
        self.assertEqual(403, response.status_code)

        response = self.client.get(reverse('crm_edit_action_document', args=[action.id]))
        self.assertEqual(403, response.status_code)

        response = self.client.get(reverse('crm_view_action_document', args=[action.id]))
        self.assertEqual(403, response.status_code)
