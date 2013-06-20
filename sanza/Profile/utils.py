# -*- coding: utf-8 -*-

from sanza.Crm.models import Contact, Entity, Action, ActionType
from django.utils.translation import ugettext as _
from models import ContactProfile, CategoryPermission
from datetime import datetime
from sanza.utils import logger
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context


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
            
    
    contact.lastname = contact.lastname or user.last_name
    contact.firstname = contact.firstname or user.first_name
    contact.email = user.email
    contact.accept_newsletter = profile.accept_newsletter
    contact.accept_3rdparty = profile.accept_3rdparty
    contact.email_verified = True
    contact.save()
    
    profile.contact = contact
    profile.save()
    return profile

def check_category_permission(obj, permission, user):
    #check that the object has a category
    
    try:
        cat_perm = CategoryPermission.objects.get(category=obj.category)
    except AttributeError:
        #logger.debug('object category has no category')
        return True
    except CategoryPermission.DoesNotExist:
        #If no category permission exists : anyone is allowed
        #logger.debug('object category has no permission defined')
        return True
    
    #Get the contact corresponding to the logged user
    try:
        contact = user.contactprofile.contact
    except (ContactProfile.DoesNotExist, Contact.DoesNotExist, AttributeError):
        #If anonymous user or no contact exists for this profile
        #users are not allowed to check the category
        #logger.debug("user contact does't exist")
        return False
    
    if permission == 'can_view_article':
        groups = cat_perm.can_view_groups
    elif permission == 'can_edit_article':
        groups = cat_perm.can_edit_groups
    elif permission == "can_download_file":
        groups = cat_perm.can_view_groups
    else:
        #This perm is not managed : allow it
        return True
    
    for group in groups.all():
        if group.contacts.filter(id=contact.id).count() or group.entities.filter(id=contact.entity.id).count():
            #user is member of an allowed group
            return True
    #user is not member of a group : do not allow
    return False


def notify_registration(profile):
    #send message by email
    notification_email = getattr(settings, 'SANZA_NOTIFICATION_EMAIL', '')
    if notification_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        
        data = {
            'contact': profile.contact,
            'site': settings.COOP_CMS_SITE_PREFIX,
        }
        t = get_template('Profile/registration_notification_email.txt')
        content = t.render(Context(data))
        
        email = EmailMessage(
            _(u"New registration"), content, from_email,
            [notification_email], headers = {'Reply-To': profile.contact.email})
        try:
            email.send()
        except Exception:
            logger.exception("notify_registration")
