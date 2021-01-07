# -*- coding: utf-8 -*-
"""test create newsletter"""

from django.contrib.sites.models import Site
from django.urls import reverse

from model_mommy import mommy
from coop_cms.models import Newsletter
from coop_cms.settings import get_newsletter_templates

from balafon.Emailing.tests import BaseTestCase


class AddNewsletterTest(BaseTestCase):

    def test_view_newsletter(self):
        url = reverse("emailing_new_newsletter")
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Newsletter.objects.count(), 0)

    def test_create_newsletter(self):
        url = reverse("emailing_new_newsletter")
        site1 = Site.objects.get_current()
        site2 = mommy.make(Site)
        templates = get_newsletter_templates(None, None)
        data = {
            "subject": "test",
            "template": templates[0][0],
            'site': site2.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Newsletter.objects.count(), 1)
        newsletter = Newsletter.objects.all()[0]
        self.assertEqual(newsletter.subject, data["subject"])
        self.assertEqual(newsletter.template, data["template"])
        self.assertEqual(newsletter.site, site2)
