# Generated by Django 2.2.17 on 2020-11-23 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0005_auto_20180409_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactProfileCustomField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('value', models.CharField(blank=True, default='', max_length=200, verbose_name='value')),
                ('entity_field', models.BooleanField(default=False)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='Profile.ContactProfile')),
            ],
        ),
    ]