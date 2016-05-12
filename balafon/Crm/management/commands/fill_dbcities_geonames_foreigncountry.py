# coding: utf8

import codecs
import difflib
import os
import urllib
import zipfile

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
            if x.possibilities == "":
                pass
            print(x.city.name.encode('utf8'))
            print("\t[0] : No match")
            temp = x.possibilities.split("|")
            count = 0
            if len(temp) == 1:
                print("\t[1] : " + x.possibilities)
                count = 1
            else:
                for i in range (1,len(temp)):
                    count += 1
                    print("\t[" + `i` + "] : " + temp[i])
            choice = -1
            while choice > count or choice < 0:
                choice = int(raw_input("\nWrite the value of the corresponding name : "))
            if choice > 0:
                if len(temp) == 1:
                    x.city.name = temp[choice-1]
                    x.city.save()
                    print("\nName changed to : " + temp[choice-1] + "\n\n")
                    x.change_validated = "yes"
                    x.save()
                else:
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


def fill_db(cntry, country_name):
    
    #Add all the cities from GeoNames in the database
        
    
    with codecs.open("dev/balafon/balafon/Crm/fixtures/" + cntry + ".txt","r","utf8") as file1:
        nbcities = 0
        count = 0
        for l in file1:
            nbcities += 1
        for l in file1:
            try:
                words = l.split("\t")
                cname = words[2]
                dept = words[5]
                reg = words[3]
                if len(Zone.objects.filter(name=country_name, type=ZoneType.objects.get(name="Pays"))) > 0:
                    zonec = Zone.objects.filter(name=country_name, type=ZoneType.objects.get(name="Pays"))[0]
                else:
                    zonec = Zone(name=country_name, type=ZoneType.objects.get(name="Pays"))
                    zonec.save()
                if reg != "":
                    if len(Zone.objects.filter(name=reg, type=ZoneType.objects.get(name="Région".decode('utf8')))) > 0:
                        zoner = Zone.objects.filter(name=reg, type=ZoneType.objects.get(name="Région".decode('utf8')))[0]
                    else:
                        zoner = Zone(name=reg, type=ZoneType.objects.get(name="Région".decode('utf8')), parent=zonec, code=words[4])
                        zoner.save()
                else:
                    zoner = zonec
                if dept != '':
                    if len(Zone.objects.filter(name=dept, type=ZoneType.objects.get(name="Département".decode('utf8')))) > 0:
                        zoned = Zone.objects.filter(name=dept, type=ZoneType.objects.get(name="Département".decode('utf8')))[0]
                    else:
                        zoned = Zone(name=dept, type=ZoneType.objects.get(name="Département".decode('utf8')), parent=zoner, code=words[6])
                        zoned.save()
                else:
                    zoned = zoner
                new=City(name=cname, parent=zoned, district_id=words[8], latitude=float(words[9]), longitude=float(words[10]), zip_code=words[1], geonames_valid=True, country=country_name)
                new.save()
                count += 1
                if count % 500 == 0:
                    print(count + "/" + nbcities)
            except UnicodeEncodeError:
                print("Error " + words[1])
                pass
    
    
def update_existingdb(country_name):
    #Modify city names (already in the database) to correspond to GeoNames ones
    cities = list(City.objects.filter(country=country_name, geonames_valid=False))
    
    rightcities = list(City.objects.filter(country=country_name, geonames_valid=True))
    rcities = []
    for i in rightcities:
        rcities.append(i.name)
    
    for c in cities:
        try:
            name_changed = 0        #Detect if the city name has already changed (0 if not / 1 if it changed)
            cname1 = remove_accents(c.name.lower())
            matches = difflib.get_close_matches(cname1, rcities, cutoff=0.5)
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
                    print("[Special Cases] --- " + c.name)
                elif len(matches) > 1:
                    possibilities = ""
                    for e in matches:
                        possibilities = possibilities + "|" + e 
                    if possibilities != "":
                        special_cases(c, possibilities)
                    print("[Special Cases] " + c.name)
        except UnicodeEncodeError:
            special_cases(c,"")
            pass
        except AttributeError:
            pass    
        
        
