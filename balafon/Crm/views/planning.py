# -*- coding: utf-8 -*-
"""display actions in different planning views"""

from datetime import datetime, date
import json

from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.views.generic import RedirectView
from django.views.generic.dates import MonthArchiveView, WeekArchiveView, DayArchiveView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.views.generic import ListView

from balafon.Crm import models
from balafon.Crm.utils import get_in_charge_users
from balafon.settings import get_planning_ordering
from balafon.permissions import can_access
try:
    from balafon.Users.models import CustomMenu
    HAS_CUSTOM_MENU = True
except ImportError:
    HAS_CUSTOM_MENU = False


class ActionArchiveView(object):
    """view"""
    paginate_by = 50
    planning_type = ''

    @method_decorator(user_passes_test(can_access))
    def dispatch(self, *args, **kwargs):
        return super(ActionArchiveView, self).dispatch(*args, **kwargs)

    def _get_selection(self, filter_value):
        """filtering"""
        try:
            values = {}
            for item in filter_value.split(","):
                try:
                    prefix, val = item[0], int(item[1:])
                except IndexError:
                    continue
                if prefix in values:
                    values[prefix].append(val)
                else:
                    values[prefix] = [val]
            return dict(values)
        except ValueError:
            raise Http404

    def _get_queryset(self):
        """return actions displayed by this page. The date is managed by each Archive"""
        return models.Action.objects.all().order_by("planned_date", "priority")

    def get_ordering(self):
        ordering = get_planning_ordering()
        if ordering:
            return ordering
        else:
            return (
                (1, _("Ascending"), ("planned_date", "id")),
                (0, _("Descending"), ("-planned_date", "-id")),
                (2, _("Contact"), ("contacts__lastname", "planned_date", "id")),
                (3, _("Entity"), ("entities__name", "planned_date", "id")),
            )

    def order_queryset(self, queryset, ordering):

        for value, label, lookup in self.get_ordering():
            if value == ordering:
                queryset = queryset.order_by(*lookup)
        return queryset

    def get_queryset(self):
        """queryset ob objects"""
        values = self.request.GET.get("filter", None)
        queryset = self._get_queryset()

        name = self.request.GET.get("name", None)
        if name:
            queryset = queryset.filter(
                Q(entities__name__icontains=name) | Q(contacts__lastname__icontains=name)
            )

        if values and values != "null":
            values_dict = self._get_selection(values)
            selected_types = values_dict.get("t", [])
            if selected_types:
                if 0 in selected_types:
                    if len(selected_types) == 1:
                        # only : no types
                        queryset = queryset.filter(type__isnull=True)
                    else:
                        # combine no types and some types
                        queryset = queryset.filter(Q(type__isnull=True) | Q(type__in=selected_types))
                else:
                    # only some types
                    queryset = queryset.filter(type__in=selected_types)

            selected_status = values_dict.get("s", [])
            if selected_status:
                # only some status
                action_types = models.ActionType.objects.filter(id__in=selected_types)
                allowed_status = [status.id for status in self._get_allowed_status(action_types, selected_types)]
                selected_status = [status for status in selected_status if status in allowed_status]
                if selected_status:
                    queryset = queryset.filter(status__in=selected_status)

            selected_users = values_dict.get("u", [])
            if selected_users:
                queryset = queryset.filter(in_charge__in=selected_users)

            ordering = self.get_ordering()[0][0]
            list_ordering = values_dict.get("o", [])
            try:
                ordering = list_ordering[0]
            except IndexError:
                pass
            queryset = self.order_queryset(queryset, ordering)

        return queryset

    def _get_allowed_status(self, action_types, selected_types):
        """list of allowed status"""
        action_status = []
        for action_type in action_types:
            if action_type.id in selected_types:
                setattr(action_type, 'selected', True)
                action_status.extend(action_type.allowed_status.all())
        # unique action status sorted by name
        return sorted(set(action_status), key=lambda status: status.name)

    def get_context_data(self, *args, **kwargs):
        """get context for template"""
        context = super(ActionArchiveView, self).get_context_data(*args, **kwargs)
        action_types = models.ActionType.objects.all().order_by('order_index', 'name')
        action_status = []
        in_charge = get_in_charge_users()
        values = self.request.GET.get("filter", None)
        ordering = self.get_ordering()[0][0]
        if values and values != "null":
            context["filter"] = values
            values_dict = self._get_selection(values)

            selected_types = values_dict.get("t", [])
            for action_type in action_types:
                if action_type.id in selected_types:
                    setattr(action_type, 'selected', True)

            # list of unique action status sorted by name
            action_status = self._get_allowed_status(action_types, selected_types)

            if 0 in selected_types:
                context["no_type_selected"] = True

            selected_users = values_dict.get("u", [])
            for user in in_charge:
                if user.id in selected_users:
                    setattr(user, 'selected', True)

            selected_status = values_dict.get("s", [])
            for status in action_status:
                if status.id in selected_status:
                    setattr(status, 'selected', True)

            list_ordering = values_dict.get("o", [])
            try:
                ordering = list_ordering[0]
            except IndexError:
                pass

        if HAS_CUSTOM_MENU:
            context['planning_custom_menus'] = [
                menu for menu in CustomMenu.objects.filter(position=CustomMenu.POSITION_PLANNING) if menu.get_children()
            ]

        context["action_types"] = action_types
        context["in_charge"] = in_charge
        context["action_status"] = action_status
        context["planning_type"] = self.planning_type
        context["order_value"] = "o{0}".format(ordering)
        context["order_values"] = [("o{0}".format(index), label) for (index, label, lookup) in self.get_ordering()]

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
        self.request.session["redirect_url"] = self.request.get_full_path()
        return super(ActionArchiveView, self).get(*args, **kwargs)


