# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from StringIO import StringIO
from django.conf import settings
from django.core.urlresolvers import reverse
from sanza.Crm.models import Contact, Entity, Group, Action, Opportunity
from sanza.Search.models import Search
from django.shortcuts import get_object_or_404
from sanza.permissions import can_access
import json

#@user_passes_test(can_access)
#def export_database_json(request):
#    
#    if not request.user.is_staff:
#        raise PermissionDenied
#    
#    content = StringIO()
#    
#    call_command('dumpdata', 'auth', 'Crm', 'Search',  'Emailing', indent=1, stdout=content)
#    content.seek(0)
#    response = HttpResponse(content.read(), content_type='application/json')
#    response['Content-Disposition'] = 'attachment; filename={0}.json'.format('sanza')
#    return response

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
            "contact": Contact,
            "entity": Entity,
            "action": Action,
            "opportunity": Opportunity,
            "search": Search,
        }[model_type]
        
        obj = get_object_or_404(model, id=obj_id)
        
        value = request.POST["value"]
        value = value.strip(u" \t\r\n")
        if value[-4:] == u"<br>":
            value = value[:-4]
        value = value.replace(u"<br>", u"\n").replace(u"&nbsp;", u" ")
        
        setattr(obj, field_name, value)
        obj.save()   
    except Http404:
        raise
    except Exception, msg:
        return HttpResponse(json.dumps({"ok": False, "error": unicode(msg)}), content_type='application/json')
    return HttpResponse(json.dumps({"ok": True}), content_type='application/json')
