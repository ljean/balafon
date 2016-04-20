# coding: utf8

import codecs
import difflib
import os.path
import time

from django.core.management.base import BaseCommand
from django.conf import settings

from balafon.Crm.models import City


def Enleve_Accents(txt):
    ch1 = "àâçéèêëîïôùûüÿ-".decode("utf8")
    ch2 = "aaceeeeiiouuuy "
    s = ""
    for c in txt:
        i = ch1.find(c)
        if i >= 0:
            s += ch2[i]
        else:
            s += c
    return s


def Cas_Part(txt):
    filename = os.path.join(settings.PROJECT_PATH, 'temp', 'caspart.txt')
    with open("\Users\Maxence\Documents\caspart.txt","a") as fichier:
        fichier.write(txt + "\n")


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        with open("\Users\Maxence\Documents\caspart.txt","w") as fichier:
            fichier.write("")
        with open("\Users\Maxence\Documents\log.txt","w") as fic:
            fic.write("")
        cities=City.objects.all()
        for c in cities:
            try :
                b=0
                tab=[]
                if c.parent.type.name != "Pays":
                    nom=Enleve_Accents(c.name)
                    with codecs.open("\Users\Maxence\Downloads\Possibilites\GeoNames_f.txt","r","latin-1") as fichier:
                        for line in fichier:
                            mots=line.split("\t")
                            if mots[5]==c.parent.name:
                                tab.append(mots[2])
                    r=difflib.get_close_matches(c.name.lower(),tab)
                    for e in r:
                        nom1=Enleve_Accents(e)
                        if nom.lower()==nom1.lower():
                            b=1
                            print("Valid name : " + c.name + " ---> " + e)
                            c.name=e
                            c.save()
                    if b==0:
                        if len(r)==0:
                            print("No match found for " + c.name)
                        elif len(r)==1:
                            print("Change to accept")
                            Cas_Part(`c.id` + "\t" + c.name + "\t" + r[0])
                        elif len(r)>1:
                            print("Change to accept")
                            st=`c.id` + "\t" + c.name
                            for i in r:
                                st = st + "\t" + i
                            Cas_Part(st)
                                
                    print("_______________\n")
            except UnicodeEncodeError:
                with open("\Users\Maxence\Documents\log.txt","a") as fic:
                    fic.write("Erreur sur la ville d'id :\t" + `c.id` + "\n")
                    pass