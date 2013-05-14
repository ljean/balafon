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
from coop_cms.models import ArticleCategory
from django.template import Template, Context
from utils import create_profile_contact, notify_registration
from registration.models import RegistrationProfile

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.save()
        self._login()

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
        contact = mommy.make_one(models.Contact, email=user.email)
        contact.entity.contact_set.all()[0].delete()
        self._create_profile_and_check(user)
        self.assertEqual(models.Contact.objects.count(), 1)
        self.assertEqual(models.Action.objects.count(), 0)
        
        
    def test_create_sanza_contact_multiple_email(self):
        user = self._create_user()
        contact1 = mommy.make_one(models.Contact, email=user.email)
        contact2 = mommy.make_one(models.Contact, email=user.email)
        contact1.entity.contact_set.all()[0].delete()
        contact2.entity.contact_set.all()[0].delete()
        
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
        
    
