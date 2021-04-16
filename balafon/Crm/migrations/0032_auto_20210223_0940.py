# Generated by Django 2.2.18 on 2021-02-23 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0031_auto_20201202_1754'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ['ordering', 'name'], 'verbose_name': 'team member', 'verbose_name_plural': 'team members'},
        ),
        migrations.AddField(
            model_name='teammember',
            name='ordering',
            field=models.IntegerField(default=0, verbose_name='ordering'),
        ),
    ]