# -*- coding: utf-8 -*-
"""unit testing"""

from datetime import datetime, date, timedelta
import json
import logging
from unittest import skipIf
from StringIO import StringIO
import sys

from django.conf import settings
from django.contrib.auth.models import User, Group, AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core import mail, management
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.test import TestCase
from django.utils import timezone

from coop_cms.utils import RequestManager
from model_mommy import mommy

from balafon.utils import is_allowed_homepage
from balafon.Crm import models
from balafon.Emailing.models import Emailing
from balafon.Search.models import Search
from balafon.Users.models import UserPreferences, Favorite, UserHomepage, CustomMenu, CustomMenuItem


class BaseTestCase(TestCase):

    def setUp(self):
        """before each test"""
        logging.disable(logging.CRITICAL)
        RequestManager().clean()
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def tearDown(self):
        """after each test"""
        logging.disable(logging.NOTSET)

    def _login(self):
        """login user"""
        return self.client.login(username="toto", password="abc")


class NotifyDueActionsTestCase(BaseTestCase):
    
    def setUp(self):
        """before each test"""
        super(NotifyDueActionsTestCase, self).setUp()
        self._from_email = settings.DEFAULT_FROM_EMAIL
        settings.DEFAULT_FROM_EMAIL = "toto@toto.fr"
        
    def tearDown(self):
        """after each test"""
        super(NotifyDueActionsTestCase, self).tearDown()
        settings.DEFAULT_FROM_EMAIL = self._from_email
    
    def now(self):
        """get current datetime"""
        if settings.USE_TZ:
            return datetime.now().replace(tzinfo=timezone.utc)
        else:
            return datetime.now()
    
    def _notify_due_actions(self, verbosity=0):
        """call notify_due_actions and check what is printed on the console"""
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('notify_due_actions', verbosity=verbosity, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        return buf.readlines()
    
    def test_notify_due_actions(self):
        """notify some actions"""
        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        team_member = mommy.make(models.TeamMember, user=user)
        actions = [
            mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=team_member),
        ]

        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for action in actions:
            self.assertTrue(email.body.find(action.subject) > 0)
            self.assertTrue(email.body.find(action.planned_date.strftime("%d/%m/%Y %H:%M")) > 0)

    def test_notify_due_actions_not_in_staff(self):
        """do nto notify actions if team member is not active"""
        user = mommy.make(User, is_active=True, is_staff=False, email="toto@toto.fr")
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        team_member = mommy.make(models.TeamMember, user=user, active=False)

        mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
        mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
        mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=team_member),

        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
    
    def test_notify_due_actions_disabled(self):
        """do not notify if user disable this option"""

        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        mommy.make(UserPreferences, user=user, notify_due_actions=False)
        team_member = mommy.make(models.TeamMember, user=user)

        mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member)
        mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member)
        mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=team_member)

        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
    
    def test_notify_due_actions_no_preferences(self):
        """do not notify if user has no preferences set"""

        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        team_member = mommy.make(models.TeamMember, user=user)

        mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member)
        mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member)
        mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=team_member)

        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
        
    def test_notify_due_actions_some_in_future(self):
        """notify only today and past actions"""

        tomorrow = datetime.today() + timedelta(1)
        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        team_member = mommy.make(models.TeamMember, user=user)

        notified_actions = [
            mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
        ]
        other_actions = [
            mommy.make(models.Action, subject="WXCVBN", planned_date=tomorrow, done=False, in_charge=team_member)
        ]

        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for action in notified_actions:
            self.assertTrue(email.body.find(action.subject) > 0)
            self.assertTrue(email.body.find(action.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
    
        for action in other_actions:
            self.assertFalse(email.body.find(action.subject) > 0)
            self.assertFalse(email.body.find(action.planned_date.strftime("%d/%m/%Y %H:%M"))>0)

    def test_notify_due_actions_some_not_in_charge(self):
        """only notify user is in charge"""

        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        team_member = mommy.make(models.TeamMember, user=user)
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        notified_actions = [
            mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
        ]
        other_actions = [
            mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False)
        ]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for action in notified_actions:
            self.assertTrue(email.body.find(action.subject) > 0)
        
        for action in other_actions:
            self.assertFalse(email.body.find(action.subject) > 0)
            
    def test_notify_due_actions_some_done(self):
        """only notify not done actions"""

        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        team_member = mommy.make(models.TeamMember, user=user)
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        notified_actions = [
            mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
        ]
        other_actions = [
            mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=True, in_charge=team_member),
        ]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for action in notified_actions:
            self.assertTrue(email.body.find(action.subject) > 0)
        
        for action in other_actions:
            self.assertFalse(email.body.find(action.subject) > 0)
            
    def test_notify_due_actions_some_not_planned(self):
        """only notify planned actions"""

        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        team_member = mommy.make(models.TeamMember, user=user)
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        notified_actions = [
            mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
        ]
        other_actions= [
            mommy.make(models.Action, subject="WXCVBN", done=False, in_charge=team_member),
        ]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)

    def test_notify_due_actions_some_planned_date(self):
        """notify today actions"""
        user = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        team_member = mommy.make(models.TeamMember, user=user)
        mommy.make(UserPreferences, user=user, notify_due_actions=True)
        notified_actions = [
            mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=team_member),
            mommy.make(models.Action, subject="WXCVBN", planned_date=datetime.today(), done=False, in_charge=team_member),
        ]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for action in notified_actions:
            self.assertTrue(email.body.find(action.subject) > 0)


