# -*- coding: utf-8 -*-
"""user customization"""

import re

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, NoReverseMatch

from coop_cms.utils import RequestManager, RequestNotFound

from balafon.permissions import can_access


class UserPreferences(models.Model):
    """user preferences"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    notify_due_actions = models.BooleanField(default=False, verbose_name=_("Notify due actions"))
    message_in_favorites = models.BooleanField(
        default=False,
        verbose_name=_("Create automatically a favorite for message posted from the public form")
    )

    class Meta:
        verbose_name = _('User preferences')
        verbose_name_plural = _('User preferences')
    
    def __str__(self):
        return self.user.username


class Favorite(models.Model):
    """user favorite items"""

    user = models.ForeignKey(User, verbose_name=_("user"), related_name="user_favorite_set", on_delete=models.CASCADE)
    content_type = models.ForeignKey(
        ContentType, verbose_name=_("content_type"), related_name="user_favorite_set", on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField(verbose_name=_("object id"))
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')
        unique_together = (('user', 'content_type', 'object_id'),)
        
    def __str__(self):
        return "{0} - {1}".format(self.user, self.content_object)


class UserHomepage(models.Model):
    """User homepage"""

    user = models.OneToOneField(User, verbose_name=_("user"), on_delete=models.CASCADE)
    url = models.URLField(verbose_name=_("URL"))
    
    class Meta:
        verbose_name = _('User homepage')
        verbose_name_plural = _('User homepages')
        
    def __str__(self):
        return "{0} - {1}".format(self.user, self.url)


class CustomMenu(models.Model):
    """Menus that can be added to the Balafon menu"""
    POSITION_MENU = 0
    POSITION_PLANNING = 1

    POSITION_CHOICES = (
        (POSITION_MENU, _('Menu')),
        (POSITION_PLANNING, _('Planning')),
    )

    label = models.CharField(max_length=100, verbose_name=_("label"))
    icon = models.CharField(max_length=20, verbose_name=_("icon"), blank=True, default="")
    order_index = models.IntegerField(default=0)
    position = models.IntegerField(
        default=0, choices=POSITION_CHOICES, verbose_name=_('position'),
        help_text=_('Where the menu will be set')
    )

    class Meta:
        verbose_name = _('Custom menu')
        verbose_name_plural = _('Custom menus')
        ordering = ['order_index', 'label']

    def get_children(self):
        """returns children"""
        children = []
        try:
            request = RequestManager().get_request()
            if can_access(request.user):
                for item in self.custommenuitem_set.all():
                    if item.only_for_users.count() == 0 or (request.user in item.only_for_users.all()):
                        if item.get_url(*request.resolver_match.args, **request.resolver_match.kwargs):
                            children.append(item)
        except (RequestNotFound, AttributeError):
            pass
        return children

    def __str__(self):
        return self.label


class CustomMenuItem(models.Model):
    """Menus items hat can be added to the Balafon menu"""
    parent = models.ForeignKey(CustomMenu, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, verbose_name=_("label"))
    icon = models.CharField(max_length=20, verbose_name=_("icon"), blank=True, default="")
    url = models.CharField(max_length=100, verbose_name=_("url"), default='', blank=True)
    reverse = models.CharField(max_length=100, verbose_name=_("reverse"), default='', blank=True)
    reverse_kwargs = models.CharField(
        max_length=100, verbose_name=_("reverse_kwargs"), default='', blank=True,
        help_text=_('kwargs to use for building the reverse. kw1:defaultval1,kw2,kw3:defaultval3 ')
    )
    order_index = models.IntegerField(default=0)
    only_for_users = models.ManyToManyField(
        User, blank=True, verbose_name=_("only for users"), limit_choices_to={'is_staff': True}
    )
    attributes = models.CharField(max_length=100, verbose_name=_("attributes"), default="", blank=True)
    query_string = models.CharField(max_length=100, verbose_name=_("query string"), default="", blank=True)

    class Meta:
        verbose_name = _('Custom menu item')
        verbose_name_plural = _('Custom menu items')
        ordering = ['order_index', 'label']

    def __str__(self):
        return "{0} > {1}".format(self.parent.label, self.label)

    def get_attrs(self):
        attrs = self.attributes
        if 'class=' in attrs:
            pattern = re.compile('class=\"(?P<css_class>.*)\"')
        
            def replacer(match):
                value = match.group('css_class')
                return 'class="{0} dropdown-link"'.format(value)

            attrs = pattern.sub(replacer, attrs)
        else:
            attrs += ' class="dropdown-link"'
        return attrs

    def get_url(self, *args, **kwargs):
        """return the url to display"""
        if hasattr(self, '_cached_url'):
            return getattr(self, '_cached_url')
        url = ''
        if self.url:
            url = self.url
        elif self.reverse:
            reverse_kwargs = {}
            if self.reverse_kwargs:
                args_keywords = self.reverse_kwargs.split(',')
                for arg_keyword in args_keywords:
                    if ':' in arg_keyword:
                        slices = arg_keyword.split(':')
                        keyword = slices[0]
                        default_value = ":".join(slices[1:])
                    else:
                        keyword = arg_keyword
                        default_value = None
                    reverse_kwargs[keyword] = kwargs.get(keyword, default_value)
            try:
                if not self.query_string:
                    query_string = ''
                    request = RequestManager().get_request()
                    if request:
                        query_string = "?" + request.META['QUERY_STRING'] or ''
                else:
                    query_string = self.query_string
                try:
                    url = reverse(self.reverse, kwargs=reverse_kwargs) + query_string
                except TypeError:
                    pass
            except NoReverseMatch as err:
                if settings.DEBUG:
                    print("NoReverseMatch", err)

        if url:
            setattr(self, '_cached_url', url)
        return url


class UserPermissions(models.Model):
    """user preferences"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_create_group = models.BooleanField(
        default=True, verbose_name=_('can create group'), help_text=_('If not checked, the user can not create group')
    )

    class Meta:
        verbose_name = _('User permissions')
        verbose_name_plural = _('User permissions')

    def __str__(self):
        return self.user.username
