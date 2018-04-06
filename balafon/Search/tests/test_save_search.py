# -*- coding: utf-8 -*-
"""test we can save a search"""

from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse

from coop_cms.tests import BeautifulSoup
from model_mommy import mommy

from balafon.Crm import models

from balafon.Search.tests import BaseTestCase
from balafon.Search.models import Search, SearchField, SearchGroup


class SearchSaveTest(BaseTestCase):
    """Save a search"""

    def test_view_name_existing_search(self):
        """test view save an existing search: name is set"""
        search = mommy.make(Search, name="ABC")

        url = reverse("search_save", args=[search.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("#id_name")), 1)
        self.assertEqual(soup.select("#id_name")[0]["value"], "ABC")

        self.assertEqual(len(soup.select("#id_search_id")), 1)
        self.assertEqual(soup.select("#id_search_id")[0]["value"], '{0}'.format(search.id))

    def test_view_name_new_search(self):
        """test view save a new search: name is empty"""

        url = reverse("search_save", args=[0])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select("#id_name")), 1)
        self.assertEqual(len(soup.select("#id_search_id")), 1)
        self.assertEqual(soup.select("#id_name")[0].get("value", ""), "")

        self.assertEqual(len(soup.select("#id_search_id")), 1)
        self.assertEqual(soup.select("#id_search_id")[0]["value"], "0")

    def test_save_search(self):
        """save a new search"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
        }
        data = {
            'name': "ABC",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)

        self.assertEqual(Search.objects.count(), 1)
        search_1 = Search.objects.all()[0]

        self.assertEqual(response.status_code, 200)
        next_url = reverse("search", args=[search_1.id])
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(next_url)
        )

        self.assertEqual(search_1.name, data["name"])
        self.assertEqual(search_1.searchgroup_set.count(), 1)

        search_group = search_1.searchgroup_set.all()[0]
        self.assertEqual(search_group.name, "gr0")

        self.assertEqual(search_group.searchfield_set.count(), 1)
        search_field = search_group.searchfield_set.all()[0]
        self.assertEqual(search_field.field, "group")
        self.assertEqual(search_field.value, "{0}".format(group1.id))
        self.assertEqual(search_field.is_list, False)

    def test_open_search(self):
        """test open an existing search"""

        group1 = mommy.make(models.Group)

        search = mommy.make(Search)
        search_group = mommy.make(SearchGroup, name="gr0", search=search)
        mommy.make(
            SearchField, field='group', value='{0}'.format(group1.id), is_list=False, search_group=search_group
        )

        url = reverse("search", args=[search.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        self.assertEqual(soup.select("input[name=gr0-_-group-_-0]")[0]["value"], '{0}'.format(group1.id))

    def test_open_multi_search(self):
        """open an existing search on several groups"""

        group1 = mommy.make(models.Group, name="AAA")
        group2 = mommy.make(models.Group, name="BBB")
        group3 = mommy.make(models.Group, name="ABB")

        search = mommy.make(Search)
        search_group = mommy.make(SearchGroup, name="gr0", search=search)
        value = "['{0}', '{1}']".format(group1.id, group2.id)
        mommy.make(
            SearchField, field='all_groups', value=value, is_list=True, search_group=search_group
        )

        url = reverse("search", args=[search.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        nodes = soup.select("select[name=gr0-_-all_groups-_-0] option")
        self.assertEqual([int(n["value"]) for n in nodes], [group1.id, group3.id, group2.id])

        selected_nodes = soup.select("select[name=gr0-_-all_groups-_-0] option[selected=selected]")
        self.assertEqual([int(n["value"]) for n in selected_nodes], [group1.id, group2.id])

    def test_view_multi_search_only_1(self):
        """open existing search on several groups but only is set"""

        group1 = mommy.make(models.Group, name="AAA")
        group2 = mommy.make(models.Group, name="BBB")
        group3 = mommy.make(models.Group, name="ABB")

        search = mommy.make(Search)
        search_group = mommy.make(SearchGroup, name="gr0", search=search)
        value = "['{0}']".format(group1.id)
        mommy.make(
            SearchField, field='all_groups', value=value, is_list=True, search_group=search_group)

        url = reverse("search", args=[search.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        nodes = soup.select("select[name=gr0-_-all_groups-_-0] option")
        self.assertEqual([int(n["value"]) for n in nodes], [group1.id, group3.id, group2.id])

        selected_nodes = soup.select("select[name=gr0-_-all_groups-_-0] option[selected=selected]")
        self.assertEqual([int(n["value"]) for n in selected_nodes], [group1.id])

    def test_view_multi_search_none(self):
        """open an existing search no groups defined"""

        group1 = mommy.make(models.Group, name="AAA")
        group2 = mommy.make(models.Group, name="BBB")
        group3 = mommy.make(models.Group, name="ABB")

        search = mommy.make(Search)
        search_group = mommy.make(SearchGroup, name="gr0", search=search)
        value = "[]"
        mommy.make(
            SearchField, field='all_groups', value=value, is_list=True, search_group=search_group)

        url = reverse("search", args=[search.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content)

        nodes = soup.select("select[name=gr0-_-all_groups-_-0] option")
        self.assertEqual([int(n["value"]) for n in nodes], [group1.id, group3.id, group2.id])

        selected_nodes = soup.select("select[name=gr0-_-all_groups-_-0] option[selected=selected]")
        self.assertEqual(selected_nodes, [])

    def test_save_search_multi_values(self):
        """save a search with multiple values fields"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)
        group2 = mommy.make(models.Group)

        groups = [group1.id, group2.id]
        search_data = {
            "gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups],
        }
        data = {
            'name': "ABC",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)

        self.assertEqual(Search.objects.count(), 1)
        search_1 = Search.objects.all()[0]

        self.assertEqual(response.status_code, 200)
        next_url = reverse("search", args=[search_1.id])
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(next_url)
        )

        self.assertEqual(search_1.name, data["name"])
        self.assertEqual(search_1.searchgroup_set.count(), 1)

        search_group = search_1.searchgroup_set.all()[0]
        self.assertEqual(search_group.name, "gr0")

        self.assertEqual(search_group.searchfield_set.count(), 1)
        search_field = search_group.searchfield_set.all()[0]
        self.assertEqual(search_field.field, "all_groups")
        self.assertEqual(search_field.value, "['{0}', '{1}']".format(*groups))
        self.assertEqual(search_field.is_list, True)

    def test_save_search_multi_values_only_1(self):
        """save a search with multiple values fields: only 1 group is set"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)
        mommy.make(models.Group)

        groups = [group1.id]
        search_data = {
            "gr0-_-all_groups-_-0": ['{0}'.format(x) for x in groups],
        }
        data = {
            'name': "ABC",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)

        self.assertEqual(Search.objects.count(), 1)
        search_1 = Search.objects.all()[0]

        self.assertEqual(response.status_code, 200)
        next_url = reverse("search", args=[search_1.id])
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(next_url)
        )

        self.assertEqual(search_1.name, data["name"])
        self.assertEqual(search_1.searchgroup_set.count(), 1)

        search_group = search_1.searchgroup_set.all()[0]
        self.assertEqual(search_group.name, "gr0")

        self.assertEqual(search_group.searchfield_set.count(), 1)
        search_field = search_group.searchfield_set.all()[0]
        self.assertEqual(search_field.field, "all_groups")
        self.assertEqual(search_field.value, "['{0}']".format(group1.id))
        self.assertEqual(search_field.is_list, True)

    def test_save_search_multi_values_none(self):
        """save a search with multiple values fields: empty"""
        url = reverse("search_save", args=[0])

        search_data = {
            "gr0-_-all_groups-_-0": '',
        }
        data = {
            'name': "ABC",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)

        self.assertEqual(Search.objects.count(), 0)

        self.assertEqual(response.status_code, 200)

    def test_save_search_several_groups(self):
        """save search on several groups"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)
        group2 = mommy.make(models.Group)
        group3 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
            "gr0-_-group-_-1": group2.id,
            "gr1-_-group-_-0": group3.id,
        }
        data = {
            'name': "ABC",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)

        self.assertEqual(Search.objects.count(), 1)
        search_1 = Search.objects.all()[0]

        self.assertEqual(response.status_code, 200)
        next_url = reverse("search", args=[search_1.id])
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(next_url)
        )

        self.assertEqual(search_1.name, data["name"])
        self.assertEqual(search_1.searchgroup_set.count(), 2)

        search_group = search_1.searchgroup_set.filter(name="gr0")[0]
        self.assertEqual(search_group.name, "gr0")
        self.assertEqual(search_group.searchfield_set.count(), 2)

        search_fields = search_group.searchfield_set.all().order_by("value")
        search_field = search_fields[0]
        self.assertEqual(search_field.field, "group")
        self.assertEqual(search_field.value, "{0}".format(group1.id))
        self.assertEqual(search_field.count, 0)
        search_field = search_fields[1]
        self.assertEqual(search_field.field, "group")
        self.assertEqual(search_field.value, "{0}".format(group2.id))
        self.assertEqual(search_field.count, 1)

        search_group = search_1.searchgroup_set.filter(name="gr1")[0]
        self.assertEqual(search_group.name, "gr1")
        self.assertEqual(search_group.searchfield_set.count(), 1)
        search_field = search_group.searchfield_set.all()[0]
        self.assertEqual(search_field.field, "group")
        self.assertEqual(search_field.value, "{0}".format(group3.id))
        self.assertEqual(search_field.count, 0)

    def test_no_name(self):
        """save search without name"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
        }
        data = {
            'name': "",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Search.objects.count(), 0)
        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".field-error")), 1)

    def test_already_existing_name(self):
        """save search with an existing name"""
        mommy.make(Search, name="ABC")
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
        }
        data = {
            'name': "ABC",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Search.objects.count(), 1)
        search_1 = Search.objects.all()[0]
        self.assertEqual(search_1.name, data["name"])
        self.assertEqual(search_1.searchgroup_set.count(), 0)

        soup = BeautifulSoup(response.content)
        self.assertEqual(len(soup.select(".field-error")), 1)

    def test_save_existing_search(self):
        """save an existing search"""
        search = mommy.make(Search, name="ABC")
        url = reverse("search_save", args=[search.id])

        group1 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
        }
        data = {
            'name': search.name,
            'search_id': search.id,
            "search_fields": json.dumps(search_data),
        }

        response = self.client.post(url, data=data)

        self.assertEqual(Search.objects.count(), 1)
        search_1 = Search.objects.all()[0]

        self.assertEqual(response.status_code, 200)
        next_url = reverse("search", args=[search_1.id])
        self.assertContains(
            response,
            '<script>$.colorbox.close(); window.location="{0}";</script>'.format(next_url)
        )

        self.assertEqual(search_1.name, data["name"])
        self.assertEqual(search_1.searchgroup_set.count(), 1)

        search_group = search_1.searchgroup_set.all()[0]
        self.assertEqual(search_group.name, "gr0")

        self.assertEqual(search_group.searchfield_set.count(), 1)
        search_field = search_group.searchfield_set.all()[0]
        self.assertEqual(search_field.field, "group")
        self.assertEqual(search_field.value, "{0}".format(group1.id))

    def test_save_search_anonymous(self):
        """save search as anonymous user"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
        }
        data = {
            'name': "Test",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        self.client.logout()

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_save_search_non_staff(self):
        """save search as non-staff user"""
        url = reverse("search_save", args=[0])

        group1 = mommy.make(models.Group)

        search_data = {
            "gr0-_-group-_-0": group1.id,
        }
        data = {
            'name': "Test",
            'search_id': 0,
            "search_fields": json.dumps(search_data),
        }

        self.user.is_staff = False
        self.user.save()

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