class DummyRequest(object):
    """Dummy request: do nothing"""
    pass


class UpdateFavoriteTestCase(BaseTestCase):
    """manage favorites"""
    
    def _template_content(self):
        """template with favorite item tag"""
        return """
        {% load favorite_tags %}
        <ul class="users">
        {% for u in users %}
            <li>{{ u.username }}{% favorite_item u %}</li>
        {% endfor %}
        </ul>
        """
        
    def test_render_template(self):
        """make sure render do not fail"""
        for i in xrange(5):
            mommy.make(User)
        
        template = Template(self._template_content())
        
        dummy_request = DummyRequest()
        setattr(dummy_request, 'user', self.user)
        context = {
            'users': User.objects.all(),
            'request': dummy_request,
        }
        
        template.render(Context(context))
        
    def test_render_template_not_logged(self):
        """render for anonymous"""
        self.client.logout()
        for i in xrange(5):
            mommy.make(User)
        
        template = Template(self._template_content())
        
        dummy_request = DummyRequest()
        setattr(dummy_request, 'user', AnonymousUser())
        context = {
            'users': User.objects.all(),
            'request': dummy_request,
        }
        
        template.render(Context(context))
        
    def test_post_not_logged(self):
        """post favorite update for anonymous"""
        self.client.logout()
        user = mommy.make(User)
        data = {
            'content_type': ContentType.objects.get_for_model(User).id,
            'object_id': user.id, 
        }
        url = reverse('users_toggle_favorite')
        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)
        redirect_url = "/accounts/login/?next={0}".format(url)
        self.assertTrue(response['Location'].find(redirect_url) >= 0)

        self.assertEqual(0, Favorite.objects.count())

    def test_post_add(self):
        """post add favorite"""
        logged_user = self.user
        faved_user = mommy.make(User)
        
        data = {
            'content_type': ContentType.objects.get_for_model(User).id,
            'object_id': faved_user.id, 
        }
        
        response = self.client.post(reverse('users_toggle_favorite'), data)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content)
        self.assertEqual(True, resp_data['success'])
        self.assertEqual(True, resp_data['status'])
        self.assertEqual(1, Favorite.objects.count())
        
        fav = Favorite.objects.all()[0]
        self.assertEqual(fav.content_object, faved_user)
        self.assertEqual(fav.user, logged_user)
        
    def test_post_remove(self):
        """post remove favorite"""

        logged_user = self.user
        faved_user = mommy.make(User)
        
        user_ct = ContentType.objects.get_for_model(User)
        Favorite.objects.create(
            user=logged_user,
            object_id=faved_user.id,
            content_type=user_ct
        )
        self.assertEqual(1, Favorite.objects.count())
        
        data = {
            'content_type': user_ct.id,
            'object_id': faved_user.id, 
        }
        response = self.client.post(reverse('users_toggle_favorite'), data)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content)
        self.assertEqual(True, resp_data['success'])
        self.assertEqual(False, resp_data['status'])
        self.assertEqual(0, Favorite.objects.count())

    def test_post_wrong_id(self):
        """post wrong id"""

        user_ct = ContentType.objects.get_for_model(User)
        
        data = {
            'content_type': user_ct.id,
            'object_id': 1111, 
        }
        response = self.client.post(reverse('users_toggle_favorite'), data)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content)
        self.assertEqual(False, resp_data['success'])
        
    def test_post_wrong_ct(self):
        """post wrong content type"""

        faved_user = mommy.make(User)
        
        data = {
            'content_type': 55555,
            'object_id': faved_user.id, 
        }
        response = self.client.post(reverse('users_toggle_favorite'), data)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content)
        self.assertEqual(False, resp_data['success'])
        
        
