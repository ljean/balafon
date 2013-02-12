# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from sanza.Crm.models import Contact, Entity

class ContactProfile(models.Model):
    user = models.OneToOneField(User)
    contact = models.OneToOneField(Contact)

    #User.profile = property(lambda u: ContactProfile.objects.get_or_create(user=u)[0])

    def __unicode__(self):
        return self.user.username
    
 
#signals
def create_profile(sender, instance, signal, created, **kwargs):
    if not created:
        create_profile = False
        try:
            profile = ContactProfile.objects.get(user=instance)
        except ContactProfile.DoesNotExist:
            create_profile = True
    else:
        create_profile = True
        
    if create_profile:
        entity = Entity(
            name = instance.username,
            is_single_contact = True
        )
        entity.save()
        #This create a default contact
        contact = entity.contact_set.all()[0]
        
        contact.lastname = instance.last_name
        contact.firstname = instance.first_name
        contact.email = instance.email
        contact.save()
        
        ContactProfile(user=instance, contact=contact).save()

signals.post_save.connect(create_profile, sender=User)