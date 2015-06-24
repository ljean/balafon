# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from django.contrib.auth.models import User

from rest_framework import serializers

from sanza.Crm.models import Action, Contact, City, TeamMember


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer):
    """Serializers define the API representation."""

    class Meta:
        model = TeamMember
        fields = ('id', 'name',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializers define the API representation."""

    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name')


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'name')


class ContactSerializer(serializers.ModelSerializer):
    """Serialize a contact"""
    get_city = CitySerializer(read_only=True)
    get_address = serializers.CharField(read_only=True)
    get_address2 = serializers.CharField(read_only=True)
    get_address3 = serializers.CharField(read_only=True)
    get_zip_code = serializers.CharField(read_only=True)
    get_phone = serializers.CharField(read_only=True)
    get_view_url = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id', 'fullname', 'lastname', 'firstname', 'get_city', 'get_address', 'get_address2', 'get_address3',
            'get_zip_code', 'mobile', 'get_phone', 'notes', 'get_view_url'
        )


class ActionSerializer(serializers.ModelSerializer):
    """Serialize an action"""
    contacts = ContactSerializer(many=True, read_only=True)
    last_modified_by = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Action
        fields = (
            'id', 'contacts', 'subject', 'planned_date', 'end_datetime',
            'in_charge', 'detail', 'last_modified_by', 'modified', 'get_action_number'
        )


class ActionUpdateDateSerializer(serializers.ModelSerializer):
    """Serialize date for updating action date"""

    class Meta:
        model = Action
        fields = ('planned_date', 'end_datetime',)


class ContactIdSerializer(serializers.ModelSerializer):
    """Serialize contact Id"""

    class Meta:
        model = Contact
        fields = ('id', )


class ActionUpdateSerializer(serializers.ModelSerializer):
    """Serialize data for updating an action"""
    contacts = ContactIdSerializer(many=True, read_only=True)

    class Meta:
        model = Action
        fields = ('contacts', 'planned_date', 'end_datetime', 'subject', 'in_charge', 'detail', )
