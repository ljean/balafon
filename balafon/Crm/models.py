# -*- coding: utf-8 -*-
"""models"""
# pylint: disable=model-no-explicit-unicode

from __future__ import unicode_literals

import uuid
import unicodedata
from six.moves.urllib.parse import urlparse
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.conf import settings as project_settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from coop_cms.utils import RequestManager, RequestNotFound, dehtml
from django_extensions.db.models import TimeStampedModel
from sorl.thumbnail import default as sorl_thumbnail

from balafon.Crm import settings
from balafon.utils import now_rounded, logger, validate_rgb
from balafon.Users.models import Favorite


@python_2_unicode_compatible
class NamedElement(models.Model):
    """Base class for models with a name field"""
    name = models.CharField(_('Name'), max_length=200)
    
    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True


@python_2_unicode_compatible
class LastModifiedModel(TimeStampedModel):
    """track the user who last modified an object"""

    created_by = models.ForeignKey(
        User, default=None, blank=True, null=True, verbose_name=_("created by"), related_name='+',
    )

    last_modified_by = models.ForeignKey(
        User, default=None, blank=True, null=True, verbose_name=_("last modified by")
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """save object : update the last_modified_by from request"""
        current_user = None
        try:
            request = RequestManager().get_request()
            if request.user.is_authenticated():
                # object can be modified by anonymous user : subscription page for example, view magic-link ...
                current_user = request.user
        except (RequestNotFound, AttributeError):
            pass

        if current_user:
            if not self.id:
                self.created_by = current_user
            self.last_modified_by = current_user

        return super(LastModifiedModel, self).save(*args, **kwargs)


def _get_logo_dir(obj, filename):
    """path to directory for media files"""
    return '{0}/{1}/{2}'.format(settings.ENTITY_LOGO_DIR, "types", filename)


@python_2_unicode_compatible
class EntityType(NamedElement):
    """Type of entity: It might be removed in future"""

    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICE = ((GENDER_MALE, _('Male')), (GENDER_FEMALE, _('Female')))
    
    # required for translation into some languages (french for example)
    gender = models.IntegerField(_('gender'), choices=GENDER_CHOICE, default=GENDER_MALE)
    order = models.IntegerField(_('order'), default=0)
    logo = models.ImageField(_("logo"), blank=True, default="", upload_to=_get_logo_dir)
    subscribe_form = models.BooleanField(
        default=True, verbose_name=_('Subscribe form'),
        help_text=_('This type will be proposed on the public subscribe form')
    )
    
    def is_male(self):
        """True if this type is male gender: used for correct wording in french"""
        return self.gender == EntityType.GENDER_MALE
    
    class Meta:
        verbose_name = _('entity type')
        verbose_name_plural = _('entity types')
        ordering = ['order']


@python_2_unicode_compatible
class ZoneType(NamedElement):
    """Type of zones (cities, coutries, ...)"""
    type = models.CharField(_('type'), max_length=200)
    
    class Meta:
        verbose_name = _('zone type')
        verbose_name_plural = _('zone types')


@python_2_unicode_compatible
class BaseZone(NamedElement):
    """Base class for zones"""
    parent = models.ForeignKey('Zone', blank=True, default=None, null=True)

    def get_full_name(self):
        """full name"""
        if self.parent:
            return '{0} - {1}'.format(self.parent.get_full_name(), self.name)
        return self.name

    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True


@python_2_unicode_compatible
class Zone(BaseZone):
    """A zone is a group of cities : departements, region, country..."""
    type = models.ForeignKey(ZoneType)
    code = models.CharField(_('code'), max_length=10, blank=True, default="")
    groups = models.ManyToManyField(
        "Zone", blank=True, verbose_name=_('parent groups'), related_name='children_groups_set'
    )
    
    def is_country(self):
        """is this zone corrspond to top-most: country"""
        return self.type.type == 'country'
    
    def is_foreign_country(self):
        """if country: is it different from default country"""
        if self.is_country():
            dcn = settings.get_default_country()
            default_country = Zone.objects.get(name=dcn, type__type='country')
            return self.id != default_country.id
        return False

    class Meta:
        verbose_name = _('zone')
        verbose_name_plural = _('zones')
        ordering = ['name']


@python_2_unicode_compatible
class City(BaseZone):
    """city"""
    groups = models.ManyToManyField(
        Zone, blank=True, verbose_name=_('group'), related_name='city_groups_set'
    )

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        ordering = ['name']
    
    def get_country(self):
        """get country"""
        obj = self
        while obj.parent:
            obj = obj.parent
            if obj.is_country():
                return obj
        return None
    
    def get_foreign_country(self):
        """get country only if different from default"""
        country = self.get_country()
        if country and country.is_foreign_country():
            return country
        return None

    def get_friendly_name(self):
        """friendly name"""
        if self.parent:
            return '{0} ({1})'.format(
                self.name,
                self.parent.code if self.parent.code else self.parent.name[:2]
            )
        return self.name
    

def get_entity_logo_dir(instance, filename):
    """path to logo in media"""
    return '{0}/{1}/{2}'.format(settings.ENTITY_LOGO_DIR, instance.id, filename)


@python_2_unicode_compatible
class StreetType(NamedElement):
    """A selection for street type"""

    class Meta:
        verbose_name = _('street type')
        verbose_name_plural = _('street types')
        ordering = ('name', )


class AddressModel(LastModifiedModel):
    """Base class for entity or contact"""

    address = models.CharField(_('address'), max_length=200, blank=True, default='')
    address2 = models.CharField(_('address 2'), max_length=200, blank=True, default='')
    address3 = models.CharField(_('address 3'), max_length=200, blank=True, default='')

    zip_code = models.CharField(_('zip code'), max_length=20, blank=True, default='')
    cedex = models.CharField(_('cedex'), max_length=200, blank=True, default='')
    city = models.ForeignKey(City, verbose_name=_('city'), blank=True, default=None, null=True)

    #These fields are just kept for editing the address field
    street_number = models.CharField(_('street number'), max_length=20, blank=True, default='')
    street_type = models.ForeignKey(StreetType, default=None, blank=True, null=True, verbose_name=_('street type'))

    billing_address = models.CharField(_('address'), max_length=200, blank=True, default='')
    billing_address2 = models.CharField(_('address 2'), max_length=200, blank=True, default='')
    billing_address3 = models.CharField(_('address 3'), max_length=200, blank=True, default='')

    billing_zip_code = models.CharField(_('zip code'), max_length=20, blank=True, default='')
    billing_cedex = models.CharField(_('cedex'), max_length=200, blank=True, default='')
    billing_city = models.ForeignKey(
        City, verbose_name=_('city'), blank=True, default=None, null=True, related_name='%(class)s_billing_set'
    )

    # These fields are just kept for editing the address field
    billing_street_number = models.CharField(_('street number'), max_length=20, blank=True, default='')
    billing_street_type = models.ForeignKey(
        StreetType, default=None, blank=True, null=True, verbose_name=_('street type'),
        related_name='%(class)s_billing_set'
    )

    class Meta:
        abstract = True

    def get_full_address(self):
        """join address fields"""
        return ' '.join(self.get_address_fields())

    def get_address_fields(self):
        """address fields: address, cedex, zipcode, city..."""
        if self.city:
            fields = [
                self.address, self.address2, self.address3, " ".join([self.zip_code, self.city.name, self.cedex])
            ]
            country = self.city.get_foreign_country()
            if country:
                fields.append(country.name)
            return [field for field in fields if field]
        return []

    def get_billing_address_fields(self):
        """address fields: address, cedex, zipcode, city..."""
        if self.billing_city:
            fields = [
                self.billing_address, self.billing_address2, self.billing_address3, " ".join(
                    [self.billing_zip_code, self.billing_city.name, self.billing_cedex]
                )
            ]
            country = self.billing_city.get_foreign_country()
            if country:
                fields.append(country.name)
            return [field for field in fields if field]
        return []

    def get_billing_full_address(self):
        """join address fields"""
        billing_address = ' '.join(self.get_billing_address_fields())
        if not billing_address:
            return self.get_full_address()
        return billing_address

    def has_billing_address(self):
        """has a billing address"""
        return len(self.get_billing_address_fields()) > 0

    def get_country(self):
        """country"""
        return self.city.get_country() if self.city else None

    def get_foreign_country(self):
        """country if not default"""
        return self.city.get_foreign_country() if self.city else None

    def get_display_address(self):
        """addresses"""
        return self.get_full_address()


@python_2_unicode_compatible
class Entity(AddressModel):
    """Entity correspond to a company, association, public administration ..."""
    name = models.CharField(_('name'), max_length=200, db_index=True)
    description = models.CharField(_('description'), max_length=200, blank=True, default="")
    type = models.ForeignKey(EntityType, verbose_name=_('type'), blank=True, null=True, default=None)
    relationship_date = models.DateField(_('relationship date'), default=None, blank=True, null=True)
    
    logo = models.ImageField(_("logo"), blank=True, default="", upload_to=get_entity_logo_dir)
    
    phone = models.CharField(_('phone'), max_length=200, blank=True, default='')
    fax = models.CharField(_('fax'), max_length=200, blank=True, default='')
    email = models.EmailField(_('email'), blank=True, default='')
    website = models.CharField(_('web site'), max_length=200, blank=True, default='')

    notes = models.TextField(_('notes'), blank=True, default="")
    
    imported_by = models.ForeignKey("ContactsImport", default=None, blank=True, null=True)
    
    is_single_contact = models.BooleanField(_("is single contact"), default=False)
    
    favorites = GenericRelation(Favorite)
    
    def save(self, *args, **kwargs):
        """save"""

        # add http if missing in website url
        if self.website:
            parsing = urlparse(self.website)
            if not parsing.scheme:
                self.website = "http://"+self.website
            
        super(Entity, self).save(*args, **kwargs)
        if self.contact_set.filter(has_left=False).count() == 0:
            Contact.objects.create(entity=self, main_contact=True, has_left=False)
        elif self.contact_set.filter(main_contact=True, has_left=False).count() == 0:
            #Always at least 1 main contact per entity
            contact = self.default_contact
            contact.main_contact = True
            contact.save()
        if self.is_single_contact:
            contact = self.default_contact
            self.name = "{0} {1}".format(contact.lastname, contact.firstname).lower()
            #don't put *args, *kwargs -> it may cause integrity error
            super(Entity, self).save()
    
    def __str__(self):
        return self.name

    def get_view_url(self):
        absolute_url = reverse('crm_view_entity', args=[self.id])
        try:
            return "//" + Site.objects.get_current().domain + absolute_url
        except Site.objects.DoesNotExist:
            return absolute_url

    def get_preview_url(self):
        """absolute_url in popup"""
        return "{0}?preview=1".format(self.get_absolute_url())

    def get_email_address(self):
        """email address"""
        if self.name:
            return '"{1}" <{0}>'.format(self.email, self.name)
        else:
            return self.email
    
    def get_safe_logo(self):
        """get entity logo or default one"""
        if self.logo:
            width, height = self.logo.width, self.logo.height
            image_format = "64" if width > height else "x64"
            return sorl_thumbnail.backend.get_thumbnail(self.logo.file, image_format, crop='center').url
        else:
            return self.default_logo()
    
    def default_logo(self):
        """get default logo"""
        if self.type and self.type.logo:
            file_ = sorl_thumbnail.backend.get_thumbnail(self.type.logo.file, "64x64", crop='center')
            return file_.url
        
        if self.is_single_contact:
            logo = "img/single-contact.png"
        else:
            logo = "img/entity.png"
        
        return "{0}{1}".format(project_settings.STATIC_URL, logo)
    
    def get_logo_center_style(self):
        """get logo style to apply to img html tag to get the logo centered"""
        if self.logo:
            width, height = self.logo.width, self.logo.height
            if width > height:
                width, height = 64, height * 64 / width
                return mark_safe('style="margin: {0}px 0"'.format((64 - height) / 2))
            else:
                width, height = width * 64 / height, height
                return mark_safe('style="margin-left: 0 {0}px"'.format((64 - width) / 2))
                
    def get_absolute_url(self):
        """url to the entity page"""
        return reverse('crm_view_entity', args=[self.id])

    def get_phones(self):
        """phones"""
        return [self.phone]

    def main_contacts(self):
        """all contacts of the entity with the 'main' flag checked"""
        return [
            contact
            for contact in self.contact_set.filter(main_contact=True, has_left=False).order_by("lastname", "firstname")
        ]
    
    def last_action(self):
        """last action done with the entity"""
        try:
            return Action.objects.filter(
                Q(contacts__entity=self) | Q(entities=self), done=True,
                done_date__isnull=False).order_by("-done_date")[0]
        except IndexError:
            return None
        
    def next_action(self):
        """next action to do with the entity"""
        try:
            return Action.objects.filter(
                Q(contacts__entity=self) | Q(entities=self), done=False,
                planned_date__isnull=False,
                done_date__isnull=True
            ).order_by("planned_date")[0]
        except IndexError:
            return None
        
    def single_contact(self):
        """is it just one contact --> a physical person"""
        try:
            if self.is_single_contact:
                return self.default_contact
        except IndexError:
            pass
        return None
    
    @property
    def default_contact(self):
        """returns the main contact"""
        if self.contact_set.filter(main_contact=True, has_left=False).count():
            return self.contact_set.filter(main_contact=True, has_left=False)[0]
        return self.contact_set.all()[0]
    
    def current_opportunities(self):
        """current opportunities"""
        return self.opportunity_set.filter(ended=False).count()

    def logo_thumbnail(self):
        """logo thumbnail"""
        return sorl_thumbnail.backend.get_thumbnail(self.logo.file, "128x128", crop='center')

    def set_custom_field(self, field_name, value, is_link=False):
        """set the value of a custom field"""
        field, is_new = CustomField.objects.get_or_create(model=CustomField.MODEL_ENTITY, name=field_name)
        if is_new:
            field.is_link = is_link
            field.save()
        field_value = EntityCustomFieldValue.objects.get_or_create(custom_field=field, entity=self)[0]
        field_value.value = value
        field_value.save()

    def add_to_group(self, group_name):
        """add to group"""
        group = Group.objects.get_or_create(name=group_name)[0]
        group.entities.add(self)
        group.save()

    def get_custom_fields(self):
        """additional fields"""
        return CustomField.objects.filter(model=CustomField.MODEL_ENTITY)

    def __getattribute__(self, attr):
        """add additional fields to the object"""
        prefix = "custom_field_"
        prefix_length = len(prefix)
        if attr[:prefix_length] == prefix:
            field_name = attr[prefix_length:]
            try:
                custom_field = CustomField.objects.get(model=CustomField.MODEL_ENTITY, name=field_name)
                custom_field_value = self.entitycustomfieldvalue_set.get(entity=self, custom_field=custom_field)
                return custom_field_value.value
            except EntityCustomFieldValue.DoesNotExist:
                return ''  # If no value defined: return empty string
        return object.__getattribute__(self, attr)

    class Meta:
        verbose_name = _('entity')
        verbose_name_plural = _('entities')
        ordering = ('name',)


@python_2_unicode_compatible
class EntityRole(NamedElement):
    """what a contact is doing in an entity"""
    class Meta:
        verbose_name = _('entity role')
        verbose_name_plural = _('entity roles')


def get_contact_photo_dir(instance, filename):
    """directory foe contacts photos in media"""
    return '{0}/{1}/{2}'.format(settings.CONTACT_PHOTO_DIR, instance.id, filename)


@python_2_unicode_compatible
class SameAs(models.Model):
    """Link between two contacts for the same physical person"""

    def __str__(self):
        return _("Same As: {0}").format(
            ['{0}'.format(contact) for contact in self.contact_set.order_by('same_as_priority')]
        )

    def priority_contact(self):
        """The contact with priority 1"""
        try:
            return "{0}".format(
                ['{0}'.format(contact) for contact in self.contact_set.order_by('same_as_priority')][0]
            )
        except IndexError:
            return ""
    priority_contact.short_description = _('Priority contact')

    def other_contacts(self):
        """all contacts except the 1st one"""
        try:
            return "{0}".format(
                ['{0}'.format(contact) for contact in self.contact_set.order_by('same_as_priority')][1:]
            )
        except IndexError:
            return ""
    other_contacts.short_description = _('Other contacts')

    def contacts_count(self):
        """Numbers of same-as contacts"""
        return self.contact_set.count()
    contacts_count.short_description = _('Contacts count')

    class Meta:
        verbose_name = _('same as')
        verbose_name_plural = _('sames as')


@python_2_unicode_compatible
class RelationshipType(models.Model):
    """type of relationship: client-provider, partner ..."""
    name = models.CharField(max_length=100, blank=False, verbose_name=_("name"))
    reverse = models.CharField(max_length=100, blank=True, default="", verbose_name=_("reverse relation"))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('relationship type')
        verbose_name_plural = _('relationship types')


@python_2_unicode_compatible
class Relationship(TimeStampedModel):
    """a relationship between two contacts"""
    contact1 = models.ForeignKey("Contact", verbose_name=_("contact 1"), related_name="relationships1")
    contact2 = models.ForeignKey("Contact", verbose_name=_("contact 2"), related_name="relationships2")
    relationship_type = models.ForeignKey("RelationshipType", verbose_name=_("relationship type"))
    
    def __str__(self):
        return _("{0} {1} of {2}").format(self.contact1, self.relationship_type, self.contact2)
    
    class Meta:
        verbose_name = _('relationship')
        verbose_name_plural = _('relationships')
    

@python_2_unicode_compatible
class Contact(AddressModel):
    """a contact : how to contact a physical person. A physical person may have several contacts"""
    GENDER_NOT_SET = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_COUPLE = 3
    
    GENDER_CHOICE = (
        (GENDER_NOT_SET, ''),
        (GENDER_MALE, _('Mr')),
        (GENDER_FEMALE, _('Mrs')),
        (GENDER_COUPLE, _('Mrs and Mr'))
    )

    entity = models.ForeignKey(Entity)
    role = models.ManyToManyField(EntityRole, blank=True, default=None, verbose_name=_('Roles'))
    
    gender = models.IntegerField(_('gender'), choices=GENDER_CHOICE, blank=True, default=GENDER_NOT_SET)
    gender_title = models.CharField(
        max_length=50, verbose_name=_('gender title'), default='', blank=True,
        help_text=_('Overwrites gender if defined')
    )
    title = models.CharField(_('title'), max_length=200, blank=True, default='')
    lastname = models.CharField(_('last name'), max_length=200, blank=True, default='', db_index=True)
    firstname = models.CharField(_('first name'), max_length=200, blank=True, default='')
    nickname = models.CharField(_('nickname'), max_length=200, blank=True, default='')
    
    photo = models.ImageField(_("photo"), blank=True, default="", upload_to=get_contact_photo_dir)
    birth_date = models.DateField(_("birth date"), blank=True, default=None, null=True)
    job = models.CharField(_("job"), max_length=200, blank=True, default="")
    
    main_contact = models.BooleanField(_("main contact"), default=True, db_index=True)
    accept_notifications = models.BooleanField(
        _("accept notifications"),
        default=True,
        help_text=_('We may have to notify you some events (e.g. a new message).')
    )
    email_verified = models.BooleanField(_("email verified"), default=False)
    
    phone = models.CharField(_('phone'), max_length=200, blank=True, default='')
    mobile = models.CharField(_('mobile'), max_length=200, blank=True, default='')
    email = models.EmailField(_('email'), blank=True, default='')
    
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    
    notes = models.TextField(_('notes'), blank=True, default="")
    
    same_as = models.ForeignKey(SameAs, blank=True, null=True, default=None, verbose_name=_('same as'))
    same_as_priority = models.IntegerField(default=0, verbose_name=_('same as priority'))
    
    relationships = models.ManyToManyField("Contact", blank=True, default=None, through=Relationship)
    
    has_left = models.BooleanField(_('has left'), default=False)
    
    imported_by = models.ForeignKey("ContactsImport", default=None, blank=True, null=True)
    
    favorites = GenericRelation(Favorite)

    favorite_language = models.CharField(
        _("favorite language"), max_length=10, default="", blank=True, choices=settings.get_language_choices()
    )

    def get_view_url(self):
        if self.entity.is_single_contact:
            absolute_url = reverse('crm_view_entity', args=[self.entity.id])
        else:
            absolute_url = reverse('crm_view_contact', args=[self.id])
        try:
            return "//" + Site.objects.get_current().domain + absolute_url
        except Site.objects.DoesNotExist:
            return absolute_url

    def get_preview_url(self):
        """absolute url in popup"""
        return "{0}?preview=1".format(self.get_absolute_url())
    
    def get_relationships(self):
        """get all retlationships for this contact"""

        class ContactRelationship(object):
            """
            A private class for relationship
            It mimics a regular model object
            Used to handle relationships and reverse relationships in a same list
            """
            def __init__(self, id_, contact, type_, type_name):
                self.id = id_  # pylint: disable=invalid-name
                self.contact = contact
                self.type = type_
                self.type_name = type_name

        relationships = []
        for relationship in Relationship.objects.filter(contact1=self):
            relationships.append(
                ContactRelationship(
                    id_=relationship.id, contact=relationship.contact2,
                    type_=relationship.relationship_type, type_name=relationship.relationship_type.name
                )
            )
            
        for relationship in Relationship.objects.filter(contact2=self):
            relationships.append(
                ContactRelationship(
                    id_=relationship.id, contact=relationship.contact1, type_=relationship.relationship_type,
                    type_name=(relationship.relationship_type.reverse or relationship.relationship_type.name)
                )
            )
            
        return relationships
    
    def can_add_relation(self):
        """relationships enabled?"""
        return RelationshipType.objects.count() > 0

    def get_same_as(self):
        """get contacts marked as same as"""
        if self.same_as:
            return Contact.objects.filter(same_as=self.same_as).exclude(id=self.id)
        return Contact.objects.none()

    def get_same_email(self):
        """get contacts with same email address"""
        if self.email:
            return Contact.objects.filter(Q(email=self.email) | Q(entity__email=self.email)).exclude(id=self.id)
        return Contact.objects.none()

    def get_safe_photo(self):
        """photo or default one"""
        if self.photo:
            return self.photo_thumbnail().url
        else:
            return self.default_logo()
    
    def get_photo_center_style(self):
        """get photo style"""
        if self.photo:
            width, height = self.photo.width, self.photo.height
            if width > height:
                width, height = 64, height * 64 / width
                return mark_safe('style="margin: {0}px 0"'.format((64 - height) / 2))
            else:
                width, height = width * 64 / height, height
                return mark_safe('style="margin: 0 {0}px"'.format((64 - width) / 2))

    def default_logo(self):
        """default image for a contact"""
        if self.entity.is_single_contact:
            logo = "img/single-contact.png"
        else:
            logo = "img/contact.png"
        return "{0}{1}".format(project_settings.STATIC_URL, logo)
    
    def photo_thumbnail(self):
        """photo thumbnail"""
        width, height = self.photo.width, self.photo.height
        image_format = "64" if width > height else "x64"
        return sorl_thumbnail.backend.get_thumbnail(self.photo.file, image_format, crop='center')

    def get_custom_fields(self):
        """additional fields"""
        return CustomField.objects.filter(model=CustomField.MODEL_CONTACT)
        
    def get_name_and_entity(self):
        """name and entity"""
        if self.entity.is_single_contact:
            return self.fullname
        return "{0} ({1})".format(self.fullname, self.entity.name)

    def __getattribute__(self, attr):
        """
        get an attribute: look if an additional field exists
        If an attribute is not defined: for example address: try to get it from entity
        """
        if attr[:4] == "get_":
            address_fields = ('address', 'address2', 'address3', 'zip_code', 'cedex', 'city')
            billing_address_fields = (
                'billing_address', 'billing_address2', 'billing_address3', 'billing_zip_code', 'billing_cedex',
                'billing_city'
            )
            field_name = attr[4:]
            if field_name in ('phone', 'email',):
                mine = getattr(self, field_name)
                return mine or getattr(self.entity, field_name)
            elif field_name in address_fields:
                is_contact_address_defined = any([getattr(self, field) for field in address_fields])
                if is_contact_address_defined:
                    return getattr(self, field_name)
                return getattr(self.entity, field_name)
            elif field_name in billing_address_fields:
                is_billing_contact_address_defined = any([getattr(self, field) for field in address_fields])
                if is_billing_contact_address_defined:
                    return getattr(self, field_name)
                return getattr(self.entity, field_name)
            else:
                prefix = "custom_field_"
                prefix_length = len(prefix)
                if field_name[:prefix_length] == prefix:
                    value = getattr(self, field_name)
                    if not value:  # if no value for the custom field
                        try:
                            # Try to get a value for a custom field with same name on entity
                            value = getattr(self.entity, field_name)
                        except CustomField.DoesNotExist:
                            # No custom field with same name on entity: returns empty string
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
                except ContactCustomFieldValue.DoesNotExist:
                    return ''  # If no value defined: return empty string
            else:
                entity_prefix = "entity_"
                full_prefix = entity_prefix + prefix
                if attr[:len(full_prefix)] == full_prefix:  # if the attr is entity_custom_field_<something>
                    # return self.entity.custom_field_<something>
                    return getattr(self.entity, attr[len(entity_prefix):])

        return object.__getattribute__(self, attr)
    
    def get_absolute_url(self):
        """url to contact page"""
        return reverse('crm_view_contact', args=[self.id])

    def has_address(self):
        """returns True if address field is set"""
        return self.address.strip() != ''

    def get_address_fields(self):
        """get address fields: address, zip, city..."""
        fields = super(Contact, self).get_address_fields()
        if fields:
            return fields
        else:
            return self.entity.get_address_fields()

    def get_country(self):
        """country"""
        country = super(Contact, self).get_country()
        if country:
            return country
        elif not self.entity.is_single_contact:
            return self.entity.get_country()

    def get_billing_full_address(self):
        """billing address"""
        billing_address = super(Contact, self).get_billing_full_address()
        if billing_address:
            return billing_address
        elif not self.entity.is_single_contact:
            return self.entity.get_billing_full_address()

    def get_foreign_country(self):
        """country if different from default"""
        country = super(Contact, self).get_foreign_country()
        if country:
            return country
        elif not self.entity.is_single_contact:
            return self.entity.get_foreign_country()

    def get_email_address(self):
        """email address"""
        if self.lastname or self.firstname:
            return '"{1}" <{0}>'.format(self.get_email, self.fullname)
        else:
            return self.get_email
        
    def get_phones(self):
        """list of phones"""
        return [x for x in (self.phone, self.mobile) if x]
    
    def get_roles(self):
        """list of roles"""
        return [x.name for x in self.role.all()]
    
    def has_entity(self):
        """is it member of an entity (not a single contact or an individual)"""
        try:
            if settings.ALLOW_SINGLE_CONTACT:
                return not self.entity.is_single_contact
            else:
                if self.entity.type:
                    return self.entity.type.id != getattr(project_settings, 'BALAFON_INDIVIDUAL_ENTITY_ID', 1)
                return False
        except AttributeError:
            return True
        
    def get_entity_name(self):
        """entity name"""
        return self.entity.name if self.has_entity() else ""
            
    def __str__(self):
        fullname = "{0} {1}".format(self.lastname, self.firstname).strip()
        if not fullname:
            fullname = self.email
        if self.entity.is_single_contact:
            return fullname
        return "{0} ({1})".format(fullname, self.entity.name)

    def get_gender_text(self):
        if self.gender_title:
            return self.gender_title
        elif self.gender:
            return self.get_gender_display()
        return ""
            
    @property
    def fullname(self):
        """fullname"""
        if not (self.firstname or self.lastname):
            if self.email:
                return self.email.strip()
            else:
                return "< {0} >".format(ugettext("Unknown")).strip()
        
        if self.gender and self.lastname:
            title = '{0} '.format(self.get_gender_text())
        else:
            title = ''
        
        if (not self.firstname) or (not self.lastname):
            return "{1}{0.firstname}{0.lastname}".format(self, title).strip()

        return "{1}{0.firstname} {0.lastname}".format(self, title).strip()

    @property
    def display_name(self):
        """fullname"""
        firstname = self.firstname.strip()
        lastname = self.lastname.strip()
        email = self.email.strip()
        if not (firstname or lastname):
            if email:
                return email
            else:
                return "< {0} >".format(ugettext("Unknown")).strip()

        return "{0} {1}".format(lastname, firstname).strip()

    @property
    def full_address(self):
        """address for custom templating in newsletter"""
        fields = self.get_address_fields()
        return ' '.join(fields)

    @property
    def entity_name(self):
        """entity name  for custom templating in newsletter"""
        if self.entity.is_single_contact:
            return ''
        return self.entity.name

    @property
    def city_name(self):
        """city name for custom templating in newsletter"""
        city = self.get_city
        if city:
            return city.name
        return ''

    @property
    def gender_name(self):
        """gender as string for custom templating in newsletter"""
        for gender, name in Contact.GENDER_CHOICE:
            if self.gender == gender:
                return '{0}'.format(name)  # lazy translation must be converted in unicode
        return ''

    @property
    def gender_dear(self):
        """return male/female version of Dear"""
        if self.gender == Contact.GENDER_MALE:
            return ugettext('Dear (male)')

        elif self.gender == Contact.GENDER_FEMALE:
            return ugettext('Dear (female)')

        elif self.gender == Contact.GENDER_COUPLE:
            return ugettext('Dears (couple)')

        return ''

    def set_custom_field(self, field_name, value, is_link=False):
        """set the value of a custom field"""
        field, is_new = CustomField.objects.get_or_create(model=CustomField.MODEL_CONTACT, name=field_name)
        if is_new:
            field.is_link = is_link
            field.save()
        field_value = ContactCustomFieldValue.objects.get_or_create(custom_field=field, contact=self)[0]
        field_value.value = value
        field_value.save()

    def get_custom_field(self, field_name):
        """get the value of a custom field"""
        field = CustomField.objects.get_or_create(model=CustomField.MODEL_CONTACT, name=field_name)[0]
        field_value = ContactCustomFieldValue.objects.get_or_create(custom_field=field, contact=self)[0]
        return field_value.value

    def add_to_group(self, group_name):
        """add to group"""
        group = Group.objects.get_or_create(name=group_name)[0]
        group.contacts.add(self)
        group.save()

    def save(self, *args, **kwargs):
        """save"""
        try:
            int(self.gender)
        except ValueError:
            self.gender = 0

        super(Contact, self).save(*args, **kwargs)
        if not self.uuid:
            name = '{0}-contact-{1}-{2}-{3}'.format(project_settings.SECRET_KEY, self.id, self.fullname, self.email)
            ascii_name = unicodedata.normalize('NFKD', name).encode("ascii", 'ignore')
            self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, '{0}'.format(ascii_name))
            return super(Contact, self).save()
        
        if self.entity.is_single_contact:
            # force the entity name for ordering
            self.entity.save()
            
    class Meta:
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')
        ordering = ('lastname', 'firstname')


