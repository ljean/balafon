# coding: utf8

from django.core.management.base import BaseCommand
from balafon.Crm.models import City,Contact,Entity

def Enleve_Accents(txt):
    ch1 = "àâçéèêëîïôùûüÿ-".decode("utf8")
    ch2 = "aaceeeeiiouuuy "
    s = ""
    for c in txt:
        i = ch1.find(c)
        if i>=0:
            s += ch2[i]
        else:
            s += c
    return s

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        contacts=Contact.objects.all()
        entities=Entity.objects.all()
        cities=City.objects.all()
        prec=City(name="", parent=None)
        for c in cities:
            try:
                if c.id != prec.id and Enleve_Accents(c.name.lower())==Enleve_Accents(prec.name.lower()) and c.parent==prec.parent:
                    for co in contacts:
                        if co.city!=None:
                            if co.city==c:
                                co.city=prec
                                co.save()
                    for e in entities:
                        if e.city!=None:
                            if e.city==c:
                                e.city=prec
                                e.save()
                    c.delete()
                    print(c.name + "[deleted]")
                prec=c
            except ValueError:
                    pass