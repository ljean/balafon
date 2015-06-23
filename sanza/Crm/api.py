# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from rest_framework import generics, serializers, viewsets

from sanza.Crm.models import Action, ActionType, Contact
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


class UpdateActionDate(generics.UpdateAPIView):
    """update an action date"""
    model = Action
    serializer_class = serializers.ActionUpdateDateSerializer

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])


class UpdateAction(generics.UpdateAPIView):
    """update an action"""
    model = Action
    serializer_class = serializers.ActionUpdateSerializer
    contacts = None

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])

    def update(self, request, *args, **kwargs):
        self.contacts = request.data.get("contacts", [])
        response = super(UpdateAction, self).update(request, *args, **kwargs)
        return response

    def perform_update(self, serializer):
        obj = serializer.save()
        obj.contacts.clear()
        for contact_id in self.contacts:
            try:
                contact = Contact.objects.get(id=contact_id)
                obj.contacts.add(contact)
            except Contact.DoesNotExist:
                pass
        obj.save()
        return obj


class CreateAction(generics.CreateAPIView):
    """create an action"""
    model = Action
    serializer_class = serializers.ActionUpdateSerializer
    contacts = None

    def create(self, request, *args, **kwargs):
        self.contacts = request.data.get("contacts", [])
        response = super(CreateAction, self).create(request, *args, **kwargs)
        return response

    def perform_create(self, serializer):
        obj = serializer.save()

        obj.type = ActionType.objects.get_or_create(name="Intervention")[0]

        obj.contacts.clear()
        for contact_id in self.contacts:
            try:
                contact = Contact.objects.get(id=contact_id)
                obj.contacts.add(contact)
            except Contact.DoesNotExist:
                pass
        obj.save()
        return obj


class DeleteAction(generics.DestroyAPIView):
    """delete an action"""
    model = Action

    def get_queryset(self):
        return self.model.objects.filter(pk=self.kwargs['pk'])