def update_doubles(country_name):       #Update contacts and entities and remove the cities appearing twice or more
        
    cities=list(City.objects.filter(country=country_name).order_by('name', 'parent', 'zip_code'))
    prec=City(name="", parent=None)
    for c in cities:
        try:
            if c.district_id == "999":
                if len(c.parent.code) == 2:
                    c.district_id = c.parent.code + "0"
                elif len(c.parent.code) == 3:
                    c.district_id = c.parent.code
                c.save()
            if remove_accents(c.name.lower()) == remove_accents(prec.name.lower()) and (c.parent == prec.parent or c.parent.name == prec.country or c.country == prec.parent.name) :
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
            if contacts:
                contacts[0].city.zip_code = contacts[0].zip_code
                contacts[0].city.save()
                print("[saved] " + contacts[0].zip_code + "  " + contacts[0].city.name)
                haschanged = 1
            if haschanged == 0:
                entities = Entity.objects.filter(city=c)
                if entities:
                    entities[0].city.zip_code = entities[0].zip_code
                    entities[0].city.save()
                    print("[saved] " + entities[0].zip_code + "  " + entities[0].city.name)
        except UnicodeEncodeError:
            print("Unicode Error")
            pass

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        print("Updating database, please wait ...\n\n")
        for m in City.objects.filter(country=None):
            if m.parent.type.name == 'Pays':
                m.country = m.parent.name
                m.save()
            elif m.parent.parent.type.name == 'Pays':
                m.country = m.parent.parent.name
                m.save()
            elif m.parent.parent.parent.type.name == 'Pays':
                m.country = m.parent.parent.parent.name
                m.save()
        
        cntry = ''
        while cntry == '':
            country_name = raw_input("\nEnter the name of the country :\n")
            if country_name == 'Italie':
                cntry = 'IT'
            elif country_name == 'Royaume-Uni':
                cntry = 'GB'
            elif country_name == 'Espagne':
                cntry = 'ES'
            elif country_name == 'Allemagne':
                cntry = 'DE'
            elif country_name == 'Belgique':
                cntry = 'BE'
            elif country_name == 'Luxembourg':
                cntry = 'LU'
            elif country_name == 'Suisse':
                cntry = 'CH'
            else:
                print("Unknown name")

        urllib.urlretrieve('http://download.geonames.org/export/zip/' + cntry + '.zip', '/Users/Maxence/Documents/' + cntry + '.zip')
        zfile = zipfile.ZipFile('/Users/Maxence/Documents/' + cntry + '.zip','r')
        for i in zfile.namelist():
            if i== cntry + '.txt':
                data = zfile.read(i)                   ## lecture du fichier compresse 
                fp = open('dev/balafon/balafon/Crm/fixtures/' + cntry + '.txt', "wb")  ## creation en local du nouveau fichier 
                fp.write(data)                         ## ajout des donnees du fichier compresse dans le fichier local 
                fp.close() 
        zfile.close()
        os.remove('/Users/Maxence/Documents/' + cntry + '.zip')
        
        choose = -1
        while choose != 0:        
            print("\nChoose the action :")
            print("\t[0] Quit")
            print("\t[1] Fill the database from \'fixtures/" + cntry + ".txt\'")
            print("\t[2] Manage special cases")
            print("\t[3] Update contacts and entities and delete cities appearing twice or more")
            print("\t[4] Update existing cities")
            print("\t[5] Run all")
            print("\t[6] Update zip code of all cities\n\n")
            
            choose = int(raw_input("Enter the value of action : "))
            if choose == 1:
                fill_db(cntry, country_name)
            elif choose == 2:
                manage_spe_cases()
            elif choose == 3:
                update_doubles(country_name)
            elif choose == 4:
                update_existingdb(country_name)
            elif choose == 5:
                fill_db(cntry, country_name)
                update_doubles(country_name)
                update_existingdb(country_name)
                manage_spe_cases()
                update_doubles(country_name)
                return
            elif choose == 6:
                update_zip_code()