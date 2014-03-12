# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
import json
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, user_passes_test
import models, forms
from sanza.utils import logger
from sanza.permissions import can_access
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

@user_passes_test(can_access)
def toggle_favorite(request):
    try:
        if request.method == "POST":
            form = forms.UpdateFavoriteForm(request.POST)
            
            if form.is_valid():
                object_id = form.cleaned_data["object_id"]
                content_type = form.cleaned_data["content_type"]
                
                favorite, is_new = models.Favorite.objects.get_or_create(
                    user = request.user,
                    content_type = content_type,
                    object_id = object_id
                )
                
                if not favorite.content_object:
                    favorite.delete()
                    raise Exception(_(u'Invalid object'))
            
                label = getattr(favorite.content_object, 'name', unicode(favorite.content_object))
                if is_new:
                    data = {
                        'success': True,
                        'status': True,
                    }
                else:
                    favorite.delete()
                    data = {
                        'success': True,
                        'status': False,
                    }
            else:
                raise Exception(u"{0}".format(form.errors))
        else:
            raise Exception(u"POST expected")
    except Exception:
        data = {'success': False, 'message': _(u'An error occured')}
        logger.exception("update_favorite")
    return HttpResponse(json.dumps(data), content_type="application/json")


@user_passes_test(can_access)
def list_favorites(request):
    
    request.session["redirect_url"] = reverse('users_favorites_list')
    
    content_types = ContentType.objects.filter(user_favorite_set__user=request.user).distinct()
    
    favs_by_type = []
    for ct in content_types:
        try:
            template_name = "Users/_section_favorites_{0}.html".format(ct.model)
            get_template(template_name)
        except TemplateDoesNotExist:
            template_name = "Users/_section_favorites.html"
            
        favs_by_type.append(
            (
                ct.model_class()._meta.verbose_name_plural.capitalize(),
                [x.content_object for x in models.Favorite.objects.filter(user=request.user, content_type=ct)],
                template_name,
            )
        )
        
    context = {
        'favs_by_type': favs_by_type,
    }
    
    return render_to_response(
        'Users/favorites_list.html',
        context,
        context_instance=RequestContext(request)
    )