# -*- coding: utf-8 -*-

from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from balafon.Crm.models import Group, Contact
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization


class ContactResource(ModelResource):
    fullname = fields.CharField('fullname', readonly=True)
    full_address = fields.CharField('get_full_address', readonly=True)
    phone = fields.CharField('get_phone', readonly=True)
    email = fields.CharField('get_email', readonly=True)
    
    class Meta:
        queryset = Contact.objects.all().order_by('lastname', 'firstname')
        resource_name = 'contact'
        fields = ['id', 'lastname', 'firstname']
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()


class GroupResource(ModelResource):
    #contacts = fields.ManyToManyField(ContactResource, 'contacts', readonly=True)
    all_contacts = fields.ManyToManyField(ContactResource, 'all_contacts', readonly=True)
    
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        fields = ['name', 'description']
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
        
    #def obj_get(self, bundle, **kwargs):
    #    print "obj_get", kwargs
    #    x = super(GroupResource, self).obj_get(bundle, **kwargs)
    #    print x, type(x)
    #    return x