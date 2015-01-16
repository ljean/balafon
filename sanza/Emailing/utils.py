# -*- coding: utf-8 -*-

from datetime import datetime
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import get_connection, EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from coop_cms.models import Newsletter
from coop_cms.settings import get_newsletter_context_callbacks
from coop_cms.utils import dehtml
from coop_cms.utils import make_links_absolute

from sanza.Crm.models import Action, ActionType, Contact, Entity, Subscription, SubscriptionType
from sanza.Emailing.models import MagicLink


def format_context(text, data):
    # { and } need to be escaped for the format function
    text = text.replace('{', '{{').replace('}', '}}')
    
    # #!- and -!# are turned into { and }
    text = text.replace('#!-', '{').replace('-!#', '}')
    
    return text.format(**data)


def get_emailing_context(emailing, contact):
    data = dict(contact.__dict__)
    data['fullname'] = contact.fullname
    
    #clone the object: Avoid overwriting {tags} for ever
    newsletter = Newsletter()
    newsletter.__dict__ = dict(emailing.newsletter.__dict__)
    
    newsletter.subject = format_context(newsletter.subject, data)
    html_content = format_context(newsletter.content, data)
    
    #magic links
    links = re.findall('href="(?P<url>.+?)"', html_content)
    
    for link in links:
        if (not link.lower().startswith('mailto:')) and (link[0] != "#"): #mailto and internal links are not magic
            magic_link, _is_new = MagicLink.objects.get_or_create(emailing=emailing, url=link)
            magic_url = newsletter.get_site_prefix()+reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid])
            html_content = html_content.replace('href="{0}"'.format(link), 'href="{0}"'.format(magic_url))
        
    unregister_url = newsletter.get_site_prefix()+reverse('emailing_unregister', args=[emailing.id, contact.uuid])
    
    newsletter.content = html_content
    
    context_dict = {
        'title': newsletter.subject,
        'newsletter': newsletter,
        'by_email': True,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'SITE_PREFIX': emailing.get_domain_url_prefix(),
        'my_company': settings.SANZA_MY_COMPANY,
        'unregister_url': unregister_url,
        'contact': contact,
        'emailing': emailing,
    }
    
    for callback in get_newsletter_context_callbacks():
        d = callback(newsletter)
        if d:
            context_dict.update(d)
    
    return context_dict


def send_newsletter(emailing, max_nb):
    #Create automatically an action type for logging one action by contact
    emailing_action_type, _is_new = ActionType.objects.get_or_create(name=_(u'Emailing'))

    #Clean the urls
    emailing.newsletter.content = make_links_absolute(
        emailing.newsletter.content, emailing.newsletter, site_prefix=emailing.get_domain_url_prefix()
    )
    
    connection = get_connection()
    from_email = settings.COOP_CMS_FROM_EMAIL
    emails = []
    
    nb_contacts = emailing.send_to.count()
        
    contacts = list(emailing.send_to.all()[:max_nb])
    for contact in contacts:
        
        if contact.get_email:
            context = Context(get_emailing_context(emailing, contact))
            t = get_template(emailing.newsletter.get_template_name())
            lang = settings.LANGUAGE_CODE[:2]
            translation.activate(lang)
            html_text = t.render(context)
            html_text = make_links_absolute(
                html_text, emailing.newsletter, site_prefix=emailing.get_domain_url_prefix()
            )
            
            text = dehtml(html_text)
            list_unsubscribe_url = emailing.get_domain_url_prefix() + reverse(
                "emailing_unregister", args=[emailing.id, contact.uuid]
            )
            list_unsubscribe_email = getattr(settings, 'COOP_CMS_REPLY_TO', '') or from_email
            headers = {
                "List-Unsubscribe": u"<{0}>, <mailto:{1}?subject=unsubscribe>".format(
                    list_unsubscribe_url, list_unsubscribe_email
                )
            }

            if getattr(settings, 'COOP_CMS_REPLY_TO', None):
                headers['Reply-To'] = settings.COOP_CMS_REPLY_TO
            email = EmailMultiAlternatives(
                emailing.newsletter.subject,
                text,
                from_email,
                [contact.get_email_address()],
                headers=headers
            )
            email.attach_alternative(html_text, "text/html")
            emails.append(email)
            
            #create action
            action = Action.objects.create(
                subject=context['title'], planned_date=emailing.scheduling_dt,
                type=emailing_action_type, detail=text, done=True,
                display_on_board=False, done_date=datetime.now()
            )
            action.contacts.add(contact)
            action.save()
            
        #print contact, "processed"
        emailing.send_to.remove(contact)
        emailing.sent_to.add(contact)
    
    emailing.save()
    nb_sent = connection.send_messages(emails)
    return nb_sent or 0


