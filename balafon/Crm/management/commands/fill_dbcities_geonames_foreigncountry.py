# coding: utf8


import codecs
import difflib

from balafon.Crm.models import City
from balafon.Crm.models import Zone
from balafon.Crm.models import Contact
from balafon.Crm.models import Entity
from balafon.Crm.models import SpecialCaseCity
from balafon.Crm.models import ZoneType

from django.core.management.base import BaseCommand


def remove_accents(txt):
    ch1 = "àâäçéèêëîïôöùûüÿ-".decode("utf8")
    ch2 = "aaaceeeeiioouuuy "
    s = ""
    for c in txt:
        i = ch1.find(c)
        if i >= 0:
            s += ch2[i]
        else:
            s += c
    return s


def special_cases(city, txt):
    ct = SpecialCaseCity(city=city, oldname=city.name, possibilities=txt, change_validated="no")
    ct.save()


def manage_spe_cases():       #Change the name of the special cases cities            
    spe_cases = SpecialCaseCity.objects.filter(change_validated="no")
    for x in spe_cases:
        try:
            print(x.city.name.encode('utf8'))
            print("\t[0] : No match")
            temp = x.possibilities.split("|")
            count = 0
            for p in temp:
                count += 1
                print("\t[" + `count` + "] : " + p)
            choice = -1
            while choice > count or choice < 0:
                choice = int(raw_input("\nWrite the value of the corresponding name : "))
            if choice > 0:
                x.city.name = temp[choice]
                x.city.save()
                print("\nName changed to : " + temp[choice] + "\n\n")
                x.change_validated = "yes"
                x.save()
            else:
                print("No modification\n\n")
                x.delete()
        except UnicodeEncodeError:
            print("Error unknown character - try changing name in admin")
            pass


def fill_db():
    dict_dept = {}
    cities = list(City.objects.filter(parent__name='Suisse'))
    
    #Add all the cities from GeoNames in the database
    
    with codecs.open("dev/balafon/balafon/Crm/fixtures/CH.txt","r","latin-1") as file1:
        for l in file1:
            words = l.split("\t")
            cname = words[2]
            dept = words[5]
            reg = words[3]
            if dict_dept.get(dept) == None:
                dict_dept[dept] = []
                tab = dict_dept.get(dept)
                tab.append(cname)
            else:
                tab = dict_dept.get(dept)
                tab.append(cname)
            zonec = Zone.objects.get(name='Suisse')
            if len(Zone.objects.filter(name=reg)) > 0:
                zoner = Zone.objects.filter(name=reg)[0]
            else:
                zoner = Zone(name=reg, type=ZoneType.objects.get(name="Région".decode('utf8')), parent=zonec, code=words[4])
                zoner.save()
            if len(Zone.objects.filter(name=dept)) > 0:
                zoned = Zone.objects.filter(name=dept)[0]
            else:
                zoned = Zone(name=dept, type=ZoneType.objects.get(name="Département".decode('utf8')), parent=zoner, code=words[6])
                zoned.save()
            new=City(name=cname, parent=zoned, district_id=words[8], latitude=float(words[9]), longitude=float(words[10]), zip_code=words[1], geonames_valid=True)
            new.save()
            print("[added]  " + cname)
            
    #Modify city names (already in the database) to correspond to GeoNames ones
    if not cities == False:
        for c in cities:
            try:
                if c.parent.name == 'Suisse':
                    name_changed = 0        #Detect if the city name has already changed (0 if not / 1 if it changed)
                    cname1 = remove_accents(c.name.lower())
                    tab1 = dict_dept.get(c.parent.name)
                    matches = difflib.get_close_matches(cname1, tab1,3,0.5)
                    for m in matches:
                        if remove_accents(m.lower()) == cname1:
                            print("[saved] " + c.name + " ---> " + m)
                            c.name = m
                            c.save()
                            name_changed = 1
                    if name_changed == 0:
                        if len(matches) == 0:
                            print("No result found")
                        elif len(matches) == 1:
                            special_cases(c, matches[0])
                            print("[Special Cases] " + c.name)
                        elif len(matches) > 1:
                            possibilities = ""
                            for e in matches:
                                possibilities = possibilities + "|" + e
                            special_cases(c, possibilities)
                            print("[Special Cases] " + c.name)
            except UnicodeEncodeError:
                special_cases(c,"")
                pass
            except AttributeError:
                pass    
        
        
def update_doubles():       #Update contacts and entities and remove the cities appearing twice or more
        
    cities=City.objects.filter(parent__parent__parent__name='Suisse').order_by("name", "parent")
    prec=City(name="", parent=None)
    for c in cities:
        try:
            if c.district_id == "999":
                if len(c.parent.code) == 2:
                    c.district_id = c.parent.code + "0"
                elif len(c.parent.code) == 3:
                    c.dsitrict_id = c.parent.code
                c.save()
            if remove_accents(c.name.lower()) == remove_accents(prec.name.lower()) and c.parent==prec.parent:
                if c.geonames_valid and not prec.geonames_valid:
                    rightcity = c
                    wrongcity = prec
                else:
                    rightcity = prec
                    wrongcity = c       
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
                prec = rightcity
            else:
                prec = c
        except ValueError:
            pass
        except AssertionError:
            pass
        
        
def update_zip_code():      #Give a zip code to cities that don't have one
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
    
    def handle(self, *args, **options):
        
        choose = -1
        while choose != 0:        
            print("Choose the action :")
            print("\t[0] Quit")
            print("\t[1] Fill the database from \'fixtures/GeoNames_f.txt\'")
            print("\t[2] Manage special cases")
            print("\t[3] Update contacts and entities and delete cities appearing twice or more")
            print("\t[4] Run all")
            print("\t[5] Update the zip code of all cities\n\n")
            
            choose = int(raw_input("Enter the value of action : "))
            if choose == 0:
                return
            elif choose == 1:
                fill_db()
            elif choose == 2:
                manage_spe_cases()
            elif choose == 3:
                update_doubles()
            elif choose == 5:
                update_zip_code()
            elif choose == 4:
                fill_db()
                manage_spe_cases()
                update_zip_code()
                return