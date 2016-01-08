# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=100, verbose_name='label')),
                ('icon', models.CharField(default=b'', max_length=20, verbose_name='icon', blank=True)),
                ('order_index', models.IntegerField(default=0)),
                ('position', models.IntegerField(default=0, help_text='Where the menu will be set', verbose_name='position', choices=[(0, 'Menu'), (1, 'Planning')])),
            ],
            options={
                'ordering': ['order_index', 'label'],
                'verbose_name': 'Custom menu',
                'verbose_name_plural': 'Custom menus',
            },
        ),
        migrations.CreateModel(
            name='CustomMenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=100, verbose_name='label')),
                ('icon', models.CharField(default=b'', max_length=20, verbose_name='icon', blank=True)),
                ('url', models.CharField(default=b'', max_length=100, verbose_name='url', blank=True)),
                ('reverse', models.CharField(default=b'', max_length=100, verbose_name='reverse', blank=True)),
                ('order_index', models.IntegerField(default=0)),
                ('attributes', models.CharField(default=b'', max_length=100, verbose_name='attributes', blank=True)),
                ('only_for_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='only for users', blank=True)),
                ('parent', models.ForeignKey(to='Users.CustomMenu')),
            ],
            options={
                'ordering': ['order_index', 'label'],
                'verbose_name': 'Custom menu item',
                'verbose_name_plural': 'Custom menu items',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='object id')),
                ('content_type', models.ForeignKey(related_name='user_favorite_set', verbose_name='content_type', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='user_favorite_set', verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Favorite',
                'verbose_name_plural': 'Favorites',
            },
        ),
        migrations.CreateModel(
            name='UserHomepage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(verbose_name='URL')),
                ('user', models.OneToOneField(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User homepage',
                'verbose_name_plural': 'User homepages',
            },
        ),
        migrations.CreateModel(
            name='UserPreferences',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notify_due_actions', models.BooleanField(default=False, verbose_name='Notify due actions')),
                ('message_in_favorites', models.BooleanField(default=False, verbose_name='Create automatically a favorite for message posted from the public form')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together=set([('user', 'content_type', 'object_id')]),
        ),
    ]
