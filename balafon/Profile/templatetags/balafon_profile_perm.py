# -*- coding: utf-8 -*-

from django import template
from django.template.base import Variable, VariableDoesNotExist
from balafon.Profile.models import CategoryPermission
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from coop_cms.settings import get_article_class
from coop_cms.shortcuts import get_article
from balafon.Profile.utils import create_profile_contact, check_category_permission
from django.template.defaultfilters import slugify

register = template.Library()

class IfCanDoArticle(template.Node):
    def __init__(self, title, perm, lang, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.title = title
        self.perm = perm
        self.lang = lang

    def __iter__(self):
        for node in self.nodelist_true:
            yield node
        for node in self.nodelist_false:
            yield node

    def _check_perm(self, user, force_lang=None, current_lang=None):
        Article = get_article_class()
        slug = slugify(self.title)
        try:
            if force_lang:
                article = get_article(slug, force_lang=force_lang)
            else:
                article = get_article(slug, current_lang=current_lang)
        except Article.DoesNotExist:
            article = Article.objects.create(slug=slug, title=self.title)
        return user.has_perm(self.perm, article)

    def render(self, context):
        request = context.get('request')
        
        try:
            v = template.Variable(self.title)
            self.title = v.resolve(context)
        except template.VariableDoesNotExist:
            self.title = self.title.strip("'").strip('"')
        
        if self._check_perm(request.user, force_lang=self.lang, current_lang=request.LANGUAGE_CODE):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

@register.tag
def if_can_do_article(parser, token):
    args = token.contents.split()
    title = args[1]
    perm = args[2] if len(args)>2 else 'can_view_article'
    lang = args[3] if len(args)>3 else None
    
    nodelist_true = parser.parse(('else', 'endif'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfCanDoArticle(title, perm, lang, nodelist_true, nodelist_false)

