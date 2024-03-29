# Generated by Django 2.2.18 on 2021-02-23 09:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0023_auto_20210218_0828'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paymentmode',
            options={'ordering': ['ordering', 'id'], 'verbose_name': 'Payment mode', 'verbose_name_plural': 'Payment modes'},
        ),
        migrations.AddField(
            model_name='paymentmode',
            name='ordering',
            field=models.IntegerField(default=0, verbose_name='ordering'),
        ),
    ]
