# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from django.core.management.base import BaseCommand

from balafon.Crm import models


class Command(BaseCommand):
    help = u"add a new credit of emailings"
    use_argparse = False

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        for region in models.Zone.objects.filter(type__type='region'):
            print(region.name)

        print('**********')

        large_region_type = models.ZoneType.objects.get_or_create(name='Grandes régions', type='large_region')[0]

        mapping = [
            ['Hauts de France', ['Nord-Pas-de-Calais', 'Picardie']],
            ['Normandie', ['Haute-Normandie', 'Basse-Normandie']],
            ['Ile-de-France', ['Ile-de-France']],
            ['Grand-Est', ['Alsace', 'Champagne-Ardenne', 'Lorraine']],
            ['Bretagne', ['Bretagne']],
            ['Pays de la Loire', ['Pays de la Loire']],
            ['Centre Val de Loire', ['Centre']],
            ['Bourgogne Franche-Comté', ['Bourgogne', 'Franche-Comté']],
            ['Nouvelle Aquitaine', ['Aquitaine', 'Poitou-Charentes', 'Limousin']],
            ['Occitanie Pyrénées-Méditerranée', ['Midi-Pyrénées', 'Languedoc-Roussillon']],
            ['Auvergne Rhône-Alpes', ['Auvergne', 'Rhône-Alpes']],
            [u"Provence-Alpes-Côte d'Azur", [u"Provence-Alpes-Côte d'Azur"]],
            [u"Corse", ['Corse']],
            [u"Guyane", ['Guyane']],
        ]

        for large_region_name, child_region_names in mapping:

            large_region = models.Zone.objects.get_or_create(
                name=large_region_name, type=large_region_type
            )[0]

            for child_region_name in child_region_names:
                try:
                    child_region = models.Zone.objects.get(
                        name=child_region_name, type__type='region'
                    )
                    child_region.groups.add(large_region)
                    child_region.save()
                except models.Zone.DoesNotExist:
                    print("#", child_region_name, "missing")
