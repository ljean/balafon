# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0003_actiontype_hide_contacts_buttons'),
    ]

    operations = [
        migrations.AddField(
            model_name='actiontype',
            name='mail_to_subject',
            field=models.CharField(default=b'', help_text='This would be used as subject when sending the action by email', max_length=100, verbose_name='Subject of email', blank=True),
        ),
    ]
