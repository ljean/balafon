# -*- coding: utf-8 -*-
"""cities"""

import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse

from sanza.Crm import models
from sanza.Crm.settings import get_default_country
from sanza.permissions import can_access
from sanza.utils import log_error


def get_city_name(request, city):
    """view"""
    #Anybody can accesss (public contact form of a website)
    try:
        city_id = int(city)
        city = models.City.objects.get(id=city_id)
        return HttpResponse(json.dumps({'name': city.name}), 'application/json')
    except ValueError:
        return HttpResponse(json.dumps({'name': city}), 'application/json')


@user_passes_test(can_access)
@log_error
def get_city_id(request):
    """view"""
    name = (request.GET.get('name'))
    country_id = int(request.GET.get('country', 0))
    default_country = models.Zone.objects.get(name=get_default_country(), parent__isnull=True)
    if country_id == 0 or country_id == default_country.id:
        cities = models.City.objects.filter(name__iexact=name).exclude(parent__code='')
    else:
        cities = models.City.objects.filter(name__iexact=name, parent__id=country_id)
    if cities.count() != 1:
        city_id = name
    else:
        city_id = cities[0].id
    return HttpResponse(json.dumps({'id': city_id}), 'application/json')


def get_cities(request):
    """view"""
    #subscribe form : no login required
    term = request.GET.get('term')
    country_id = int(request.GET.get('country', 0))
    default_country = models.Zone.objects.get(name=get_default_country(), parent__isnull=True)
    if country_id == 0 or country_id == default_country.id:
        cities_queryset = models.City.objects.filter(name__icontains=term).exclude(parent__code='')[:10]
        cities = [{'id': x.id, 'name': x.name} for x in cities_queryset]
    else:
        cities_queryset = models.City.objects.filter(name__icontains=term, parent__id=country_id)[:10]
        cities = [{'id': x.id, 'name': x.name} for x in cities_queryset]
    return HttpResponse(json.dumps(cities), 'application/json')
