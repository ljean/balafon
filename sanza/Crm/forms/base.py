# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms
from form_utils.forms import BetterModelForm, BetterForm

from coop_cms.bs_forms import BootstrapableMixin

from sanza.Crm import models
from sanza.Crm.widgets import CityAutoComplete
from sanza.Crm.utils import get_default_country


class BetterBsForm(BetterForm, BootstrapableMixin):
    """Base class inherit from Bootstrap and form-utils BetterForm"""

    class Media:
        """Media files"""
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )

    def __init__(self, *args, **kwargs):
        super(BetterBsForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()
        for field in self.fields.values():
            if field.widget.__class__.__name__ == forms.Select().__class__.__name__:
                klass = field.widget.attrs.get("class", "")
                if not "chosen-select" in klass:
                    field.widget.attrs["class"] = klass + " chosen-select"


class BetterBsModelForm(BetterModelForm, BootstrapableMixin):
    """Base class inherit from Bootstrap and form-utils BetterModelForm"""

    class Media:
        """Media files"""
        css = {
            'all': ('chosen/chosen.css',)
        }
        js = (
            'chosen/chosen.jquery.js',
        )

    def __init__(self, *args, **kwargs):
        super(BetterBsModelForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()
        for field in self.fields.values():
            if field.widget.__class__.__name__ == forms.Select().__class__.__name__:
                css_class = field.widget.attrs.get("class", "")
                if not "chosen-select" in css_class:
                    field.widget.attrs["class"] = css_class + " chosen-select"


class _CityBasedForm(object):
    """Base class for form with a City field"""

    def __init__(self, *args, **kwargs):
        self.country_id = 0

    def _get_city_parent(self, city):
        """get city parent"""
        parent = city.parent
        while parent:
            country = parent
            parent = parent.parent
        return country

    def _post_init(self, *args, **kwargs):
        """must be called at the end of __init__ of the subclasses"""
        self.country_id = 0
        if len(args):
            try:
                self.country_id = int(args[0]["country"])
            except KeyError:
                pass
        if not self.country_id:
            self.country_id = get_default_country().id

        self.fields['city'].widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})

        zones_choices = [(z.id, z.name) for z in models.Zone.objects.filter(parent__isnull=True).order_by('name')]
        self.fields['country'].choices = [(0, '')] + zones_choices

        try:
            city = getattr(kwargs.get('instance'), 'city', 0)
            if city:
                self.fields['country'].initial = self._get_city_parent(city).id
        except models.City.DoesNotExist:
            pass

    def _get_country(self, country_id):
        """get the country"""
        if country_id:
            return models.Zone.objects.get(id=country_id, parent__isnull=True, type__type="country")
        else:
            return get_default_country()

    def clean_city(self):
        """city validation"""
        city = self.cleaned_data['city']
        if isinstance(city, models.City):
            return city
        else:
            try:
                if not city:
                    return None
                try:
                    city_id = int(city)
                    return models.City.objects.get(id=city_id)
                except (ValueError, TypeError):
                    pass

                zip_code = self.cleaned_data['zip_code']

                try:
                    country_id = int(self.cleaned_data.get('country')) or self.country_id
                except (ValueError, TypeError):
                    country_id = self.country_id

                country = self._get_country(country_id)
                default_country = get_default_country()

                if country != default_country:
                    city = models.City.objects.get_or_create(name=city, parent=country)[0]
                else:
                    if len(zip_code) < 2:
                        raise ValidationError(ugettext(u'You must enter a valid zip code for selecting a new city'))
                    dep = models.Zone.objects.get(code=zip_code[:2])
                    city = models.City.objects.get_or_create(name=city, parent=dep)[0]
                return city
            except ValidationError:
                raise
            except Exception, msg:
                raise ValidationError(msg)


class ModelFormWithCity(BetterBsModelForm, _CityBasedForm):
    """ModelForm with city"""
    city = forms.CharField(
        required=False,
        label=_(u'City'),
        widget=CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    country = forms.ChoiceField(required=False, label=_(u'Country'))

    def __init__(self, *args, **kwargs):
        super(ModelFormWithCity, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)


class FormWithCity(BetterBsForm, _CityBasedForm):
    """Form with city"""

    country = forms.ChoiceField(required=False, label=_(u'Country'))
    zip_code = forms.CharField(required=False, label=_(u'zip code'))
    city = forms.CharField(required=False, label=_(u'City'))

    def __init__(self, *args, **kwargs):
        super(FormWithCity, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)


class ModelFormWithAddress(ModelFormWithCity):
    """ModelForm with address"""

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            prefix = u" ".join([
                instance.street_number,
                instance.street_type.name if instance.street_type else '',
            ]).strip()
            instance.address = instance.address.replace(prefix, '', 1).strip()
        super(ModelFormWithAddress, self).__init__(*args, **kwargs)
        if not models.StreetType.objects.count():
            self.fields['street_number'].widget = forms.HiddenInput()
            self.fields['street_type'].widget = forms.HiddenInput()

    def clean_address(self):
        """add street type and number to the address"""
        street_number = self.cleaned_data['street_number']
        street_type = self.cleaned_data['street_type']
        address = self.cleaned_data['address']
        if street_number or street_type:
            return u" ".join([street_number, street_type.name if street_type else '', address]).strip()
        return address

