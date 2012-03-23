# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.core.urlresolvers import reverse
from django.conf import settings as project_settings
from datetime import datetime, date
import uuid, unicodedata
from sanza.Crm import settings
from django.contrib.sites.models import Site
from sorl.thumbnail import default as sorl_thumbnail
from django_extensions.db.models import TimeStampedModel, AutoSlugField
from django.contrib.auth.models import User

class NamedElement(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True
    

class EntityType(NamedElement):

    class Meta:
        verbose_name = _(u'entity type')
        verbose_name_plural = _(u'entity types')


class ActivitySector(NamedElement):

    class Meta:
        verbose_name = _(u'activity sector')
        verbose_name_plural = _(u'activity sectors')

class Relationship(NamedElement):

    class Meta:
        verbose_name = _(u'relationship')
        verbose_name_plural = _(u'relationships')

class ZoneType(NamedElement):
    type = models.CharField(_('type'), max_length=200)
    
    class Meta:
        verbose_name = _(u'zone type')
        verbose_name_plural = _(u'zone types')


class BaseZone(NamedElement):
    parent = models.ForeignKey('Zone', blank=True, default=None, null=True)

    def get_full_name(self):
        if self.parent:
            return u'{0} - {1}'.format(self.parent.get_full_name(), self.name)
        return self.name

    def __unicode__(self):
        if self.parent and self.parent.code:
            return u"{0} ({1})".format(self.name, self.parent.code)
        return self.name    
    
    class Meta:
        abstract = True

class Zone(BaseZone):
    type = models.ForeignKey(ZoneType)
    code = models.CharField(_('code'), max_length=10, blank=True, default="")

    class Meta:
        verbose_name = _(u'zone')
        verbose_name_plural = _(u'zones')
        ordering = ['name']

class City(BaseZone):
    groups = models.ManyToManyField(Zone, blank=True, null=True,
        verbose_name=_(u'group'), related_name='city_groups_set')

    class Meta:
        verbose_name = _(u'city')
        verbose_name_plural = _(u'cities')
        
    def get_friendly_name(self):
        if self.parent:
            return u'{0} ({1})'.format(self.name,
                self.parent.code if self.parent.code else self.parent.name[:2])
        return self.name
    

def _get_entity_logo_dir(instance, filename):
    return u'{0}/{1}/{2}'.format(settings.ENTITY_LOGO_DIR, instance.id, filename)

class Entity(TimeStampedModel):
    name = models.CharField(_('name'), max_length=200, db_index=True)
    description = models.CharField(_('description'), max_length=200, blank=True, default="")
    type = models.ForeignKey(EntityType, verbose_name=_(u'type'))
    activity_sector = models.ForeignKey(ActivitySector, blank=True, default=None, null=True, verbose_name=_(u'activity sector'))
    relationship = models.ForeignKey(Relationship, verbose_name=_(u'relationship'))
    relationship_date = models.DateField(_(u'relationship date'), default=None, blank=True, null=True)
    
    logo = models.ImageField(_("logo"), blank=True, default=u"", upload_to=_get_entity_logo_dir)
    
    phone = models.CharField(_('phone'), max_length=200, blank=True, default= u'')
    fax = models.CharField(_('fax'), max_length=200, blank=True, default= u'')
    email = models.EmailField(_('email'), blank=True, default= u'')
    website = models.URLField(_('web site'), blank=True, default='')
    
    address = models.CharField(_('address'), max_length=200, blank=True, default=u'')
    address2 = models.CharField(_('address 2'), max_length=200, blank=True, default=u'')
    address3 = models.CharField(_('address 3'), max_length=200, blank=True, default=u'')
    
    zip_code = models.CharField(_('zip code'), max_length=10, blank=True, default=u'')
    cedex = models.CharField(_('cedex'), max_length=200, blank=True, default=u'')
    city = models.ForeignKey(City, verbose_name=_('city'), blank=True, default=None, null=True)
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm_view_entity', args=[self.id])

    def get_full_address(self):
        if self.city:
            fields = [self.address, self.address2, self.address3, self.zip_code, self.city.name, self.cedex]
            return u' '.join([f for f in fields if f])
        return u''
    
    def get_display_address(self):
        return self.get_full_address()
        #if self.city:
        #    parent = self.city.parent
        #    name, code = parent.name, parent.code
        #    addr += u'({0}{2}{1})'.format(name, code, u' ' if len(code) else u'')
        #return addr
    
    def main_contacts(self):
        return [c for c in self.contact_set.filter(main_contact=True)]
    
    def last_action(self):
        try:
            return self.action_set.all().order_by("-created")[0]
        except IndexError:
            return ''
        
    def current_opportunities(self):
        return self.opportunity_set.filter(ended=False).count()

    def logo_thumbnail(self):
        return sorl_thumbnail.backend.get_thumbnail(self.logo.file, "128x128")

    class Meta:
        verbose_name = _(u'entity')
        verbose_name_plural = _(u'entities')

class EntityRole(NamedElement):

    class Meta:
        verbose_name = _(u'entity role')
        verbose_name_plural = _(u'entity roles')    

def _get_contact_photo_dir(instance, filename):
    return u'{0}/{1}/{2}'.format(settings.CONTACT_PHOTO_DIR, instance.id, filename)

class SameAs(models.Model):
    
    def __unicode__(self):
        return _(u"Same As: {0}").format(self.id)
    
    class Meta:
        verbose_name = _(u'same as')
        verbose_name_plural = _(u'sames as')


class Contact(TimeStampedModel):
    
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICE = ((GENDER_MALE, _('Mr.')), (GENDER_FEMALE, _('Mrs.')))
    
    entity = models.ForeignKey(Entity)
    role = models.ManyToManyField(EntityRole, blank=True, null=True, default=None, verbose_name=_(u'Roles'))
    
    gender = models.IntegerField(_(u'gender'), choices=GENDER_CHOICE, blank=True, default=0)
    title = models.CharField(_(u'title'), max_length=200, blank=True, default=u'')
    lastname = models.CharField(_(u'last name'), max_length=200, blank=True, default=u'', db_index=True)
    firstname = models.CharField(_(u'first name'), max_length=200, blank=True, default=u'')
    nickname = models.CharField(_(u'nickname'), max_length=200, blank=True, default=u'')
    
    photo = models.ImageField(_(u"photo"), blank=True, default=u"", upload_to=_get_contact_photo_dir)
    birth_date = models.DateField(_(u"birth date"), blank=True, default=None, null=True)
    job = models.CharField(_(u"job"), max_length=200, blank=True, default=u"")
    
    main_contact = models.BooleanField(_("main contact"), default=True, db_index=True)
    accept_newsletter = models.BooleanField(_("accept newsletter"), default=False, db_index=True)
    accept_3rdparty = models.BooleanField(_("accept third parties"), default=False)
    
    phone = models.CharField(_('phone'), max_length=200, blank=True, default= u'')
    mobile = models.CharField(_('mobile'), max_length=200, blank=True, default= u'')
    email = models.EmailField(_('email'), blank=True, default= u'')
    
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    
    #optional : use the entity address in most cases
    address = models.CharField(_('address'), max_length=200, blank=True, default=u'')
    address2 = models.CharField(_('address 2'), max_length=200, blank=True, default=u'')
    address3 = models.CharField(_('address 3'), max_length=200, blank=True, default=u'')
    zip_code = models.CharField(_('zip code'), max_length=10, blank=True, default=u'')
    cedex = models.CharField(_('cedex'), max_length=200, blank=True, default=u'')
    city = models.ForeignKey(City, verbose_name=_('city'), blank=True, default=None, null=True)
    
    notes = models.CharField(_('notes'), max_length=500, blank=True, default="")
    
    same_as = models.ForeignKey(SameAs, blank=True, null=True, default=None)
    
    has_left = models.BooleanField(_(u'has left'), default=False)
    
    def get_full_address(self):
        if self.city:
            fields = [self.address, self.address2, self.address3, self.zip_code, self.city.name, self.cedex]
            return u' '.join([f for f in fields if f])
        return self.entity.get_full_address()
    
    def __getattribute__(self, attr):
        if attr[:4] == "get_":
            field_name = attr[4:]
            if field_name in ('phone', 'email', 'address', 'zip_code', 'cedex', 'city'):
                mine = getattr(self, field_name)
                return mine or getattr(self.entity, field_name)
        return object.__getattribute__(self, attr)
    
    def get_absolute_url(self):
        return reverse('crm_edit_contact', args=[self.id])

    def get_email_address(self):
        return u'"{1}" <{0}>'.format(self.get_email, self.fullname)
        
    def get_phones(self):
        return [x for x in (self.phone, self.mobile) if x]
    
    def get_roles(self):
        return [x.name for x in self.role.all()]
        
    def __unicode__(self):
        if self.gender:
            #title = _('Mr. ') if self.gender==Contact.GENDER_MALE else _('Mrs. ')
            title = self.get_gender_display()
            title += u' '
        else:
            title = u''
        if not (self.firstname or self.lastname):
            return u"< {0} >".format(__(u"Unknown"))
        return _(u"{1}{0.firstname} {0.lastname}").format(self, title)
            
    @property
    def fullname(self):
        return unicode(self)

    def save(self, *args, **kwargs):
        try:
            int(self.gender)
        except ValueError:
            self.gender = 0

        super(Contact, self).save(*args, **kwargs)
        if not self.uuid:
            ln = unicodedata.normalize('NFKD', unicode(self.lastname)).encode("utf8",'ignore')
            name = '{0}-contact-{1}-{2}'.format(project_settings.SECRET_KEY, self.id, ln)
            self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, name)
            return super(Contact, self).save()

    class Meta:
        verbose_name = _(u'contact')
        verbose_name_plural = _(u'contacts')
    
