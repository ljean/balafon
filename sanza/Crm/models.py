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
from django.db.models.signals import post_save

class NamedElement(models.Model):
    name = models.CharField(_(u'Name'), max_length=200)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True
    

class EntityType(NamedElement):
    
    def _get_logo_dir(self, filename):
        return u'{0}/{1}/{2}'.format(settings.ENTITY_LOGO_DIR, "types", filename)
    
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICE = ((GENDER_MALE, _('Male')), (GENDER_FEMALE, _('Female')))
    
    #required for translation into some languages (french for example)
    gender = models.IntegerField(_(u'gender'), choices=GENDER_CHOICE, default=GENDER_MALE)
    order = models.IntegerField(_(u'order'), default=0)
    logo = models.ImageField(_("logo"), blank=True, default=u"", upload_to=_get_logo_dir)
    subscribe_form = models.BooleanField(default=True, verbose_name=_(u'Subscribe form'),
        help_text=_(u'This type will be proposed on the public subscribe form'))
    
    def is_male(self):
        return (self.gender == EntityType.GENDER_MALE)
    
    class Meta:
        verbose_name = _(u'entity type')
        verbose_name_plural = _(u'entity types')
        ordering = ['order']


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
        #Conf49 : No department code in the excel export
        #if self.parent and self.parent.code:
        #    return u"{0} ({1})".format(self.name, self.parent.code)
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
    type = models.ForeignKey(EntityType, verbose_name=_(u'type'), blank=True, null=True, default=None)
    relationship_date = models.DateField(_(u'relationship date'), default=None, blank=True, null=True)
    
    logo = models.ImageField(_("logo"), blank=True, default=u"", upload_to=_get_entity_logo_dir)
    
    phone = models.CharField(_('phone'), max_length=200, blank=True, default= u'')
    fax = models.CharField(_('fax'), max_length=200, blank=True, default= u'')
    email = models.EmailField(_('email'), blank=True, default= u'')
    website = models.URLField(_('web site'), blank=True, default='')
    
    address = models.CharField(_('address'), max_length=200, blank=True, default=u'')
    address2 = models.CharField(_('address 2'), max_length=200, blank=True, default=u'')
    address3 = models.CharField(_('address 3'), max_length=200, blank=True, default=u'')
    
    zip_code = models.CharField(_('zip code'), max_length=20, blank=True, default=u'')
    cedex = models.CharField(_('cedex'), max_length=200, blank=True, default=u'')
    city = models.ForeignKey(City, verbose_name=_('city'), blank=True, default=None, null=True)
    
    notes = models.TextField(_('notes'), blank=True, default="")
    
    imported_by = models.ForeignKey("ContactsImport", default=None, blank=True, null=True)
    
    is_single_contact = models.BooleanField(_("is single contact"), default=False)
    
    def save(self, *args, **kwargs):
        super(Entity, self).save(*args, **kwargs)
        if self.contact_set.filter(has_left=False).count() == 0:
            Contact.objects.create(entity=self, main_contact=True, has_left=False)
        elif self.contact_set.filter(main_contact=True, has_left=False).count() == 0:
            #Always at least 1 main contact per entity
            c = self.contact_set.all()[0]
            c.main_contact = True
            c.save()
    
    def __unicode__(self):
        return self.name
    
    def get_safe_logo(self):
        if self.logo:
            return sorl_thumbnail.backend.get_thumbnail(self.logo.file, "128x128", crop='center').url
        else:
            return self.default_logo()
    
    def default_logo(self):
        if self.type and self.type.logo:
            file = sorl_thumbnail.backend.get_thumbnail(self.type.logo.file, "128x128", crop='center')
            return file.url
        
        if self.is_single_contact:
            logo = "img/single-contact.png"
        else:
            logo = "img/entity.png"
        
        return u"{0}{1}".format(project_settings.STATIC_URL, logo)

    def get_absolute_url(self):
        return reverse('crm_view_entity', args=[self.id])

    def get_full_address(self):
        if self.city:
            fields = [self.address, self.address2, self.address3, self.zip_code, self.city.name, self.cedex]
            return u' '.join([f for f in fields if f])
        return u''

    def get_phones(self):
        return [self.phone]
        
    def get_display_address(self):
        return self.get_full_address()
    
    def main_contacts(self):
        return [c for c in self.contact_set.filter(main_contact=True).order_by("lastname", "firstname")]
    
    def last_action(self):
        try:
            return Action.objects.filter(contact__entity=self, done_date__isnull=False).order_by("-done_date")[0]
        except IndexError:
            return None
        
    def next_action(self):
        try:
            return Action.objects.filter(contact__entity=self, planned_date__isnull=False, done_date__isnull=True).order_by("-planned_date")[0]
        except IndexError:
            return None
        
    def single_contact(self):
        if self.is_single_contact:
            return self.contact_set.all()[0]
        return None
        
    def current_opportunities(self):
        return self.opportunity_set.filter(ended=False).count()

    def logo_thumbnail(self):
        return sorl_thumbnail.backend.get_thumbnail(self.logo.file, "128x128", crop='center')

    def get_custom_fields(self):
        return CustomField.objects.filter(model=CustomField.MODEL_ENTITY)

    def __getattribute__(self, attr):
        prefix = "custom_field_"
        prefix_length = len(prefix)
        if attr[:prefix_length] == prefix:
            field_name = attr[prefix_length:]
            try:
                custom_field = CustomField.objects.get(model=CustomField.MODEL_ENTITY, name=field_name)
                custom_field_value = self.entitycustomfieldvalue_set.get(entity=self, custom_field=custom_field)
                return custom_field_value.value
            except EntityCustomFieldValue.DoesNotExist:
                return u'' #If no value defined: return empty string
        return object.__getattribute__(self, attr)

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
    GENDER_CHOICE = ((GENDER_MALE, _('Mr')), (GENDER_FEMALE, _('Mrs')))
    
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
    email_verified = models.BooleanField(_("email verified"), default=False)
    
    phone = models.CharField(_('phone'), max_length=200, blank=True, default= u'')
    mobile = models.CharField(_('mobile'), max_length=200, blank=True, default= u'')
    email = models.EmailField(_('email'), blank=True, default= u'')
    
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    
    #optional : use the entity address in most cases
    address = models.CharField(_('address'), max_length=200, blank=True, default=u'')
    address2 = models.CharField(_('address 2'), max_length=200, blank=True, default=u'')
    address3 = models.CharField(_('address 3'), max_length=200, blank=True, default=u'')
    zip_code = models.CharField(_('zip code'), max_length=20, blank=True, default=u'')
    cedex = models.CharField(_('cedex'), max_length=200, blank=True, default=u'')
    city = models.ForeignKey(City, verbose_name=_('city'), blank=True, default=None, null=True)
    
    notes = models.TextField(_('notes'), blank=True, default="")
    
    same_as = models.ForeignKey(SameAs, blank=True, null=True, default=None)
    
    has_left = models.BooleanField(_(u'has left'), default=False)
    
    imported_by = models.ForeignKey("ContactsImport", default=None, blank=True, null=True)
    
    def default_logo(self):
        if self.entity.is_single_contact:
            logo = "img/single-contact.png"
        else:
            logo = "img/contact.png"
        return u"{0}{1}".format(project_settings.STATIC_URL, logo)
    
    def photo_thumbnail(self):
        return sorl_thumbnail.backend.get_thumbnail(self.photo.file, "128x128", crop='center')

    def get_full_address(self):
        if self.city:
            fields = [self.address, self.address2, self.address3, self.zip_code, self.city.name, self.cedex]
            return u' '.join([f for f in fields if f])
        return self.entity.get_full_address()
    
    def get_custom_fields(self):
        return CustomField.objects.filter(model=CustomField.MODEL_CONTACT)
        
    def get_name_and_entity(self):
        if self.entity.is_single_contact:
            return self.fullname
        return u"{0} ({1})".format(self.fullname, self.entity.name)

    def __getattribute__(self, attr):
        if attr[:4] == "get_":
            address_fields = ('address', 'address2', 'address3', 'zip_code', 'cedex', 'city')
            field_name = attr[4:]
            if field_name in ('phone', 'email',):
                mine = getattr(self, field_name)
                return mine or getattr(self.entity, field_name)
            elif field_name in address_fields:
                is_contact_address_defined = any([getattr(self, f) for f in address_fields])
                if is_contact_address_defined:
                    return getattr(self, field_name)
                return getattr(self.entity, field_name)
            else:
                prefix = "custom_field_"
                prefix_length = len(prefix)
                if field_name[:prefix_length] == prefix:
                    value = getattr(self, field_name)
                    if not value: #if no value for the custom field
                        try:
                            #Try to get a value for a custom field with same name on entity
                            value = getattr(self.entity, field_name)
                        except CustomField.DoesNotExist:
                            #No custom field with same name on entity: returns empty string
                            pass
                    return value
        else:
            prefix = "custom_field_"
            prefix_length = len(prefix)
            if attr[:prefix_length] == prefix:
                field_name = attr[prefix_length:]
                try:
                    custom_field = CustomField.objects.get(model=CustomField.MODEL_CONTACT, name=field_name)
                    custom_field_value = self.contactcustomfieldvalue_set.get(contact=self, custom_field=custom_field)
                    return custom_field_value.value
                except (CustomField.DoesNotExist, ContactCustomFieldValue.DoesNotExist):
                    return u'' #If no value defined: return empty string
            else:
                entity_prefix = "entity_"
                full_prefix = entity_prefix + prefix
                if attr[:len(full_prefix)] == full_prefix: # if the attr is entity_custom_field_<something>
                    #return self.entity.custom_field_<something>
                    return getattr(self.entity, attr[len(entity_prefix):])

        return object.__getattribute__(self, attr)
    
    def get_absolute_url(self):
        return reverse('crm_view_contact', args=[self.id])

    def get_email_address(self):
        return u'"{1}" <{0}>'.format(self.get_email, self.fullname)
        
    def get_phones(self):
        return [x for x in (self.phone, self.mobile) if x]
    
    def get_roles(self):
        has_left = [__(u'has left')] if self.has_left else []
        return has_left + [x.name for x in self.role.all()]
        
    def __unicode__(self):
        if not (self.firstname or self.lastname):
            if self.email:
                return self.email
            else:
                return u"< {0} >".format(__(u"Unknown"))
        
        if self.gender and self.lastname:
            title = self.get_gender_display()
            title += u' '
        else:
            title = u''
        
        if (not self.firstname) or (not self.lastname):
            return _(u"{1}{0.firstname}{0.lastname}").format(self, title)
        
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
            ln = unicodedata.normalize('NFKD', unicode(self.fullname)).encode("utf8",'ignore')
            name = '{0}-contact-{1}-{2}-{3}'.format(project_settings.SECRET_KEY, self.id, ln, self.email)
            self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, name)
            return super(Contact, self).save()

    class Meta:
        verbose_name = _(u'contact')
        verbose_name_plural = _(u'contacts')
    
