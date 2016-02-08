# -*- coding: utf-8 -*-
"""forms"""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError

import floppyforms as forms

from balafon.utils import is_allowed_homepage
from balafon.Users.models import UserPreferences


class UserPreferencesAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserPreferencesAdminForm, self).__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(is_staff=True)

    class Meta:
        model = UserPreferences
        fields = ('user', 'notify_due_actions', 'message_in_favorites', )


class ContentTypeField(forms.CharField): 
    def clean(self, value):
        super(ContentTypeField, self).clean(value)
        if value:
            try:
                return ContentType.objects.get(id=value)
            except ContentType.DoesNotExist:
                raise ValidationError(_(u"The content type {0} doesn't exist").format(value))
        return value


class UpdateFavoriteForm(forms.Form):
    object_id = forms.IntegerField(required=True)
    content_type = ContentTypeField(required=True)
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            kwargs['initial'] = {
                'object_id': instance.id,
                'content_type': ContentType.objects.get_for_model(instance.__class__).id,
            }
        super(UpdateFavoriteForm, self).__init__(*args, **kwargs)


class UrlForm(forms.Form):
    url = forms.CharField(required=True)

    def clean_url(self):
        url = self.cleaned_data['url']
        if not is_allowed_homepage(url):
            raise ValidationError(_(u"The url {0} is not allowed as homepage".format(url)))
        return url
