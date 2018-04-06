# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms.forms import BoundField
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms.__future__ as forms

from coop_cms.bs_forms import BootstrapableMixin

from balafon.Crm import models
from balafon.Crm.widgets import CityAutoComplete
from balafon.Crm.utils import get_default_country


class Fieldset(object):

    def __init__(self, name, fields, legend, classes):
        self.name = name
        self.fields = fields
        self.legend = legend
        self.classes = classes

    def __iter__(self):
        for field in self.fields:
            yield field


class FormWithFieldsetMixin(object):

    def get_fieldsets(self):
        """return the list of fieldsets"""
        return self.Meta.fieldsets

    @property
    def fieldsets(self):
        for fieldset_name, fieldset_attrs in self.get_fieldsets():

            fields = []
            for field_name in fieldset_attrs.get('fields', None) or []:
                if field_name in self.fields:
                    fields.append(
                        BoundField(self, self.fields[field_name], field_name)
                    )

            yield Fieldset(
                fieldset_name,
                fields=fields,
                legend=fieldset_attrs.get('legend', ''),
                classes=fieldset_attrs.get('classes', ''),
            )


class BsPopupForm(forms.Form, BootstrapableMixin):
    def __init__(self, *args, **kwargs):
        super(BsPopupForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()


class BetterBsForm(forms.Form, BootstrapableMixin):
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
                field_class = field.widget.attrs.get("class", "")
                if not "chosen-select" in field_class:
                    field.widget.attrs["class"] = field_class + " chosen-select"


class BsPopupModelForm(forms.ModelForm, BootstrapableMixin):  # (BetterModelForm):
    """Base class inherit from Bootstrap and form-utils BetterModelForm"""

    def __init__(self, *args, **kwargs):
        super(BsPopupModelForm, self).__init__(*args, **kwargs)
        self._bs_patch_field_class()


class BetterBsModelForm(forms.ModelForm, BootstrapableMixin):  # (BetterModelForm):
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
                if "chosen-select" not in css_class:
                    field.widget.attrs["class"] = css_class + " chosen-select"


class _CityBasedForm(object):
    """Base class for form with a City field"""

    def __init__(self, *args, **kwargs):
        self.country_id = 0

    def _get_city_parent(self, city):
        """get city parent"""
        parent = city.parent
        country = None
        while parent:
            country = parent
            parent = parent.parent
        return country

    def _manage_country_field(self, field_prefix, *args, **kwargs):
        """"""
        setattr(self, field_prefix + 'country_id', 0)
        if len(args):
            try:
                setattr(self, field_prefix + 'country_id', int(args[0][field_prefix + "country"]))
            except (KeyError, ValueError):
                pass
        if not getattr(self, field_prefix + 'country_id', 0):
            setattr(self, field_prefix + 'country_id', get_default_country().id)

        self.fields[field_prefix + 'city'].widget = CityAutoComplete(
            attrs={'placeholder': _('Enter a city'), 'size': '80'}
        )

        zones_choices = [
            (zone.id, zone.name) for zone in models.Zone.objects.filter(parent__isnull=True).order_by('name')
        ]
        self.fields[field_prefix + 'country'].choices = [(0, '')] + zones_choices

        try:
            city = getattr(kwargs.get('instance'), field_prefix + 'city', 0)
            if city:
                city_parent = self._get_city_parent(city)
                if city_parent:
                    self.fields[field_prefix + 'country'].initial = city_parent.id
        except models.City.DoesNotExist:
            pass

    def _post_init(self, *args, **kwargs):
        """must be called at the end of __init__ of the subclasses"""
        self._manage_country_field('', *args, **kwargs)

    def _get_country(self, country_id):
        """get the country"""
        if country_id:
            return models.Zone.objects.get(id=country_id, parent__isnull=True, type__type="country")
        else:
            return get_default_country()

    def _clean_city_field(self, field_prefix):
        """city validation"""
        city = self.cleaned_data[field_prefix + 'city']
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

                zip_code = self.cleaned_data[field_prefix + 'zip_code']

                try:
                    country_id = int(self.cleaned_data.get(field_prefix + 'country')) \
                        or getattr(self, field_prefix + 'country_id')
                except (ValueError, TypeError):
                    country_id = getattr(self, field_prefix + 'country_id')

                country = self._get_country(country_id)
                default_country = get_default_country()

                if country != default_country:
                    city = models.City.objects.get_or_create(name=city, parent=country)[0]
                else:
                    if len(zip_code) < 2:
                        raise ValidationError(ugettext('You must enter a valid zip code for selecting a new city'))
                    dep = models.Zone.objects.get(code=zip_code[:2])
                    city = models.City.objects.get_or_create(name=city, parent=dep)[0]
                return city
            except ValidationError:
                raise
            except Exception as msg:
                raise ValidationError(msg)

    def clean_city(self):
        """city validation"""
        return self._clean_city_field('')


class ModelFormWithCity(BetterBsModelForm, _CityBasedForm):
    """ModelForm with city"""
    city = forms.CharField(
        required=False,
        label=_('City'),
        widget=CityAutoComplete(attrs={'placeholder': _('Enter a city'), 'size': '80'})
    )
    country = forms.ChoiceField(required=False, label=_('Country'))

    def __init__(self, *args, **kwargs):
        super(ModelFormWithCity, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)


class FormWithCity(BetterBsForm, _CityBasedForm):
    """Form with city"""

    country = forms.ChoiceField(required=False, label=_('Country'))
    zip_code = forms.CharField(required=False, label=_('zip code'))
    city = forms.CharField(required=False, label=_('City'))

    def __init__(self, *args, **kwargs):
        super(FormWithCity, self).__init__(*args, **kwargs)
        self._post_init(*args, **kwargs)


class BillingModelFormWithCity(ModelFormWithCity):
    """ModelForm with city"""
    billing_city = forms.CharField(
        required=False,
        label=_('City'),
        widget=CityAutoComplete(attrs={'placeholder': _('Enter a city'), 'size': '80'})
    )
    billing_country = forms.ChoiceField(required=False, label=_('Country'))

    def __init__(self, *args, **kwargs):
        super(BillingModelFormWithCity, self).__init__(*args, **kwargs)

    def _post_init(self, *args, **kwargs):
        """called at the end of __init__ of the parent class"""
        super(BillingModelFormWithCity, self)._post_init(*args, **kwargs)
        self._manage_country_field('billing_', *args, **kwargs)

    def clean_billing_city(self):
        """city validation"""
        return self._clean_city_field('billing_')


class ModelFormWithAddress(BillingModelFormWithCity):
    """ModelForm with address"""

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            prefix = " ".join([
                instance.street_number,
                instance.street_type.name if instance.street_type else '',
            ]).strip()
            instance.address = instance.address.replace(prefix, '', 1).strip()

            billing_prefix = " ".join([
                instance.billing_street_number,
                instance.billing_street_type.name if instance.billing_street_type else '',
            ]).strip()
            instance.billing_address = instance.billing_address.replace(billing_prefix, '', 1).strip()

        super(ModelFormWithAddress, self).__init__(*args, **kwargs)

        if not models.StreetType.objects.count():
            self.fields['street_number'].widget = forms.HiddenInput()
            self.fields['street_type'].widget = forms.HiddenInput()
            self.fields['billing_street_number'].widget = forms.HiddenInput()
            self.fields['billing_street_type'].widget = forms.HiddenInput()

    def clean_address(self):
        """add street type and number to the address"""
        street_number = self.cleaned_data['street_number']
        street_type = self.cleaned_data['street_type']
        address = self.cleaned_data['address']
        if street_number or street_type:
            return " ".join([street_number, street_type.name if street_type else '', address]).strip()
        return address

    def clean_billing_address(self):
        """add street type and number to the address"""
        billing_street_number = self.cleaned_data['billing_street_number']
        billing_street_type = self.cleaned_data['billing_street_type']
        billing_address = self.cleaned_data['billing_address']
        if billing_street_number or billing_street_type:
            return " ".join(
                [billing_street_number, billing_street_type.name if billing_street_type else '', billing_address]
            ).strip()
        return billing_address
