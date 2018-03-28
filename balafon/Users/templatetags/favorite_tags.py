# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django import template

from balafon.Users.forms import UpdateFavoriteForm
from balafon.Users.models import Favorite

register = template.Library()


@register.inclusion_tag('Users/_favorite_item.html', takes_context=True)
def favorite_item(context, object):
    content_type = ContentType.objects.get_for_model(object.__class__)
    user = context['request'].user
    if user and user.is_authenticated():
        is_in_favorite = Favorite.objects.filter(
            user=context['request'].user,
            content_type=content_type,
            object_id=object.id
        ).count()
    else:
        is_in_favorite = 0

    return {
        'status': is_in_favorite,
        'post_url': reverse('users_toggle_favorite'),
        'form': UpdateFavoriteForm(instance=object),
    }