def on_update_same_as(sender, instance, **kwargs):
    """update the SameAs contacts when a contact is deleted"""
    if instance.same_as:
        if instance.same_as.contact_set.exclude(id=instance.id).count() > 1:
            # If still some other contacts : Rebuild the priority orders for others
            same_as_contacts = instance.same_as.contact_set.exclude(id=instance.id).order_by('same_as_priority')
            for index, contact in enumerate(same_as_contacts):
                contact.same_as_priority = 1 + index
                contact.save()
        else:
            # If the other contact is now alone: delete the same_as
            same_as = instance.same_as
            for contact in same_as.contact_set.all():
                contact.same_as = None
                contact.same_as_priority = 0
                contact.save()
            same_as.delete()


pre_delete.connect(on_update_same_as, sender=Contact)


@python_2_unicode_compatible
class SubscriptionType(models.Model):
    """Subscription type: a mailing list for example"""
    name = models.CharField(max_length=100, verbose_name=_("name"))
    site = models.ForeignKey(Site, blank=True, null=True)
    order_index = models.IntegerField(default=0, verbose_name=_("order index"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Subscription type')
        verbose_name_plural = _('Subscription types')
        ordering = ('order_index', )


@python_2_unicode_compatible
class Subscription(models.Model):
    """contact is subscribing to a mailing list"""
    subscription_type = models.ForeignKey(SubscriptionType)
    contact = models.ForeignKey(Contact)
    
    accept_subscription = models.BooleanField(
        _("accept subscription"), default=False,
        help_text=_('Keep this checked if you want to receive our newsletter.')
    )
    
    subscription_date = models.DateTimeField(blank=True, default=None, null=True)
    unsubscription_date = models.DateTimeField(blank=True, default=None, null=True)

    def __str__(self):
        return "{0} {1}".format(self.subscription_type, self.contact)


@python_2_unicode_compatible
class Group(TimeStampedModel):
    """Group of contacts or entities"""
    name = models.CharField(_('name'), max_length=200, unique=True, db_index=True)
    description = models.CharField(_('description'), max_length=200, blank=True, default="")
    entities = models.ManyToManyField(Entity, blank=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    subscribe_form = models.BooleanField(
        default=False, verbose_name=_('Subscribe form'),
        help_text=_('This group will be proposed on the public subscribe form')
    )
    fore_color = models.CharField(
        blank=True, default='', max_length=7, validators=[validate_rgb], verbose_name=_('Fore color'),
        help_text=_("Fore color. Must be a rgb code. For example: #ffffff")
    )
    background_color = models.CharField(
        blank=True, default='', max_length=7, validators=[validate_rgb], verbose_name=_('Background color'),
        help_text=_("Background color. Must be a rgb code. For example: #000000")
    )
    
    favorites = GenericRelation(Favorite)

    def __str__(self):
        return self.name
    
    @property
    def all_contacts(self):
        """all contacts on the group: directly or from entity"""
        return Contact.objects.filter(Q(id__in=self.contacts.all()) | Q(entity__id__in=self.entities.all()))

    def save(self, *args, **kwargs):
        """save: remove trailing spaces in name"""
        self.name = self.name.strip()
        return super(Group, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')


@python_2_unicode_compatible
class OpportunityStatus(NamedElement):
    """status for an opportynity"""
    ordering = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _('opportunity status')
        verbose_name_plural = _('opportunity status')


@python_2_unicode_compatible
class OpportunityType(NamedElement):
    """type for an opprtunity"""
    class Meta:
        verbose_name = _('opportunity type')
        verbose_name_plural = _('opportunity types')


@python_2_unicode_compatible
class Opportunity(TimeStampedModel):
    """An opportunity is kind of project. It makes possible to group different actions"""
    PROBABILITY_LOW = 1
    PROBABILITY_MEDIUM = 2
    PROBABILITY_HIGH = 3
    PROBABILITY_CHOICES = (
        (PROBABILITY_LOW, _('low')),
        (PROBABILITY_MEDIUM, _('medium')),
        (PROBABILITY_HIGH, _('high')),
    )
    
    #TO BE REMOVED--
    entity = models.ForeignKey(Entity, blank=True, null=True, default=None)
    #---------------
    name = models.CharField(_('name'), max_length=200)
    status = models.ForeignKey(OpportunityStatus, default=None, blank=True, null=True)
    type = models.ForeignKey(OpportunityType, blank=True, null=True, default=None)
    detail = models.TextField(_('detail'), blank=True, default='')
    #TO BE REMOVED---
    probability = models.IntegerField(
        _('probability'), default=PROBABILITY_MEDIUM, choices=PROBABILITY_CHOICES
    )
    amount = models.DecimalField(_('amount'), default=None, blank=True, null=True, max_digits=11, decimal_places=2)
    #----------------
    ended = models.BooleanField(_('closed'), default=False, db_index=True)
    #TO BE REMOVED---
    start_date = models.DateField(_('starting date'), blank=True, null=True, default=None)
    end_date = models.DateField(_('closing date'), blank=True, null=True, default=None)
    #----------------
    display_on_board = models.BooleanField(
        verbose_name=_('display on board'),
        default=settings.OPPORTUNITY_DISPLAY_ON_BOARD_DEFAULT,
        db_index=True
    )
    
    favorites = GenericRelation(Favorite)
    
    def get_start_date(self):
        """start date of the project: first action"""
        try:
            return self.action_set.filter(planned_date__isnull=False).order_by("planned_date")[0].planned_date
        except IndexError:
            return None
        
    def get_end_date(self):
        """end date: last action"""
        try:
            return self.action_set.filter(planned_date__isnull=False).order_by("-planned_date")[0].planned_date
        except IndexError:
            return None
    
    def default_logo(self):
        """dafult logo"""
        logo = "img/folder.png"
        return "{0}{1}".format(project_settings.STATIC_URL, logo)
    
    def __str__(self):
        return "{0.name}".format(self)

    class Meta:
        verbose_name = _('opportunity')
        verbose_name_plural = _('opportunities')


@python_2_unicode_compatible
class ActionSet(NamedElement):
    """group some actions types"""
    ordering = models.IntegerField(verbose_name=_('display ordering'), default=10)

    class Meta:
        verbose_name = _('action set')
        verbose_name_plural = _('action sets')
        ordering = ['ordering']


@python_2_unicode_compatible
class ActionStatus(NamedElement):
    """status for an action"""
    ordering = models.IntegerField(verbose_name=_('display ordering'), default=10)
    is_final = models.BooleanField(
        default=False,
        verbose_name=_('is final'),
        help_text=_('The action will be marked done when it gets a final status')
    )
    fore_color = models.CharField(
        blank=True, default='', max_length=7, validators=[validate_rgb], verbose_name=_('Fore color'),
        help_text=_("Fore color. Must be a rgb code. For example: #ffffff")
    )
    background_color = models.CharField(
        blank=True, default='', max_length=7, validators=[validate_rgb], verbose_name=_('Background color'),
        help_text=_("Background color. Must be a rgb code. For example: #000000")
    )
    next_on_send = models.ForeignKey(
        "ActionStatus", verbose_name=_('Next status on send by email'), default=None, null=True, blank=True,
        on_delete=models.CASCADE, help_text=_('automatically change the status when sent by email'), related_name="+"
    )
    allowed_on_frozen = models.BooleanField(
        default=True, verbose_name=_('allowed on frozen'), help_text=_('If False, not shown if action si frozen')
    )

    @property
    def style(self):
        style = ""
        if self.background_color:
            style += "background: {0}; ".format(self.background_color)
        if self.fore_color:
            style += "color: {0}; ".format(self.fore_color)
        return style

    class Meta:
        verbose_name = _('action status')
        verbose_name_plural = _('action status')
        ordering = ['ordering']


@python_2_unicode_compatible
class ActionNumberGenerator(models.Model):
    class Meta:
        verbose_name = _('action number generator')
        verbose_name_plural = _('action number generators')

    name = models.CharField(_('name'), max_length=200, blank=True, default="")
    number = models.IntegerField(
        _('number'), default=0, help_text=_('This number is auto-generated.')
    )

    def __str__(self):
        return self.name

    def next(self):
        self.number += 1
        self.save()
        return self.number


@python_2_unicode_compatible
class ActionType(NamedElement):
    """type of an action"""
    subscribe_form = models.BooleanField(
        default=False, verbose_name=_('Subscribe form'),
        help_text=_('This action type will be proposed on the public subscribe form')
    )
    set = models.ForeignKey(ActionSet, blank=True, default=None, null=True, verbose_name=_("action set"))
    last_number = models.IntegerField(_('last number'), default=0)
    number_auto_generated = models.BooleanField(_('generate number automatically'), default=False)
    number_generator = models.ForeignKey(
        ActionNumberGenerator, blank=True, default=None, null=True, verbose_name=_('number generator')
    )
    default_template = models.CharField(
        _('document template'), max_length=200, blank=True, default="",
        help_text=_('Action of this type will have a document with the given template')
    )
    allowed_status = models.ManyToManyField(
        ActionStatus, blank=True, default=None, help_text=_('Action of this type allow the given status')
    )
    default_status = models.ForeignKey(
        ActionStatus, blank=True, default=None, null=True,
        help_text=_('Default status for actions of this type'),
        related_name='type_default_status_set'
    )
    allowed_status2 = models.ManyToManyField(
        ActionStatus, blank=True, default=None, help_text=_('Action of this type allow the given status'),
        related_name="type_status2_set"
    )
    default_status2 = models.ForeignKey(
        ActionStatus, blank=True, default=None, null=True,
        help_text=_('Default status for actions of this type'),
        related_name='type_default_status2_set'
    )
    is_editable = models.BooleanField(
        _('is editable'),
        default=True,
        help_text=_('If default_template is set, define if the template has a editable content')
    )
    action_template = models.CharField(
        _('action template'), max_length=200, blank=True, default="",
        help_text=_('Action of this type will be displayed using the given template')
    )
    order_index = models.IntegerField(default=10, verbose_name=_("Order"))
    is_amount_calculated = models.BooleanField(default=False, verbose_name=_("Is amount calculated"))
    next_action_types = models.ManyToManyField('ActionType', blank=True, verbose_name=_('next action type'))
    not_assigned_when_cloned = models.BooleanField(default=False, verbose_name=_("Not assigned when cloned"))
    generate_uuid = models.BooleanField(default=False, verbose_name=_("Generate UUID for action"))
    hide_contacts_buttons = models.BooleanField(
        default=False,
        verbose_name=_('hide contacts buttons'),
        help_text=_('The add and remove contact buttons will be hidden')
    )
    mail_to_subject = models.CharField(
        max_length=100, default='', blank=True, verbose_name=_('Subject of email'),
        help_text=_('This would be used as subject when sending the action by email')
    )
    track_status = models.BooleanField(
        default=False, verbose_name=_('Track status'), help_text=_('If checked, all status changed is stored in DB')
    )
    is_default = models.BooleanField(
        default=False, verbose_name=_('is default'),
        help_text=_('If checked, can be added from list. Action without types are not displayed')
    )
    label = models.CharField(
        max_length=100, default='', blank=True, verbose_name=_('label'),
        help_text=_('If set, replace name on commercial document')
    )

    def status_defined(self):
        """true if a status is defined for this type"""
        return self.allowed_status.count() > 0
    status_defined.short_description = _("Status defined")

    def has_final_status(self):
        return self.allowed_status.filter(is_final=True).exists()

    def action_number(self):
        if self.number_auto_generated:
            if self.number_generator:
                return '{0}: {1}'.format(self.number_generator.name, self.number_generator.number)
            else:
                return '{0}'.format(self.last_number)
        return ""
    action_number.short_description = _('Last number')

    def save(self, *args, **kwargs):
        """save: create the corresponding men"""
        ret = super(ActionType, self).save(*args, **kwargs)

        if self.id:
            if self.next_action_types.count():
                ActionMenu.create_action_menu(
                    action_type=self,
                    view_name='crm_clone_action',
                    label=ugettext('Duplicate'),
                    icon='duplicate',
                    a_attrs='class="colorbox-form"'
                )
            else:
                ActionMenu.objects.filter(action_type=self, view_name='crm_clone_action').delete()

            # update action uuid if needed
            for action in self.action_set.all():
                if self.generate_uuid:
                    if not action.uuid:
                        action.save(from_save_type=True)  # force uuid to be generated
                else:
                    if action.uuid:
                        action.uuid = ''
                        action.save(from_save_type=True)  # force uuid to be empty
        return ret
    
    class Meta:
        verbose_name = _('action type')
        verbose_name_plural = _('action types')
        ordering = ['order_index', 'name']


@python_2_unicode_compatible
class TeamMember(models.Model):
    """A member of the team : can be in charge of actions"""
    user = models.OneToOneField(User, default=None, blank=True, null=True, verbose_name=_("user"))
    name = models.CharField(max_length=100, verbose_name=_("name"))
    active = models.BooleanField(default=True, verbose_name=(_("active")))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('team member')
        verbose_name_plural = _('team members')


@python_2_unicode_compatible
class ActionMenu(models.Model):
    """A menu to add to every action of this type"""

    action_type = models.ForeignKey(ActionType, verbose_name=_('Action type'))
    view_name = models.CharField(_('view_name'), max_length=200)
    icon = models.CharField(_('icon'), max_length=30, default="", blank=True)
    label = models.CharField(_('label'), max_length=200)
    a_attrs = models.CharField(
        max_length=50,
        verbose_name=_("Link args"),
        blank=True,
        default="",
        help_text=_('Example: class="colorbox-form" for colorbos display')
    )
    order_index = models.IntegerField(default=0, verbose_name=_("order_index"))
    only_for_status = models.ManyToManyField(ActionStatus, blank=True, verbose_name=_('Only for status'))

    class Meta:
        verbose_name = _('action menu')
        verbose_name_plural = _('action menus')
        ordering = ['order_index']

    def only_for_status_str(self):
        """returns status as string for admin"""
        all_status = list(self.only_for_status.all())
        if all_status:
            return ', '.join([status.name for status in all_status])
        return ""
    only_for_status_str.short_description = _('Only for status')

    @classmethod
    def create_action_menu(cls, action_type, view_name, label=None, icon='', a_attrs=''):
        queryset = ActionMenu.objects.filter(action_type=action_type, view_name=view_name)
        if not queryset.exists():
            return ActionMenu.objects.create(
                view_name=view_name,
                action_type=action_type,
                label=label or view_name,
                icon=icon,
                a_attrs=a_attrs
            )

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class Action(LastModifiedModel):
    """action : something to do"""
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, _('low priority')),
        (PRIORITY_MEDIUM, _('medium priority')),
        (PRIORITY_HIGH, _('high priority')),
    )
    
    class Meta:
        verbose_name = _('action')
        verbose_name_plural = _('actions')

    subject = models.CharField(_('subject'), max_length=200, blank=True, default="")
    planned_date = models.DateTimeField(_('planned date'), default=None, blank=True, null=True, db_index=True)
    type = models.ForeignKey(ActionType, blank=True, default=None, null=True)
    detail = models.TextField(_('detail'), blank=True, default='')
    priority = models.IntegerField(_('priority'), default=PRIORITY_MEDIUM, choices=PRIORITY_CHOICES)
    opportunity = models.ForeignKey(Opportunity, blank=True, default=None, null=True, verbose_name=_('opportunity'))
    done = models.BooleanField(_('done'), default=False, db_index=True)
    done_date = models.DateTimeField(_('done date'), blank=True, null=True, default=None, db_index=True)
    in_charge = models.ForeignKey(TeamMember, verbose_name=_('in charge'), blank=True, null=True, default=None)
    display_on_board = models.BooleanField(verbose_name=_('display on board'), default=True, db_index=True)
    archived = models.BooleanField(verbose_name=_('archived'), default=False, db_index=True)
    amount = models.DecimalField(
        _('amount'), default=None, blank=True, null=True, max_digits=11, decimal_places=2
    )
    number = models.IntegerField(
        _('number'), default=0, help_text=_('This number is auto-generated based on action type.')
    )
    status = models.ForeignKey(ActionStatus, blank=True, default=None, null=True)
    status2 = models.ForeignKey(ActionStatus, blank=True, default=None, null=True, related_name='status2_set')
    contacts = models.ManyToManyField(Contact, blank=True, default=None, verbose_name=_('contacts'))
    entities = models.ManyToManyField(Entity, blank=True, default=None, verbose_name=_('entities'))
    favorites = GenericRelation(Favorite)
    end_datetime = models.DateTimeField(_('end date'), default=None, blank=True, null=True, db_index=True)
    parent = models.ForeignKey("Action", blank=True, default=None, null=True, verbose_name=_("parent"))
    uuid = models.CharField(max_length=100, blank=True, default='', db_index=True)
    previous_status = models.ForeignKey(ActionStatus, blank=True, default=None, null=True, related_name='+')
    frozen = models.BooleanField(
        default=False, verbose_name=_('frozen'), help_text=_('Some data (date, sale, ...) can not be changed ')
    )

    def __str__(self):
        return '{0} - {1}'.format(self.planned_date, self.subject or self.type)

    def show_duration(self):
        """Show duration on action line. If False show end_time"""
        return True

    def duration(self):
        """returns duration of the action"""
        if self.end_datetime:
            delta = self.end_datetime - self.planned_date
            hours, remainder = divmod(delta.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)

            if days:
                return _("{0} days {1}:{2:02}").format(int(days), int(hours), int(minutes))
            else:
                return '{0}:{1:02}'.format(int(hours), int(minutes))

    def has_non_editable_document(self):
        """true if a non editable doc is linked to this action"""
        return self.type and self.type.default_template and (not self.type.is_editable)
    
    def has_editable_document(self):
        """true if an editable doc is linked to this action"""
        return self.type and self.type.default_template and self.type.is_editable

    def get_action_template(self):
        if self.type and self.type.action_template:
            try:
                #Check if the template exists but return its name
                get_template(self.type.action_template)
                return self.type.action_template
            except TemplateDoesNotExist:
                message = "get_action_template: TemplateDoesNotExist {0}".format(self.type.action_template)
                logger.warning(message)
        return 'Crm/_action.html'

    def get_recipients(self, html=True):
        """returns contacts and entites as html code. Use template for easy customization"""
        template_file = get_template("Crm/_actions/recipients.html")
        text = template_file.render({'action': self})
        if not html:
            text = dehtml(text)
        return text

    def get_action_number(self):
        if self.type and self.number:
            return _('{0} N° {1}').format(self.type.label or self.type.name, self.number)
        return ''

    def get_menus(self):
        if self.type:
            queryset = ActionMenu.objects.filter(action_type=self.type)
            if self.status:
                queryset = queryset.filter(
                    Q(only_for_status=self.status) | Q(only_for_status__isnull=True)
                )
            return queryset
        return ActionMenu.objects.none()

    def save(self, *args, **kwargs):
        """save"""

        from_save_type = kwargs.pop('from_save_type', False)

        if self.status and self.status.is_final:
            self.done = True
        elif self.type and self.type.allowed_status.filter(is_final=True).exists():
            self.done = False

        if not self.done_date and self.done:
            self.done_date = now_rounded()
        elif self.done_date and not self.done:
            self.done_date = None

        if not from_save_type:  # avoid infinite loop
            # generate number automatically based on action type
            if self.number == 0 and self.type and self.type.number_auto_generated:
                if self.type.number_generator:
                    self.number = self.type.number_generator.next()
                else:
                    self.number = self.type.last_number = self.type.last_number + 1
                    self.type.save()

        created_track = None
        if self.status and self.type and self.type.track_status:
            if self.previous_status != self.status:
                created_track = ActionStatusTrack(
                    status=self.status,
                    datetime=datetime.now()
                )
                self.previous_status = self.status

        ret = super(Action, self).save(*args, **kwargs)

        if self.type:
            if self.type.generate_uuid and not self.uuid:
                name = '{0}-action-{1}-{2}'.format(
                    project_settings.SECRET_KEY, self.id, self.type.id if self.type else 0
                )
                ascii_name = unicodedata.normalize('NFKD', name).encode("ascii", 'ignore')
                self.uuid = uuid.uuid5(uuid.NAMESPACE_URL, '{0}'.format(ascii_name))
                super(Action, self).save()

            if not self.type.generate_uuid and self.uuid:
                self.uuid = ''
                super(Action, self).save()

        if created_track is not None:
            created_track.action = self
            created_track.save()

        return ret

    def clone(self, new_type, planned_date=None):
        """Create a new action with same values but different types"""
        new_action = Action(parent=self)

        attrs_to_clone = [
            'subject', 'detail', 'priority', 'opportunity', 'amount', 'end_datetime'
        ]

        if not new_type.not_assigned_when_cloned:
            attrs_to_clone += ['in_charge', ]

        for attr in attrs_to_clone:
            setattr(new_action, attr, getattr(self, attr))

        if planned_date is not None:
            new_action.planned_date = planned_date
        else:
            new_action.planned_date = self.planned_date

        new_action.type = new_type
        new_action.status = new_type.default_status
        new_action.status2 = new_type.default_status2
        new_action.save()

        for contact in self.contacts.all():
            new_action.contacts.add(contact)

        for entity in self.entities.all():
            new_action.entities.add(entity)
        new_action.save()
        return new_action

    @property
    def mail_to(self):
        """returns a mailto link"""
        unique_emails = sorted(list(set(
            [
                contact.get_email_address() for contact in self.contacts.all() if contact.get_email
            ] + [
                entity.get_email_address() for entity in self.entities.all() if entity.email
            ]
        )))

        if not unique_emails:
            return ""

        return reverse('crm_mailto_action', args=[self.id])


@python_2_unicode_compatible
class ActionDocument(models.Model):
    """A document"""
    content = models.TextField(_('content'), blank=True, default="")
    action = models.OneToOneField(Action)
    template = models.CharField(_('template'), max_length=200)
    
    def get_edit_url(self):
        """edit url"""
        return reverse('crm_edit_action_document', args=[self.action.id])
        
    def get_absolute_url(self):
        """view url"""
        return reverse('crm_view_action_document', args=[self.action.id])
    
    def get_pdf_url(self):
        """pdf url"""
        return reverse('crm_pdf_action_document', args=[self.action.id])
    
    def can_edit_object(self, user):
        """can edit?"""
        return user.is_staff and self.action.has_editable_document()
    
    def can_view_object(self, user):
        """can view?"""
        return user.is_staff
    
    def __str__(self):
        return "{0} - {1}".format(self.template, self.action)
    

@python_2_unicode_compatible
class CustomField(models.Model):
    """An additional field for a contact or an entity"""

    MODEL_ENTITY = 1
    MODEL_CONTACT = 2
    
    MODEL_CHOICE = (
        (MODEL_ENTITY, _('Entity')),
        (MODEL_CONTACT, _('Contact')),
    )
    
    name = models.CharField(max_length=100, verbose_name=_('name'))
    label = models.CharField(max_length=100, verbose_name=_('label'), blank=True, default='')
    model = models.IntegerField(verbose_name=_('model'), choices=MODEL_CHOICE)
    widget = models.CharField(max_length=100, verbose_name=_('widget'), blank=True, default='')
    ordering = models.IntegerField(verbose_name=_('display ordering'), default=10)
    import_order = models.IntegerField(verbose_name=_('import ordering'), default=0)
    export_order = models.IntegerField(verbose_name=_('export ordering'), default=0)
    is_link = models.BooleanField(default=False, verbose_name=_('is link'))
    
    def __str__(self):
        return _("{0}:{1}").format(self.model_name(), self.name)
    
    def model_name(self):
        """model name : entity or contact"""
        if self.model == self.MODEL_ENTITY:
            return 'entity'
        else:
            return 'contact'
    
    class Meta:
        verbose_name = _('custom field')
        verbose_name_plural = _('custom fields')
        ordering = ('ordering', 'import_order', 'export_order')


@python_2_unicode_compatible
class CustomFieldValue(models.Model):
    """base class for custom field value"""
    custom_field = models.ForeignKey(CustomField, verbose_name=_('custom field'))
    value = models.TextField(verbose_name=_('value'))
    
    class Meta:
        verbose_name = _('custom field value')
        verbose_name_plural = _('custom field values')
        abstract = True


@python_2_unicode_compatible
class EntityCustomFieldValue(CustomFieldValue):
    """a value for a custom field on an entity"""
    entity = models.ForeignKey(Entity)
    
    class Meta:
        verbose_name = _('entity custom field value')
        verbose_name_plural = _('entity custom field values')

    def __str__(self):
        return '{0} {1}'.format(self.entity, self.custom_field)


@python_2_unicode_compatible
class ContactCustomFieldValue(CustomFieldValue):
    """a value for a custom field of a contact"""
    contact = models.ForeignKey(Contact)
    
    class Meta:
        verbose_name = _('contact custom field value')
        verbose_name_plural = _('contact custom field values')

    def __str__(self):
        return '{0} {1}'.format(self.contact, self.custom_field)


def _get_import_dir(contact_import, filename):
    """directory fro storing the files to import"""
    return '{0}/{1}'.format(settings.CONTACTS_IMPORT_DIR, filename)


@python_2_unicode_compatible
class ContactsImport(TimeStampedModel):
    """import from csv"""
    
    ENCODINGS = (
        ('utf-8', 'utf-8'),
        ('iso-8859-15', 'iso-8859-15'),
        ('cp1252', 'cp1252')
    )
    
    SEPARATORS = (
        (',', _('Coma')),
        (';', _('Semi-colon')),
    )

    import_file = models.FileField(
        _('import file'), upload_to=_get_import_dir,
        help_text=_('CSV file following the import contacts format.')
    )
    name = models.CharField(
        max_length=100, verbose_name=_('name'), blank=True, default='',
        help_text=_('Optional name for searching contacts more easily. If not defined, use the name of the file.')
    )
    imported_by = models.ForeignKey(User, verbose_name=_('imported by'))
    encoding = models.CharField(max_length=50, default='utf-8', choices=ENCODINGS)
    separator = models.CharField(max_length=5, default=',', choices=SEPARATORS)
    entity_type = models.ForeignKey(
        EntityType, verbose_name=_('entity type'), blank=True, null=True, default=None,
        help_text=_('All created entities will get this type. Ignored if the entity already exist.')
    )
    groups = models.ManyToManyField(
        Group, verbose_name=_('groups'), blank=True, default=None,
        help_text=_('The created entities will be added to the selected groups.')
    )
    entity_name_from_email = models.BooleanField(
        verbose_name=_('generate entity name from email address'), default=True
    )

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('contact import')
        verbose_name_plural = _('contact imports')


@python_2_unicode_compatible
class MailtoSettings(models.Model):
    """make possible to send emails to actions contacts via mailto"""
    action_type = models.OneToOneField(ActionType, verbose_name=_("action type"))
    bcc = models.BooleanField(default=False, verbose_name=_("carbon copy"))
    subject = models.CharField(
        verbose_name=_("subject"), default="", max_length=100, blank=True, help_text=_("Use action subject if empty")
    )
    body_template = models.TextField(verbose_name=_("body template"), default="", blank=True)

    def __str__(self):
        return '{0}'.format(self.action_type)

    class Meta:
        verbose_name = _('Mailto settings')
        verbose_name_plural = _('Mailto settings')


@python_2_unicode_compatible
class ActionStatusTrack(models.Model):
    action = models.ForeignKey(Action)
    status = models.ForeignKey(ActionStatus)
    datetime = models.DateTimeField()

    def __str__(self):
        return '{0} / {1}'.format(self.action, self.status)

    class Meta:
        verbose_name = _('Action state track')
        verbose_name_plural = _('Action state tracks')
        ordering = ('-datetime', )