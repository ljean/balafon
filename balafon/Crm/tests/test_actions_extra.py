# -*- coding: utf-8 -*-
"""unit testing"""

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-branches

from django.contrib.auth.models import User
from django.urls import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.unit_tests import TestCase
from balafon.Crm import models
from balafon.Crm.tests import BaseTestCase


class DoActionTest(BaseTestCase):
    """Do action"""

    def test_do_action(self):
        """do it"""
        action = mommy.make(models.Action, done=False)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(action.done, False)

        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'done': True})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, True)

    def test_undo_action(self):
        """undo it"""
        action = mommy.make(models.Action, done=True)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(action.done, True)

        response = self.client.post(reverse('crm_do_action', args=[action.id]), data={'done': False})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, reverse("crm_board_panel"))
        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.done, False)

    def test_view_action_warning_not_in_charge(self):
        """warning if not in charge"""
        user = mommy.make(User, is_active=True, is_staff=True, last_name="L", first_name="F")
        team_member = mommy.make(models.TeamMember, user=user)
        action = mommy.make(models.Action, done=True, in_charge=team_member)
        response = self.client.get(reverse('crm_do_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, "warning")


class ActionAutoGenerateNumberTestCase(TestCase):
    """test number can be autogenerated"""

    def test_create_auto_number(self):
        """create auto number"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)

    def test_create_several_auto_number(self):
        """create several numbers"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 2)
        no_gen_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=False)
        action = models.Action.objects.create(type=no_gen_type, subject="a")
        self.assertEqual(action.number, 0)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 3)

    def test_save_several_auto_number(self):
        """save : number is not changed"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)
        action.save()
        self.assertEqual(action.number, 1)

    def test_create_several_auto_types(self):
        """number generated by type"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=True)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 1)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 2)
        no_gen_type = mommy.make(models.ActionType, last_number=27, number_auto_generated=True)
        action = models.Action.objects.create(type=no_gen_type, subject="a")
        self.assertEqual(action.number, 28)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 3)

    def test_create_no_number_generation(self):
        """create action with no auto generation"""
        action_type = mommy.make(models.ActionType, last_number=0, number_auto_generated=False)
        action = models.Action.objects.create(type=action_type, subject="a")
        self.assertEqual(action.number, 0)