class Group(TimeStampedModel):
    name = models.CharField(_(u'name'), max_length=200, unique=True, db_index=True)
    description = models.CharField(_(u'description'), max_length=200, blank=True, default="")
    entities = models.ManyToManyField(Entity, blank=True, null=True)
    subscribe_form = models.BooleanField(default=False, verbose_name=_(u'Subscribe form'),
        help_text=_(u'This group will be proposed on the public subscribe form'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u'group')
        verbose_name_plural = _(u'groups')
        
class OpportunityStatus(NamedElement):
    ordering = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _(u'opportunity status')
        verbose_name_plural = _(u'opportunity status')

class OpportunityType(NamedElement):
    
    class Meta:
        verbose_name = _(u'opportunity type')
        verbose_name_plural = _(u'opportunity types')

class Opportunity(TimeStampedModel):
    
    PROBABILITY_LOW = 1
    PROBABILITY_MEDIUM = 2
    PROBABILITY_HIGH = 3
    PROBABILITY_CHOICES = (
        (PROBABILITY_LOW, _(u'low')),
        (PROBABILITY_MEDIUM, _(u'medium')),
        (PROBABILITY_HIGH, _(u'high')),
    )
    
    entity = models.ForeignKey(Entity)
    name = models.CharField(_('name'), max_length=200)
    status = models.ForeignKey(OpportunityStatus)
    type = models.ForeignKey(OpportunityType, blank=True, null=True, default=None)
    detail = models.TextField(_('detail'), blank=True, default='')
    probability = models.IntegerField(_('probability'), default=PROBABILITY_MEDIUM,
        choices=PROBABILITY_CHOICES)
    amount = models.PositiveIntegerField(_(u'amount'), default=0)
    ended = models.BooleanField(_(u'closed'), default=False, db_index=True)
    start_date = models.DateField(_('starting date'), blank=True, null=True, default=None)
    end_date = models.DateField(_('closing date'), blank=True, null=True, default=None)
    display_on_board = models.BooleanField(verbose_name=_(u'display on board'), default=True, db_index=True)
    
    def __unicode__(self):
        return u"{0.entity} - {0.name}".format(self)

    class Meta:
        verbose_name = _(u'opportunity')
        verbose_name_plural = _(u'opportunities')

class ActionType(NamedElement):

    class Meta:
        verbose_name = _(u'action type')
        verbose_name_plural = _(u'action types')


class Action(TimeStampedModel):
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, _(u'low')),
        (PRIORITY_MEDIUM, _(u'medium')),
        (PRIORITY_HIGH, _(u'high')),
    )

    entity = models.ForeignKey(Entity)
    subject = models.CharField(_('subject'), max_length=200)
    planned_date = models.DateTimeField(_('planned date'), default=None, blank=True, null=True, db_index=True)
    type = models.ForeignKey(ActionType, blank=True, default=None, null=True)
    detail = models.TextField(_('detail'), blank=True, default='')
    priority = models.IntegerField(_('priority'), default=PRIORITY_MEDIUM, choices=PRIORITY_CHOICES)
    opportunity = models.ForeignKey(Opportunity, blank=True, default=None, null=True)
    contact = models.ForeignKey(Contact, blank=True, default=None, null=True)
    done = models.BooleanField(_(u'done'), default=False, db_index=True)
    done_date = models.DateTimeField(_('done date'), blank=True, null=True, default=None, db_index=True)
    in_charge = models.ForeignKey(User, verbose_name=_(u'in charge'), blank=True, null=True, default=None,
        limit_choices_to={'first_name__regex': '.+'})
    display_on_board = models.BooleanField(verbose_name=_(u'display on board'), default=True, db_index=True)

    def __unicode__(self):
        return u'{0.subject} with {0.entity}'.format(self)
        
    def save(self, *args, **kwargs):
        if not self.done_date and self.done:
            self.done_date = datetime.now()
        elif self.done_date and not self.done:
            self.done_date = None
        return super(Action, self).save(*args, **kwargs)
        