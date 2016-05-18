# coding: utf8

from django.core.management.base import BaseCommand
from balafon.Crm.models import City

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        with open("\Users\Maxence\Documents\caspart.txt","r") as fichier:
            for line in fichier:
                mots=line.split("\t")
                ide=mots[0]
                city=mots[1]
                if len(mots)>3:
                    print("\n" + city)
                    print("\t[0] No corresponding")
                    for i in range(2,len(mots)):
                        print("\t[" + `i-1` + "] : " + mots[i])
                    choice=int(raw_input("Choose the number corresponding"))
                    if choice==0:
                        print("\nNo modification")
                    else:
                        c=City.objects.get(id=ide)
                        c.name=mots[choice+1]
                        c.save()
                        print("Change saved : " + mots[1] + " ---> " + mots[choice+1])
                elif len(mots)==3:
                    choice1=raw_input(city + "  will be replaced by  " + mots[2] + "\nAccept ? (y/n)")
                    if choice1=="y":
                        c=City.objects.get(id=ide)
                        c.name=mots[2]
                        c.save()
                        print("\nChange saved : " + mots[1] + " ---> " + mots[2])
                    elif choice1=="n":
                        print("No modification")
                print("_____________")