class Group(TimeStampedModel):
    name = models.CharField(_(u'name'), max_length=200, unique=True, db_index=True)
    description = models.CharField(_(u'description'), max_length=200, blank=True, default="")
    entities = models.ManyToManyField(Entity, blank=True, null=True)
    contacts = models.ManyToManyField(Contact, blank=True, null=True)
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
    
    #TO BE REMOVED--
    entity = models.ForeignKey(Entity, blank=True, null=True, default=None)
    #---------------
    name = models.CharField(_('name'), max_length=200)
    status = models.ForeignKey(OpportunityStatus)
    type = models.ForeignKey(OpportunityType, blank=True, null=True, default=None)
    detail = models.TextField(_('detail'), blank=True, default='')
    #TO BE REMOVED---
    probability = models.IntegerField(_('probability'), default=PROBABILITY_MEDIUM,
        choices=PROBABILITY_CHOICES)
    amount = models.DecimalField(_(u'amount'), default=0, max_digits=11, decimal_places=2)
    #----------------
    ended = models.BooleanField(_(u'closed'), default=False, db_index=True)
    #TO BE REMOVED---
    start_date = models.DateField(_('starting date'), blank=True, null=True, default=None)
    end_date = models.DateField(_('closing date'), blank=True, null=True, default=None)
    #----------------
    display_on_board = models.BooleanField(verbose_name=_(u'display on board'),
        default=settings.OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT, db_index=True)
    
    def get_start_date(self):
        try:
            return self.action_set.filter(planned_date__isnull=False).order_by("planned_date")[0].planned_date
        except:
            return None
        
    def get_end_date(self):
        try:
            return self.action_set.filter(planned_date__isnull=False).order_by("-planned_date")[0].planned_date
        except:
            return None
    
    def default_logo(self):
        logo = "img/folder.png"
        return u"{0}{1}".format(project_settings.STATIC_URL, logo)
    
    def __unicode__(self):
        return u"{0.name}".format(self)

    class Meta:
        verbose_name = _(u'opportunity')
        verbose_name_plural = _(u'opportunities')

