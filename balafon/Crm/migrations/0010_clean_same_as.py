# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    """Set same_as_priority for all same-as contacts """

    # Your migration code goes here
    # We can't import the SameAs model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    same_as_model = apps.get_model("Crm", "SameAs")

    for same_as in same_as_model.objects.all():

        if same_as.contact_set.count() == 1:

            for contact in same_as.contact_set.all():
                contact.same_as = None
                contact.same_as_priority = 0
                contact.save()

        if same_as.contact_set.count() <= 1:

            same_as.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0009_remove_sameas_main_contact'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
