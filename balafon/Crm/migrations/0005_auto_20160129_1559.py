# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import balafon.utils


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0004_actiontype_mail_to_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionstatus',
            name='background_color',
            field=models.CharField(default=b'', validators=[balafon.utils.validate_rgb], max_length=7, blank=True, help_text='Background color. Must be a rgb code. For example: #000000', verbose_name='Background color'),
        ),
        migrations.AddField(
            model_name='actionstatus',
            name='fore_color',
            field=models.CharField(default=b'', validators=[balafon.utils.validate_rgb], max_length=7, blank=True, help_text='Fore color. Must be a rgb code. For example: #ffffff', verbose_name='Fore color'),
        ),
        migrations.AddField(
            model_name='actionstatus',
            name='is_final',
            field=models.BooleanField(default=False, help_text='The action will be marked done when it gets a final status', verbose_name='is final'),
        ),
    ]