class ListFavoritesTestCase(BaseTestCase):
    """view list of favorites"""

    def test_not_logged(self):
        """do not see if anonymous user"""
        self.client.logout()
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('login')>0)
        
    def test_empty_list(self):
        """view empty list"""
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        
    def test_list(self):
        """view list"""
        logged_user = self.user
        faved_users = [mommy.make(User, username='user-{0}'.format(i)) for i in xrange(5)]
        not_faved_users = [mommy.make(User, username='NOT-{0}'.format(i)) for i in xrange(5)]
        
        user_ct = ContentType.objects.get_for_model(User)
        for user in faved_users:
            Favorite.objects.create(user=logged_user, content_type=user_ct, object_id=user.id)
        
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        for user in faved_users:
            self.assertContains(response, user)
        for user in not_faved_users:
            self.assertNotContains(response, user)
            
    def test_someone_else_list(self):
        """do not see someone else list"""
        logged_user = self.user
        other_user = mommy.make(User)
        faved_users = [mommy.make(User, username='user-{0}'.format(i)) for i in xrange(5)]
        not_my_faved_users = [mommy.make(User, username='OTHER-{0}'.format(i)) for i in xrange(5)]
        
        user_ct = ContentType.objects.get_for_model(User)
        
        for user in faved_users:
            Favorite.objects.create(user=logged_user, content_type=user_ct, object_id=user.id)
        
        for user in not_my_faved_users:
            Favorite.objects.create(user=other_user, content_type=user_ct, object_id=user.id)
        
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        
        for user in faved_users:
            self.assertContains(response, user)
        for user in not_my_faved_users:
            self.assertNotContains(response, user)
            
    def test_list_different_cts(self):
        """different contentypes in list"""
        logged_user = self.user
        faved_users = [mommy.make(User, username='user-{0}'.format(i)) for i in xrange(5)]
        faved_groups = [mommy.make(Group, name='group-{0}'.format(i)) for i in xrange(5)]
        
        user_ct = ContentType.objects.get_for_model(User)
        group_ct = ContentType.objects.get_for_model(Group)
        
        for user in faved_users:
            Favorite.objects.create(user=logged_user, content_type=user_ct, object_id=user.id)
        
        for group in faved_groups:
            Favorite.objects.create(user=logged_user, content_type=group_ct, object_id=group.id)
        
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        for user in faved_users:
            self.assertContains(response, user)
        for user in faved_groups:
            self.assertContains(response, user)


class DeleteFavoriteTestCase(BaseTestCase):
    """Delete favorite"""

    def test_favorite_deleted_after_action_deleted(self):
        """test favorite is delete if object is deleted"""
        the_models = (
            models.Action, models.Entity, models.Contact, models.Group, models.Opportunity,
            Emailing, Search
        )
        
        for model_class in the_models:
            obj = mommy.make(model_class)
            logged_user = self.user
    
            content_type = ContentType.objects.get_for_model(model_class)
    
            Favorite.objects.create(user=logged_user, content_type=content_type, object_id=obj.id)
            
            self.assertEqual(1, Favorite.objects.count())
        
            obj.delete()
        
            self.assertEqual(0, Favorite.objects.count())


