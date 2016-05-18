# -*- coding: utf-8 -*-

import codecs
import difflib
import os.path

from balafon.Crm.models import City
from balafon.Crm.models import Zone
from balafon.Crm.models import Contact
from balafon.Crm.models import Entity
from balafon.Crm.models import SpecialCaseCity

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
    special_case = SpecialCaseCity(city=city, oldname=city.name, possibilities=txt, change_validated="no")
    special_case.save()


def manage_spe_cases():
    """Change the name of the special cases cities"""

    spe_cases = SpecialCaseCity.objects.filter(change_validated="no")
    for spe_case in spe_cases:
        try:
            print(spe_case.city.name.encode('utf-8'))
            if spe_case.possibilities == "":
                new_name = raw_input("Error - Write the name to set for this city :")
                spe_case.city.name = new_name
                spe_case.city.save()
                spe_case.change_validated = "yes"
                spe_case.save()
            else:
                print("\t[0] : No match")
                temp = spe_case.possibilities.split("|")
                count = 0
                for p in temp:
                    count += 1
                    print("\t[" + `count` + "] : " + p)
                choice = -1
                while choice > count or choice < 0:
                    choice = int(raw_input("\nWrite the value of the corresponding name : "))
                if choice > 0:
                    spe_case.city.name = temp[choice - 1]
                    spe_case.city.save()
                    print("\nName changed to : " + temp[choice - 1] + "\n\n")
                    spe_case.change_validated = "yes"
                    spe_case.save()
                else:
                    print("No modification\n\n")

        except UnicodeEncodeError:
            print("Error unknown character - try changing name in admin")
            pass


def fill_db():
    dict_dept = {}
    cities = list(City.objects.all())
    
    # Add all the cities from GeoNames in the database
    app_dir_name = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    geonames_file_name = os.path.join(app_dir_name, 'fixtures/GeoNames_f.txt')

    with codecs.open(geonames_file_name, "r", "latin-1") as file1:
        for l in file1:
            words = l.split("\t")
            cname = words[2]
            dept = words[5]
            if dict_dept.get(dept) is None:
                dict_dept[dept] = []
                tab = dict_dept.get(dept)
                tab.append(cname)
            else:
                tab = dict_dept.get(dept)
                tab.append(cname)
            zone = Zone.objects.get(name = dept)
            new=City(name=cname, parent=zone, district_id=words[8], latitude=float(words[9]), longitude=float(words[10]), zip_code=words[1])
            new.save()
            print("[added]  " + cname)
            
    # Modify city names (already in the database) to correspond to GeoNames ones
    if not cities == False:
        for c in cities:
            try:
                if c.parent.type.name != 'Pays':
                    name_changed = 0        #Detect if the city name has already changed (0 if not / 1 if it changed)
                    cname1 = remove_accents(c.name.lower())
                    tab1 = dict_dept.get(c.parent.name)
                    matches = difflib.get_close_matches(cname1, tab1)
                    for m in matches:
                        if remove_accents(m.lower()) == cname1:
                            print("Change saved : " + c.name + " ---> " + m)
                            c.name = m
                            c.save()
                            name_changed = 1
                    if name_changed == 0:
                        if len(matches) == 0:
                            print("No result found")
                        elif len(matches) == 1:
                            special_cases(c, matches[0])
                            print("City added to \'Special Cases\'")
                        elif len(matches) < 1:
                            possibilities = ""
                            for e in matches:
                                possibilities = possibilities + e + "|"
                            special_cases(c, possibilities)
                            print("City added to \'Special Cases\'")
            except TypeError:
                print("TypeError")
                pass
            except UnicodeEncodeError:
                special_cases(c,"")
                pass
            except AttributeError:
                pass    
        
        
def update_doubles():
    """Update contacts and entities and remove the cities appearing twice or more"""
        
    cities = City.objects.exclude(parent__type__name='Pays')
    prec = City(name="", parent=None)
    for city in cities:
        try:
            if city.district_id == "999":
                if len(city.parent.code) == 2:
                    city.district_id = city.parent.code + "0"
                elif len(city.parent.code) == 3:
                    city.dsitrict_id = city.parent.code
                city.save()
            if remove_accents(city.name.lower()) == remove_accents(prec.name.lower()) and city.parent == prec.parent:
                if city.district_id[2] != "0" and prec.district_id[2] == "0":
                    rightcity = city
                    wrongcity = prec
                else:
                    rightcity = prec
                    wrongcity = city
                contacts = Contact.objects.filter(city=wrongcity)
                for o in contacts:
                    o.city = rightcity
                    o.save()
                entities = Entity.objects.filter(city=wrongcity)
                for e in entities:
                    e.city = rightcity
                    e.save()
                wrongcity.delete()
                print("[deleted]  " + wrongcity.name)
            prec=city
        except ValueError:
            pass
        except AssertionError:
            pass
        
        
def update_zip_code():
    """Give a zip code to cities that don't have one"""
    cities = City.objects.filter(zip_code="00000")
    for c in cities:
        try:
            haschanged = 0
            contacts = Contact.objects.filter(city=c)
            if not contacts:
                print("\n")
            else:
                contacts[0].city.zip_code = contacts[0].zip_code
                contacts[0].city.save()
                print("[saved] " + contacts[0].zip_code + "  " + contacts[0].city.name)
                haschanged = 1
            if haschanged == 0:
                entities = Entity.objects.filter(city=c)
                if not entities:
                    print("\n")
                else:
                    entities[0].city.zip_code = entities[0].zip_code
                    entities[0].city.save()
                    print("[saved] " + entities[0].zip_code + "  " + entities[0].city.name)
        except UnicodeEncodeError:
            print("Unicode Error")
            pass


class Command(BaseCommand):
    """Command class"""

    def handle(self, *args, **options):
        """called when command is executed"""
        
        choose = -1
        while choose != 0:        

            print("Choose the action :")
            print("\t[0] Quit")
            print("\t[1] Fill the database from \'fixtures/GeoNames_f.txt\'")
            print("\t[2] Manage special cases")
            print("\t[3] Update contacts and entities and delete cities appearing twice or more")
            print("\t[4] Update the zip code of all cities")
            print("\t[5] Run all\n\n")
            
            choose = int(raw_input("Enter the value of action : "))

            if choose == 1:
                fill_db()

            elif choose == 2:
                manage_spe_cases()

            elif choose == 3:
                update_doubles()

            elif choose == 4:
                update_zip_code()

            elif choose == 5:
                fill_db()
                manage_spe_cases()
                update_doubles()
                update_zip_code()
                break