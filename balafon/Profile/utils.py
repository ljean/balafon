# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from balafon.utils import logger, now_rounded
from balafon.Crm import settings as crm_settings
from balafon.Crm.models import Contact, Entity, EntityType, Action, ActionType, Group
from balafon.Emailing.models import SubscriptionType
from balafon.Emailing.utils import save_subscriptions
from balafon.Profile.models import ContactProfile, CategoryPermission


def create_profile_contact(user):
    profile = user.contactprofile
    if not profile:
        profile = ContactProfile(user=user)
    rename_entity = False
    
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
            if profile and profile.entity_type:
                entity_type = profile.entity_type
            else:
                if crm_settings.ALLOW_SINGLE_CONTACT:
                    entity_type = None
                else:
                    et_id = getattr(settings, 'BALAFON_INDIVIDUAL_ENTITY_ID', 1)
                    entity_type, x = EntityType.objects.get_or_create(id=et_id)
                    rename_entity = True

            entity = Entity(
                name=profile.entity_name if profile else user.username,
                is_single_contact=(entity_type is None) and crm_settings.ALLOW_SINGLE_CONTACT,
                type=entity_type
            )
            
            entity.save()
            # This create a default contact
            contact = entity.default_contact

        if warn_duplicates:
            action_type = ActionType.objects.get_or_create(name=_(u"Balafon admin"))[0]
            action = Action.objects.create(
                subject=_(u"A user have registred with email {0} used by several other contacts".format(user.email)),
                type=action_type,
                planned_date=now_rounded(),
                detail=_(u'You should check that this contact is not duplicated'),
                display_on_board=True
            )
            action.contacts.add(contact)
            action.save()

    fields = (
        'gender', 'firstname', 'lastname', 'phone', 'mobile', 'address', 'address2', 'address3',
        'zip_code', 'city', 'cedex', 'country',
    )
    if profile:
        for field in fields:
            value = getattr(profile, field, None)
            if value:
                setattr(contact, field, value)

    contact.lastname = contact.lastname or user.last_name
    contact.firstname = contact.firstname or user.first_name
    contact.email = user.email
    contact.email_verified = True
    if not contact.lastname:
        contact.lastname = user.email.split("@")[0]

    contact.save()

    try:
        ids = [int(s) for s in profile.subscriptions_ids.split(",")]
    except ValueError:
        ids = []

    subscription_types = []
    for subscription_type_id in ids:
        try:
            subscription_types.append(SubscriptionType.objects.get(id=subscription_type_id))
        except SubscriptionType.DoesNotExist:
            pass
    save_subscriptions(contact, subscription_types)

    try:
        groups_ids = [int(s) for s in profile.groups_ids.split(",")]
    except ValueError:
        groups_ids = []

    for group_id in groups_ids:
        try:
            group = Group.objects.get(id=group_id)
            group.contacts.add(contact)
            group.save()
        except Group.DoesNotExist:
            pass

    action_type = ActionType.objects.get_or_create(name=_(u"Account creation"))[0]
    action = Action.objects.create(
        subject=_(u"Create an account on web site"),
        type=action_type,
        planned_date=now_rounded(),
        display_on_board=False,
        done=True
    )
    action.contacts.add(contact)
    action.save()
    
    if rename_entity:
        contact.entity.name = u"{0.lastname} {0.firstname}".format(contact).strip().upper()
        contact.entity.save()
    
    profile.contact = contact
    profile.save()
    return profile


def check_category_permission(obj, permission, user):
    """check that the object has a category"""
    
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
        if not contact.id:
            return False
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
    """send message by email"""
    notification_email = getattr(settings, 'BALAFON_NOTIFICATION_EMAIL', '')
    if notification_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        
        data = {
            'contact': profile.contact,
            'site': getattr(settings, 'COOP_CMS_SITE_PREFIX', None),
        }
        t = get_template('Profile/registration_notification_email.txt')
        content = t.render(Context(data))
        
        email = EmailMessage(
            _(u"New registration"), content, from_email,
            [notification_email], headers={'Reply-To': profile.contact.email})
        try:
            email.send()
        except Exception:
            logger.exception("notify_registration")