class ActionMenuTest(BaseTestCase):
    """Custom menu action"""

    def test_action_menu(self):
        """test custom menus are displayed"""
        action_type1 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_do_action', a_attrs='class="colorbox-form"', order_index=2
        )

        menu2 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="remove", label="DELETE ME", view_name='crm_delete_action', a_attrs='target="_blank"', order_index=1
        )

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 2)

        self.assertEqual(li_tags[0].text.strip(), menu2.label)
        self.assertEqual(li_tags[0].a['target'], '_blank')
        self.assertEqual(li_tags[0].a['href'], reverse('crm_delete_action', args=[action.id]))
        self.assertEqual(li_tags[0].a.i['class'], ['fas', 'fa-{0}'.format(menu2.icon)])

        self.assertEqual(li_tags[1].text.strip(), menu1.label)
        self.assertEqual(li_tags[1].a['class'], ['colorbox-form'])
        self.assertEqual(li_tags[1].a['href'], reverse('crm_do_action', args=[action.id]))
        self.assertEqual(li_tags[1].a.i['class'], ['fas', 'fa-{0}'.format(menu1.icon)])

    def test_action_menu_status(self):
        """test custom menus are displayed"""
        action_type1 = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_type1.allowed_status.add(action_status1)
        action_type1.allowed_status.add(action_status2)
        action_type1.save()

        action = mommy.make(models.Action, type=action_type1, status=action_status1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_do_action', a_attrs='class="colorbox-form"', order_index=2
        )
        menu1.only_for_status.add(action_status1)
        menu1.save()

        menu2 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="remove", label="DELETE ME", view_name='crm_delete_action', a_attrs='target="_blank"', order_index=1
        )
        menu2.only_for_status.add(action_status2)
        menu2.save()

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 1)

        self.assertEqual(li_tags[0].text.strip(), menu1.label)
        self.assertEqual(li_tags[0].a['class'], ['colorbox-form'])
        self.assertEqual(li_tags[0].a['href'], reverse('crm_do_action', args=[action.id]))
        self.assertEqual(li_tags[0].a.i['class'], ['fas', 'fa-{0}'.format(menu1.icon)])

    def test_action_menu_status_ony_empty(self):
        """test custom menus are displayed"""
        action_type1 = mommy.make(models.ActionType)
        action_status1 = mommy.make(models.ActionStatus)
        action_status2 = mommy.make(models.ActionStatus)
        action_type1.allowed_status.add(action_status1)
        action_type1.allowed_status.add(action_status2)
        action_type1.save()

        action = mommy.make(models.Action, type=action_type1, status=action_status1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_do_action', a_attrs='class="colorbox-form"', order_index=2
        )

        menu2 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="remove", label="DELETE ME", view_name='crm_delete_action', a_attrs='target="_blank"', order_index=1
        )
        menu2.only_for_status.add(action_status2)
        menu2.save()

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 1)

        self.assertEqual(li_tags[0].text.strip(), menu1.label)
        self.assertEqual(li_tags[0].a['class'], ['colorbox-form'])
        self.assertEqual(li_tags[0].a['href'], reverse('crm_do_action', args=[action.id]))
        self.assertEqual(li_tags[0].a.i['class'], ['fas', 'fa-{0}'.format(menu1.icon)])

    def test_action_menu_one_not_set(self):
        """test custom menus are displayed only for associated types"""
        action_type1 = mommy.make(models.ActionType)
        action_type2 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_do_action', a_attrs='class="colorbox-form"', order_index=2
        )

        mommy.make(
            models.ActionMenu, action_type=action_type2,
            icon="remove", label="DELETE ME", view_name='crm_delete_action', a_attrs='target="_blank"', order_index=1
        )

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 1)

        self.assertEqual(li_tags[0].text.strip(), menu1.label)
        self.assertEqual(li_tags[0].a['class'], ['colorbox-form'])
        self.assertEqual(li_tags[0].a['href'], reverse('crm_do_action', args=[action.id]))
        self.assertEqual(li_tags[0].a.i['class'], ['fas', 'fa-{0}'.format(menu1.icon)])

    def test_action_menu_no_type(self):
        """test action is displayed if no type defined"""
        action = mommy.make(models.Action, type=None)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 0)

    def test_action_no_menu(self):
        """test action is displayed if no custom menu"""
        action_type1 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 0)

    def test_action_inavlid_view_name(self):
        """test custom menus are displayed only for associated types"""
        action_type1 = mommy.make(models.ActionType)

        action = mommy.make(models.Action, type=action_type1)
        entity = mommy.make(models.Entity)
        action.entities.add(entity)
        action.save()

        menu1 = mommy.make(
            models.ActionMenu, action_type=action_type1,
            icon="cog", label="DO ME", view_name='crm_blabla_dummy', a_attrs='class="colorbox-form"', order_index=2
        )

        url = reverse('crm_view_entity', args=[entity.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)

        li_tags = soup.select('.ut-custom-action-menu-item')
        self.assertEqual(len(li_tags), 1)

        self.assertEqual(li_tags[0].text.strip(), menu1.label)
        self.assertEqual(li_tags[0].a['class'], ['colorbox-form'])
        self.assertEqual(li_tags[0].a['href'], '')
        self.assertEqual(li_tags[0].a.i['class'], ['fas', 'fa-{0}'.format(menu1.icon)])


class CloneActionTest(BaseTestCase):
    """clone an action"""

    def test_view_clone_action_1_type(self):
        """it should display hidden input for the only allowed type"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        html_fields = soup.select("#id_action_type")
        self.assertEqual(1, len(html_fields))
        self.assertEqual(html_fields[0]["type"], "hidden")
        self.assertEqual(html_fields[0]["value"], "{0}".format(action_type_2.id))

    def test_view_clone_action_2_types(self):
        """it should display a select with allowed types"""
        action_type_1 = mommy.make(models.ActionType, order_index=1)
        action_type_2 = mommy.make(models.ActionType, order_index=2)
        action_type_3 = mommy.make(models.ActionType, order_index=3)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.next_action_types.add(action_type_3)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        html_fields = soup.select("#id_action_type")
        self.assertEqual(1, len(html_fields))
        options = html_fields[0].select("option")
        self.assertEqual(len(options), 2)
        self.assertEqual(options[0]["value"], "{0}".format(action_type_2.id))
        self.assertEqual(options[1]["value"], "{0}".format(action_type_3.id))

    def test_view_clone_action_no_types(self):
        """it should display an empty select"""
        action_type_1 = mommy.make(models.ActionType, order_index=1)

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        html_fields = soup.select("#id_action_type")
        self.assertEqual(1, len(html_fields))
        options = html_fields[0].select("option")
        self.assertEqual(len(options), 0)

    def test_view_clone_action_type_is_none(self):
        """it should display 404"""
        action = mommy.make(models.Action, type=None)
        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(404, response.status_code)

    def test_view_clone_anonymous(self):
        """it should display hidden input for the only allowed type"""
        self.client.logout()

        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(302, response.status_code)

    def test_view_clone_non_staff(self):
        """it should display hidden input for the only allowed type"""
        self.user.is_staff = False
        self.user.save()

        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        response = self.client.get(reverse('crm_clone_action', args=[action.id]))
        self.assertEqual(302, response.status_code)

    def test_post_clone_action(self):
        """it should clone"""
        action_status_1 = mommy.make(models.ActionStatus)
        action_type_1 = mommy.make(models.ActionType)
        action_type_1.allowed_status.add(action_status_1)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)
        team_member = mommy.make(models.TeamMember)

        action = mommy.make(models.Action, type=action_type_1, done=True, status=action_status_1, in_charge=team_member)

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertContains(response, 'reload: {0}'.format(reverse('crm_edit_action', args=[new_action.id])))

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(new_action.in_charge, original_action.in_charge)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.status, None)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)

    def test_post_clone_action_dont_affect(self):
        """it should clone without assigning the user to the task"""
        action_status_1 = mommy.make(models.ActionStatus)
        action_type_1 = mommy.make(models.ActionType)
        action_type_1.allowed_status.add(action_status_1)
        action_type_2 = mommy.make(models.ActionType, not_assigned_when_cloned=True)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)

        team_member = mommy.make(models.TeamMember)

        action = mommy.make(models.Action, type=action_type_1, done=True, status=action_status_1, in_charge=team_member)

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertContains(response, 'reload: {0}'.format(reverse('crm_edit_action', args=[new_action.id])))

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.in_charge, None)
        self.assertEqual(new_action.status, None)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)

    def test_post_clone_action_default_status(self):
        """it should clone"""
        action_status = mommy.make(models.ActionStatus)
        action_status_1 = mommy.make(models.ActionStatus)
        action_type_1 = mommy.make(models.ActionType)
        action_type_1.allowed_status.add(action_status_1)
        action_type_2 = mommy.make(models.ActionType, default_status=action_status)
        action_type_2.allowed_status.add(action_status)
        action_type_2.save()
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        contact = mommy.make(models.Contact)
        entity = mommy.make(models.Entity)

        action = mommy.make(models.Action, type=action_type_1, done=True, status=action_status_1)

        action.contacts.add(contact)
        action.entities.add(entity)

        action.save()

        data = {
            'action_type': action_type_2.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(2, models.Action.objects.count())
        original_action = models.Action.objects.get(type=action_type_1)
        new_action = models.Action.objects.get(type=action_type_2)

        self.assertContains(response, 'reload: {0}'.format(reverse('crm_edit_action', args=[new_action.id])))

        self.assertEqual(original_action.subject, new_action.subject)
        self.assertEqual(new_action.parent, original_action)
        self.assertEqual(new_action.contacts.count(), 1)
        self.assertEqual(new_action.entities.count(), 1)
        self.assertEqual(list(original_action.contacts.all()), list(new_action.contacts.all()))
        self.assertEqual(list(original_action.entities.all()), list(new_action.entities.all()))
        self.assertEqual(new_action.done, False)
        self.assertEqual(original_action.done, True)
        self.assertEqual(new_action.status, action_status)
        self.assertEqual(new_action.planned_date, original_action.planned_date)
        self.assertEqual(new_action.amount, original_action.amount)

    def test_post_clone_action_anonymous(self):
        """it should not clone and redirect to login page"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': action_type_2.id
        }

        self.client.logout()

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_action_non_staff(self):
        """it should not clone and redirect to login page"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': action_type_2.id
        }

        self.user.is_staff = False
        self.user.save()

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(302, response.status_code)

        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_action_invalid(self):
        """it should not clone and show error"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': 'bla'
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".error-msg")), 1)
        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_no_type(self):
        """it should not clone and show error"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': ''
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".error-msg")), 1)
        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_other_type(self):
        """it should not clone and show error"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_3 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=action_type_1)

        data = {
            'action_type': action_type_3.id
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".error-msg")), 1)
        self.assertEqual(1, models.Action.objects.count())

    def test_post_clone_type_is_none(self):
        """it should not clone and 404"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        action = mommy.make(models.Action, type=None)

        data = {
            'action_type': action_type_2,
        }

        response = self.client.post(
            reverse('crm_clone_action', args=[action.id]),
            data=data
        )
        self.assertEqual(404, response.status_code)
        self.assertEqual(1, models.Action.objects.count())

    def test_action_menu(self):
        """it should create and delete an action menu"""
        action_type_1 = mommy.make(models.ActionType)
        action_type_2 = mommy.make(models.ActionType)
        action_type_1.next_action_types.add(action_type_2)
        action_type_1.save()

        self.assertEqual(1, models.ActionMenu.objects.count())
        menu = models.ActionMenu.objects.all()[0]
        self.assertEqual(menu.action_type, action_type_1)
        self.assertEqual(menu.view_name, 'crm_clone_action')

        action_type_1.next_action_types.clear()
        action_type_1.save()

        self.assertEqual(0, models.ActionMenu.objects.count())


class MailtoActionTest(BaseTestCase):
    """Send email to action contacts"""

    def test_mailto_action_contact(self):
        """send email to the ony contact"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Test&body=Hello")

    def test_mailto_action_entity(self):
        """send email to the ony entity"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)
        entity = mommy.make(models.Entity, email="toto@toto.fr")
        action.entities.add(entity)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Test&body=Hello")

    def test_mailto_action_several(self):
        """send email to the several contacts"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)

        entity = mommy.make(models.Entity, email="entity@toto.fr")

        contact1 = mommy.make(models.Contact, email="toto@toto.fr")
        contact2 = mommy.make(models.Contact, email="c2@toto.fr")
        contact3 = mommy.make(models.Contact, entity=entity, email="")
        contact4 = mommy.make(models.Contact, entity=entity, email="c3@toto.fr")
        contact5 = mommy.make(models.Contact)
        contact6 = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact1)
        action.contacts.add(contact2)
        action.contacts.add(contact3)
        action.contacts.add(contact4)
        action.contacts.add(contact5)
        action.contacts.add(contact6)

        entity = mommy.make(models.Entity, email="blabla@toto.fr")
        action.entities.add(entity)

        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            "mailto:blabla@toto.fr,c2@toto.fr,c3@toto.fr,entity@toto.fr,toto@toto.fr?subject=Test&body=Hello"
        )

    def test_mailto_action_bcc(self):
        """send email to the ony contact"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)

        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", bcc=True, action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:?bcc=toto@toto.fr&subject=Test&body=Hello")

    def test_mailto_action_subject(self):
        """send email to the ony contact"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)

        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", subject="Subject", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Subject&body=Hello")

    def test_mailto_action_body(self):
        """send email to the ony contact"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)

        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello {{ action.subject }}", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Test&body=Hello%20Test")

    def test_mailto_action_no_settings(self):
        """send email to the ony contact"""

        # Give super user right in order to allow access to admin changelist
        self.user.is_superuser = True
        self.user.save()

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Test&body=")

    def test_mailto_action_no_settings_not_superuser(self):
        """send email to the ony contact"""

        # No super user right in order to forbid access to admin changelist
        self.user.is_superuser = False
        self.user.save()

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject=u"Test", type=type)
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Test&body=")

    def test_mailto_action_invalid_action(self):
        """send email to the ony contact"""

        type = mommy.make(models.ActionType)
        action = mommy.make(models.Action, subject="Test", type=type)
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id + 1])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_mailto_action_next_status(self):
        """send email to the ony contact"""

        type = mommy.make(models.ActionType)
        status2 = mommy.make(models.ActionStatus)
        status1 = mommy.make(models.ActionStatus, next_on_send=status2)
        action = mommy.make(models.Action, subject="Test", type=type, status=status1)
        contact = mommy.make(models.Contact, email="toto@toto.fr")
        action.contacts.add(contact)
        action.save()

        mommy.make(models.MailtoSettings, body_template="Hello", action_type=type)

        url = reverse("crm_mailto_action", args=[action.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "mailto:toto@toto.fr?subject=Test&body=Hello")

        action = models.Action.objects.get(id=action.id)
        self.assertEqual(action.status, status2)
