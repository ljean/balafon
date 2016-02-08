# -*- coding: utf-8 -*-
"""test we can search contact by entity"""

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings


from model_mommy import mommy

from coop_cms.tests import BeautifulSoup

from balafon.Crm import models

from balafon.Search.tests import BaseTestCase


@override_settings(BALAFON_SEARCH_NB_IN_PAGE=10)
class SearchPaginationTest(BaseTestCase):
    """search that the results are paginated fields"""

    @override_settings()
    def test_search_no_pagination(self):
        """less than default number, it should not display pagination"""
        del settings.BALAFON_SEARCH_NB_IN_PAGE  # use default settings

        entities = [mommy.make(models.Entity, name=u"tiny{0:02d}#".format(i)) for i in range(50)]

        url = reverse('search')

        data = {"gr0-_-entity_name-_-0": 'tiny'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('ul.pagination')))

        for entity in entities:
            self.assertContains(response, entity.name)

    @override_settings()
    def test_search_default_pagination(self):
        """more than default number, it should display pagination"""
        del settings.BALAFON_SEARCH_NB_IN_PAGE  # use default settings

        entities = [mommy.make(models.Entity, name=u"tiny{0:02d}#".format(i)) for i in range(51)]

        url = reverse('search')

        data = {"gr0-_-entity_name-_-0": 'tiny'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select('ul.pagination')))

        for entity in entities[:-1]:
            self.assertContains(response, entity.name)
        self.assertNotContains(response, entities[-1].name)

    def test_search_custom_pagination_less(self):
        """less than custom number, it should not display pagination"""

        entities = [mommy.make(models.Entity, name=u"tiny{0:02d}#".format(i)) for i in range(10)]

        url = reverse('search')

        data = {"gr0-_-entity_name-_-0": 'tiny'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(0, len(soup.select('ul.pagination')))

        for entity in entities:
            self.assertContains(response, entity.name)

    def test_search_custom_pagination(self):
        """more than custom number, it should display pagination"""

        entities = [mommy.make(models.Entity, name=u"tiny{0:02d}#".format(i)) for i in range(11)]

        url = reverse('search')

        data = {"gr0-_-entity_name-_-0": 'tiny'}

        response = self.client.post(url, data=data)
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(1, len(soup.select('ul.pagination')))

        for entity in entities[:-1]:
            self.assertContains(response, entity.name)
        self.assertNotContains(response, entities[-1].name)
