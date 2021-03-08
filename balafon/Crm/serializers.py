# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

import re

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.translation import ugettext

from rest_framework import serializers

from balafon.Crm.models import (
    Action, ActionType, ActionStatus, Contact, City, Entity, EntityType, TeamMember, Zone
)
from balafon.Crm.settings import get_default_country


class TeamMemberSerializer(serializers.HyperlinkedModelSerializer):
    """Serializers define the API representation."""

    class Meta:
        model = TeamMember
        fields = ('id', 'name', )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """Serializers define the API representation."""

    class Meta:
        model = User
        fields = ('id', 'username', 'last_name', 'first_name', )


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'name')


class CountrySerializer(serializers.ModelSerializer):
    is_foreign_country = serializers.BooleanField(read_only=True)

    class Meta:
        model = Zone
        fields = ('id', 'name', 'is_foreign_country', )


class ContactSerializer(serializers.ModelSerializer):
    """Serialize a contact"""
    get_city = CitySerializer(read_only=True)
    get_country = CountrySerializer(read_only=True)
    get_address = serializers.CharField(read_only=True)
    get_address2 = serializers.CharField(read_only=True)
    get_address3 = serializers.CharField(read_only=True)
    get_zip_code = serializers.CharField(read_only=True)
    get_cedex = serializers.CharField(read_only=True)
    get_billing_city = CitySerializer(read_only=True)
    get_billing_country = CountrySerializer(read_only=True)
    get_billing_address = serializers.CharField(read_only=True)
    get_billing_address2 = serializers.CharField(read_only=True)
    get_billing_address3 = serializers.CharField(read_only=True)
    get_billing_zip_code = serializers.CharField(read_only=True)
    get_billing_cedex = serializers.CharField(read_only=True)
    get_phone = serializers.CharField(read_only=True)
    get_view_url = serializers.CharField(read_only=True)

    class Meta:
        model = Contact
        fields = (
            'id', 'fullname', 'lastname', 'firstname', 'title', 'job',
            'get_city', 'get_address', 'get_address2', 'get_address3', 'get_cedex', 'get_zip_code', 'get_country',
            'get_billing_city', 'get_billing_address', 'get_billing_address2', 'get_billing_address3',
            'get_billing_cedex', 'get_billing_zip_code', 'get_billing_country',
            'mobile', 'get_phone', 'email', 'notes', 'get_view_url', 'favorite_language',
        )


class NewContactSerializer(serializers.ModelSerializer):
    """Write a new contact"""
    lastname = serializers.CharField(required=True)
    firstname = serializers.CharField(required=True)
    address = serializers.CharField(required=True)
    zip_code = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = Contact
        fields = (
            'lastname', 'firstname', 'email', 'address', 'address2', 'address3', 'cedex', 'zip_code',
            'country', 'city'
        )

    def validate_country(self, country_id):
        try:
            return Zone.objects.get(id=country_id, parent__isnull=True)
        except Zone.DoesNotExist:
            raise serializers.ValidationError(ugettext('Invalid country'))

    def validate_zip_code(self, zip_code):
        return zip_code.strip()

    def validate_city(self, city_name):
        words = re.split(r'\W+', city_name)
        city_name = '-'.join([word.capitalize() for word in words if word])
        if not city_name:
            raise serializers.ValidationError(ugettext('The city name is required'))
        return city_name

    def get_city(self, validated_data):
        zip_code = validated_data['zip_code']
        city_name = validated_data['city']
        country = validated_data.pop('country')
        default_country = get_default_country()
        if country.name != default_country:
            city = City.objects.get_or_create(name=city_name, parent=country)[0]
        else:
            if len(zip_code) < 2:
                raise serializers.ValidationError(ugettext('You must enter a zip code'))
            try:
                dep = Zone.objects.get(Q(code=zip_code[:2]) | Q(code=zip_code[:3]))
            except Zone.DoesNotExist:
                raise serializers.ValidationError(ugettext('Invalid zip code'))
            city = City.objects.get_or_create(name=city_name, parent=dep)[0]
        return city

    def validate(self, attrs):
        validated_data = super(NewContactSerializer, self).validate(attrs)
        validated_data['city'] = self.get_city(validated_data)
        return validated_data


class EntityTypeSerializer(serializers.ModelSerializer):
    """Serialize an entity type"""

    class Meta:
        model = EntityType
        fields = ('id', 'name',)


class EntitySerializer(serializers.ModelSerializer):
    """Serialize an entity"""
    city = CitySerializer(read_only=True)
    type = EntityTypeSerializer(read_only=True)
    get_view_url = serializers.CharField(read_only=True)
    country = CountrySerializer(read_only=True)
    billing_city = CitySerializer(read_only=True)
    billing_country = CountrySerializer(read_only=True)

    class Meta:
        model = Entity
        fields = (
            'id', 'name', 'type', 'city', 'address', 'address2', 'address3', 'cedex', 'country', 'zip_code',
            'billing_city', 'billing_address', 'billing_address2', 'billing_address3', 'billing_cedex',
            'billing_zip_code', 'billing_country', 'phone', 'email', 'website', 'notes', 'get_view_url',
        )


class ActionStatusSerializer(serializers.ModelSerializer):
    """action status"""

    class Meta:
        model = ActionStatus
        fields = ('id', 'name')


class ActionTypeSerializer(serializers.ModelSerializer):
    """action type serializer"""
    allowed_status = ActionStatusSerializer(many=True, read_only=True)
    default_status = ActionStatusSerializer(read_only=True)
    default_status2 = ActionStatusSerializer(read_only=True)

    class Meta:
        model = ActionType
        fields = (
            'id', 'name', 'allowed_status', 'default_status', 'allowed_status2', 'default_status2', 'order_index',
        )


class ActionSerializer(serializers.ModelSerializer):
    """Serialize an action"""
    contacts = ContactSerializer(many=True, read_only=True)
    entities = EntitySerializer(many=True, read_only=True)
    last_modified_by = UserSerializer(many=False, read_only=True)
    mail_to = serializers.CharField(read_only=True)

    class Meta:
        model = Action
        fields = (
            'id', 'contacts', 'entities', 'subject', 'planned_date', 'end_datetime', 'type', 'status', 'status2',
            'in_charge', 'detail', 'last_modified_by', 'modified', 'get_action_number', 'mail_to'
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
    planned_date = serializers.DateTimeField(allow_null=True)
    end_datetime = serializers.DateTimeField(allow_null=True)

    class Meta:
        model = Action
        fields = (
            'contacts', 'planned_date', 'end_datetime', 'subject', 'in_charge', 'detail', 'type', 'status', 'status2',
        )
