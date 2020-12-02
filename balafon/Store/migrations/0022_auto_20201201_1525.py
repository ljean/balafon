# Generated by Django 2.2.17 on 2020-12-01 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0021_saleitem_is_extra'),
    ]

    operations = [
        migrations.AddField(
            model_name='storemanagementactiontype',
            name='footer_template_name',
            field=models.CharField(blank=True, default='', help_text='Set the name of a custom template for commercial document footer', max_length=100, verbose_name='footer template name'),
        ),
        migrations.AddField(
            model_name='storemanagementactiontype',
            name='header_template_name',
            field=models.CharField(blank=True, default='', help_text='Set the name of a custom template for commercial document header', max_length=100, verbose_name='header template name'),
        ),
    ]