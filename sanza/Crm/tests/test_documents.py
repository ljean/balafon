# -*- coding: utf-8 -*-
"""unit testing"""
from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from coop_cms.settings import is_perm_middleware_installed
from model_mommy import mommy

from sanza.Crm import models
from sanza.Crm.tests import BaseTestCase


class ActionDocumentTestCase(BaseTestCase):

    def test_new_document_edit(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        self.assertNotEqual(a.actiondocument, None)

    def test_new_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        self.assertNotEqual(a.actiondocument, None)

    def test_no_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        a = models.Action.objects.get(id=a.id)
        try:
            doc = a.actiondocument
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)

    def test_no_document_edit(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)
        a = models.Action.objects.get(id=a.id)
        try:
            doc = a.actiondocument
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)

    def test_no_document_pdf(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)

    def test_no_type_view(self):
        c = mommy.make(models.Contact)
        a = mommy.make(models.Action, type=None)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)

        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)

        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(404, response.status_code)

        a = models.Action.objects.get(id=a.id)
        try:
            doc = a.actiondocument
            exception_raised = False
        except models.ActionDocument.DoesNotExist:
            exception_raised = True
        self.assertEqual(exception_raised, True)

    def test_view_document_view(self):
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        #Create
        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        a = models.Action.objects.get(id=a.id)
        a.actiondocument.content = "This is a test for document actions"
        a.actiondocument.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, a.actiondocument.content)

        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, a.actiondocument.content)

    def _check_anonymous_not_allowed(self, response, url):
        if is_perm_middleware_installed():
            self.assertEqual(302, response.status_code)
            auth_url = reverse("auth_login")
            self.assertRedirects(response, auth_url+'?next='+url)
        else:
            self.assertEqual(403, response.status_code)

    def test_anonymous_document_view(self):
        self.client.logout()
        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        url = reverse('crm_edit_action_document', args=[a.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)

        url = reverse('crm_view_action_document', args=[a.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)

        url = reverse('crm_pdf_action_document', args=[a.id])
        response = self.client.get(url)
        self._check_anonymous_not_allowed(response, url)

    def test_not_staff_document_view(self):
        self.client.logout()

        user = User.objects.create(username="titi", is_staff=False, is_active=True)
        user.set_password("abc")
        user.save()
        self.client.login(username="titi", password="abc")

        c = mommy.make(models.Contact)
        at = mommy.make(models.ActionType, default_template="documents/standard_letter.html")
        a = mommy.make(models.Action, type=at)
        a.contacts.add(c)
        a.save()

        response = self.client.get(reverse('crm_edit_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)

        response = self.client.get(reverse('crm_view_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)

        response = self.client.get(reverse('crm_pdf_action_document', args=[a.id]))
        self.assertEqual(403, response.status_code)
