# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from decimal import Decimal

from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import ugettext as _

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from balafon.settings import is_profile_installed
from balafon.Crm.models import Action, ActionType, Contact, Entity
from balafon.Profile.models import ContactProfile
from balafon.Store.models import (
    Favorite, SaleItem, StoreItem, StoreItemCategory, StoreItemTag, StoreManagementActionType, DeliveryPoint,
    SaleAnalysisCode, Voucher, PaymentMode
)
from balafon.Store import settings
from balafon.Store.api import serializers
from balafon.Store.settings import get_cart_type_name, get_cart_processed_callback, get_notify_cart_callback
from balafon.Store.utils import notify_cart_to_admin, confirm_cart_to_user


class CanAccessStorePermission(permissions.BasePermission):
    """Define who can access the store"""

    def has_permission(self, request, view):
        """check permission"""

        # Allow authenticated users
        if request.user.is_authenticated:
            return True

        # Allow anonymous user if settings
        return settings.is_public_api_allowed()


def get_public_api_permissions():
    """get public api permissions"""
    return [CanAccessStorePermission]


class SaleItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = SaleItem.objects.all()
    serializer_class = serializers.SaleItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ('PUT', 'POST'):
            return serializers.UpdateSaleItemSerializer
        else:
            return super(SaleItemViewSet, self).get_serializer_class(*args, **kwargs)

    def get_queryset(self):
        """returns objects"""
        action_id = self.kwargs['action_id']
        return self.queryset.filter(sale__action__id=action_id)


class StoreItemViewSet(viewsets.ModelViewSet):
    """returns sales items"""
    queryset = StoreItem.objects.filter(published=True)
    serializer_class = serializers.StoreItemSerializer
    permission_classes = get_public_api_permissions()

    def get_queryset(self):
        """returns objects"""
        contact = None
        if is_profile_installed():
            try:
                if self.request.user.is_authenticated:
                    profile = ContactProfile.objects.get(user=self.request.user)
                    contact = profile.contact
            except ContactProfile.DoesNotExist:
                pass

        if contact:
            # The contact exists : show items with a only_for_groups if contact is member of one of the groups
            self.queryset = self.queryset.filter(
                Q(only_for_groups=None) |
                Q(only_for_groups__contacts=contact) |
                Q(only_for_groups__entities=contact.entity)
            ).distinct()
        else:
            # The contact doesn't exist : Don't show items with a only_for_groups
            self.queryset = self.queryset.filter(only_for_groups=None)

        name = self.request.GET.get('name', None)
        if name:
            return self.queryset.filter(name__icontains=name)[:20]

        fullname = self.request.GET.get('fullname', None)
        if fullname:
            return self.queryset.filter(name__icontains=fullname)

        category = self.request.GET.get('category', None)
        if category:
            return self.queryset.filter(category=category)

        tag = self.request.GET.get('tag', None)
        if tag:
            return self.queryset.filter(tags=tag)

        ids = self.request.GET.get('ids', None)
        if ids is not None:
            int_ids = [int(id_) for id_ in ids.split(',') if id_.isdigit()]
            return self.queryset.filter(id__in=int_ids)

        return self.queryset.prefetch_related("tags")


class StoreItemCategoryViewSet(viewsets.ModelViewSet):
    """returns categories"""
    queryset = StoreItemCategory.objects.all()
    serializer_class = serializers.StoreItemCategorySerializer
    permission_classes = get_public_api_permissions()


class StoreItemTagViewSet(viewsets.ModelViewSet):
    """returns tags"""
    queryset = StoreItemTag.objects.all()
    serializer_class = serializers.StoreItemTagSerializer
    permission_classes = get_public_api_permissions()


