# -*- coding: utf-8 -*-
"""test email sending"""

from datetime import datetime
from unittest import skipIf

from django.conf import settings
from django.contrib.sites.models import Site
from django.core import management
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.translation import activate

from coop_cms.models import Newsletter
from coop_cms.settings import is_localized, is_multilang
from coop_cms.tests.test_newsletter import NewsletterTest as BaseNewsletterTest
from coop_cms.utils import get_url_in_language
from model_mommy import mommy

from balafon.Crm import models
from balafon.Emailing.models import Emailing, MagicLink
from balafon.Emailing.tests import BaseTestCase


class SendEmailingTest(BaseTestCase):

    def setUp(self):
        activate(settings.LANGUAGES[0][0])
        super(SendEmailingTest, self).setUp()
        settings.COOP_CMS_FROM_EMAIL = 'toto@toto.fr'
        settings.COOP_CMS_REPLY_TO = 'titi@toto.fr'

        site = Site.objects.get_current()
        site.domain = settings.COOP_CMS_SITE_PREFIX
        site.save()

    def tearDown(self):
        activate(settings.LANGUAGES[0][0])

    @override_settings(COOP_CMS_REPLY_TO="")
    def test_send_newsletter(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact, entity=entity,
                email=name+'@toto.fr', lastname=name.capitalize()
            ) for name in names
        ]

        content = '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a>'
        content += '<a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>'

        newsletter_data = {
            'subject': 'This is the subject',
            'content': content,
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=mommy.make(models.SubscriptionType, site=site)
        )

        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        # check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)

        for email, contact in zip(outbox, contacts):
            viewonline_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_view_online', args=[emailing.id, contact.uuid]
            )
            unsubscribe_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_unregister', args=[emailing.id, contact.uuid]
            )

            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
            self.assertEqual(email.subject, newsletter_data['subject'])
            self.assertTrue(email.body.find(entity.name) >= 0)
            self.assertEqual(email.extra_headers.get('Reply-To', ''), '')
            self.assertEqual(
                email.extra_headers['List-Unsubscribe'],
                '<{0}>, <mailto:{1}?subject=unsubscribe>'.format(unsubscribe_url, email.from_email)
            )

            self.assertTrue(email.body.find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][1], "text/html")

            self.assertTrue(email.alternatives[0][0].find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][0].find(entity.name) >= 0)
            self.assertTrue(email.alternatives[0][0].find(viewonline_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url) >= 0)
            # Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.fr") > 0)
            # Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1") > 0)

            # check magic links
            self.assertTrue(MagicLink.objects.count() > 0)

            # check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)

    @skipIf(len(settings.LANGUAGES) < 2, "LANGUAGES less than 2")
    @override_settings(COOP_CMS_REPLY_TO="")
    def test_send_newsletter_language(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact, entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize(),
                firstname=name,
            ) for name in names
        ]

        origin_lang = settings.LANGUAGES[0][0]
        trans_lang = settings.LANGUAGES[1][0]

        content = '<h2>Hello #!-fullname-!#!</h2><p>{0}Visit <a href="http://toto.{0}">{0}</a>'
        content += '<a href="mailto:me@me.{0}">mailme</a><a href="#art1">internal link</a></p>'

        newsletter_data = {
            'subject_'+origin_lang: 'This is the {0} subject'.format(origin_lang),
            'subject_'+trans_lang: 'This is the {0} subject'.format(trans_lang),
            'content_'+origin_lang: content.format(origin_lang, ),
            'content_'+trans_lang: content.format(trans_lang),
            'template': 'test/newsletter_contact_lang.html'
        }

        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=mommy.make(models.SubscriptionType, site=site),
            lang=trans_lang
        )

        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)

        activate(trans_lang)
        for email, contact in zip(outbox, contacts):
            viewonline_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_view_online', args=[emailing.id, contact.uuid]
            )
            unsubscribe_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_unregister', args=[emailing.id, contact.uuid]
            )

            view_en_url = reverse("emailing_view_online_lang", args=[emailing.id, contact.uuid, 'en'])

            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
            self.assertEqual(email.subject, newsletter_data['subject_'+trans_lang])
            self.assertTrue(email.body.find(entity.name) >= 0)
            #print email.body
            self.assertEqual(email.extra_headers.get('Reply-To', ''), '')
            self.assertEqual(
                email.extra_headers['List-Unsubscribe'],
                '<{0}>, <mailto:{1}?subject=unsubscribe>'.format(unsubscribe_url, email.from_email)
            )
            self.assertTrue(email.body.find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][1], "text/html")

            self.assertTrue(email.alternatives[0][0].find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][0].find(entity.name) >= 0)
            #Check links are not magic
            self.assertTrue(email.alternatives[0][0].find(viewonline_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(view_en_url) >= 0)
            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.{0}".format(trans_lang)) > 0)
            #Check internal links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1") > 0)

            #check magic links
            self.assertTrue(MagicLink.objects.count() > 0)

            #check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)

    @skipIf(len(settings.LANGUAGES) < 2, "LANGUAGES less than 2")
    @override_settings(COOP_CMS_REPLY_TO="")
    def test_send_newsletter_contact_language(self):
        """test that we use the favorite language of the contact when sending him a newsletter"""

        entity = mommy.make(models.Entity, name="my corp")

        origin_lang = settings.LANGUAGES[0][0]
        trans_lang = settings.LANGUAGES[1][0]

        names = ['alpha', 'beta', 'gamma']
        langs = ['', origin_lang, trans_lang]

        contacts = [
            mommy.make(
                models.Contact,
                entity=entity,
                email=name+'@toto.fr',
                lastname=name.capitalize(),
                firstname=name,
                favorite_language=lang
            ) for (name, lang) in zip(names, langs)
        ]

        content = '<h2>Hello #!-fullname-!#!</h2><p>{0}Visit <a href="http://toto.{0}">{0}</a>'
        content += '<a href="mailto:me@me.{0}">mailme</a><a href="#art1">internal link</a></p>'

        newsletter_data = {
            'subject_'+origin_lang: 'This is the {0} subject'.format(origin_lang),
            'subject_'+trans_lang: 'This is the {0} subject'.format(trans_lang),
            'content_'+origin_lang: content.format(origin_lang),
            'content_'+trans_lang: content.format(trans_lang),
            'template': 'test/newsletter_contact.html'
        }

        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=mommy.make(models.SubscriptionType, site=site),
            lang=''
        )

        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        activate(origin_lang)

        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda email: email.to)
        contacts.sort(key=lambda contact: contact.get_email)

        activate(trans_lang)
        for email, contact, lang in zip(outbox, contacts, langs):
            viewonline_url = reverse(
                'emailing_view_online', args=[emailing.id, contact.uuid]
            )

            unsubscribe_url = reverse(
                'emailing_unregister', args=[emailing.id, contact.uuid]
            )

            contact_lang = lang or origin_lang
            viewonline_url = get_url_in_language(viewonline_url, contact_lang)
            unsubscribe_url = get_url_in_language(unsubscribe_url, contact_lang)

            viewonline_url = emailing.get_domain_url_prefix() + viewonline_url
            unsubscribe_url = emailing.get_domain_url_prefix() + unsubscribe_url

            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)

            self.assertEqual(email.subject, newsletter_data['subject_'+contact_lang])
            self.assertTrue(email.body.find(entity.name) >= 0)
            #print email.body
            self.assertEqual(email.extra_headers.get('Reply-To', ''), '')
            self.assertEqual(
                email.extra_headers['List-Unsubscribe'],
                '<{0}>, <mailto:{1}?subject=unsubscribe>'.format(unsubscribe_url, email.from_email)
            )
            self.assertTrue(email.body.find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][1], "text/html")

            self.assertTrue(email.alternatives[0][0].find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][0].find(entity.name) >= 0)
            self.assertTrue(email.alternatives[0][0].find(viewonline_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url) >= 0)
            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.{0}".format(contact_lang)) > 0)
            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1") > 0)

            #check magic links
            self.assertTrue(MagicLink.objects.count() > 0)

            #check an action has been created
            contact = models.Contact.objects.get(id=contact.id)
            self.assertEqual(contact.action_set.count(), 1)
            self.assertEqual(contact.action_set.all()[0].subject, email.subject)

    @override_settings(COOP_CMS_REPLY_TO="reply_to@toto.fr")
    def test_send_newsletter_reply_to(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact, entity=entity,
                email=name+'@toto.fr', lastname=name.capitalize()
            ) for name in names
        ]

        content = '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a>'
        content += '<a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>'

        newsletter_data = {
            'subject': 'This is the subject',
            'content': content,
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=mommy.make(models.SubscriptionType, site=site)
        )

        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)

        for email, contact in zip(outbox, contacts):
            viewonline_url = reverse(
                'emailing_view_online', args=[emailing.id, contact.uuid]
            )

            unsubscribe_url = reverse(
                'emailing_unregister', args=[emailing.id, contact.uuid]
            )

            viewonline_url = emailing.get_domain_url_prefix() + viewonline_url
            unsubscribe_url = emailing.get_domain_url_prefix() + unsubscribe_url

            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)
            self.assertEqual(email.subject, newsletter_data['subject'])
            self.assertTrue(email.body.find(entity.name) >= 0)
            #print email.body
            self.assertEqual(email.extra_headers['Reply-To'], settings.COOP_CMS_REPLY_TO)
            self.assertEqual(
                email.extra_headers['List-Unsubscribe'],
                '<{0}>, <mailto:{1}?subject=unsubscribe>'.format(unsubscribe_url, settings.COOP_CMS_REPLY_TO)
            )
            self.assertTrue(email.body.find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][0].find(entity.name) >= 0)
            self.assertTrue(email.alternatives[0][0].find(viewonline_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url) >= 0)

            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.fr") > 0)

            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1") > 0)

            #check magic links
            self.assertTrue(MagicLink.objects.count() > 0)

            #check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)

    @override_settings(COOP_CMS_REPLY_TO="")
    def test_send_newsletter_from_email(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact, entity=entity,
                email=name+'@toto.fr', lastname=name.capitalize()
            ) for name in names
        ]

        content = '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a>'
        content += '<a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>'

        newsletter_data = {
            'subject': 'This is the subject',
            'content': content,
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=mommy.make(models.SubscriptionType, site=site),
            from_email="abcd@defg.fr"
        )

        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)

        for email, contact in zip(outbox, contacts):
            viewonline_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_view_online', args=[emailing.id, contact.uuid]
            )
            unsubscribe_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_unregister', args=[emailing.id, contact.uuid]
            )

            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, emailing.from_email)
            self.assertEqual(email.subject, newsletter_data['subject'])
            self.assertTrue(email.body.find(entity.name) >= 0)
            #print email.body
            self.assertEqual(
                email.extra_headers['List-Unsubscribe'],
                '<{0}>, <mailto:{1}?subject=unsubscribe>'.format(unsubscribe_url, emailing.from_email)
            )
            self.assertTrue(email.body.find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][0].find(entity.name) >= 0)
            self.assertTrue(email.alternatives[0][0].find(viewonline_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url) >= 0)

            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.fr") > 0)

            #Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1") > 0)

            #check magic links
            self.assertTrue(MagicLink.objects.count() > 0)

            #check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)

    @override_settings(COOP_CMS_REPLY_TO="")
    def test_send_newsletter_check_unregister_name(self):

        entity = mommy.make(models.Entity, name="my corp")

        names = ['alpha', 'beta', 'gamma']
        contacts = [
            mommy.make(
                models.Contact, entity=entity,
                email=name + '@toto.fr', lastname=name.capitalize()
            ) for name in names
            ]

        content = '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a>'
        content += '<a href="mailto:me@me.fr">mailme</a><a href="#art1">internal link</a></p>'

        newsletter_data = {
            'subject': 'This is the subject',
            'content': content,
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        subscription_1 = mommy.make(models.SubscriptionType, site=site, name="MY_COMPANY_#1")
        subscription_2 = mommy.make(models.SubscriptionType, site=site, name="MY_COMPANY_#2")

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=subscription_2,
            from_email="abcd@defg.fr"
        )

        for contact in contacts:
            emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        # check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))

        self.assertEqual(len(mail.outbox), len(contacts))

        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)

        for email, contact in zip(outbox, contacts):
            viewonline_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_view_online', args=[emailing.id, contact.uuid]
            )
            unsubscribe_url = emailing.get_domain_url_prefix() + reverse(
                'emailing_unregister', args=[emailing.id, contact.uuid]
            )

            self.assertFalse(email.body.find(subscription_1.name) >= 0)
            self.assertTrue(email.body.find(subscription_2.name) >= 0)

            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.from_email, emailing.from_email)
            self.assertEqual(email.subject, newsletter_data['subject'])
            self.assertTrue(email.body.find(entity.name) >= 0)
            # print email.body
            self.assertEqual(
                email.extra_headers['List-Unsubscribe'],
                '<{0}>, <mailto:{1}?subject=unsubscribe>'.format(unsubscribe_url, emailing.from_email)
            )
            self.assertTrue(email.body.find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(contact.fullname) >= 0)
            self.assertTrue(email.alternatives[0][0].find(entity.name) >= 0)
            self.assertTrue(email.alternatives[0][0].find(viewonline_url) >= 0)
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url) >= 0)

            # Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("mailto:me@me.fr") > 0)

            # Check mailto links are not magic
            self.assertTrue(email.alternatives[0][0].find("#art1") > 0)

            # check magic links
            self.assertTrue(MagicLink.objects.count() > 0)

            # check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)

    def test_view_magic_link(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity, email='toto@toto.fr', lastname='Toto')
        emailing = mommy.make(Emailing)
        emailing.sent_to.add(contact)
        emailing.save()

        link = "http://www.google.fr"
        magic_link = MagicLink.objects.create(emailing=emailing, url=link)

        response = self.client.get(reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid]))
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], link)

    def test_unregister_mailinglist(self):
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)
        third_party_subscription = mommy.make(models.SubscriptionType, name="3rd_party", site=site1)

        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto'
        )

        subscription1 = mommy.make(
            models.Subscription,
            subscription_type=newsletter_subscription,
            contact=contact,
            accept_subscription=True
        )

        subscription2 = mommy.make(
            models.Subscription,
            subscription_type=third_party_subscription,
            contact=contact,
            accept_subscription=True
        )

        emailing = mommy.make(Emailing, subscription_type=newsletter_subscription)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_unregister', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(200, response.status_code)

        subscription1 = models.Subscription.objects.get(id=subscription1.id)
        self.assertEqual(subscription1.accept_subscription, False)
        self.assertEqual(subscription1.contact, contact)

        subscription2 = models.Subscription.objects.get(id=subscription2.id)
        self.assertEqual(subscription2.accept_subscription, True)
        self.assertEqual(subscription2.contact, contact)

        self.assertEqual(emailing.unsub.count(), 1)
        self.assertEqual(list(emailing.unsub.all()), [contact])

    def test_unregister_mailinglist_dont_exist(self):
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)

        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto'
        )

        emailing = mommy.make(Emailing, subscription_type=newsletter_subscription)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_unregister', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(200, response.status_code)

        subscription1 = models.Subscription.objects.get(subscription_type=newsletter_subscription)
        self.assertEqual(subscription1.accept_subscription, False)
        self.assertEqual(subscription1.contact, contact)
        self.assertEqual(emailing.unsub.count(), 1)
        self.assertEqual(list(emailing.unsub.all()), [contact])

    def test_unregister_mailinglist_twice(self):
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)

        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto'
        )

        subscription1 = mommy.make(
            models.Subscription,
            subscription_type=newsletter_subscription,
            contact=contact,
            accept_subscription=False
        )

        emailing = mommy.make(Emailing, subscription_type=newsletter_subscription)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_unregister', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(200, response.status_code)

        subscription1 = models.Subscription.objects.get(id=subscription1.id)
        self.assertEqual(subscription1.accept_subscription, False)
        self.assertEqual(subscription1.contact, contact)

        self.assertEqual(emailing.unsub.count(), 1)
        self.assertEqual(list(emailing.unsub.all()), [contact])

    def test_unregister_mailinglist_notfound_emailing(self):
        site1 = Site.objects.get_current()

        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto'
        )

        url = reverse('emailing_unregister', args=[1, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(200, response.status_code)

        self.assertEqual(Emailing.objects.count(), 0)

    def test_unregister_mailinglist_not_found_contact(self):
        site1 = Site.objects.get_current()

        newsletter_subscription = mommy.make(models.SubscriptionType, name="newsletter", site=site1)

        emailing = mommy.make(Emailing, subscription_type=newsletter_subscription)

        url = reverse('emailing_unregister', args=[emailing.id, "aaaa"])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(404, response.status_code)

        self.assertEqual(emailing.unsub.count(), 0)

    def test_view_online(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert'
        )
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing = mommy.make(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact.fullname)
        self.assertEqual(MagicLink.objects.count(), 2)

        magic_link0 = MagicLink.objects.all()[0]
        self.assertContains(response, reverse('emailing_view_link', args=[magic_link0.uuid, contact.uuid]))
        self.assertEqual(magic_link0.url, '/this-link-without-prefix-in-template')

        magic_link1 = MagicLink.objects.all()[1]
        self.assertContains(response, reverse('emailing_view_link', args=[magic_link1.uuid, contact.uuid]))
        self.assertEqual(magic_link1.url, 'http://toto.fr')

    @skipIf(not is_localized() or not is_multilang(), "not localized")
    def test_emailing_view_online_lang(self):
        """test view emailing in other lang"""
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert'
        )
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing = mommy.make(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()

        #default_lang = settings.LANGUAGES[0][0]
        other_lang = settings.LANGUAGES[1][0]

        url = reverse('emailing_view_online_lang', args=[emailing.id, contact.uuid, other_lang])
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        next_url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])[3:]
        redirect_url = other_lang + next_url
        self.assertTrue(response['Location'].find(redirect_url) >= 0)

    @override_settings(SECRET_KEY=u"super-héros")
    def test_view_online_utf_links(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert'
        )
        newsletter_data = {
            'subject': 'This is the subject',
            'content': u'<h2>Hello #!-fullname-!#!</h2><p>Visit <a href="http://toto.fr/à-bientôt">à bientôt</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing = mommy.make(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, contact.fullname)
        self.assertEqual(MagicLink.objects.count(), 2)

        magic_link0 = MagicLink.objects.all()[0]
        self.assertContains(response, reverse('emailing_view_link', args=[magic_link0.uuid, contact.uuid]))
        self.assertEqual(magic_link0.url, '/this-link-without-prefix-in-template')

        magic_link1 = MagicLink.objects.all()[1]
        self.assertContains(response, reverse('emailing_view_link', args=[magic_link1.uuid, contact.uuid]))
        self.assertEqual(magic_link1.url, u'http://toto.fr/à-bientôt')

    def test_view_long_links(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert'
        )
        short_link = "http://toto.fr/{0}".format("abcde" * 100)[:499]
        long_link = "http://toto.fr/{0}".format("abcde" * 100)  # >500 chars
        newsletter_data = {
            'subject': 'This is the subject',
            'content': u'<p>Visit <a href="{0}">long link</a> <a href="{1}">long link</a></p>'.format(
                short_link, long_link),
            'template': 'test/newsletter_no_link.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing = mommy.make(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertEqual(MagicLink.objects.count(), 1)

        magic_link0 = MagicLink.objects.all()[0]
        self.assertContains(response, reverse('emailing_view_link', args=[magic_link0.uuid, contact.uuid]))
        self.assertEqual(magic_link0.url, short_link)

        self.assertContains(response, long_link)

    def test_view_duplicate_links(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert'
        )
        short_link = "http://toto.fr/abcde/"
        newsletter_data = {
            'subject': 'This is the subject',
            'content': u'<p>Visit <a href="{0}">link1</a> <a href="{1}">link2</a></p>'.format(
                short_link, short_link
            ),
            'template': 'test/newsletter_no_link.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing = mommy.make(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()

        url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        self.assertEqual(MagicLink.objects.count(), 1)

        magic_link0 = MagicLink.objects.all()[0]
        self.assertContains(response, reverse('emailing_view_link', args=[magic_link0.uuid, contact.uuid]))
        self.assertEqual(magic_link0.url, short_link)

    def test_view_duplicate_emailing(self):
        entity = mommy.make(models.Entity, name="my corp")
        contact = mommy.make(
            models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert'
        )
        short_link = "http://toto.fr/abcde/"
        newsletter_data = {
            'subject': 'This is the subject',
            'content': u'<p>Visit <a href="{0}">link1</a></p>'.format(
                short_link
            ),
            'template': 'test/newsletter_no_link.html'
        }
        newsletter = mommy.make(Newsletter, **newsletter_data)
        emailing1 = mommy.make(Emailing, newsletter=newsletter)
        emailing1.sent_to.add(contact)
        emailing1.save()

        emailing2 = mommy.make(Emailing, newsletter=newsletter)
        emailing2.sent_to.add(contact)
        emailing2.save()

        for emailing in (emailing1, emailing2):
            url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
            response = self.client.get(url)
            self.assertEqual(200, response.status_code)

            magic_links = MagicLink.objects.filter(emailing=emailing)
            self.assertEqual(magic_links.count(), 1)

            magic_link0 = magic_links[0]
            self.assertContains(response, reverse('emailing_view_link', args=[magic_link0.uuid, contact.uuid]))
            self.assertEqual(magic_link0.url, short_link)


class NewsletterTest(BaseNewsletterTest):
    """test coop_cms newsletter"""

    def test_send_newsletter_template(self):
        def extra_checker(e):
            site = Site.objects.get(id=settings.SITE_ID)
            url = "http://"+site.domain+"/this-link-without-prefix-in-template"
            self.assertTrue(e.alternatives[0][0].find(url) >= 0)
        super(NewsletterTest, self).test_send_test_newsletter('test/newsletter_contact.html')


class CustomTemplateTest(BaseTestCase):
    """Test the user-templating"""

    def test_send_newsletter(self):
        entity = mommy.make(models.Entity, name="my corp")
        city = mommy.make(models.City, name='MaVille')

        contact = mommy.make(
            models.Contact,
            gender=models.Contact.GENDER_MALE,
            entity=entity,
            email='john@toto.fr',
            lastname=u'Doe',
            firstname=u'John',
            address='2 rue de la lune',
            zip_code='42424',
            city=city
        )

        content = '''
        <h2>Hello #!-gender_dear-!# #!-gender_name-!# #!-firstname-!# #!-lastname-!#</h2>
        Email: #!-email-!#
        Addresse: #!-address-!# #!-zip_code-!# #!-city_name-!#
        Address: #!-full_address-!#
        Entity: #!-entity_name-!#
        '''

        newsletter_data = {
            'subject': 'Hello #!-firstname-!#',
            'content': content,
            'template': 'test/newsletter_contact.html',
        }

        newsletter = mommy.make(Newsletter, **newsletter_data)

        site = Site.objects.get_current()
        site.domain = "toto.fr"
        site.save()

        emailing = mommy.make(
            Emailing,
            newsletter=newsletter,
            status=Emailing.STATUS_SCHEDULED,
            scheduling_dt=datetime.now(),
            sending_dt=None,
            subscription_type=mommy.make(models.SubscriptionType, site=site),
        )

        emailing.send_to.add(contact)
        emailing.save()

        management.call_command('emailing_scheduler', verbosity=0, interactive=False)

        emailing = Emailing.objects.get(id=emailing.id)

        # check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), 1)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(email.to, [contact.get_email_address()])
        self.assertEqual(email.from_email, settings.COOP_CMS_FROM_EMAIL)

        self.assertTrue(email.alternatives[0][1], "text/html")

        html_body = email.alternatives[0][0]
        self.assertTrue(html_body.find(contact.fullname) >= 0)

        self.assertEqual(email.subject, 'Hello John')

        fields = (
            'firstname', 'lastname', 'gender_dear', 'gender_name', 'email', 'city_name', 'address', 'zip_code',
            'full_address', 'entity_name'
        )
        for field_name in fields:
            self.assertTrue(email.body.find(getattr(contact, field_name)) >= 0)
            self.assertTrue(html_body.find(getattr(contact, field_name)) >= 0)
