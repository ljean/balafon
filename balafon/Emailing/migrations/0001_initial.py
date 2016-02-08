# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0001_initial'),
        ('coop_cms', '0002_auto_20160108_1628'),
    ]

    operations = [
        migrations.CreateModel(
            name='Emailing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('status', models.IntegerField(default=1, choices=[(1, 'Edition in progress'), (2, 'Sending is scheduled'), (3, 'Sending in progress'), (4, 'Sent')])),
                ('scheduling_dt', models.DateTimeField(default=None, null=True, verbose_name='scheduling date', blank=True)),
                ('sending_dt', models.DateTimeField(default=None, null=True, verbose_name='sending date', blank=True)),
                ('lang', models.CharField(default=b'', max_length=5, verbose_name='language', blank=True, choices=[(b'', 'Par d\xe9faut'), (b'fr', 'Fran\xe7ais'), (b'en', 'English')])),
                ('from_email', models.CharField(default=b'', max_length=100, verbose_name='From email', blank=True)),
                ('hard_bounce', models.ManyToManyField(related_name='emailing_hard_bounce', to='Crm.Contact', blank=True)),
                ('newsletter', models.ForeignKey(to='coop_cms.Newsletter')),
                ('opened_emails', models.ManyToManyField(related_name='emailing_opened', to='Crm.Contact', blank=True)),
                ('rejected', models.ManyToManyField(related_name='emailing_rejected', to='Crm.Contact', blank=True)),
                ('send_to', models.ManyToManyField(related_name='emailing_to_be_received', to='Crm.Contact', blank=True)),
                ('sent_to', models.ManyToManyField(related_name='emailing_received', to='Crm.Contact', blank=True)),
                ('soft_bounce', models.ManyToManyField(related_name='emailing_soft_bounce', to='Crm.Contact', blank=True)),
                ('spam', models.ManyToManyField(related_name='emailing_spam', to='Crm.Contact', blank=True)),
                ('subscription_type', models.ForeignKey(to='Crm.SubscriptionType')),
                ('unsub', models.ManyToManyField(related_name='emailing_unsub', to='Crm.Contact', blank=True)),
            ],
            options={
                'verbose_name': 'emailing',
                'verbose_name_plural': 'emailings',
            },
        ),
        migrations.CreateModel(
            name='MagicLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=500)),
                ('uuid', models.CharField(default=b'', max_length=100, db_index=True, blank=True)),
                ('emailing', models.ForeignKey(to='Emailing.Emailing')),
                ('visitors', models.ManyToManyField(to='Crm.Contact', blank=True)),
            ],
        ),
    ]
