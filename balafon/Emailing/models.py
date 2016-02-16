# -*- coding: utf-8 -*-
"""models"""

from datetime import datetime
import uuid
import unicodedata

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
if DJANGO_VERSION > (1, 8, 0):
    from django.contrib.contenttypes.fields import GenericRelation
else:
    from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.utils.dateformat import DateFormat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

from coop_cms.models import Newsletter
from django_extensions.db.models import TimeStampedModel

from balafon.Crm.models import Contact, Action, SubscriptionType
from balafon.Crm.settings import get_language_choices
from balafon.Emailing.settings import is_mandrill_used
from balafon.Users.models import UserPreferences, Favorite


class Emailing(TimeStampedModel):
    """configuration on an emailing"""
    
    STATUS_EDITING = 1
    STATUS_SCHEDULED = 2
    STATUS_SENDING = 3
    STATUS_SENT = 4
    
    STATUS_CHOICES = (
        (STATUS_EDITING, _(u'Edition in progress')),
        (STATUS_SCHEDULED, _(u'Sending is scheduled')),
        (STATUS_SENDING, _(u'Sending in progress')),
        (STATUS_SENT, _(u'Sent')),
    )

    class Meta:
        verbose_name = _(u'Emailing')
        verbose_name_plural = _(u'Emailings')

    subscription_type = models.ForeignKey(SubscriptionType)
    newsletter = models.ForeignKey(Newsletter) 
    send_to = models.ManyToManyField(Contact, blank=True, related_name="emailing_to_be_received")
    sent_to = models.ManyToManyField(Contact, blank=True, related_name="emailing_received")
    opened_emails = models.ManyToManyField(Contact, blank=True, related_name="emailing_opened")
    status = models.IntegerField(default=STATUS_EDITING, choices=STATUS_CHOICES)

    hard_bounce = models.ManyToManyField(Contact, blank=True, related_name="emailing_hard_bounce")
    soft_bounce = models.ManyToManyField(Contact, blank=True, related_name="emailing_soft_bounce")
    spam = models.ManyToManyField(Contact, blank=True, related_name="emailing_spam")
    unsub = models.ManyToManyField(Contact, blank=True, related_name="emailing_unsub")
    rejected = models.ManyToManyField(Contact, blank=True, related_name="emailing_rejected")

    scheduling_dt = models.DateTimeField(_(u"scheduling date"), blank=True, default=None, null=True)
    sending_dt = models.DateTimeField(_(u"sending date"), blank=True, default=None, null=True)

    favorites = GenericRelation(Favorite)
    lang = models.CharField(
        _(u"language"),
        max_length=5,
        default="",
        blank=True,
        choices=get_language_choices()
    )
    from_email = models.CharField(max_length=100, blank=True, default="", verbose_name=_(u"From email"))

    def __unicode__(self):
        return u"{0} - {1}".format(self.newsletter.subject, self.get_info(extra=True))

    class Meta:
        verbose_name = _(u'emailing')
        verbose_name_plural = _(u'emailings')

    def get_info(self, extra=False):
        """returns info about the status in order to diplsay it on emailing page"""
        text = self.get_status_display()
        if self.status == Emailing.STATUS_EDITING:
            text = _("{0} - {1}").format(text, DateFormat(self.created).format(" d F Y H:i"))
            if extra:
                text += _(u" - {0} recipients").format(self.send_to.count())
        if self.status == Emailing.STATUS_SCHEDULED:
            text = _("{0} - {1}").format(text, DateFormat(self.scheduling_dt).format(" d F Y H:i"))
            if extra:
                total = self.send_to.count() + self.sent_to.count()
                text += _(u" - {0}/{1} sent").format(self.sent_to.count(), total)
        elif self.status == Emailing.STATUS_SENT:
            text = _("{0} - {1}").format(text, DateFormat(self.sending_dt).format(" d F Y H:i"))
            if extra:
                text += _(u" - {0} sent").format(self.sent_to.count())

        return text
        
    def next_action(self):
        """what to to next"""
        action = ""
        if self.status == Emailing.STATUS_EDITING:
            action = '<a class="colorbox-form action-button" href="{1}">{0}</a>'.format(
                ugettext(u'Send'), reverse("emailing_confirm_send_mail", args=[self.id])
            )
        if self.status == Emailing.STATUS_SCHEDULED:
            action = '<a class="colorbox-form action-button" href="{1}">{0}</a>'.format(
                ugettext(u'Cancel'), reverse("emailing_cancel_send_mail", args=[self.id])
            )
        return mark_safe(action)

    def get_domain_url_prefix(self):
        """domain url prefix"""
        if self.subscription_type.site:
            domain_protocol = getattr(settings, "BALAFON_DOMAIN_PROTOCOL", "http://")
            return domain_protocol + self.subscription_type.site.domain
        return ""
    
    def get_contacts(self):
        """full list of contacts"""
        return list(self.send_to.all()) + list(self.sent_to.all())
        
    def save(self, *args, **kwargs):
        """save"""
        if self.status == Emailing.STATUS_SENT and self.sending_dt == None:
            self.sending_dt = datetime.now()
        return super(Emailing, self).save(*args, **kwargs)


class MagicLink(models.Model):
    """A tracking link"""

    class Meta:
        verbose_name = _(u'Magic link')
        verbose_name_plural = _(u'Magic links')

    emailing = models.ForeignKey(Emailing)
    url = models.URLField(max_length=500)
    visitors = models.ManyToManyField(Contact, blank=True)
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    
    def __unicode__(self):
        return self.url
    
    def save(self, *args, **kwargs):
        """save"""
        super(MagicLink, self).save(*args, **kwargs)
        if not self.uuid:
            name = u'{0}-magic-link-{1}-{2}'.format(settings.SECRET_KEY, self.id, self.url)
            name = unicodedata.normalize('NFKD', unicode(name)).encode("ascii", 'ignore')
            self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, name)
            return super(MagicLink, self).save()


def force_message_in_favorites(sender, instance, signal, created, **kwargs):
    """force an action to be in user favorites"""
    action = instance
    if created and action.type and action.type.name == ugettext(u"Message"):
        for user_pref in UserPreferences.objects.filter(message_in_favorites=True):
            content_type = ContentType.objects.get_for_model(action.__class__)
            Favorite.objects.get_or_create(
                user=user_pref.user,
                content_type=content_type,
                object_id=action.id
            )
            
signals.post_save.connect(force_message_in_favorites, sender=Action)

if is_mandrill_used():
    # Import the mandrill backend
    import balafon.Emailing.backends.mandrill  # pylint: disable=unused-import
