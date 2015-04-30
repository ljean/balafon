# -*- coding: utf-8 -*-
"""display actions in different planning views"""

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import Http404
from django.views.generic.dates import MonthArchiveView, WeekArchiveView, DayArchiveView
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from sanza.Crm import models
from sanza.Crm.utils import get_in_charge_users
from sanza.permissions import can_access


class ActionArchiveView(object):
    """view"""

    @method_decorator(user_passes_test(can_access))
    def dispatch(self, *args, **kwargs):
        return super(ActionArchiveView, self).dispatch(*args, **kwargs)

    def _get_selection(self, filter_value):
        """filtering"""
        try:
            values = {}
            for item in filter_value.split(","):
                prefix, val = item[0], int(item[1:])
                if prefix in values:
                    values[prefix].append(val)
                else:
                    values[prefix] = [val]
            return dict(values)
        except ValueError:
            raise Http404

    def get_queryset(self):
        """queryset ob objects"""
        values = self.request.GET.get("filter", None)
        queryset = self.queryset
        if values and values != "null":
            values_dict = self._get_selection(values)

            selected_types = values_dict.get("t", [])
            if selected_types:
                if 0 in selected_types:
                    if len(selected_types) == 1:
                        #only : no types
                        queryset = queryset.filter(type__isnull=True)
                    else:
                        #combine no types and some types
                        queryset = queryset.filter(Q(type__isnull=True) | Q(type__in=selected_types))
                else:
                    #only some types
                    queryset = queryset.filter(type__in=selected_types)

            selected_users = values_dict.get("u", [])
            if selected_users:
                queryset = queryset.filter(in_charge__in=selected_users)

        return queryset

    def get_context_data(self, *args, **kwargs):
        """get context for template"""
        context = super(ActionArchiveView, self).get_context_data(*args, **kwargs)
        action_types = models.ActionType.objects.all()
        in_charge = get_in_charge_users()
        values = self.request.GET.get("filter", None)
        if values and values != "null":
            context["filter"] = values
            values_dict = self._get_selection(values)

            selected_types = values_dict.get("t", [])
            for action_type in action_types:
                if action_type.id in selected_types:
                    setattr(action_type, 'selected', True)
            if 0 in selected_types:
                context["no_type_selected"] = True

            selected_users = values_dict.get("u", [])
            for user in in_charge:
                if user.id in selected_users:
                    setattr(user, 'selected', True)

        context["action_types"] = action_types
        context["in_charge"] = in_charge
        return context

    def get_dated_queryset(self, **lookup_kwargs):
        """queryset"""
        date_field = self.get_date_field()

        since = lookup_kwargs['%s__gte' % date_field]
        until = lookup_kwargs['%s__lt' % date_field]

        lookup1 = Q(end_datetime__isnull=True) & Q(planned_date__gte=since) & Q(planned_date__lt=until)
        lookup2 = Q(end_datetime__isnull=False) & Q(planned_date__lt=until) & Q(end_datetime__gte=since)

        queryset = self.get_queryset()
        return queryset.filter(lookup1 | lookup2)

    def get(self, *args, **kwargs):
        """http get"""
        self.request.session["redirect_url"] = self.request.path
        return super(ActionArchiveView, self).get(*args, **kwargs)


class ActionMonthArchiveView(ActionArchiveView, MonthArchiveView):
    """view"""
    queryset = models.Action.objects.all().order_by("planned_date", "priority")
    date_field = "planned_date"
    month_format = '%m'
    allow_future = True
    allow_empty = True


class ActionWeekArchiveView(ActionArchiveView, WeekArchiveView):
    """view"""
    queryset = models.Action.objects.all().order_by("planned_date", "priority")
    date_field = "planned_date"
    week_format = "%U"
    allow_future = True
    allow_empty = True


class ActionDayArchiveView(ActionArchiveView, DayArchiveView):
    """view"""
    queryset = models.Action.objects.all().order_by("planned_date", "priority")
    date_field = "planned_date"
    allow_future = True
    allow_empty = True
    month_format = '%m'


class NotPlannedActionArchiveView(ActionArchiveView, ListView):
    """view"""
    queryset = models.Action.objects.filter(planned_date=None).order_by("priority")
    template_name = "Crm/action_archive_not_planned.html"
