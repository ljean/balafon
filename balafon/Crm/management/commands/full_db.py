# coding: utf8


import codecs
import difflib

from balafon.Crm.models import City
from balafon.Crm.models import Zone
from balafon.Crm.models import SpecialCasesCities

from django.core.management.base import BaseCommand


def remove_accents(txt):
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


def special_cases(city, txt):
    ct = SpecialCasesCities(city = city, possibilities = txt)
    ct.save()


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        dict_dept = {}
        cities = City.object.all()
        
        #Add all the cities from GeoNames in the database
        
        with codecs.open("fixtures\GeoNames_f.txt","r","latin-1") as file1:
            for line in file1:
                words = line.split("\t")
                cname = words[2]
                dept = words[5]
                if dict_dept.get(dept) == None:
                    dict_dept[dept] = []
                    tab = dict_dept.get(dept)
                    tab.append(cname)
                else:
                    tab = dict_dept.get(dept)
                    tab.append(cname)
                zone = Zone.objects.get(name = dept)
                new=City(name=cname,parent=zone)
                new.save()
                print("Nouvelle entree : " + cname)
                
        #Modify city names (already in the database) to correspond to GeoNames ones
                
        for city in cities:
            try:
                if city.parent.type != 'Pays':
                    name_changed = 0        #Detect if the city name has already changed (0 if not / 1 if it changed)
                    cname1 = remove_accents(city.name.lower())
                    tab1 = dict_dept.get(city.parent.name)
                    matches = difflib.get_close_matches(cname1, tab1)
                    for match in matches:
                        if remove_accents(match.lower()) == cname1:
                            print("Change saved : " + city.name + " ---> " + match)
                            city.name = match
                            city.save()
                            name_changed = 1
                    if name_changed == 0:
                        if len(matches) == 0:
                            print("No result found")
                        elif len(matches) == 1:
                            special_cases(city, matches[0])
                            print("City added to \'Special Cases\'")
                        elif len(matches) < 1:
                            possibilities = ""
                            for elem in matches:
                                possibilities = possibilities + elem + "|"
                            special_cases(city, possibilities)
                            print("City added to \'Special Cases\'")
            except UnicodeEncodeError:
                special_cases(city,"")
                pass
            
        #Change the name of the special cases cities
            
        spe_cases = SpecialCasesCities.objects.all()
        for case in spe_cases:
            print(case.city.name)
            if case.possibilities == "":
                new_name = raw_input("Error - Write the name to set for this city :")
                case.city.name = new_name;
                case.save()
            else:
                print("\t[0] : No match")
                temp = possibilities.split("|")
                count = 1
                for poss in temp:
                    print("\t[" + `count` + "] : " + poss)
                    count += 1
                choice = int(raw_input("\nWrite the value of the corresponding name : \n"))
                if choice > 0:
                    case.city.name = temp[choice - 1]
                    case.save()
                    print("\nName changed to : " + temp[choice - 1])
                else:
                    print("No modification")
                
        #Update contacts and entities and remove the cities appearing twice or more
        
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