class ActionMonthArchiveView(ActionArchiveView, MonthArchiveView):
    """view"""
    date_field = "planned_date"
    month_format = '%m'
    allow_future = True
    allow_empty = True
    planning_type = 'month'


class ActionWeekArchiveView(ActionArchiveView, WeekArchiveView):
    """view"""
    date_field = "planned_date"
    week_format = "%W"
    allow_future = True
    allow_empty = True
    planning_type = 'week'


class ActionDayArchiveView(ActionArchiveView, DayArchiveView):
    """view"""
    date_field = "planned_date"
    allow_future = True
    allow_empty = True
    month_format = '%m'
    planning_type = 'day'


class NotPlannedActionArchiveView(ActionArchiveView, ListView):
    """view"""
    queryset = models.Action.objects.filter(planned_date=None).order_by("priority")
    template_name = "Crm/action_archive_not_planned.html"

    def _get_queryset(self):
        """return actions displayed by this page"""
        return models.Action.objects.filter(planned_date=None).order_by("priority")


class TodayActionsView(RedirectView):
    """Redirect to today action"""
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        now = datetime.now()
        self.url = reverse('crm_actions_of_day', args=[now.year, now.month, now.day])
        return super(TodayActionsView, self).get_redirect_url(*args, **kwargs)


class ThisWeekActionsView(RedirectView):
    """Redirect this week actions action"""
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        now = datetime.now()
        self.url = reverse('crm_actions_of_week', args=[now.year, now.strftime("%W")])
        return super(ThisWeekActionsView, self).get_redirect_url(*args, **kwargs)


class ThisMonthActionsView(RedirectView):
    """Redirect this month actions action"""
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        now = datetime.now()
        self.url = reverse('crm_actions_of_month', args=[now.year, now.month])
        return super(ThisMonthActionsView, self).get_redirect_url(*args, **kwargs)


@user_passes_test(can_access)
def go_to_planning_date(request):
    """returns the url for displaying date"""

    if request.method != 'POST':
        raise Http404

    planning_type = request.POST.get('planning_type', '')
    planning_date = request.POST.get('planning_date', '')
    filters = request.POST.get('filters', '')

    try:
        planning_date = date(*[int(val) for val in planning_date.split('-')])
    except ValueError:
        raise Http404

    url = ''
    if planning_type == 'month':
        url = reverse('crm_actions_of_month', args=[planning_date.year, planning_date.month])

    elif planning_type == 'week':
        url = reverse('crm_actions_of_week', args=[planning_date.year, int(planning_date.strftime("%W"))])

    elif planning_type == 'day':
        url = reverse('crm_actions_of_day', args=[planning_date.year, planning_date.month, planning_date.day])

    if url:
        if filters:
            url += '?filter=' + filters
        data = json.dumps({'url': url})
        return HttpResponse(data, content_type='application/json')
    else:
        raise Http404
