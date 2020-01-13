# -*- coding: utf-8 -*-

from unittest import skipIf

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context

from coop_cms.models import ArticleCategory
from coop_cms.settings import get_article_class

from balafon.Crm import models
if "balafon.Profile" in settings.INSTALLED_APPS:
    from balafon.Profile.models import CategoryPermission
from balafon.Profile.tests import BaseTestCase
from balafon.Profile.utils import create_profile_contact


@skipIf(not ("balafon.Profile" in settings.INSTALLED_APPS), "registration not installed")
class IfProfilePermTemplateTagsTest(BaseTestCase):

    def _request(self):
        class DummyRequest:
            def __init__(self, user):
                self.LANGUAGE_CODE = settings.LANGUAGES[0][0]
                self.user = user
        return DummyRequest(self.user)

    def setUp(self):
        super(IfProfilePermTemplateTagsTest, self).setUp()
        ct = ContentType.objects.get_for_model(get_article_class())
        perm = Permission.objects.get(codename='change_article', content_type=ct)
        self.user.user_permissions.add(perm)
        self.user.save()

    def test_create_article(self):
        tpl = Template('{% load balafon_profile_perm %}{% if_can_do_article "test" %}HELLO{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")

        article_class = get_article_class()
        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
        self.assertEqual(a.slug, "test")

    def test_existing_article(self):
        article_class = get_article_class()
        article_class.objects.create(slug='test', title="Test")

        tpl = Template('{% load balafon_profile_perm %}{% if_can_do_article "test" %}HELLO{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")

        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
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
        article_class = get_article_class()
        article_class.objects.create(slug='test', title="Test", category=cat)

        tpl = Template('{% load balafon_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "SORRY")

        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
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
        article_class = get_article_class()
        article_class.objects.create(slug='test', title="Test", category=cat)

        tpl = Template('{% load balafon_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "SORRY")

        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
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
        article_class = get_article_class()
        article_class.objects.create(slug='test', title="Test", category=cat)

        tpl = Template('{% load balafon_profile_perm %}{% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}')
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")

        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
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
        article_class = get_article_class()
        article_class.objects.create(slug='test', title="Test", category=cat)

        tpl = Template(
            '''{% spaceless %}{% load balafon_profile_perm %}
            {% if_can_do_article "test" can_edit_article %}HELLO{% else %}SORRY{% endif %}{% endspaceless %}'''
        )
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "SORRY")

        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
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
        article_class = get_article_class()
        article_class.objects.create(slug='test', title="Test", category=cat)

        tpl = Template(
            '''{% spaceless %}{% load balafon_profile_perm %}
            {% if_can_do_article "test" can_edit_article %}HELLO{% else %}SORRY{% endif %}{% endspaceless %}'''
        )
        html = tpl.render(Context({'request': self._request()}))
        self.assertEqual(html, "HELLO")

        self.assertEqual(article_class.objects.count(), 1)
        a = article_class.objects.all()[0]
        self.assertEqual(a.slug, "test")

        response = self.client.get(a.get_absolute_url())
        self.assertEqual(response.status_code, 403)

        response = self.client.get(a.get_edit_url())
        self.assertEqual(response.status_code, 200)

    def test_article_link_force_language(self):
        if len(settings.LANGUAGES) > 1:
            lang = settings.LANGUAGES[0][0]

            tpl = Template(
                '''{% spaceless %}{% load balafon_profile_perm %}
                {% if_can_do_article "test" %}HELLO{% else %}SORRY{% endif %}{% endspaceless %}'''
            )
            request = self._request()
            request.LANGUAGE_CODE = settings.LANGUAGES[1][0]
            html = tpl.render(Context({'request': request}))
            self.assertEqual(html, "HELLO")

            article_class = get_article_class()
            self.assertEqual(article_class.objects.count(), 1)
            a = article_class.objects.all()[0]
            self.assertEqual(a.slug, "test")

    def test_article_existing_link_force_language_(self):
        if len(settings.LANGUAGES) > 1:
            article_class = get_article_class()

            lang = settings.LANGUAGES[0][0]

            article = article_class.objects.create(slug="test", title="Test")

            request = self._request()
            lang = request.LANGUAGE_CODE = settings.LANGUAGES[1][0]

            setattr(article, "slug_"+lang, "test_"+lang)
            article.save()

            tpl = Template(
                '''{% spaceless %}
                {% load balafon_profile_perm %}
                {% if_can_do_article "test" can_view_article '+lang+' %}HELLO{% else %}SORRY{% endif %}
                {% endspaceless %}'''
            )
            html = tpl.render(Context({'request': request}))
            self.assertEqual(html, "HELLO")

            self.assertEqual(article_class.objects.count(), 1)
            a = article_class.objects.all()[0]
            self.assertEqual(a.slug, "test")
            self.assertEqual(getattr(article, "slug_"+lang), "test_"+lang)
