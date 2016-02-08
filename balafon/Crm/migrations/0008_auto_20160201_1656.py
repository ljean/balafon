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

        same_as.main_contact.same_as_priority = 1
        same_as.main_contact.save()

        other_contacts_queryset = same_as.contact_set.exclude(id=same_as.main_contact.id)
        for index, other_contact in enumerate(other_contacts_queryset):
            other_contact.same_as_priority = index + 2
            other_contact.save()


class Migration(migrations.Migration):

    dependencies = [
        ('Crm', '0007_auto_20160201_1638'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]


