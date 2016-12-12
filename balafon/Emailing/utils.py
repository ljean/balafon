# -*- coding: utf-8 -*-
"""utilities"""

from datetime import datetime
import re
import sys

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import Site
from django.core.mail import get_connection, EmailMessage, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import get_language as django_get_language, ugettext as _

from coop_cms.models import Newsletter
from coop_cms.settings import get_newsletter_context_callbacks
from coop_cms.utils import dehtml, make_links_absolute

from balafon.utils import logger
from balafon.Crm.models import Action, ActionType, Contact, Entity, Subscription, SubscriptionType
from balafon.Emailing.models import Emailing, MagicLink
from balafon.Emailing.settings import is_mandrill_used


class EmailSendError(Exception):
    """An exception raise when sending email failed"""
    pass


def format_context(text, data):
    """replace custom templating by something compliant with python format function"""

    # { and } need to be escaped for the format function
    text = text.replace('{', '{{').replace('}', '}}')

    # #!- and -!# are turned into { and }
    text = text.replace('#!-', '{').replace('-!#', '}')

    return text.format(**data)


def get_emailing_context(emailing, contact):
    """get context for emailing: user,...."""
    data = dict(contact.__dict__)
    for field in ('gender_name', 'gender_dear', 'city_name', 'entity_name', 'full_address', 'fullname'):
        data[field] = getattr(contact, field)
    
    # clone the object: Avoid overwriting {tags} for ever
    newsletter = Newsletter()
    newsletter.__dict__ = dict(emailing.newsletter.__dict__)

    newsletter.subject = format_context(newsletter.subject, data)

    html_content = format_context(newsletter.content, data)

    unregister_url = newsletter.get_site_prefix() + reverse('emailing_unregister', args=[emailing.id, contact.uuid])
    
    newsletter.content = html_content

    context_dict = {
        'title': dehtml(newsletter.subject).replace('\n', ''),
        'newsletter': newsletter,
        'by_email': True,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL,
        'SITE_PREFIX': emailing.get_domain_url_prefix(),
        'my_company': emailing.subscription_type.name,
        'unregister_url': unregister_url,
        'contact': contact,
        'emailing': emailing,
    }
    
    for callback in get_newsletter_context_callbacks():
        dictionary = callback(newsletter)
        if dictionary:
            context_dict.update(dictionary)
    
    return context_dict


def patch_emailing_html(html_text, emailing, contact):
    """transform links into magic link"""
    links = re.findall('href="(?P<url>.+?)"', html_text)

    ignore_links = [
        reverse("emailing_unregister", args=[emailing.id, contact.uuid]),
        reverse("emailing_view_online", args=[emailing.id, contact.uuid]),
    ]

    for lang_tuple in settings.LANGUAGES:
        ignore_links.append(
            reverse("emailing_view_online_lang", args=[emailing.id, contact.uuid, lang_tuple[0]])
        )

    for link in links:
        if (not link.lower().startswith('mailto:')) and (link[0] != "#") and link not in ignore_links:
            # mailto, internal links, 'unregister' and 'view online' are not magic
            if len(link) < 500:

                magic_links = MagicLink.objects.filter(emailing=emailing, url=link)
                if magic_links.count() == 0:
                    magic_link = MagicLink.objects.create(emailing=emailing, url=link)
                else:
                    magic_link = magic_links[0]

                view_magic_link_url = reverse('emailing_view_link', args=[magic_link.uuid, contact.uuid])
                magic_url = emailing.newsletter.get_site_prefix() + view_magic_link_url
                html_text = html_text.replace(u'href="{0}"'.format(link), u'href="{0}"'.format(magic_url))
            else:
                if 'test' not in sys.argv:
                    logger.warning(
                        "magic link size is greater than 500 ({0}) : {1}".format(len(link), link)
                    )
    return html_text


def send_newsletter(emailing, max_nb):
    """send newsletter"""

    # Create automatically an action type for logging one action by contact
    emailing_action_type = ActionType.objects.get_or_create(name=_(u'Emailing'))[0]

    # Clean the urls
    emailing.newsletter.content = make_links_absolute(
        emailing.newsletter.content, emailing.newsletter, site_prefix=emailing.get_domain_url_prefix()
    )
    
    connection = get_connection()
    from_email = emailing.from_email or settings.COOP_CMS_FROM_EMAIL
    emails = []
    
    contacts = list(emailing.send_to.all()[:max_nb])
    for contact in contacts:
        
        if contact.get_email:
            lang = emailing.lang or contact.favorite_language or settings.LANGUAGE_CODE[:2]
            translation.activate(lang)

            emailing_context = get_emailing_context(emailing, contact)
            emailing_context["LANGUAGE_CODE"] = lang
            context = Context(emailing_context)
            the_template = get_template(emailing.newsletter.get_template_name())

            html_text = the_template.render(context)

            html_text = patch_emailing_html(html_text, emailing, contact)

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
                context['title'],
                force_line_max_length(text),
                from_email,
                [contact.get_email_address()],
                headers=headers
            )
            html_text = force_line_max_length(html_text, max_length_per_line=400, dont_cut_in_quotes=True)
            email.attach_alternative(html_text, "text/html")
            if is_mandrill_used():
                email.tags = [u'{0}'.format(emailing.id), contact.uuid]
            emails.append(email)
            
            # create action
            action = Action.objects.create(
                subject=context['title'], planned_date=emailing.scheduling_dt,
                type=emailing_action_type, detail=text, done=True,
                display_on_board=False, done_date=datetime.now()
            )
            action.contacts.add(contact)
            action.save()
            
        # print contact, "processed"
        emailing.send_to.remove(contact)
        emailing.sent_to.add(contact)
    
    emailing.save()
    nb_sent = connection.send_messages(emails)
    return nb_sent or 0


