# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.management.base import BaseCommand

from balafon.Crm import models


class Command(BaseCommand):
    help = u"add a new credit of emailings"
    use_argparse = False

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        for region in models.Zone.objects.filter(type__type='region'):
            print region.name

        print '**********'

        large_region_type = models.ZoneType.objects.get_or_create(name=u'Grandes régions', type=u'large_region')[0]

        mapping = [
            [u'Hauts de France', [u'Nord-Pas-de-Calais', u'Picardie']],
            [u'Normandie', [u'Haute-Normandie', u'Basse-Normandie']],
            [u'Ile-de-France', [u'Ile-de-France']],
            [u'Grand-Est', [u'Alsace', u'Champagne-Ardenne', u'Lorraine']],
            [u'Bretagne', [u'Bretagne']],
            [u'Pays de la Loire', [u'Pays de la Loire']],
            [u'Centre Val de Loire', [u'Centre']],
            [u'Bourgogne Franche-Comté', [u'Bourgogne', u'Franche-Comté']],
            [u'Nouvelle Aquitaine', [u'Aquitaine', u'Poitou-Charentes', u'Limousin']],
            [u'Occitanie Pyrénées-Méditerranée', [u'Midi-Pyrénées', u'Languedoc-Roussillon']],
            [u'Auvergne Rhône-Alpes', [u'Auvergne', u'Rhône-Alpes']],
            [u"Provence-Alpes-Côte d'Azur", [u"Provence-Alpes-Côte d'Azur"]],
            [u"Corse", [u'Corse']],
            [u"Guyane", [u'Guyane']],
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
                    print "#", child_region_name, "missing"
