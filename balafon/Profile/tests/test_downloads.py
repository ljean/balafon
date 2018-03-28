# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import skipIf

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files import File

from coop_cms.models import ArticleCategory, Document
from model_mommy import mommy

from balafon.Crm import models
if "balafon.Profile" in settings.INSTALLED_APPS:
    from balafon.Profile.models import CategoryPermission
from balafon.Profile.tests import BaseTestCase
from balafon.Profile.utils import create_profile_contact


@skipIf(not ("balafon.Profile" in settings.INSTALLED_APPS), "registration not installed")
class DownloadTestCase(BaseTestCase):
    
    def test_download_private_permission(self):
        
        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        # Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        # Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        # Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
            
        # create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        # check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        # login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        # self.assertEquals(response['Content-Disposition'], "attachment; filename=unittest1.txt")
        self.assertEquals(response['Content-Type'], "text/plain")
        # TODO: This change I/O Exception in UnitTest
        # self.assertEqual(response.content, self._get_file().read())
        
        # logout and download
        self.client.logout()
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        
        redirect_url = response.redirect_chain[-1][0]
        login_url = reverse('auth_login')
        self.assertTrue(redirect_url.find(login_url) >= 0)
        
    def test_download_private_not_in_group(self):
        
        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        # Create group
        gr = models.Group.objects.create(name="Group")
        # Contact is not in the group: gr.contacts.add(contact)
        # gr.save()
        
        # Create category
        cat = ArticleCategory.objects.create(name="CAT")
        
        # Create CategoryPermission
        cat_perm = CategoryPermission.objects.create(category=cat)
        cat_perm.can_view_groups.add(gr)
        cat_perm.save()
            
        # create a public doc
        file_ = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file_, category=cat)
        
        # check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        # login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 403)
    
    def test_download_private_group_not_allowed(self):
        
        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        # Create group
        gr = models.Group.objects.create(name="Group")
        gr.contacts.add(contact)
        gr.save()
        
        # Create category
        cat = ArticleCategory.objects.create(name="CAT")
        cat_perm = CategoryPermission.objects.create(category=cat)
        
        # create a public doc
        file = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file, category=cat)    
        
        # check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        # login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 403)
        
    def test_download_private_no_permission(self):
        
        # Create contact for the user
        profile = create_profile_contact(self.user)
        contact = profile.contact
        
        # Create category
        cat = ArticleCategory.objects.create(name="CAT")
            
        # create a public doc
        file_ = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file_, category=cat)
        
        # check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        # login and download
        response = self.client.get(doc.get_download_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        # self.assertEquals(response['Content-Disposition'], "attachment; filename=unittest1.txt")
        self.assertEquals(response['Content-Type'], "text/plain")

    def test_download_private_no_contact_defined(self):
        
        # Create category
        cat = ArticleCategory.objects.create(name="CAT")
        cat_perm = CategoryPermission.objects.create(category=cat)
            
        # create a public doc
        file_ = File(self._get_file())
        doc = mommy.make(Document, is_private=True, file=file_, category=cat)
        
        # check the url
        private_url = reverse('coop_cms_download_doc', args=[doc.id])
        self.assertEqual(doc.get_download_url(), private_url)
        
        # login and download
        response = self.client.get(doc.get_download_url())
        self.assertEqual(response.status_code, 403)