def create_subscription_action(contact, subscriptions):
    """create action when subscribing to a list"""
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

    notification_email = getattr(settings, 'BALAFON_NOTIFICATION_EMAIL', '')
    if notification_email:
        data = {
            'contact': contact,
            'groups': contact.entity.group_set.all(),
            'actions': actions,
            'message': mark_safe(message),
            'site': Site.objects.get_current(),
        }
        the_templatate = get_template('Emailing/subscribe_notification_email.txt')
        content = the_templatate.render(Context(data))

        # remove empty lines and replace any line starting with ## by a line feed
        lines = [line if line[:2] != "##" else "" for line in content.split("\n") if line]
        content = u"\n".join(lines)
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        
        email = EmailMessage(
            _(u"Message from web site"), content, from_email,
            [notification_email], headers={'Reply-To': contact.email}
        )

        success = True
        try:
            email.send()
        except Exception:  # pylint: disable=broad-except
            success = False

        if request:
            if success:
                messages.add_message(
                    request, messages.SUCCESS,
                    _(u"The message have been sent")
                )
            else:
                messages.add_message(
                    request, messages.ERROR,
                    _(u"The message couldn't be send.")
                )


def send_verification_email(contact, subscription_types=None):
    """send an email to subscriber for checking his email"""

    if contact.email:

        if subscription_types:
            my_company = u', '.join([subscription_type.name for subscription_type in subscription_types])
        else:
            my_company = settings.BALAFON_MY_COMPANY

        data = {
            'contact': contact,
            'verification_url': reverse('emailing_email_verification', args=[contact.uuid]),
            'site': Site.objects.get_current(),
            'my_company': mark_safe(my_company),
        }
        the_template = get_template('Emailing/subscribe_verification_email.txt')
        content = the_template.render(Context(data))
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        
        email = EmailMessage(
            _(u'Verification of your email address'),
            content,
            from_email,
            [contact.email]
        )
        try:
            email.send()
        except Exception as msg:  # pylint: disable=broad-except
            raise EmailSendError(unicode(msg))
        return True
    return False


def save_subscriptions(contact, subscription_types):
    """save aubscriptions"""
    subscriptions = []
    queryset = SubscriptionType.objects.filter(site=Site.objects.get_current())
    for subscription_type in queryset:

        subscription = Subscription.objects.get_or_create(
            contact=contact,
            subscription_type=subscription_type
        )[0]

        if subscription_type in subscription_types:
            subscription.accept_subscription = True
            subscription.subscription_date = datetime.now()
            # This is added to the notification email
            subscriptions.append(subscription_type.name)
        else:
            subscription.accept_subscription = False
        subscription.save()
    return subscriptions


def on_bounce(event_type, email, description, permanent, contact_uuid, emailing_id):
    """can be called to signal soft or hard bounce"""
    action_type = ActionType.objects.get_or_create(name="bounce")[0]

    contacts = Contact.objects.filter(email=email)
    entities = Entity.objects.filter(email=email)

    subject = u"{0} - {1}".format(email, u"{0}: {1}".format(event_type, description))

    action = Action.objects.create(
        subject=subject[:200],
        planned_date=datetime.now(),
        type=action_type,
    )

    action.contacts = contacts
    action.entities = entities
    action.save()

    # Unsubscribe emails for permanent errors
    if permanent:
        all_contacts = list(contacts)
        for entity in entities:
            # for entities with the given email: Add the contacts with no email (by default the entity email is used)
            all_contacts.extend(entity.contact_set.filter(email=""))

        for contact in all_contacts:
            for subscription in contact.subscription_set.all():
                subscription.accept_subscription = False
                subscription.unsubscription_date = datetime.now()
                subscription.save()

    # Update emailing statistics
    if contact_uuid and emailing_id:
        try:
            contact = Contact.objects.get(uuid=contact_uuid)
        except Contact.DoesNotExist:
            contact = None

        try:
            emailing = Emailing.objects.get(id=emailing_id)
        except Emailing.DoesNotExist:
            emailing = None

        if contact and emailing and hasattr(emailing, event_type):
            getattr(emailing, event_type).add(contact)
            emailing.save()


def get_language():
    """wrap the django get_language and make sure: we return 2 chars"""
    lang = django_get_language()
    return lang[:2]


def force_line_max_length(text, max_length_per_line=400, dont_cut_in_quotes=True):
    """returns same text with end of lines inserted if lien length is greater than 400 chars"""
    out_text = ""
    for line in text.split(u"\n"):

        if len(line) < max_length_per_line:
            out_text += line + u"\n"
        else:
            words = []
            line_length = 0
            quotes_count = 0
            for word in line.split(u" "):
                if word:
                    words.append(word)
                    quotes_count += word.count(u'"')
                    line_length += len(word) + 1
                    in_quotes = (quotes_count % 2) == 1  # If there are not an even number we may be inside a ""
                    if line_length > max_length_per_line:
                        if not (not dont_cut_in_quotes and in_quotes):
                            # Line is more than allowed length for a line. Enter a end line character
                            out_line = u" ".join(words)
                            out_text += out_line + u"\n"
                            words = []
                            line_length = 0
            if words:
                out_line = u" ".join(words)
                out_text += out_line + u"\n"

    return out_text[:-1]   # Remove the last "\n"