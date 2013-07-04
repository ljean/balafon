# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from datetime import datetime
from model_mommy import mommy
from sanza.Crm import models
from sanza.Profile.models import CategoryPermission
from django.core import mail
from django.conf import settings
from coop_cms.settings import get_article_class
from coop_cms.models import ArticleCategory, Document
from django.core.files import File
from django.template import Template, Context
from utils import create_profile_contact, notify_registration
from registration.models import RegistrationProfile
import os.path

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()
        
    def _get_file(self, file_name='unittest1.txt'):
        full_name = os.path.normpath(os.path.dirname(__file__) + '/fixtures/' + file_name)
        return open(full_name, 'rb')

    def _login(self):
        self.client.login(username="toto", password="abc")

    
class IfProfilePermTemplateTagsTest(BaseTestCase):
    
    def _request(self):
        class DummyRequest:
            def __init__(self, user):
                self.LANGUAGE_CODE = settings.LANGUAGES[0][0]
                self.user = user
        return DummyRequest(self.user)
    
    def test_create_article(self):
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" %}HELLO{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")
        
        Article = get_article_class()
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
    def test_existing_article(self):
        Article = get_article_class()
        Article.objects.create(slug='test', title="Test")
        
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" %}HELLO{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")
        
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
    def test_user_not_allowed(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        #gr.contacts.add(contact)
        #gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
        
        #Create article
        Article = get_article_class()
        Article.objects.create(slug='test', title="Test", category=cat)
        
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "SORRY")
        
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
        response = self.client.get(a.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        
    def test_group_not_allowed(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        #cat_perm.can_view_groups.add(gr)
        cat_perm.save()
        
        #Create article
        Article = get_article_class()
        Article.objects.create(slug='test', title="Test", category=cat)
        
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "SORRY")
        
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
        response = self.client.get(a.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        
    def test_user_allowed(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
        
        #Create article
        Article = get_article_class()
        Article.objects.create(slug='test', title="Test", category=cat)
        
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")
        
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
        response = self.client.get(a.get_absolute_url())
        self.assertEqual(response.status_code, 200)
    
    def test_user_not_allowed_permission(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
        
        #Create article
        Article = get_article_class()
        Article.objects.create(slug='test', title="Test", category=cat)
        
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" can_edit_article %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "SORRY")
        
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
        response = self.client.get(a.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(a.get_edit_url())
        self.assertEqual(response.status_code, 403)
    
    def test_user_allowed_permission(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_edit_groups.add(gr)
        cat_perm.save()
        
        #Create article
        Article = get_article_class()
        Article.objects.create(slug='test', title="Test", category=cat)
        
        tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" can_edit_article %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")
        
        self.assertEqual(Article.objects.count(), 1)
        a = Article.objects.all()[0]
        self.assertEqual(a.slug, "test")
        
        response = self.client.get(a.get_absolute_url())
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(a.get_edit_url())
        self.assertEqual(response.status_code, 200)
        
        
    def test_article_link_force_language(self):
        if len(settings.LANGUAGES) > 1:
            lang = settings.LANGUAGES[0][0]
            
            tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
            request = self._request()
            request.LANGUAGE_CODE = settings.LANGUAGES[1][0]
            html = tpl.render(Context({'request': request}))
            self.assertEqual(html, "HELLO")
            
            Article = get_article_class()
            self.assertEqual(Article.objects.count(), 1)
            a = Article.objects.all()[0]
            self.assertEqual(a.slug, "test")
            
    def test_article_existing_link_force_language_(self):
        if len(settings.LANGUAGES) > 1:
            Article = get_article_class()
            
            lang = settings.LANGUAGES[0][0]
            
            article = Article.objects.create(slug="test", title="Test")
            
            request = self._request()
            lang = request.LANGUAGE_CODE = settings.LANGUAGES[1][0]
            
            setattr(article, "slug_"+lang, "test_"+lang)
            article.save()
            
            tpl = Template('{% load sanza_profile_perm %}{% if_can_do_article "test" can_view_article '+lang+' %}HELLO{% else %}SORRY{% endif %}')
            html = tpl.render(Context({'request': request}))
            self.assertEqual(html, "HELLO")
            
            self.assertEqual(Article.objects.count(), 1)
            a = Article.objects.all()[0]
            self.assertEqual(a.slug, "test")
            self.assertEqual(getattr(article, "slug_"+lang), "test_"+lang)
    

class DownloadTestCase(BaseTestCase):
    
    def test_download_private_permission(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
            
        #create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        #check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        #login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertEquals(response['Content-Disposition'], "attachment; filename=unittest1.txt")
        self.assertEquals(response['Content-Type'], "text/plain")
        #TODO: This change I/O Exception in UnitTest
        #self.assertEqual(response.content, self._get_file().read()) 
        
        #logout and download
        self.client.logout()
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        redirect_url = response.redirect_chain[-1][0]
        login_url = reverse('django.contrib.auth.views.login')
        self.assertTrue(redirect_url.find(login_url)>0)
        
    def test_download_private_not_in_group(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        # Contact is not in the group: gr.contacts.add(contact)
        #gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        #Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
            
        #create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        #check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        #login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 403)
    
    def test_download_private_group_not_allowed(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        cat_perm = CategoryPermission.objects.create(category=cat)
        
        #create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        #check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        #login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 403)
        
    def test_download_private_no_permission(self):
        
        #Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
            
        #create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        #check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        #login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        #self.assertEquals(response['Content-Disposition'], "attachment; filename=unittest1.txt")
        self.assertEquals(response['Content-Type'], "text/plain")
        
    
        
    def test_download_private_no_contact_defined(self):
        
        #Create category
        cat = ArticleCategory.objects.create(name="CAT")
        cat_perm = CategoryPermission.objects.create(category=cat)
            
        #create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        #check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        #login and download
        response = self.client.get(doc.get_download_url())
        self.assertEqual(response.status_code, 403)
        

class ProfileBackendTest(TestCase):
    
    def setUp(self):
        settings.SANZA_NOTIFICATION_EMAIL = "ljean@apidev.fr"
    
    def _create_user(self, **kwargs):
        data = {
            'username': "tutu",
            'email': "tutu@tutu.fr",
            'last_name': "Utu",
            'first_name': "Thierry"
        }
        data.update(kwargs)
        return User.objects.create(**data)
    
    def _create_profile_and_check(self, user):
        profile = create_profile_contact(user)
        contact = models.Contact.objects.get(email=user.email)
        self.assertEqual(contact.lastname, user.last_name)
        self.assertEqual(contact.firstname, user.first_name)
        return profile
    
    def test_create_sanza_contact(self):
        user = self._create_user()
        RegistrationProfile(user=user, activation_key=RegistrationProfile.ACTIVATED)
        self._create_profile_and_check(user)
        
    def test_create_sanza_contact_no_profile(self):
        user = self._create_user()
        self._create_profile_and_check(user)
    
    def test_create_sanza_contact_exists(self):
        user = self._create_user()
        self._create_profile_and_check(user)
        old_last_name = user.last_name
        old_first_name = user.first_name
        user.last_name = "John"
        user.first_name = "Doe"
        user.save()
        user.last_name = old_last_name
        user.first_name = old_first_name
        self._create_profile_and_check(user)
        self.assertEqual(models.Contact.objects.count(), 1)
    
    def test_create_sanza_contact_duplicate_email(self):
        user = self._create_user()
        contact = mommy.make(models.Contact, email=user.email)
        contact.entity.default_contact.delete()
        self._create_profile_and_check(user)
        self.assertEqual(models.Contact.objects.count(), 1)
        self.assertEqual(models.Action.objects.count(), 0)
        
        
    def test_create_sanza_contact_multiple_email(self):
        user = self._create_user()
        contact1 = mommy.make(models.Contact, email=user.email)
        contact2 = mommy.make(models.Contact, email=user.email)
        contact1.entity.default_contact.delete()
        contact2.entity.default_contact.delete()
        
        profile = create_profile_contact(user)
        contact = profile.contact
        self.assertEqual(contact.lastname, user.last_name)
        self.assertEqual(contact.firstname, user.first_name)
        
        self.assertEqual(models.Contact.objects.count(), 3)
        self.assertEqual(models.Action.objects.count(), 1)
        action = models.Action.objects.all()[0]
        self.assertEqual(action.contact, contact)
    
    def test_notifiy_registration(self):
        user = self._create_user()
        profile = self._create_profile_and_check(user)
        
        notify_registration(profile)
        self.assertEqual(len(mail.outbox), 1)
        
        notif_email = mail.outbox[0]
        self.assertEqual(notif_email.to, [settings.SANZA_NOTIFICATION_EMAIL])
        self.assertEqual(notif_email.cc, [])
        self.assertTrue(notif_email.body.find(user.email)>0)
       
class RegisterTestCase(TestCase):

    def test_register_with_very_long_email(self):
        url = reverse('registration_register')
        data = {
            'email': ('a'*30)+'@toto.fr',
            'password1': 'PAss',
            'password2': 'PAss',
            'accept_termofuse': True,
            'accept_newsletter': True,
            'accept_3rdpart': True,
        }
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email=data['email'])
        
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        rp = RegistrationProfile.objects.all()[0]
        self.assertEqual(rp.user, user)
        activation_url = reverse('registration_activate', args=[rp.activation_key])
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [data['email']])
        self.assertTrue(mail.outbox[0].body.find(activation_url))
        
        response = self.client.get(activation_url, follow=True)
        self.assertEqual(response.status_code, 200)
        contact = models.Contact.objects.get(email=data['email'])
        self.assertEqual(contact.accept_newsletter, data['accept_newsletter'])
        
        self.assertTrue(self.client.login(email=data['email'], password=data['password1']))
