# Generated by Django 2.2.9 on 2020-02-17 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0029_subscriptiontype_allowed_on_sites'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='on_contacts_list',
            field=models.BooleanField(default=False, verbose_name='Displayed on contacts list'),
        ),
    ]
