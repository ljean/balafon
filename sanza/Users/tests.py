# -*- coding: utf-8 -*-

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()
    
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission, AnonymousUser
from django.core.urlresolvers import reverse
from datetime import datetime
from model_mommy import mommy
from sanza.Crm import models
from django.core import management
from django.core import mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from bs4 import BeautifulSoup as BS4
from datetime import datetime, timedelta
from StringIO import StringIO
import sys
from sanza.Users.models import UserPreferences, Favorite
from django.contrib.contenttypes.models import ContentType
from django.template import Template, Context
from sanza.Crm.models import Action, ActionType
import json
import logging
from django.utils.translation import ugettext



class BaseTestCase(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.user = User.objects.create(username="toto")
        self.user.set_password("abc")
        self.user.is_staff = True
        self.user.save()
        self._login()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def _login(self):
        return self.client.login(username="toto", password="abc")


class NotifyDueActionsTestCase(BaseTestCase):
    
    def setUp(self):
        super(NotifyDueActionsTestCase, self).setUp()
        self._from_email = settings.DEFAULT_FROM_EMAIL
        settings.DEFAULT_FROM_EMAIL  = "toto@toto.fr"
        
    def tearDown(self):
        super(NotifyDueActionsTestCase, self).tearDown()
        settings.DEFAULT_FROM_EMAIL = self._from_email
    
    def now(self):
        if settings.USE_TZ:
            return datetime.now().replace(tzinfo=timezone.utc)
        else:
            return datetime.now()
    
    def _notify_due_actions(self, verbosity=0):
        buf = StringIO()
        sysout = sys.stdout
        sys.stdout = buf
        management.call_command('notify_due_actions', verbosity=verbosity, interactive=False, stdout=buf)
        buf.seek(0, 0)
        sys.stdout = sysout
        return buf.readlines()
    
    def test_notify_due_actions(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in actions:
            self.assertTrue(email.body.find(a.subject)>0)
            self.assertTrue(email.body.find(a.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
        
    
    def test_notify_due_actions_not_in_staff(self):
        u = mommy.make(User, is_active=True, is_staff=False, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
    
    def test_notify_due_actions_disabled(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=False)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
    
    def test_notify_due_actions_no_preferences(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        #up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False, in_charge=u)
        actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(0, len(mail.outbox))
        
    def test_notify_due_actions_some_in_future(self):
        tomorrow = datetime.today() + timedelta(1)
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=tomorrow, done=False, in_charge=u)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
            self.assertTrue(email.body.find(a.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
    
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            self.assertFalse(email.body.find(a.planned_date.strftime("%d/%m/%Y %H:%M"))>0)
    
    
    def test_notify_due_actions_some_not_in_charge(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=False)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            
    def test_notify_due_actions_some_done(self):
        tomorrow = datetime.today() + timedelta(1)
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=self.now(), done=True, in_charge=u)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            
    def test_notify_due_actions_some_not_planned(self):
        tomorrow = datetime.today() + timedelta(1)
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", done=False, in_charge=u)
        notified_actions= [a1, a2]
        other_actions= [a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
        
        for a in other_actions:
            self.assertFalse(email.body.find(a.subject)>0)
            
    
    def test_notify_due_actions_some_planned_date(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, notify_due_actions=True)
        a1 = mommy.make(models.Action, subject="AZERTY", planned_date=self.now(), done=False, in_charge=u)
        a2 = mommy.make(models.Action, subject="QSDFGH", planned_date=self.now(), done=False, in_charge=u)
        a3 = mommy.make(models.Action, subject="WXCVBN", planned_date=datetime.today(), done=False, in_charge=u)
        notified_actions= [a1, a2, a3]
        
        self._notify_due_actions(0)
        
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(email.to, [u.email])
        self.assertEqual(email.from_email, settings.DEFAULT_FROM_EMAIL)
        for a in notified_actions:
            self.assertTrue(email.body.find(a.subject)>0)
    
class UpdateFavoriteTestCase(BaseTestCase):
    
    def _template_content(self):
        return """
        {% load favorite_tags %}
        <ul class="users">
        {% for u in users %}
            <li>{{ u.username }}{% favorite_item u %}</li>
        {% endfor %}
        </ul>
        """
        
    def test_render_template(self):
        for i in xrange(5):
            mommy.make_one(User)
        
        template = Template(self._template_content())
        
        class DummyRequest(object): pass
        dummy_request = DummyRequest()
        setattr(dummy_request, 'user', self.user)
        context = {
            'users': User.objects.all(),
            'request': dummy_request,
        }
        
        html = template.render(Context(context))
        
    def test_render_template_not_logged(self):
        self.client.logout()
        for i in xrange(5):
            mommy.make_one(User)
        
        template = Template(self._template_content())
        
        class DummyRequest(object): pass
        dummy_request = DummyRequest()
        setattr(dummy_request, 'user', AnonymousUser())
        context = {
            'users': User.objects.all(),
            'request': dummy_request,
        }
        
        html = template.render(Context(context))
        
    def test_post_not_logged(self):
        self.client.logout()
        user = mommy.make_one(User)
        data = {
            'content_type': ContentType.objects.get_for_model(User).id,
            'object_id': user.id, 
        }
        url = reverse('users_toggle_favorite')
        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(response['Location'], "http://testserver/accounts/login/?next={0}".format(url))
        self.assertEqual(0, Favorite.objects.count())
        
        
    def test_post_add(self):
        logged_user = self.user
        faved_user = mommy.make_one(User)
        
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
        logged_user = self.user
        faved_user = mommy.make_one(User)
        
        user_ct = ContentType.objects.get_for_model(User)
        Favorite.objects.create(user=logged_user, object_id=faved_user.id,
            content_type=user_ct)
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
        logged_user = self.user
        
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
        logged_user = self.user
        faved_user = mommy.make_one(User)
        
        user_ct = ContentType.objects.get_for_model(User)
        
        data = {
            'content_type': 55555,
            'object_id': faved_user.id, 
        }
        response = self.client.post(reverse('users_toggle_favorite'), data)
        self.assertEqual(200, response.status_code)
        resp_data = json.loads(response.content)
        self.assertEqual(False, resp_data['success'])
        
        
class ListFavoritesTestCase(BaseTestCase):
    
    def test_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(302, response.status_code)
        self.assertTrue(response['Location'].find('login')>0)
        
    def test_empty_list(self):
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        
    def test_list(self):
        logged_user = self.user
        faved_users = [mommy.make_one(User, username='user-{0}'.format(i)) for i in xrange(5)]
        not_faved_users = [mommy.make_one(User, username='NOT-{0}'.format(i)) for i in xrange(5)]
        
        user_ct = ContentType.objects.get_for_model(User)
        for u in faved_users:
            Favorite.objects.create(user=logged_user, content_type=user_ct, object_id=u.id)
        
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        for u in faved_users:
            self.assertContains(response, u)
        for u in not_faved_users:
            self.assertNotContains(response, u)
            
    def test_someone_else_list(self):
        logged_user = self.user
        other_user = mommy.make_one(User)
        faved_users = [mommy.make_one(User, username='user-{0}'.format(i)) for i in xrange(5)]
        not_my_faved_users = [mommy.make_one(User, username='OTHER-{0}'.format(i)) for i in xrange(5)]
        
        user_ct = ContentType.objects.get_for_model(User)
        
        for u in faved_users:
            Favorite.objects.create(user=logged_user, content_type=user_ct, object_id=u.id)
        
        for u in not_my_faved_users:
            Favorite.objects.create(user=other_user, content_type=user_ct, object_id=u.id)
        
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        
        for u in faved_users:
            self.assertContains(response, u)
        for u in not_my_faved_users:
            self.assertNotContains(response, u)
            
    def test_list_different_cts(self):
        logged_user = self.user
        faved_users = [mommy.make_one(User, username='user-{0}'.format(i)) for i in xrange(5)]
        faved_groups = [mommy.make_one(Group, name='group-{0}'.format(i)) for i in xrange(5)]
        
        user_ct = ContentType.objects.get_for_model(User)
        group_ct = ContentType.objects.get_for_model(Group)
        
        for u in faved_users:
            Favorite.objects.create(user=logged_user, content_type=user_ct, object_id=u.id)
        
        for g in faved_groups:
            Favorite.objects.create(user=logged_user, content_type=group_ct, object_id=g.id)
        
        response = self.client.get(reverse('users_favorites_list'))
        self.assertEqual(200, response.status_code)
        for u in faved_users:
            self.assertContains(response, u)
        for u in faved_groups:
            self.assertContains(response, u)
        
class ActionInFavoriteTestCase(BaseTestCase):

    def test_create_action_in_favorite(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, message_in_favorites=True)
        
        at = mommy.make(ActionType, name=ugettext(u"Message"))
        a = mommy.make(Action, type=at)
        
        self.assertEqual(1, u.user_favorite_set.count())
        fav = u.user_favorite_set.all()[0]
        self.assertEqual(a, fav.content_object)
        
    def test_create_action_not_in_favorite(self):
        u = mommy.make(User, is_active=True, is_staff=True, email="toto@toto.fr")
        up = mommy.make(UserPreferences, user=u, message_in_favorites=False)
        
        at = mommy.make(ActionType, name=ugettext(u"Message"))
        a = mommy.make(Action, type=at)
        
        self.assertEqual(0, u.user_favorite_set.count())
        
        


    