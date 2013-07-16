# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('sanza.Emailing.views',
    url(r'^newsletters/$', 'newsletter_list', name='emailing_newsletter_list'),
    url(r'^view-emailing/(?P<emailing_id>\d+)/$', 'view_emailing', name='emailing_view'),
    url(r'^delete-emailing/(?P<emailing_id>\d+)/$', 'delete_emailing', name='emailing_delete'),
    url(r'^new-newsletter/$', 'new_newsletter', name='emailing_new_newsletter'),
    url(r'^confirm-send-mail/(?P<emailing_id>\d+)/$', 'confirm_send_mail', name='emailing_confirm_send_mail'),
    url(r'^cancel_send_mail/(?P<emailing_id>\d+)/$', 'cancel_send_mail', name='emailing_cancel_send_mail'),
    url(r'^subscribe/$', 'subscribe_newsletter', name='emailing_subscribe_newsletter'),
    url(r'^subscribe/(?P<contact_uuid>[\w\d-]+)$', 'subscribe_done', name='emailing_subscribe_done'),
    url(r'^subscribe-error/(?P<contact_uuid>[\w\d-]+)/$', 'subscribe_error', name='emailing_subscribe_error'),
    url(r'^email-verification/(?P<contact_uuid>[\w\d-]+)/$', 'email_verification', name='emailing_email_verification'),
    url(r'^unregister/(?P<emailing_id>\d+)/(?P<contact_uuid>[\w\d-]+)/$', 'unregister_contact', name='emailing_unregister'),
    url(r'^view-online/(?P<emailing_id>\d+)/(?P<contact_uuid>[\w\d-]+)/$', 'view_emailing_online', name='emailing_view_online'),
    url(r'^link/(?P<link_uuid>[\w\d-]+)/(?P<contact_uuid>[\w\d-]+)/$', 'view_link', name='emailing_view_link'),
)