class UserHomepageTestCase(BaseTestCase):
    """test user homepage"""
    
    def test_set_homepage_none(self):
        """set homepage for 1st time"""
        self.assertEqual(0, UserHomepage.objects.count())
        homepage_url = 'http://testserver' + reverse("crm_view_entities_list")
        
        url = reverse('users_make_homepage')
        
        response = self.client.post(url, data={'url': homepage_url})
        self.assertEqual(200, response.status_code)
        
        self.assertEqual(1, UserHomepage.objects.count())
        homepage = UserHomepage.objects.all()[0]
        
        self.assertEqual(homepage.user, self.user)
        self.assertEqual(homepage.url, homepage_url)

    def test_set_homepage_invalid(self):
        """set an invalid homepage"""
        origin_url = 'http://testserver' + reverse('users_favorites_list')
        mommy.make(UserHomepage, user=self.user, url=origin_url)
        self.assertEqual(1, UserHomepage.objects.count())
        homepage_url = "http://toto.fr/toto"
        
        url = reverse('users_make_homepage')
        
        response = self.client.post(url, data={'url': homepage_url})
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.content)

        self.assertEqual(response_data["ok"], False)

        self.assertEqual(1, UserHomepage.objects.count())
        homepage = UserHomepage.objects.all()[0]

        self.assertEqual(homepage.user, self.user)
        self.assertEqual(homepage.url, origin_url)

    def test_set_homepage_valid(self):
        """set valid homepage"""

        origin_url = 'http://testserver' + reverse('users_favorites_list')
        mommy.make(UserHomepage, user=self.user, url=origin_url)
        self.assertEqual(1, UserHomepage.objects.count())
        homepage_url = 'http://testserver' + reverse("crm_view_entities_list")

        url = reverse('users_make_homepage')

        response = self.client.post(url, data={'url': homepage_url})
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.content)

        self.assertEqual(response_data["ok"], True)

        self.assertEqual(1, UserHomepage.objects.count())
        homepage = UserHomepage.objects.all()[0]

        self.assertEqual(homepage.user, self.user)
        self.assertEqual(homepage.url, homepage_url)

    def test_is_allowed_homepage(self):
        """set is_allowed_homepage utility"""
        self.assertEqual(True, is_allowed_homepage(reverse("crm_view_entities_list")))
        self.assertEqual(True, is_allowed_homepage(reverse("users_favorites_list")))
        self.assertEqual(False, is_allowed_homepage(reverse("quick_search")))
        self.assertEqual(True, is_allowed_homepage('http://testserver' + reverse("crm_view_entities_list")))

    def test_view_homepage(self):
        """view homepage"""
        homepage_url = 'http://testserver' + reverse("crm_view_entities_list")
        homepage = mommy.make(UserHomepage, user=self.user, url=homepage_url)
        
        response = self.client.get(reverse("balafon_homepage"))
        
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], homepage.url)

    def test_view_homepage_redirect_loop(self):
        """view homepage can not cause dead loop"""
        url = 'http://testserver' + reverse("balafon_homepage")
        mommy.make(UserHomepage, user=self.user, url=url)

        response = self.client.get(url)

        self.assertEqual(302, response.status_code)
        redirect_url = reverse("crm_board_panel")
        self.assertTrue(response['Location'].find(redirect_url) >= 0)

    def test_view_homepage_redirect_invalid(self):
        """view homepage do not redirect to invalid hompeages"""
        url = 'http://testserver' + reverse("quick_search")
        mommy.make(UserHomepage, user=self.user, url=url)

        response = self.client.get(reverse("balafon_homepage"))

        self.assertEqual(302, response.status_code)
        redirect_url = reverse("crm_board_panel")
        self.assertTrue(response['Location'].find(redirect_url) >= 0)
        
    def test_view_homepage_not_set(self):
        """view homepage go to default if nothing is set"""
        response = self.client.get(reverse("balafon_homepage"))
        
        self.assertEqual(302, response.status_code)
        redirect_url = reverse("crm_board_panel")
        self.assertTrue(response['Location'].find(redirect_url) >= 0)


