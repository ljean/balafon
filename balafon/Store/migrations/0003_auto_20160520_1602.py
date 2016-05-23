# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def store_assign_analysis_code(apps, schema_editor):
    """Assign the Internet AalysisCode to all existing sales"""
    sale_analysis_code_class = apps.get_model("Store", "SaleAnalysisCode")
    sale_class = apps.get_model("Store", "Sale")

    sale_analysis_code = sale_analysis_code_class.objects.get_or_create(name=u"Internet")[0]

    for sale in sale_class.objects.filter(analysis_code__isnull=True):
        sale.analysis_code = sale_analysis_code
        sale.save()


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0002_auto_20160503_2223'),
    ]

    operations = [
        migrations.RunPython(store_assign_analysis_code),
    ]
