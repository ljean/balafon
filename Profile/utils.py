# -*- coding: utf-8 -*-

from sanza.Crm.models import Contact, Entity, Action, ActionType
from django.utils.translation import ugettext as _
from models import ContactProfile
from datetime import datetime

def create_profile_contact(user):
    profile = user.contactprofile
    if not profile:
        profile = ContactProfile(user=user)
    
    if profile.contact:
        contact = profile.contact
    else:
        warn_duplicates = False
        contact = None
        try:
            contact = Contact.objects.get(email=user.email)
        except Contact.DoesNotExist:
            pass
        except Contact.MultipleObjectsReturned:
            warn_duplicates = True
        
        if not contact:
            entity = Entity(
                name = user.username,
                is_single_contact = True
            )
            entity.save()
            #This create a default contact
            contact = entity.contact_set.all()[0]
        
        if warn_duplicates:
            at, _x = ActionType.objects.get_or_create(name=_(u"Sanza admin"))
            action = Action.objects.create(
                subject = _(u"A user have registred with email {0} used by several other contacts".format(user.email)),
                type = at,
                planned_date = datetime.now(),
                contact = contact,
                detail = _(u'You should check that this contact is not duplicated'),
                display_on_board = True
            )
            
    contact.lastname = user.last_name
    contact.firstname = user.first_name
    contact.email = user.email
    contact.accept_newsletter = profile.accept_newsletter
    contact.accept_3rdparty = profile.accept_3rdparty
    contact.save()
    
    profile.contact = contact
    profile.save()
    return profile