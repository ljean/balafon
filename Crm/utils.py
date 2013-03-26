# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from sanza.Crm import models
from django.utils.translation import ugettext as _

def get_users(self):
    return User.objects.exclude(firstame="", lastname="")
    
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

def resolve_city(city_name, zip_code, country='', default_department=''):
    default_country = get_default_country()
    foreign_city = bool(country) and (country!=default_country)
    if foreign_city:
        zone_type = models.ZoneType.objects.get(type='country')
        parent, _is_new = models.Zone.objects.get_or_create(name=country, type=zone_type)
    else:
        code = zip_code[:2] or default_department
        try:
            parent = models.Zone.objects.get(code=code)
        except models.Zone.DoesNotExist, msg:
            parent = None
    try:
        return models.City.objects.get(name__iexact=city_name, parent=parent)
    except models.City.DoesNotExist:
        return models.City.objects.create(name=city_name, parent=parent)
        
def get_actions_by_set(actions):
    actions_dict = {}
    for a in actions:
        key = a.type.set if a.type else None
        try:
            actions_dict[key].append(a)
        except KeyError:
            actions_dict[key] = [a]
    
    actions_by_set = []    
    for a_set in models.ActionSet.objects.all().order_by('ordering'):
        acts = actions_dict.get(a_set, None)
        if acts:
            actions_by_set.append((a_set.id, a_set.name, acts))
    title = _(u"Other kind of actions") if models.ActionSet.objects.count() else _(u"Actions")
    actions_by_set += [(0, title, actions_dict.get(None, []))]
    return actions_by_set