class ActionSet(NamedElement):
    ordering = models.IntegerField(verbose_name=_(u'display ordering'), default=10)
    class Meta:
        verbose_name = _(u'action set')
        verbose_name_plural = _(u'action sets')

class ActionType(NamedElement):
    
    subscribe_form = models.BooleanField(default=False, verbose_name=_(u'Subscribe form'),
        help_text=_(u'This action type will be proposed on the public subscribe form'))
    set = models.ForeignKey(ActionSet, blank=True, default=None, null=True)

    class Meta:
        verbose_name = _(u'action type')
        verbose_name_plural = _(u'action types')


class Action(TimeStampedModel):
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, _(u'low priority')),
        (PRIORITY_MEDIUM, _(u'medium priority')),
        (PRIORITY_HIGH, _(u'high priority')),
    )

    entity = models.ForeignKey(Entity, blank=True, default=None, null=True)
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
    archived = models.BooleanField(verbose_name=_(u'archived'), default=False, db_index=True)
    amount = models.DecimalField(_(u'amount'), default=0, max_digits=11, decimal_places=2)
    

    def __unicode__(self):
        return u'{0.subject} with {0.entity}'.format(self)
        
    def save(self, *args, **kwargs):
        if not self.done_date and self.done:
            self.done_date = datetime.now()
        elif self.done_date and not self.done:
            self.done_date = None
        return super(Action, self).save(*args, **kwargs)
        
