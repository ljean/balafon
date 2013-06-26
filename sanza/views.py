# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from StringIO import StringIO
from django.conf import settings
from django.core.urlresolvers import reverse

@login_required
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
        
