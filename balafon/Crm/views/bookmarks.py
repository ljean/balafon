# -*- coding: utf-8 -*-
"""bookmarks -> display on board: will be removed in future"""

import json

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from balafon.Crm import models
from balafon.permissions import can_access
from balafon.utils import logger


@user_passes_test(can_access)
def view_board_panel(request):
    """view"""
    return HttpResponseRedirect(reverse("users_favorites_list"))


def _toggle_object_bookmark(request, object_model, object_id):
    """util"""
    # pylint: disable=broad-except
    try:
        if request.is_ajax() and request.method == "POST":
            obj = get_object_or_404(object_model, id=object_id)
            obj.display_on_board = not obj.display_on_board
            obj.save()
            data = {'bookmarked': obj.display_on_board}
            return HttpResponse(json.dumps(data), 'application/json')
        raise Http404
    except Exception:
        logger.exception("_toggle_object_bookmarked")


@user_passes_test(can_access)
def toggle_action_bookmark(request, action_id):
    """view"""
    return _toggle_object_bookmark(request, models.Action, action_id)


@user_passes_test(can_access)
def toggle_opportunity_bookmark(request, opportunity_id):
    """view"""
    return _toggle_object_bookmark(request, models.Opportunity, opportunity_id)
