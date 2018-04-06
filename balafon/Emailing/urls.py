# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^newsletters/$', views.newsletter_list, name='emailing_newsletter_list'),
    url(r'^view-emailing/(?P<emailing_id>\d+)/$', views.view_emailing, name='emailing_view'),
    url(
        r'^update-emailing/(?P<pk>\d+)/$',
        views.EmailingUpdateView.as_view(),
        name='emailing_update_emailing'
    ),
    url(r'^delete-emailing/(?P<emailing_id>\d+)/$', views.delete_emailing, name='emailing_delete'),
    url(r'^new-newsletter/$', views.new_newsletter, name='emailing_new_newsletter'),
    url(r'^confirm-send-mail/(?P<emailing_id>\d+)/$', views.confirm_send_mail, name='emailing_confirm_send_mail'),
    url(r'^cancel_send_mail/(?P<emailing_id>\d+)/$', views.cancel_send_mail, name='emailing_cancel_send_mail'),
    url(r'^subscribe/$', views.SubscribeView.as_view(), name='emailing_subscribe_newsletter'),

    url(r'^email-subscribe/$', views.EmailSubscribeView.as_view(), name='emailing_email_subscribe_newsletter'),
    url(
        r'^email-subscribe/(?P<subscription_type>\d+)/$',
        views.EmailSubscribeView.as_view(),
        name='emailing_email_subscribe_subscription'
    ),
    url(r'^email-subscribe/done/$', views.EmailSubscribeDoneView.as_view(), name='emailing_subscribe_email_done'),
    url(r'^email-subscribe/error/$', views.EmailSubscribeErrorView.as_view(), name='emailing_subscribe_email_error'),
    url(
        r'^subscribe/(?P<contact_uuid>[\w\d-]+)$',
        views.subscribe_done,
        name='emailing_subscribe_done'
    ),
    url(
        r'^subscribe-error/(?P<contact_uuid>[\w\d-]+)/$',
        views.subscribe_error,
        name='emailing_subscribe_error'
    ),
    url(
        r'^email-verification/(?P<contact_uuid>[\w\d-]+)/$',
        views.email_verification,
        name='emailing_email_verification'
    ),
    url(
        r'^unregister/(?P<emailing_id>\d+)/(?P<contact_uuid>[\w\d-]+)/$',
        views.unregister_contact,
        name='emailing_unregister'
    ),
    url(
        r'^view-online/(?P<emailing_id>\d+)/(?P<contact_uuid>[\w\d-]+)/$',
        views.view_emailing_online,
        name='emailing_view_online'
    ),
    url(
        r'^view-online-lang/(?P<emailing_id>\d+)/(?P<contact_uuid>[\w\d-]+)/(?P<lang>\w+)/$',
        views.view_emailing_online_lang,
        name='emailing_view_online_lang'
    ),
    url(
        r'^link/(?P<link_uuid>[\w\d-]+)/(?P<contact_uuid>[\w\d-]+)/$',
        views.view_link,
        name='emailing_view_link'
    ),
    url(
        r'^email-img/(?P<emailing_id>\d+)/(?P<contact_uuid>[\w\d-]+)/$',
        views.email_tracking,
        name='emailing_email_tracking'
    ),
]
