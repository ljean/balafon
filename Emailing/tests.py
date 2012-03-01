# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from datetime import datetime
from model_mommy import mommy
from sanza.Crm import models
from sanza.Emailing.models import Emailing, MagicLink, EmailingCounter
from coop_cms.models import Newsletter
from django.core import management
from django.core import mail
from django.conf import settings
from coop_cms import tests as coop_cms_tests

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()

    def _login(self):
        self.client.login(username="toto", password="abc")


class EmailingManagement(BaseTestCase):
    def test_view_newsletters_list(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter1 = mommy.make_one(Newsletter, subject='newsletter1')
        newsletter2 = mommy.make_one(Newsletter, subject='newsletter2')
        
        emailing1 = mommy.make_one(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing1.send_to.add(c)
        emailing1.save()
        
        emailing2 = mommy.make_one(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENDING,
            scheduling_dt = datetime.now(), sending_dt = None)
        emailing2.send_to.add(contacts[0])
        emailing2.save()
        
        emailing3 = mommy.make_one(Emailing,
            newsletter=newsletter1, status=Emailing.STATUS_SENT,
            scheduling_dt = datetime.now(), sending_dt = datetime.now())
        emailing3.send_to.add(contacts[-1])
        emailing3.save()
        
        response = self.client.get(reverse('emailing_newsletter_list'))
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'newsletter1')
        self.assertContains(response, 'newsletter2')
        
        self.assertContains(response, emailing1.get_info())
        self.assertContains(response, emailing2.get_info())
        self.assertContains(response, emailing3.get_info())

    def test_emailing_next_action(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make_one(Emailing,
            status=Emailing.STATUS_EDITING,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        next_url = reverse('emailing_confirm_send_mail', args=[emailing.id])
        self.assertTrue(emailing.next_action().find(next_url))
        
        emailing.status = Emailing.STATUS_SCHEDULED
        emailing.save()
        next_url = reverse('emailing_cancel_send_mail', args=[emailing.id])
        self.assertTrue(emailing.next_action().find(next_url))
        
        emailing.status = Emailing.STATUS_SENDING
        emailing.save()
        self.assertEqual(emailing.next_action(), "")
        
        emailing.status = Emailing.STATUS_SENT
        emailing.save()
        self.assertEqual(emailing.next_action(), "")
        
    def test_view_magic_link(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make_one(Emailing,
            status=Emailing.STATUS_SENT,
            scheduling_dt = datetime.now(), sending_dt = datetime.now())
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        emailing2 = mommy.make_one(Emailing)
        
        google = "http://www.google.fr"
        google_link = MagicLink.objects.create(emailing=emailing, url=google)
        for c in contacts:
            google_link.visitors.add(c)
        google_link.save()
        
        toto = "http://www.toto.fr"
        toto_link = MagicLink.objects.create(emailing=emailing, url=toto)
        toto_link.visitors.add(contacts[0])
        toto_link.save()
        
        titi = "http://www.titi.fr"
        titi_link = MagicLink.objects.create(emailing=emailing2, url=titi)
        titi_link.visitors.add(contacts[0])
        titi_link.save()
        
        url = reverse('emailing_view', args=[emailing.id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, toto)
        self.assertContains(response, google)
        self.assertNotContains(response, titi)
        
    def test_confirm_sending(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make_one(Emailing, status=Emailing.STATUS_EDITING)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        next_url = reverse('emailing_confirm_send_mail', args=[emailing.id])
        response = self.client.get(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url, data={"confirm": "1"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        self.assertTrue(emailing.scheduling_dt > datetime.now())
        
        
    def test_cancel_sending(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        emailing = mommy.make_one(Emailing, status=Emailing.STATUS_SCHEDULED, scheduling_dt=datetime.now())
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        next_url = reverse('emailing_cancel_send_mail', args=[emailing.id])
        response = self.client.get(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url)
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SCHEDULED)
        self.assertNotEqual(emailing.scheduling_dt, None)
        
        response = self.client.post(next_url, data={"confirm": "1"})
        self.assertEqual(200, response.status_code)
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_EDITING)
        self.assertEqual(emailing.scheduling_dt, None)
        
    

class SendEmailingTest(BaseTestCase):

    def test_send_newsletter(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        
        management.call_command('add_emailing_counter', 5, verbosity=0, interactive=False)
        
        emailing = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        management.call_command('emailing_scheduler', verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        
        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), len(contacts))
        
        self.assertEqual(1, EmailingCounter.objects.count())
        counter = EmailingCounter.objects.all()[0]
        self.assertEqual(5, counter.total)
        self.assertEqual(counter.total - len(contacts), counter.credit)
        
        self.assertEqual(len(mail.outbox), len(contacts))
        
        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)
        
        for email, contact in zip(outbox, contacts):
            self.assertEqual(email.to, [contact.get_email_address()])
            self.assertEqual(email.subject, newsletter_data['subject'])
            self.assertTrue(email.body.find(entity.name)>=0)
            #print email.body
            self.assertTrue(email.body.find(contact.fullname)>=0)
            self.assertTrue(email.alternatives[0][1], "text/html")
            self.assertTrue(email.alternatives[0][0].find(contact.fullname)>=0)
            self.assertTrue(email.alternatives[0][0].find(entity.name)>=0)
            viewonline_url = settings.COOP_CMS_SITE_PREFIX + reverse('emailing_view_online', args=[emailing.id, contact.uuid])
            self.assertTrue(email.alternatives[0][0].find(viewonline_url)>=0)
            unsubscribe_url = settings.COOP_CMS_SITE_PREFIX + reverse('emailing_unregister', args=[emailing.id, contact.uuid])
            self.assertTrue(email.alternatives[0][0].find(unsubscribe_url)>=0)
            
            #check magic links
            self.assertTrue(MagicLink.objects.count()>0)
            
            #check an action has been created
            c = models.Contact.objects.get(id=contact.id)
            self.assertEqual(c.action_set.count(), 1)
            self.assertEqual(c.action_set.all()[0].subject, email.subject)
            
            
    def test_send_newsletter_limit(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        
        emailing = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        management.call_command('add_emailing_counter', 5, verbosity=0, interactive=False)
        
        management.call_command('emailing_scheduler', 2, verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        
        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_SENDING)
        self.assertEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 1)
        self.assertEqual(emailing.sent_to.count(), 2)
        
        self.assertEqual(len(mail.outbox), emailing.sent_to.count())
        
        outbox = list(mail.outbox)
        outbox.sort(key=lambda e: e.to)
        contacts.sort(key=lambda c: c.get_email)
        
        for email, contact in zip(outbox, emailing.sent_to.all()):
            self.assertEqual(email.to, [contact.get_email_address()])
            
        mail.outbox = []

        management.call_command('emailing_scheduler', 2, verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertNotEqual(emailing.sending_dt, None)
        self.assertEqual(emailing.send_to.count(), 0)
        self.assertEqual(emailing.sent_to.count(), 3)
        self.assertEqual(len(mail.outbox), 1)
        
        self.assertEqual(1, EmailingCounter.objects.count())
        counter = EmailingCounter.objects.all()[0]
        self.assertEqual(5, counter.total)
        self.assertEqual(counter.total - len(contacts), counter.credit)
        
    def test_send_newsletter_no_credit(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        
        emailing = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        management.call_command('emailing_scheduler', 2, verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        
        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_CREDIT_MISSING)
        self.assertEqual(len(mail.outbox), 0)
        
    def test_send_newsletter_credit_missing(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        
        emailing = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        for x in range(10):
            management.call_command('add_emailing_counter', 1, verbosity=0, interactive=False)
        
        management.call_command('emailing_scheduler', 2, verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        
        #check emailing status
        self.assertEqual(emailing.status, Emailing.STATUS_CREDIT_MISSING)
        self.assertEqual(len(mail.outbox), 0)
        
    def test_send_newsletter_credit_missing_new_credit(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        
        emailing = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        management.call_command('add_emailing_counter', 1, verbosity=0, interactive=False)
        
        management.call_command('emailing_scheduler', 2, verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_CREDIT_MISSING)
        self.assertEqual(len(mail.outbox), 0)
        
        management.call_command('add_emailing_counter', 10, verbosity=0, interactive=False)
        emailing.status = Emailing.STATUS_SCHEDULED
        emailing.save()
        management.call_command('emailing_scheduler', verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_SENT)
        self.assertEqual(len(mail.outbox), 3)
        
    def test_send_newsletter_credit_missing_new_emailing(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        names = ['alpha', 'beta', 'gamma']
        contacts = [mommy.make_one(models.Contact, entity=entity,
            email=name+'@toto.fr', lastname=name.capitalize()) for name in names]
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        
        emailing = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        for c in contacts:
            emailing.send_to.add(c)
        emailing.save()
        
        emailing2 = mommy.make_one(Emailing,
            newsletter=newsletter, status=Emailing.STATUS_SCHEDULED,
            scheduling_dt = datetime.now(), sending_dt = None)
        emailing2.send_to.add(contacts[0])
        emailing2.save()
        
        management.call_command('add_emailing_counter', 1, verbosity=0, interactive=False)
        
        management.call_command('emailing_scheduler', 2, verbosity=0, interactive=False)
        
        emailing = Emailing.objects.get(id=emailing.id)
        self.assertEqual(emailing.status, Emailing.STATUS_CREDIT_MISSING)
        
        emailing2 = Emailing.objects.get(id=emailing2.id)
        self.assertEqual(emailing2.status, Emailing.STATUS_SENT)
        
        self.assertEqual(len(mail.outbox), 1)
        
            
    def test_view_magic_link(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        contact = mommy.make_one(models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto')
        emailing = mommy.make_one(Emailing)
        emailing.sent_to.add(contact)
        emailing.save()
        
        link = "http://www.google.fr"
        magic_link = MagicLink.objects.create(emailing=emailing, url=link)
        
        response = self.client.get(reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid]))
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], link)
        
        
    def test_unregister_mailinglist(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        contact = mommy.make_one(models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Toto', accept_newsletter=True)
        emailing = mommy.make_one(Emailing)
        emailing.sent_to.add(contact)
        emailing.save()
        
        url = reverse('emailing_unregister', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        response = self.client.post(url, data={'unregister': True})
        self.assertEqual(200, response.status_code)
        
        contact = models.Contact.objects.get(id=contact.id)
        self.assertEqual(contact.accept_newsletter, False)
    
    def test_view_online(self):
        entity = mommy.make_one(models.Entity, name="my corp")
        contact = mommy.make_one(models.Contact, entity=entity,
            email='toto@toto.fr', lastname='Azerty', firstname='Albert')
        newsletter_data = {
            'subject': 'This is the subject',
            'content': '<h2>Hello {fullname}!</h2><p>Visit <a href="http://toto.fr">us</a></p>',
            'template': 'test/newsletter_contact.html'
        }
        newsletter = mommy.make_one(Newsletter, **newsletter_data)
        emailing = mommy.make_one(Emailing, newsletter=newsletter)
        emailing.sent_to.add(contact)
        emailing.save()
        
        url = reverse('emailing_view_online', args=[emailing.id, contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, contact.fullname)
        self.assertEqual(MagicLink.objects.count(), 1)
        ml = MagicLink.objects.all()[0]
        self.assertContains(response, reverse('emailing_view_link', args=[ml.uuid, contact.uuid]))
        

class NewsletterTest(coop_cms_tests.NewsletterTest):
    def test_send_newsletter_template(self):
        super(NewsletterTest, self).test_send_test_newsletter('test/newsletter_contact.html')
        
class SubscribeTest(TestCase):
    
    def setUp(self):
        self.group1 = mommy.make_one(models.Group, name="ABC", subscribe_form=True)
        self.group2 = mommy.make_one(models.Group, name="DEF", subscribe_form=True)
        self.group3 = mommy.make_one(models.Group, name="GHI", subscribe_form=False)
    
    def test_view_subscribe_newsletter(self):
        url = reverse("emailing_subscribe_newsletter")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
        self.assertContains(response, self.group1.name)
        self.assertContains(response, self.group2.name)
        self.assertNotContains(response, self.group3.name)
        
    def test_subscribe_newsletter_no_entity(self):
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': str(self.group1.id),
        }
        
        response = self.client.post(url, data=data, follow=False)
        
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)
        
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [self.group1])
        
    def test_subscribe_newsletter_entity(self):
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'entity': 'Toto',
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': [self.group1.id, self.group2.id],
        }
        
        response = self.client.post(url, data=data, follow=False)
        #print response.content
        self.assertEqual(302, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 1)
        
        contact = models.Contact.objects.all()[0]
        
        self.assertNotEqual(contact.uuid, '')
        self.assertTrue(response['Location'].find(reverse('emailing_subscribe_done', args=[contact.uuid]))>=0)
        
        self.assertEqual(contact.entity.name, data['entity'])
        self.assertEqual(contact.lastname, data['lastname'])
        self.assertEqual(contact.firstname, data['firstname'])
        self.assertEqual(list(contact.entity.group_set.all()), [self.group1, self.group2])
        
    def test_subscribe_newsletter_private_group(self):
        url = reverse("emailing_subscribe_newsletter")
        
        data = {
            'entity': 'Toto',
            'lastname': 'Dupond',
            'firstname': 'Pierre',
            'groups': [self.group1.id, self.group3.id],
        }
        
        response = self.client.post(url, data=data, follow=False)
        
        self.assertEqual(200, response.status_code)
        self.assertEqual(models.Contact.objects.count(), 0)
    
    def test_view_subscribe_done(self):
        contact = mommy.make_one(models.Contact)
        url = reverse('emailing_subscribe_done', args=[contact.uuid])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        unregister_url = reverse('emailing_unregister', args=[0, contact.uuid])
        self.assertContains(response, unregister_url)
        