# -*- coding: utf-8 -*-

from registration.backends.default import DefaultBackend
from forms import AcceptNewsletterRegistrationForm

class AcceptNewsletterRegistrationBackend(DefaultBackend):
    
    def get_form_class(self, request):
        return AcceptNewsletterRegistrationForm