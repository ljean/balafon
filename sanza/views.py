# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from StringIO import StringIO
from django.conf import settings
from django.core.urlresolvers import reverse
from sanza.Crm.models import Contact, Entity, Group, Action
from django.shortcuts import get_object_or_404
from sanza.permissions import can_access
import json

@user_passes_test(can_access)
def export_database_json(request):
    
    if not request.user.is_staff:
        raise PermissionDenied
    
    content = StringIO()
    
    call_command('dumpdata', 'auth', 'Crm', 'Search',  'Emailing', indent=1, stdout=content)
    content.seek(0)
    response = HttpResponse(content.read(), mimetype='application/json')
    response['Content-Disposition'] = 'attachment; filename={0}.json'.format('sanza')
    return response

def redirect_to_homepage(request):
    if getattr(settings, 'SANZA_AS_HOMEPAGE', False):
        return HttpResponseRedirect(reverse('sanza_homepage'))
    else:
        return HttpResponseRedirect(reverse('coop_cms_homepage'))
        

@user_passes_test(can_access)
def auto_save_data(request, model_type, field_name, obj_id):
    if request.method != "POST" or (not request.is_ajax()):
        raise Http404
    try:
        model = {
            "group": Group,
        }[model_type]
        
        obj = get_object_or_404(model, id=obj_id)
        setattr(obj, field_name, request.POST["value"])
        obj.save()   
    except Http404:
        raise
    except Exception, msg:
        return HttpResponse(json.dumps({"ok": False, "error": unicode(msg)}), mimetype='application/json')
    return HttpResponse(json.dumps({"ok": True}), mimetype='application/json')
