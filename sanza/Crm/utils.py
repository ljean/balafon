# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from sanza.Crm import models
from django.utils.translation import ugettext as _
from sanza.Crm import settings as crm_settings
from sanza.utils import logger
from sanza.Crm.settings import get_default_country as get_default_country_name

#@transaction.commit_manually
def filter_icontains_unaccent(qs, field, text):
    if crm_settings.is_unaccent_filter_supported():
        qs = qs.extra(
            where=[u"UPPER(unaccent("+field+")) LIKE UPPER(unaccent(%s))"],
            params = [u"%{0}%".format(text)]
        )
        return qs    
    return qs.filter(**{field+"__icontains": text})

def get_users(self):
    return User.objects.exclude(firstame="", lastname="")

def get_in_charge_users():
    return User.objects.filter(is_staff=True).exclude(first_name="")
    
#import csv, codecs, cStringIO
#
#class UTF8Recoder:
#    """
#    Iterator that reads an encoded stream and reencodes the input to UTF-8
#    """
#    def __init__(self, f, encoding):
#        self.reader = codecs.getreader(encoding)(f)
#
#    def __iter__(self):
#        return self
#
#    def next(self):
#        return self.reader.next().encode("utf-8")
#
#class UnicodeReader:
#    """
#    A CSV reader which will iterate over lines in the CSV file "f",
#    which is encoded in the given encoding.
#    """
#
#    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
#        f = UTF8Recoder(f, encoding)
#        self.reader = csv.reader(f, dialect=dialect, **kwds)
#
#    def next(self):
#        row = self.reader.next()
#        return [unicode(s, "utf-8") for s in row]
#
#    def __iter__(self):
#        return self
#
#class UnicodeWriter:
#    """
#    A CSV writer which will write rows to CSV file "f",
#    which is encoded in the given encoding.
#    """
#
#    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
#        # Redirect output to a queue
#        self.queue = cStringIO.StringIO()
#        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
#        self.stream = f
#        self.encoder = codecs.getincrementalencoder(encoding)()
#
#    def writerow(self, row):
#        self.writer.writerow([s.encode("utf-8") for s in row])
#        # Fetch UTF-8 output from the queue ...
#        data = self.queue.getvalue()
#        data = data.decode("utf-8")
#        # ... and reencode it into the target encoding
#        data = self.encoder.encode(data)
#        # write to the target stream
#        self.stream.write(data)
#        # empty queue
#        self.queue.truncate(0)
#
#    def writerows(self, rows):
#        for row in rows:
#            self.writerow(row)
#
from sanza.Crm.settings import get_default_country
import csv, codecs
def unicode_csv_reader(the_file, encoding, dialect=csv.excel, **kwargs):
    if kwargs.has_key('delimiter'):
        kwargs['delimiter'] = str(kwargs['delimiter'])
    csv_reader = csv.reader(the_file, dialect=dialect, **kwargs)
    for row in csv_reader:
        #yield [codecs.decode(cell, 'iso-8859-15') for cell in row] #'cp1252'
        yield [codecs.decode(cell, encoding) for cell in row]

def check_city_exists(city_name, zip_code, country):
    default_country = get_default_country()
    foreign_city = bool(country) and (country!=default_country)
    if foreign_city:
        zone_type = models.ZoneType.objects.get(type='country')
        qs = models.Zone.objects.filter(name=country, type=zone_type)
    else:
        code = zip_code[:2]
        qs = models.Zone.objects.filter(code=code)
    
    if qs.count()==0:
        #The parent doesn't exist so th city can't exist
        return False
    parent = qs[0]
    return (models.City.objects.filter(name__iexact=city_name, parent=parent).count()==1)
    
def format_city_name(city_name):
    city_name = city_name.strip()
    for formatter in crm_settings.city_formatters():
        if formatter[0] == "replace":
            c1, c2 = formatter[1:]
            city_name = city_name.replace(c1, c2)
        if formatter[0] == "capitalize_words":
            sep = formatter[1]
            words = [w.capitalize() for w in city_name.split(sep) if w]
            city_name = sep.join(words)
    return city_name
    
def resolve_city(city_name, zip_code, country='', default_department=''):
    country = country.strip()
    city_name = format_city_name(city_name)
    default_country = get_default_country()
    foreign_city = bool(country) and (country!=default_country)
    if foreign_city:
        zone_type = models.ZoneType.objects.get(type='country')
        qs = models.Zone.objects.filter(type=zone_type)
        qs = filter_icontains_unaccent(qs, '"Crm_zone"."name"', country)
        country_count = qs.count()
        if country_count == 0:
            parent = models.Zone.objects.create(name=country.capitalize(), type=zone_type)
        else:
            parent = qs[0]
            if country_count>1:
                logger.warning(u"{0} different zones for '{1}'".format(country_count, country))   
    else:
        code = zip_code[:2] or default_department
        try:
            parent = models.Zone.objects.get(code=code)
        except models.Zone.DoesNotExist, msg:
            parent = None
    
    qs = models.City.objects.filter(parent=parent)
    qs = filter_icontains_unaccent(qs, '"Crm_city"."name"', city_name)
    cities_count = qs.count()
    if cities_count:
        if cities_count>1:
            logger.warning(u"{0} different cities for '{1}' {2}".format(cities_count, city_name, parent))
        return qs[0]
    else:
        return models.City.objects.create(name=city_name, parent=parent)
        
def get_actions_by_set(actions_qs, max_nb=0, action_set_list=None):
    actions_by_set = []
    if action_set_list == None:
        action_set_list = [None] + list(models.ActionSet.objects.all().order_by('ordering'))
    
    for a_set in action_set_list:
        qs = actions_qs.filter(type__set=a_set).order_by("-planned_date", "-id")
        qs_count = qs.count()
        if qs_count:
            if max_nb:
                actions = qs[:max_nb]
            else:
                actions = qs
            actions_by_set += [(
                a_set.id if a_set else 0,
                a_set.name if a_set else u"",
                actions,
                qs_count
            )]
            
    return actions_by_set

def get_default_country():
    cn = get_default_country_name()
    try:
        default_country = models.Zone.objects.get(name=cn, parent__isnull=True, type__type="country")
    except models.Zone.DoesNotExist:
        try:
            zt = models.ZoneType.objects.get(type="country")
        except models.ZoneType.DoesNotExist:
            zt = models.ZoneType.objects.create(type="country", name=u"Country")
        default_country = models.Zone.objects.create(name=cn, parent=None, type=zt)
    return default_country