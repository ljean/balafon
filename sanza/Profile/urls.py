# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from views import AcceptNewsletterActivationView, AcceptNewsletterRegistrationView

urlpatterns = patterns('sanza.Profile.views',
    url(r'edit/$', 'edit_profile', name='profile_edit'),
    url(r'post-message/$', 'post_message', name='profile_post_message'),
)

urlpatterns += patterns('',
    url(r'^activate/complete/$',
        TemplateView.as_view(template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        AcceptNewsletterActivationView.as_view(),
        name='registration_activate'),
    url(r'^register/$',
        AcceptNewsletterRegistrationView.as_view(),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.html'),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
)
