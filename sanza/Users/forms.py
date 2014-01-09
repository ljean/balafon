# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Users.models import UserPreferences
from django.contrib.auth.models import User

class UserPreferencesAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserPreferencesAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_staff=True)

    class Meta:
        model = UserPreferences