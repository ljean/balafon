# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from datetime import date, datetime, time

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework import generics, viewsets
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView, Response

from balafon.Crm.models import Action, ActionType, ActionStatus, Contact, TeamMember, Entity
from balafon.Crm import serializers


class ContactViewSet(viewsets.ReadOnlyModelViewSet):
    """returns contacts for autocomplete"""
    permission_classes = [IsAdminUser, ]
    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer

    def get_queryset(self):
        """returns """
        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(lastname__istartswith=name)[:10]
        return self.queryset


class ContactsOrEntitiesView(APIView):
    """returns contacts or entity for autocomplete"""

    queryset = Contact.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [IsAdminUser, ]

    def get_matching_items(self, name):
        """return list of contacts"""
        contacts_and_entities = []
        if name:
            contacts = Contact.objects.filter(lastname__istartswith=name)[:10]
            contact_type = ContentType.objects.get_for_model(Contact)
            entity_type = ContentType.objects.get_for_model(Entity)
            for contact in contacts:
                city = contact.get_city
                contacts_and_entities.append({
                    'id': contact.id,
                    'name': contact.fullname,
                    'type': contact_type.id,
                    'city': city.get_friendly_name() if city else '',
                })

            entities = Entity.objects.filter(name__istartswith=name, is_single_contact=False)[:10]
            for entity in entities:
                city = entity.city
                contacts_and_entities.append({
                    'id': entity.id,
                    'name': entity.name,
                    'type': entity_type.id,
                    'city': city.get_friendly_name() if city else '',
                })
        return sorted(contacts_and_entities, key=lambda elt: elt['name'])[:10]

    def get(self, request):
        """returns """
        name = self.request.GET.get('name', None)
        return Response(self.get_matching_items(name))


class ListActionsView(generics.ListAPIView):
    """update an action date"""
    permission_classes = [IsAdminUser, ]
    model = Action
    serializer_class = serializers.ActionSerializer

    def _parse_date(self, date_str):
        """string to date"""
        year, month, day = [int(val) for val in date_str.split("-")]
        return date(year, month, day)

    def _apply_in_charge_lookup(self, queryset):
        """apply a in_charge lookup if needed"""
        in_charge = self.request.GET.get('in_charge')
        if in_charge:
            try:
                in_charge_ids = [int(_id) for _id in in_charge.split(',')]
                team_members = TeamMember.objects.filter(id__in=in_charge_ids)
                if team_members.count() == 0:
                    return self.model.objects.none()
            except ValueError:
                raise ParseError("Invalid team member")
            queryset = queryset.filter(in_charge__in=[member.id for member in team_members])
        return queryset

    def _apply_in_action_type_lookup(self, queryset):
        """apply an action type lookup if needed"""
        action_type = self.request.GET.get('action_type')
        if action_type:
            try:
                ActionType.objects.get(id=action_type)
            except (ValueError, ActionType.DoesNotExist):
                raise ParseError("Invalid action type")
            queryset = queryset.filter(type__id=action_type)
        return queryset

    def get_queryset(self):
        """returns actions"""
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if not start_date or not end_date:
            raise ParseError("Period frame missing")

        queryset = self.model.objects.all()
        queryset = self._apply_in_action_type_lookup(queryset)
        queryset = self._apply_in_charge_lookup(queryset)

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


class ListTeamMemberActionsView(ListActionsView):
    """
    Get the actions of a current team member
    The team member doesn't have to be a balafon user
    """
    permission_classes = [IsAuthenticated]

    def _apply_in_charge_lookup(self, queryset):
        """apply a in_charge lookup if needed"""
        try:
            team_member = TeamMember.objects.get(user=self.request.user)
        except TeamMember.DoesNotExist:
            raise PermissionDenied
        return queryset.filter(in_charge=team_member)


class UpdateActionDateView(generics.UpdateAPIView):
    """update an action date"""
    model = Action
    serializer_class = serializers.ActionUpdateDateSerializer
    permission_classes = [IsAdminUser, ]

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])


class EditActionMixin(object):
    """base class for create and update"""
    contacts = None

    def check_data(self, request):
        """check and prepare data"""
        self.contacts = request.data.get("contacts", [])
        action_type_id = request.data.get('type', None)
        action_status_id = request.data.get('status', None)

        if action_type_id and action_status_id:
            try:
                action_type = ActionType.objects.get(id=action_type_id)
                action_status = ActionStatus.objects.get(id=action_status_id)
                if action_status not in action_type.allowed_status.all():
                    raise ParseError(
                        "status {0} is not allowed for type {1}".format(action_type.name, action_status.name)
                    )
            except (ValueError, ActionType.DoesNotExist, ActionStatus.DoesNotExist):
                raise ParseError("Invalid parameters")

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
    permission_classes = [IsAdminUser, ]
    model = Action
    serializer_class = serializers.ActionUpdateSerializer
    contacts = None

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        """handle HTTP request"""
        self.check_data(request)
        response = super(UpdateActionView, self).update(request, *args, **kwargs)
        return response

    def perform_update(self, serializer):
        """update the action"""
        return self.save_object(serializer)


class CreateActionView(EditActionMixin, generics.CreateAPIView):
    """create an action"""
    permission_classes = [IsAdminUser, ]
    model = Action
    serializer_class = serializers.ActionUpdateSerializer
    contacts = None

    def create(self, request, *args, **kwargs):
        """handle HTTP request"""
        self.check_data(request)
        response = super(CreateActionView, self).create(request, *args, **kwargs)
        return response

    def perform_create(self, serializer):
        """create new object"""
        return self.save_object(serializer)
        #obj.type = ActionType.objects.get_or_create(name="Intervention")[0]


class DeleteActionView(generics.DestroyAPIView):
    """delete an action"""
    model = Action
    permission_classes = [IsAdminUser, ]

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])


class AboutMeView(generics.ListAPIView):
    """update an action date"""
    model = User
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)
