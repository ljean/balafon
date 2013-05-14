# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django_extensions.db.models import TimeStampedModel, AutoSlugField
from django.contrib.auth.models import User
from sanza.Crm.models import Contact
from datetime import datetime
from django.conf import settings
import uuid
from sorl.thumbnail import default as sorl_thumbnail
import re
from coop_cms.models import Newsletter
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.utils.dateformat import DateFormat

class Emailing(TimeStampedModel):
    
    STATUS_EDITING = 1
    STATUS_SCHEDULED = 2
    STATUS_SENDING = 3
    STATUS_SENT = 4
    STATUS_CREDIT_MISSING = 5
    
    STATUS_CHOICES = (
        (STATUS_EDITING, _(u'Edition in progress')),
        (STATUS_SCHEDULED, _(u'Sending is scheduled')),
        (STATUS_SENDING, _(u'Sending in progress')),
        (STATUS_SENT, _(u'Sent')),
        (STATUS_CREDIT_MISSING, _(u'Credit missing')),
    )
    
    newsletter = models.ForeignKey(Newsletter) 
    send_to = models.ManyToManyField(Contact, blank=True, related_name="emailing_to_be_received")
    sent_to = models.ManyToManyField(Contact, blank=True, related_name="emailing_received")
    status = models.IntegerField(default=STATUS_EDITING, choices=STATUS_CHOICES)
    
    scheduling_dt = models.DateTimeField(_(u"scheduling date"), blank=True, default=None, null=True)
    sending_dt = models.DateTimeField(_(u"sending date"), blank=True, default=None, null=True)

    def __unicode__(self):
        return self.newsletter.subject

    class Meta:
        verbose_name = _(u'emailing')
        verbose_name_plural = _(u'emailings')
        
    def get_info(self):
        text = self.get_status_display()
        if self.status == Emailing.STATUS_SCHEDULED:
            return _("{0} on {1}").format(text, DateFormat(self.scheduling_dt).format(" d F Y H:i"))
        elif self.status == Emailing.STATUS_SENT:
            return _("{0} on {1}").format(text, DateFormat(self.sending_dt).format(" d F Y H:i"))
        return text
        
    def next_action(self):
        action = ""
        if self.status == Emailing.STATUS_EDITING:
            action = '<a class="colorbox-form action-button" href="{1}">{0}</a>'.format(
                ugettext(u'Send'), reverse("emailing_confirm_send_mail", args=[self.id]))
        if self.status == Emailing.STATUS_SCHEDULED or self.status == Emailing.STATUS_CREDIT_MISSING:
            action = '<a class="colorbox-form action-button" href="{1}">{0}</a>'.format(
                ugettext(u'Cancel'), reverse("emailing_cancel_send_mail", args=[self.id]))
        #if self.status == Emailing.STATUS_CREDIT_MISSING:
            #action = '<a href="mailto:{1}">{0}</a>'.format(ugettext(u'Buy'), settings.ADMINS[0][1])
        return mark_safe(action)
    
    def get_contacts(self):
        return list(self.send_to.all()) + list(self.sent_to.all())
        
    def save(self, *args, **kwargs):
        if self.status == Emailing.STATUS_SENT and self.sending_dt == None:
            self.sending_dt = datetime.now()
        return super(Emailing, self).save(*args, **kwargs)


class MagicLink(models.Model):
    emailing = models.ForeignKey(Emailing)
    url = models.URLField()
    visitors = models.ManyToManyField(Contact, blank=True)
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    
    def __unicode__(self):
        return self.url
    
    def save(self, *args, **kwargs):
        super(MagicLink, self).save(*args, **kwargs)
        if not self.uuid:
            name = '{0}-magic-link-{1}-{2}'.format(settings.SECRET_KEY, self.id, self.url)
            self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, name)
            return super(MagicLink, self).save()        
        
class EmailingCounter(models.Model):
    credit = models.IntegerField(default=0, verbose_name=_(u"Credit"), help_text=_(u"Number of email used"))
    total = models.IntegerField(default=0, verbose_name=_(u"Total"), help_text=_(u"Number of amails bought"))
    bought_date = models.DateField(_(u"Bought date"), blank=True, default=None, null=True)
    finished_date = models.DateField(_(u"Finished date"), blank=True, default=None, null=True)
    
    def __unicode__(self):
        return _(u"Date : {0} - Total: {1} - Credit : {2}").format(self.bought_date, self.total, self.credit)