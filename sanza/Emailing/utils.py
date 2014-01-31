# -*- coding: utf-8 -*-

from django.template import Context
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from sanza.Crm.models import Contact, Action, ActionType
from datetime import date, timedelta, datetime
from sanza.Emailing.models import MagicLink, Emailing
from django.core.mail import get_connection, EmailMultiAlternatives
import re
from coop_cms.models import Newsletter
from coop_cms.html2text import html2text
from datetime import date
from coop_cms.utils import make_links_absolute
from django.utils import translation
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.utils.safestring import mark_safe
from coop_cms.settings import get_newsletter_context_callbacks
from django.contrib import messages

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
        if (not link.lower().startswith('mailto:')) and (link[0]!="#"): #mailto and internal links are not magic
            magic_link, _is_new = MagicLink.objects.get_or_create(emailing=emailing, url=link)
            magic_url = newsletter.get_site_prefix()+reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid])
            html_content = html_content.replace('href="{0}"'.format(link), 'href="{0}"'.format(magic_url))
        
    unregister_url = newsletter.get_site_prefix()+reverse('emailing_unregister', args=[emailing.id, contact.uuid])
    
    newsletter.content = html_content
    
    context_dict = {
        'title': newsletter.subject, 'newsletter': newsletter, 'by_email': True,
        'MEDIA_URL': settings.MEDIA_URL, 'STATIC_URL': settings.STATIC_URL,
        'SITE_PREFIX': settings.COOP_CMS_SITE_PREFIX, 'my_company': settings.SANZA_MY_COMPANY,
        'unregister_url': unregister_url, 'contact': contact, 'emailing': emailing,
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
    emailing.newsletter.content = make_links_absolute(emailing.newsletter.content, emailing.newsletter)
    
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
            html_text = make_links_absolute(html_text, emailing.newsletter)
            
            text = html2text(html_text)
            headers = {'Reply-To': settings.COOP_CMS_REPLY_TO}
            email = EmailMultiAlternatives(emailing.newsletter.subject, text, from_email, [contact.get_email_address()], headers=headers)
            email.attach_alternative(html_text, "text/html")
            emails.append(email)
            
            #create action
            action = Action.objects.create(
                subject=context['title'], planned_date=emailing.scheduling_dt,
                type = emailing_action_type, detail=text, done=True,
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
    at, _x = ActionType.objects.get_or_create(name=_(u"Subscription"))
    action = Action.objects.create(
        subject = _(u"Subscribe to {0}").format(u", ".join(subscriptions)),
        type = at,
        planned_date = datetime.now(),
        display_on_board = False
    )
    action.contacts.add(contact)
    action.save()
    return action

def send_notification_email(request, contact, actions, message):
    #send an email
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
            [notification_email], headers = {'Reply-To': contact.email})
        try:
            email.send()
            if request:
                messages.add_message(request, messages.SUCCESS,
                    _(u"The message have been sent"))
        except Exception, msg:
            if request:
                messages.add_message(request, messages.ERROR,
                    _(u"The message couldn't be send."))
    
def send_verification_email(contact):
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
            _(u'Verification of your email address'), content, from_email,
            [contact.email])
        email.send()
        return True
    return False