class VoucherView(APIView):
    """post a cart"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """receive a new cart"""
        voucher_serializer = serializers.VoucherSerializer(data=request.data)
        voucher_serializer.is_valid(raise_exception=True)
        voucher_code = voucher_serializer.validated_data['voucher_code']
        voucher = Voucher.get_active_voucher(voucher_code)
        voucher_discount_vat_incl = 0
        for item in voucher_serializer.validated_data['items']:
            quantity = Decimal('{0}'.format(item['quantity']))
            try:
                store_item = StoreItem.objects.get(id=item['id'])
            except StoreItem.DoesNotExist:
                # ignore if not existing
                continue

            if voucher:
                discount = store_item.vat_incl_price() * voucher.rate / 100
                voucher_discount_vat_incl += quantity * discount

        discount_data = {
            'voucher_code': voucher_code,
            'label': voucher.label if voucher else '',
            'discount': voucher_discount_vat_incl,
        }
        return Response(discount_data)


class CartView(APIView):
    """post a cart"""
    permission_classes = (permissions.IsAuthenticated,)
    cart_serializer = None

    def get_buyer_contact(self):
        try:
            profile = ContactProfile.objects.get(user=self.request.user)
            return profile.contact
        except ContactProfile.DoesNotExist:
            raise Contact.DoesNotExist(_("You don't have a valid profile"))

    def get_serializer(self):
        return serializers.CartSerializer(data=self.request.data)

    def post(self, request):
        """receive a new cart"""

        cart_serializer = self.get_serializer()
        if cart_serializer.is_valid():
            self.cart_serializer = cart_serializer

            discounts = {}
            vat_rates = {}
            voucher_code = cart_serializer.validated_data.get('voucher_code', '')
            voucher = Voucher.get_active_voucher(voucher_code)

            try:
                contact = self.get_buyer_contact()
            except Contact.DoesNotExist as exc:
                return Response({'ok': False, 'message': exc})

            # Get Delivery point
            try:
                delivery_point = DeliveryPoint.objects.get(id=cart_serializer.validated_data["delivery_point"])
            except DeliveryPoint.DoesNotExist:
                return Response({'ok': False, 'message': _("Invalid delivery point")})

            # Get Payment mode
            payment_mode_id = cart_serializer.validated_data.get('payment_mode')
            if payment_mode_id:
                try:
                    payment_mode = PaymentMode.objects.get(id=payment_mode_id)
                except PaymentMode.DoesNotExist:
                    return Response({'ok': False, 'message': _("Invalid payment mode")})
            else:
                payment_mode = None

            # Create a new Sale
            action_type_name = get_cart_type_name()
            action_type = ActionType.objects.get_or_create(name=action_type_name)[0]

            # Force this type to be managed by the store
            StoreManagementActionType.objects.get_or_create(action_type=action_type)

            subject = detail = ''
            if 'notes' in cart_serializer.validated_data:
                notes = cart_serializer.validated_data["notes"].strip()
                if notes:
                    subject = _('Notes')
                    detail = notes

            action = Action.objects.create(
                planned_date=cart_serializer.validated_data['purchase_datetime'],
                subject=subject,
                detail=detail,
                status=action_type.default_status,
                status2=action_type.default_status2,
                type=action_type
            )
            action.contacts.add(contact)
            action.save()

            action.sale.analysis_code = SaleAnalysisCode.objects.get_or_create(name="Internet")[0]

            action.sale.delivery_point = delivery_point
            action.sale.payment_mode = payment_mode
            action.sale.save()

            warnings = []
            is_empty = True
            # for each line add a sale item
            counter = 0
            for index, item in enumerate(cart_serializer.validated_data['items']):

                quantity = Decimal('{0}'.format(item['quantity']))

                try:
                    store_item = StoreItem.objects.get(id=item['id'])
                except StoreItem.DoesNotExist:
                    # ignore if not existing
                    continue

                if not store_item.available:
                    warnings.append(
                        _("{0} is currently not available. It has been removed from your cart").format(
                            store_item.name
                        )
                    )
                else:
                    if store_item.stock_count is not None:
                        store_item.stock_count = store_item.stock_count - quantity
                        store_item.save()

                    is_empty = False
                    SaleItem.objects.create(
                        sale=action.sale,
                        quantity=quantity,
                        item=store_item,
                        vat_rate=store_item.vat_rate,
                        pre_tax_price=store_item.pre_tax_price,
                        text=store_item.name,
                        order_index=index + 1
                    )
                    counter = index

                    # calcule s'il y a une réduction Code Promo
                    # Crée une ligne réduction pour ce code
                    if voucher:
                        discount = store_item.pre_tax_price * voucher.rate / 100
                        vat_id = store_item.vat_rate.id if store_item.vat_rate else 0
                        if vat_id not in discounts:
                            vat_rates[vat_id] = store_item.vat_rate
                            discounts[vat_id] = 0
                        discounts[vat_id] += discount * quantity

            for discount_vat, discount_value in discounts.items():
                counter += 1
                SaleItem.objects.create(
                    sale=action.sale,
                    quantity=1,
                    item=None,
                    vat_rate=vat_rates[discount_vat],
                    pre_tax_price=-discount_value,
                    text=voucher.label,
                    order_index=counter,
                    is_discount=True
                )

            # Done
            if is_empty:
                action.delete()

                return Response({
                    'ok': False,
                    'message': _('Your cart is empty. Your articles are not available'),
                    'warnings': warnings,
                })
            else:

                action.sale.save()

                on_cart_processed = get_cart_processed_callback()
                if on_cart_processed:
                    on_cart_processed(action)

                notify_cart_callback = get_notify_cart_callback()
                if notify_cart_callback is None:
                    confirm_cart_to_user(contact, action)
                    notify_cart_to_admin(contact, action)
                else:
                    notify_cart_callback(contact, action)

                return Response({
                    'ok': True,
                    'action': action.id,
                    'warnings': warnings,
                    'deliveryDate': action.planned_date,
                    'deliveryPlace': action.sale.delivery_point.name,
                })
        else:
            return Response(
                {
                    'ok': False,
                    'message': ', '.join(['{0}: {1}'.format(*err) for err in cart_serializer.errors.items()])
                }
            )


class CartNoProfileView(CartView):
    """post a cart"""
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def create_contact(lastname, firstname, email, address, zip_code, city, address2='', address3=''):
        entity_name = lastname + '_' + firstname
        entity = Entity(name=entity_name, is_single_contact=True, type=None)
        entity.save()  # This creates a default contact
        contact = entity.default_contact
        contact.lastname = lastname
        contact.firstname = firstname
        contact.email = email
        contact.email_verified = False
        contact.address = address
        contact.address2 = address2
        contact.address3 = address3
        contact.zip_code = zip_code
        contact.city = city
        contact.save()
        return contact

    def get_buyer_contact(self):
        if not settings.allow_cart_no_profile():
            raise Http404
        contact_data = self.cart_serializer.validated_data.get('contact')
        contact = self.create_contact(**contact_data)
        return contact

    def get_serializer(self):
        return serializers.CartContactSerializer(data=self.request.data)


class ProfileAPIView(APIView):
    """base class"""

    def get_profile(self, request):
        """return a valid profile"""
        # Get Contact
        try:
            profile = ContactProfile.objects.get(user=request.user)
            if not profile.contact:
                raise PermissionDenied
            return profile

        except ContactProfile.DoesNotExist:
            raise PermissionDenied


class FavoriteView(ProfileAPIView):
    """manage favorite store items"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """receive a new list of favorites"""

        favorite_serializer = serializers.FavoriteSerializer(data=request.data)
        if favorite_serializer.is_valid():

            # Check that the user has a valid profile
            self.get_profile(request)

            items_ids = [item_['id'] for item_ in favorite_serializer.validated_data['items']]

            # Delete favorites which are not in the new list
            request.user.favorite_set.exclude(id__in=items_ids).delete()

            # create new favorite
            for item_id in items_ids:
                try:
                    item = StoreItem.objects.get(id=item_id)
                except StoreItem.DoesNotExist:
                    item = None
                if item:
                    Favorite.objects.get_or_create(
                        user=request.user,
                        item=item
                    )

            return Response({'ok': True})
        else:
            return Response(
                {
                    'ok': False,
                    'message': ', '.join(['{0}: {1}'.format(*err) for err in favorite_serializer.errors.items()])
                }
            )

    def get(self, request):
        """return a new list of favorites"""

        # Check that the user has a valid profile
        self.get_profile(request)

        favorites = self.request.user.favorite_set.all()
        favorites_serializer = serializers.FavoriteItemSerializer(
            [fav.item for fav in favorites if fav.item.published],
            many=True
        )
        return Response({'favorites': favorites_serializer.data})


class LastSalesView(ProfileAPIView):
    """view last sales"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """return a last items bought by the user"""

        # Check that the user has a valid profile
        profile = self.get_profile(request)

        sale_items = SaleItem.objects.filter(
            sale__action__contacts=profile.contact
        ).order_by('-sale__action__planned_date', 'item__name')

        # Avoid duplicates
        already_in = set()
        store_items = []
        for sale_item in sale_items:
            if sale_item.item and sale_item.item.published and sale_item.item.id not in already_in:
                already_in.add(sale_item.item.id)
                store_items.append(sale_item.item)

        last_sales_serializer = serializers.StoreItemSerializer(store_items, many=True)

        return Response(last_sales_serializer.data)
