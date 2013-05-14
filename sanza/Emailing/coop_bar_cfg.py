# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from coop_bar.utils import make_link
from coop_cms import coop_bar_cfg as cms_cfg

def back_to_newsletters(request, context):
    if request.user.is_authenticated():
        return make_link(reverse("emailing_newsletter_list"), _(u'Back to newsletters'), 'fugue/table--arrow.png',
            classes=['icon', 'alert_on_click'])


def load_commands(coop_bar):
    
    coop_bar.register([
        [cms_cfg.django_admin, cms_cfg.django_admin_edit_article, cms_cfg.django_admin_navtree, cms_cfg.view_all_articles],
        [back_to_newsletters, cms_cfg.edit_newsletter, cms_cfg.cancel_edit_newsletter, cms_cfg.save_newsletter,
            cms_cfg.change_newsletter_template, cms_cfg.test_newsletter],
        [cms_cfg.cms_edit, cms_cfg.cms_view, cms_cfg.cms_save, cms_cfg.cms_cancel],
        [cms_cfg.cms_new_article, cms_cfg.cms_new_link, cms_cfg.cms_article_settings, cms_cfg.cms_set_homepage],
        [cms_cfg.cms_publish],
        [cms_cfg.cms_media_library, cms_cfg.cms_upload_image, cms_cfg.cms_upload_doc],
        [cms_cfg.log_out]
    ])
    
    coop_bar.register_header(cms_cfg.cms_extra_js)
