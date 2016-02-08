# -*- coding: utf-8 -*-
"""utils"""

import csv
import codecs

from django.contrib.auth.models import User
from django.db.models import Q

from balafon.Crm import models
from balafon.Crm import settings as crm_settings
from balafon.utils import logger


def filter_icontains_unaccent(queryset, field, text):
    """use postgres unaccent"""
    if crm_settings.is_unaccent_filter_supported():
        queryset = queryset.extra(
            where=[u"UPPER(unaccent("+field+")) LIKE UPPER(unaccent(%s))"],
            params=[u"%{0}%".format(text)]
        )
        return queryset
    else:
        field = field.split(".")[-1].strip('"')
        return queryset.filter(**{field+"__icontains": text})


def get_users(self):
    """get django users"""
    return User.objects.exclude(firstame="", lastname="")


def get_in_charge_users():
    """get balafon users"""
    return models.TeamMember.objects.filter(active=True)
    

def unicode_csv_reader(the_file, encoding, dialect=csv.excel, **kwargs):
    """read csv file properly"""
    if 'delimiter' in kwargs:
        kwargs['delimiter'] = str(kwargs['delimiter'])
    csv_reader = csv.reader(the_file, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [codecs.decode(cell, encoding) for cell in row]


def check_city_exists(city_name, zip_code, country):
    """return True if city exists"""
    default_country = crm_settings.get_default_country()
    foreign_city = bool(country) and (country != default_country)
    if foreign_city:
        zone_type = models.ZoneType.objects.get(type='country')
        queryset = models.Zone.objects.filter(name=country, type=zone_type)
    else:
        code = zip_code[:2]
        queryset = models.Zone.objects.filter(code=code)
    
    if queryset.count() == 0:
        #The parent doesn't exist so th city can't exist
        return False
    parent = queryset[0]
    return models.City.objects.filter(name__iexact=city_name, parent=parent).count() == 1


def format_city_name(city_name):
    """format city name"""
    city_name = city_name.strip()
    for formatter in crm_settings.city_formatters():
        if formatter[0] == "replace":
            sub_str, replace_str = formatter[1:]
            city_name = city_name.replace(sub_str, replace_str)
        if formatter[0] == "capitalize_words":
            sep = formatter[1]
            words = [word.capitalize() for word in city_name.split(sep) if word]
            city_name = sep.join(words)
    return city_name


def resolve_city(city_name, zip_code, country='', default_department=''):
    """get a city form a name and zip code"""
    country = country.strip()
    city_name = format_city_name(city_name)
    default_country = crm_settings.get_default_country()
    foreign_city = bool(country) and (country != default_country)
    if foreign_city:
        zone_type = models.ZoneType.objects.get(type='country')
        queryset = models.Zone.objects.filter(type=zone_type)
        queryset = filter_icontains_unaccent(queryset, '"Crm_zone"."name"', country)
        country_count = queryset.count()
        if country_count == 0:
            parent = models.Zone.objects.create(name=country.capitalize(), type=zone_type)
        else:
            parent = queryset[0]
            if country_count > 1:
                logger_message = u"{0} different zones for '{1}'".format(country_count, country)
                logger.warning(logger_message)
    else:
        code = zip_code[:2] or default_department
        try:
            parent = models.Zone.objects.get(code=code)
        except models.Zone.DoesNotExist:
            parent = None
    
    queryset = models.City.objects.filter(parent=parent)
    queryset = filter_icontains_unaccent(queryset, '"Crm_city"."name"', city_name)
    cities_count = queryset.count()
    if cities_count:
        if cities_count > 1:
            logger_message = u"{0} different cities for '{1}' {2}".format(cities_count, city_name, parent)
            logger.warning(logger_message)
        return queryset[0]
    else:
        return models.City.objects.create(name=city_name, parent=parent)


def get_actions_by_set(actions_qs, max_nb=0, action_set_list=None):
    """group actions"""
    actions_by_set = []
    if action_set_list is None:
        action_set_list = [None] + list(models.ActionSet.objects.all().order_by('ordering'))
    
    for a_set in action_set_list:
        queryset = actions_qs.filter(type__set=a_set).order_by("-planned_date", "-id")
        qs_count = queryset.count()
        if qs_count:
            if max_nb:
                actions = queryset[:max_nb]
            else:
                actions = queryset
            actions_by_set += [(
                a_set.id if a_set else 0,
                a_set.name if a_set else u"",
                actions,
                qs_count
            )]
            
    return actions_by_set


def get_default_country():
    """get default country object"""
    country_name = crm_settings.get_default_country()
    try:
        default_country = models.Zone.objects.get(name=country_name, parent__isnull=True, type__type="country")
    except models.Zone.DoesNotExist:
        try:
            zone_type = models.ZoneType.objects.get(type="country")
        except models.ZoneType.DoesNotExist:
            zone_type = models.ZoneType.objects.create(type="country", name=u"Country")
        default_country = models.Zone.objects.create(name=country_name, parent=None, type=zone_type)
    return default_country


def get_suggested_same_as_contacts(contact_id=None, lastname='', firstname='', email=''):
    """return list a suggestions for same as"""
    if not lastname and not email:
        return models.Contact.objects.none()
    else:
        query_criteria = None
        if lastname:
            query_criteria = Q(lastname__iexact=lastname, firstname__iexact=firstname)
        if email:
            email_criteria = Q(email__iexact=email) | Q(entity__email__iexact=email)
            if query_criteria:
                query_criteria = query_criteria | email_criteria
            else:
                query_criteria = email_criteria
        queryset = models.Contact.objects.filter(query_criteria)
        if contact_id:
            queryset = queryset.exclude(id=contact_id)
        return queryset