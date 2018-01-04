# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0017_zone_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='status2',
            field=models.ForeignKey(related_name='status2_set', default=None, blank=True, to='Crm.ActionStatus', null=True),
        ),
        migrations.AddField(
            model_name='actiontype',
            name='allowed_status2',
            field=models.ManyToManyField(default=None, help_text='Action of this type allow the given status', related_name='type_status2_set', to='Crm.ActionStatus', blank=True),
        ),
        migrations.AddField(
            model_name='actiontype',
            name='default_status2',
            field=models.ForeignKey(related_name='type_default_status2_set', default=None, blank=True, to='Crm.ActionStatus', help_text='Default status for actions of this type', null=True),
        ),
    ]
