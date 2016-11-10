# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0008_auto_20161109_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='storemanagementactiontype',
            name='references_text',
            field=models.TextField(default=b'', help_text='this text will be added at the bottom of the commercial document', verbose_name='references text', blank=True),
        ),
    ]