@skipIf(
    "balafon.Users.context_processors.user_config" not in settings.TEMPLATE_CONTEXT_PROCESSORS,
    "User context processor not set"
)
class CustomMenuTestCase(BaseTestCase):
    """Test if custom menus are properly displayed"""

    def test_view_custom_menu(self):
        """It should display custom menu"""
        menu = mommy.make(CustomMenu, label="MON MENU")
        menu_item = mommy.make(CustomMenuItem, parent=menu, label="MON ELEMENT", url='/test')

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)

    def test_view_custom_menu_planning(self):
        """It should display custom menu"""
        menu = mommy.make(CustomMenu, label="MON MENU", position=CustomMenu.POSITION_PLANNING)
        menu_item = mommy.make(CustomMenuItem, parent=menu, label="MON ELEMENT", url='/test')

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)
        self.assertNotContains(response, menu_item.label)

        today = date.today()
        response = self.client.get(
            reverse("crm_actions_of_day", args=[today.year, today.month, today.day]),
            follow=True
        )
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)

    def test_view_custom_menu_reverse(self):
        """It should display custom menu"""
        menu = mommy.make(CustomMenu, label="MON MENU", position=CustomMenu.POSITION_MENU)
        menu_item = mommy.make(
            CustomMenuItem,
            parent=menu,
            label="MON ELEMENT",
            reverse='crm_actions_of_day',
            reverse_kwargs='year,month,day'
        )

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)
        self.assertNotContains(response, menu_item.label)

        today = date.today()
        response = self.client.get(
            reverse("crm_actions_of_day", kwargs={'year': today.year, 'month': today.month, 'day': today.day}),
            follow=True
        )
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)

    def test_view_custom_menu_reverse_more_kwargs(self):
        """It should display custom menu"""
        menu = mommy.make(CustomMenu, label="MON MENU", position=CustomMenu.POSITION_MENU)
        menu_item = mommy.make(
            CustomMenuItem,
            parent=menu,
            label="MON ELEMENT",
            reverse='crm_actions_of_month',
            reverse_kwargs='year,month'
        )

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)
        self.assertNotContains(response, menu_item.label)

        today = date.today()
        response = self.client.get(
            reverse("crm_actions_of_day", kwargs={'year': today.year, 'month': today.month, 'day': today.day}),
            follow=True
        )
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)

    def test_view_custom_menu_reverse_missing_kwargs(self):
        """It should not display custom menu"""
        menu = mommy.make(CustomMenu, label="MON MENU", position=CustomMenu.POSITION_MENU)
        menu_item = mommy.make(
            CustomMenuItem,
            parent=menu,
            label="MON ELEMENT",
            reverse='crm_actions_of_day',
            reverse_kwargs='year,month,day'
        )

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)
        self.assertNotContains(response, menu_item.label)

        today = date.today()
        response = self.client.get(
            reverse("crm_actions_of_month", kwargs={'year': today.year, 'month': today.month}),
            follow=True
        )
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)
        self.assertNotContains(response, menu_item.label)

    def test_view_custom_menu_reverse_missing_kwargs_defaults(self):
        """It should display custom menu"""
        menu = mommy.make(CustomMenu, label="MON MENU", position=CustomMenu.POSITION_MENU)
        menu_item = mommy.make(
            CustomMenuItem,
            parent=menu,
            label="MON ELEMENT",
            reverse='crm_actions_of_day',
            reverse_kwargs='year:2015,month:1,day:1'
        )

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)

        today = date.today()
        response = self.client.get(
            reverse("crm_actions_of_month", kwargs={'year': today.year, 'month': today.month}),
            follow=True
        )
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)
        self.assertContains(
            response, reverse("crm_actions_of_day", kwargs={'year': today.year, 'month': today.month, 'day': 1})
        )

    def test_view_custom_menu_empty(self):
        """It should nor display the menu"""
        menu = mommy.make(CustomMenu)

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)

    def test_view_custom_menu_user(self):
        """It should display the menu"""
        menu = mommy.make(CustomMenu)
        menu_item = mommy.make(CustomMenuItem, parent=menu, url='/test')
        menu_item.only_for_users.add(self.user)
        menu_item.save()

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertContains(response, menu.label)
        self.assertContains(response, menu_item.label)

    def test_view_custom_menu_other_user(self):
        """It should not display the menu"""
        menu = mommy.make(CustomMenu)
        menu_item = mommy.make(CustomMenuItem, parent=menu, url='/test')
        menu_item.only_for_users.add(mommy.make(models.User))
        menu_item.save()

        response = self.client.get(reverse("balafon_homepage"), follow=True)
        self.assertEqual(200, response.status_code)

        self.assertNotContains(response, menu.label)
        self.assertNotContains(response, menu_item.label)

