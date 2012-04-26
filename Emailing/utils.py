# -*- coding: utf-8 -*-

from django.template import Context
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from sanza.Crm.models import Contact, Action, ActionType
from datetime import date, timedelta, datetime
from sanza.Emailing.models import MagicLink, EmailingCounter, Emailing
from django.core.mail import get_connection, EmailMultiAlternatives
import re
from coop_cms.models import Newsletter
from coop_cms.utils import make_links_absolute
from coop_cms.html2text import html2text
from datetime import date

class CreditMissing(Exception): pass

def get_emailing_context(emailing, contact):
    data = dict(contact.__dict__)
    data['fullname'] = contact.fullname
    
    #clone the object: Avoid overwriting {tags} for ever
    newsletter = Newsletter()
    newsletter.__dict__ = dict(emailing.newsletter.__dict__)
    
    newsletter.subject = newsletter.subject.format(**data)
    html_content = newsletter.content.format(**data)
    
    #magic links
    links = re.findall('href="(?P<url>.+?)"', html_content)
    
    for link in links:
        magic_link, _is_new = MagicLink.objects.get_or_create(emailing=emailing, url=link)
        magic_url = settings.COOP_CMS_SITE_PREFIX+reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid])
        html_content = html_content.replace('href="{0}"'.format(link), 'href="{0}"'.format(magic_url))
        
    unregister_url = settings.COOP_CMS_SITE_PREFIX+reverse('emailing_unregister', args=[emailing.id, contact.uuid])
    
    newsletter.content = html_content
    
    return {
        'title': newsletter.subject, 'newsletter': newsletter, 'by_email': True,
        'MEDIA_URL': settings.MEDIA_URL, 'STATIC_URL': settings.STATIC_URL,
        'SITE_PREFIX': settings.COOP_CMS_SITE_PREFIX, 'my_company': settings.SANZA_MY_COMPANY,
        'unregister_url': unregister_url, 'contact': contact, 'emailing': emailing,
    }
    
    
def send_newsletter(emailing, max_nb):
    #Create automatically an action type for logging one action by contact
    emailing_action_type, _is_new = ActionType.objects.get_or_create(name=_(u'Emailing'))

    #Clean the urls 
    emailing.newsletter.content = make_links_absolute(emailing.newsletter.content)

    connection = get_connection()
    from_email = settings.COOP_CMS_FROM_EMAIL
    emails = []
    
    nb_contacts = emailing.send_to.count()
    try:
        available = 0
        counter = EmailingCounter.objects.all().order_by('-credit')[0]
        if nb_contacts > counter.credit:
            available = counter.credit
            raise CreditMissing
    except (IndexError, CreditMissing):
        emailing.status = Emailing.STATUS_CREDIT_MISSING
        emailing.save()
        raise CreditMissing(
            _(u'Credit missing for sending this emailing (available: {0} - required {1}').format(
                available, nb_contacts
            )
        )
        
    contacts = list(emailing.send_to.all()[:max_nb])
    for contact in contacts:
        
        if contact.get_email:
            context = Context(get_emailing_context(emailing, contact))
            t = get_template(emailing.newsletter.get_template_name())
            html_text = t.render(context)
        
            text = html2text(html_text)
            headers = {'Reply-To': settings.COOP_CMS_REPLY_TO}
            email = EmailMultiAlternatives(emailing.newsletter.subject, text, from_email, [contact.get_email_address()], headers=headers)
            email.attach_alternative(html_text, "text/html")
            emails.append(email)
            
            #create action
            action = Action.objects.create(
                entity = contact.entity, subject=context['title'], planned_date=emailing.scheduling_dt,
                type = emailing_action_type, detail=text, contact=contact, done=True,
                display_on_board=False, done_date=datetime.now()
            )
            
        #print contact, "processed"
        emailing.send_to.remove(contact)
        emailing.sent_to.add(contact)
    
    #print "emailing", emailing.send_to.all(), emailing.sent_to.all()
    emailing.save()
    nb_sent = connection.send_messages(emails)
    
    counter.credit = counter.credit - nb_sent
    if counter.credit == 0:
        counter.finshed_date = date.today()
    counter.save()
    
    return nb_sent
    