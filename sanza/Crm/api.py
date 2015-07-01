# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from datetime import date, datetime, time

from django.db.models import Q

from rest_framework import generics, viewsets
from rest_framework.exceptions import ParseError

from sanza.Crm.models import Action, ActionType, Contact, TeamMember
from sanza.Crm import serializers


class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    """returns contacts for autocomplete"""

    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer

    def get_queryset(self):
        """returns """
        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(lastname__istartswith=name)[:10]
        return self.queryset


class ListActionsView(generics.ListAPIView):
    """update an action date"""
    model = Action
    serializer_class = serializers.ActionSerializer

    def _parse_date(self, date_str):
        year, month, day = [int(val) for val in date_str.split("-")]
        return date(year, month, day)

    def get_queryset(self):
        """returns actions"""
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')
        action_type = self.request.GET.get('action_type')
        in_charge = self.request.GET.get('in_charge')

        if not start_date or not end_date:
            raise ParseError("Period frame missing")

        queryset = self.model.objects.all()

        if action_type:
            try:
                ActionType.objects.get(id=action_type)
            except (ValueError, ActionType.DoesNotExist):
                raise ParseError("Invalid action type")
            queryset = queryset.filter(type__id=action_type)

        if in_charge:
            try:
                in_charge_ids = [int(_id) for _id in in_charge.split(',')]
                team_members = TeamMember.objects.filter(id__in=in_charge_ids)
                if team_members.count() == 0:
                    return self.model.objects.none()
            except ValueError:
                raise ParseError("Invalid team member")
            queryset = queryset.filter(in_charge__in=[member.id for member in team_members])

        try:
            start_date = self._parse_date(start_date)
            end_date = self._parse_date(end_date)
        except ValueError:
            raise ParseError("Invalid period frame")

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        if end_datetime < start_datetime:
            return self.model.objects.none()

        queryset = queryset.filter(
            Q(planned_date__lte=start_datetime, end_datetime__gte=end_datetime) |  # starts before, ends after period
            Q(planned_date__gte=start_datetime, end_datetime__lte=end_datetime) |  # starts and ends during period
            Q(planned_date__lte=start_datetime, end_datetime__gte=start_datetime) |  # starts before, ends during
            Q(planned_date__lte=end_datetime, end_datetime__gte=end_datetime) |  # starts during period, ends after
            Q(
                planned_date__gte=start_datetime,
                end_datetime__isnull=True,
                planned_date__lte=end_datetime
            )  # no end, starts during period
        )
        return queryset


class UpdateActionDateView(generics.UpdateAPIView):
    """update an action date"""
    model = Action
    serializer_class = serializers.ActionUpdateDateSerializer

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])


class EditActionMixin(object):
    """base class for create and update"""

    def save_object(self, serializer):
        """save object"""
        contacts = []
        for contact_id in self.contacts:
            try:
                contact = Contact.objects.get(id=contact_id)
                contacts.append(contact)
            except (ValueError, Contact.DoesNotExist):
                raise ParseError("Invalid contacts")

        obj = serializer.save()
        obj.contacts.clear()
        for contact in contacts:
            obj.contacts.add(contact)
        obj.save()
        return obj


class UpdateActionView(EditActionMixin, generics.UpdateAPIView):
    """update an action"""
    model = Action
    serializer_class = serializers.ActionUpdateSerializer
    contacts = None

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        """handle HTTP request"""
        self.contacts = request.data.get("contacts", [])
        response = super(UpdateActionView, self).update(request, *args, **kwargs)
        return response

    def perform_update(self, serializer):
        """update the action"""
        return self.save_object(serializer)


class CreateActionView(EditActionMixin, generics.CreateAPIView):
    """create an action"""
    model = Action
    serializer_class = serializers.ActionUpdateSerializer
    contacts = None

    def create(self, request, *args, **kwargs):
        """handle HTTP request"""
        self.contacts = request.data.get("contacts", [])
        response = super(CreateActionView, self).create(request, *args, **kwargs)
        return response

    def perform_create(self, serializer):
        """create new object"""
        return self.save_object(serializer)
        #obj.type = ActionType.objects.get_or_create(name="Intervention")[0]


class DeleteActionView(generics.DestroyAPIView):
    """delete an action"""
    model = Action

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])
