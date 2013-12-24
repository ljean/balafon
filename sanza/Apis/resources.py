# -*- coding: utf-8 -*-

from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from sanza.Crm.models import Group, Contact

class ContactResource(ModelResource):
    fullname = fields.CharField('fullname', readonly=True)
    full_address = fields.CharField('get_full_address', readonly=True)
    phone = fields.CharField('get_phone', readonly=True)
    email = fields.CharField('email', readonly=True)
    
    class Meta:
        queryset = Contact.objects.all()
        resource_name = 'contact'
        fields = ['id']


class GroupResource(ModelResource):
    #contacts = fields.ManyToManyField(ContactResource, 'contacts', readonly=True)
    all_contacts = fields.ManyToManyField(ContactResource, 'all_contacts', readonly=True)
    
    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        fields = ['name', 'description']
        
    #def obj_get(self, bundle, **kwargs):
    #    print "obj_get", kwargs
    #    x = super(GroupResource, self).obj_get(bundle, **kwargs)
    #    print x, type(x)
    #    return x