def create_subscription_action(contact, subscriptions):
    action_type = ActionType.objects.get_or_create(name=_(u"Subscription"))[0]
    action = Action.objects.create(
        subject=_(u"Subscribe to {0}").format(u", ".join(subscriptions)),
        type=action_type,
        planned_date=datetime.now(),
        display_on_board=False
    )
    action.contacts.add(contact)
    action.save()
    return action


def send_notification_email(request, contact, actions, message):
    """send an email to admin for information about new subscription"""

    notification_email = getattr(settings, 'SANZA_NOTIFICATION_EMAIL', '')
    if notification_email:
        data = {
            'contact': contact,
            'groups': contact.entity.group_set.all(),
            'actions': actions,
            'message': mark_safe(message),
            'site': Site.objects.get_current(),
        }
        t = get_template('Emailing/subscribe_notification_email.txt')
        content = t.render(Context(data))
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        
        email = EmailMessage(
            _(u"Message from web site"), content, from_email,
            [notification_email], headers={'Reply-To': contact.email}
        )
        try:
            email.send()
            if request:
                messages.add_message(
                    request, messages.SUCCESS,
                    _(u"The message have been sent")
                )
        except Exception, msg:
            if request:
                messages.add_message(
                    request, messages.ERROR,
                    _(u"The message couldn't be send.")
                )


def send_verification_email(contact):
    """send an email to subscriber for checking his email"""

    if contact.email:
        data = {
            'contact': contact,
            'verification_url': reverse('emailing_email_verification', args=[contact.uuid]),
            'site': Site.objects.get_current(),
            'my_company': mark_safe(settings.SANZA_MY_COMPANY),
        }
        t = get_template('Emailing/subscribe_verification_email.txt')
        content = t.render(Context(data))
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        
        email = EmailMessage(
            _(u'Verification of your email address'),
            content,
            from_email,
            [contact.email]
        )
        email.send()
        return True
    return False


def save_subscriptions(contact, subscription_types):
    """"""
    subscriptions = []
    queryset = SubscriptionType.objects.filter(sites=Site.objects.get_current())
    for subscription_type in queryset:

        subscription = Subscription.objects.get_or_create(
            contact=contact,
            subscription_type=subscription_type
        )[0]

        if subscription_type in subscription_types:
            subscription.accept_subscription = True
            subscription.subscription_date = datetime.now()
            #This is added to the notification email
            subscriptions.append(subscription_type.name)
        else:
            subscription.accept_subscription = False
        subscription.save()
    return subscriptions


def on_bounce(email, description, permanent):
    """can be called to signal soft or hard bounce"""
    action_type = ActionType.objects.get_or_create(name="hard_bounce" if permanent else "soft_bounce")[0]

    contacts = Contact.objects.filter(email=email)
    entities = Entity.objects.filter(email=email)

    action = Action.objects.create(
        subject=u"{0}: {1}".format(
            email, _(u"Permanent Email Error") if permanent else _(u"Email Error")
        ),
        detail=description,
        planned_date=datetime.now(),
        type=action_type,
    )

    action.contacts = contacts
    action.entities = entities
    action.save()

    #Unsubscribe emails for permanent errors
    if permanent:
        all_contacts = list(contacts)
        for entity in entities:
            #for entities with the given email: Add the contacts with no email (by default the entity email is used)
            all_contacts.extend(entity.contact_set.filter(email=""))

        for contact in all_contacts:
            for subscription in contact.subscription_set.all():
                subscription.accept_subscription = False
                subscription.unsubscription_date = datetime.now()
                subscription.save()