class CustomField(models.Model):
    
    MODEL_ENTITY = 1
    MODEL_CONTACT = 2
    
    MODEL_CHOICE = (
        (MODEL_ENTITY, _(u'Entity')),
        (MODEL_CONTACT, _(u'Contact')), 
    )
    
    name = models.CharField(max_length=100, verbose_name=_(u'name'))
    label = models.CharField(max_length=100, verbose_name=_(u'label'), blank=True, default='')
    model = models.IntegerField(verbose_name=_(u'model'), choices=MODEL_CHOICE)
    widget = models.CharField(max_length=100, verbose_name=_(u'widget'), blank=True, default='')
    ordering = models.IntegerField(verbose_name=_(u'display ordering'), default=10)
    import_order = models.IntegerField(verbose_name=_(u'import ordering'), default=0)
    export_order = models.IntegerField(verbose_name=_(u'export ordering'), default=0)
    
    def __unicode__(self):
        return _(u"{0}:{1}").format(self.model_name(), self.name)
    
    def model_name(self):
        if self.model == self.MODEL_ENTITY:
            return u'entity'
        else:
            return u'contact'
    
    class Meta:
        verbose_name = _(u'custom field')
        verbose_name_plural = _(u'custom fields')
        ordering = ('ordering', )


class CustomFieldValue(models.Model):
    custom_field = models.ForeignKey(CustomField, verbose_name = _(u'custom field'))
    value = models.TextField(verbose_name=_(u'value'))
    
    class Meta:
        verbose_name = _(u'custom field value')
        verbose_name_plural = _(u'custom field values')
        abstract = True
        
class EntityCustomFieldValue(CustomFieldValue):
    entity = models.ForeignKey(Entity)
    
    class Meta:
        verbose_name = _(u'entity custom field value')
        verbose_name_plural = _(u'entity custom field values')

    def __unicode__(self):
        return u'{0} {1}'.format(self.entity, self.custom_field)
    
class ContactCustomFieldValue(CustomFieldValue):
    contact = models.ForeignKey(Contact)
    
    class Meta:
        verbose_name = _(u'contact custom field value')
        verbose_name_plural = _(u'contact custom field values')

    def __unicode__(self):
        return u'{0} {1}'.format(self.contact, self.custom_field)
    
class ContactsImport(TimeStampedModel):
    
    ENCODINGS = (
        ('iso-8859-15', 'iso-8859-15'),
        ('cp1252', 'cp1252')
    )
    
    SEPARATORS = (
        (';', _(u'Semi-colon')),
        (',', _(u'Coma')),
    )
    
    def _get_import_dir(self, filename):
        return u'{0}/{1}'.format(settings.CONTACTS_IMPORT_DIR, filename)

    import_file = models.FileField(_(u'import file'), upload_to=_get_import_dir,
        help_text=_(u'CSV file following the import contacts format.'))
    name = models.CharField(max_length=100, verbose_name=_(u'name'), blank=True, default=u'',
        help_text=_(u'Optional name for searching contacts more easily. If not defined, use the name of the file.'))
    imported_by = models.ForeignKey(User, verbose_name=_(u'imported by'))
    encoding = models.CharField(max_length=50, default='iso-8859-15', choices=ENCODINGS)
    separator = models.CharField(max_length=5, default=';', choices=SEPARATORS)
    entity_type = models.ForeignKey(EntityType, verbose_name=_(u'entity type'),
        help_text=_(u'All created entities will get this type. Ignored if the entity already exist.'))
    groups = models.ManyToManyField(Group, verbose_name=_(u'groups'), blank=True, default=None, null=True,
        help_text=_(u'The created entities will be added to the selected groups.'))
    entity_name_from_email = models.BooleanField(verbose_name=_(u'generate entity name from email address'), default=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _(u'contact import')
        verbose_name_plural = _(u'contact imports')
