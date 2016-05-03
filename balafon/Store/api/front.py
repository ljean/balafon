# -*- coding: utf-8 -*-
"""REST api powered by django-rest-framework"""

from decimal import Decimal

from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from balafon.Crm.models import Action, ActionType
from balafon.Profile.models import ContactProfile
from balafon.Store.models import (
    Favorite, SaleItem, StoreItem, StoreItemCategory, StoreItemTag, StoreManagementActionType, DeliveryPoint,
    SaleAnalysisCode
)
from balafon.Store import settings
from balafon.Store.api import serializers
from balafon.Store.settings import get_cart_type_name
from balafon.Store.utils import notify_cart_to_admin, confirm_cart_to_user


def get_public_api_permissions():
    """get public api permissions"""
    if settings.is_public_api_allowed():
        return [permissions.IsAuthenticatedOrReadOnly]
    else:
        return [permissions.IsAuthenticated]


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
    queryset = StoreItem.objects.all()
    serializer_class = serializers.StoreItemSerializer
    permission_classes = get_public_api_permissions()

    def get_queryset(self):
        """returns objects"""
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


class CartView(APIView):
    """post a cart"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """receive a new cart"""

        cart_serializer = serializers.CartSerializer(data=request.data)
        if cart_serializer.is_valid():

            # Get Contact
            try:
                profile = ContactProfile.objects.get(user=request.user)
                contact = profile.contact
            except ContactProfile.DoesNotExist:
                return Response({'ok': False, 'message': _(u"You don't have a valid profile")})

            # Get Delivery point
            try:
                delivery_point = DeliveryPoint.objects.get(id=cart_serializer.validated_data["delivery_point"])
            except DeliveryPoint.DoesNotExist:
                return Response({'ok': False, 'message': _(u"Invalid delivery point")})

            # Create a new Sale
            action_type_name = get_cart_type_name()
            action_type = ActionType.objects.get_or_create(name=action_type_name)[0]

            # Force this type to be managed by the store
            StoreManagementActionType.objects.get_or_create(action_type=action_type)

            subject = detail = ''
            if 'notes' in cart_serializer.validated_data:
                notes = cart_serializer.validated_data["notes"].strip()
                if notes:
                    subject = _(u'Notes')
                    detail = notes

            action = Action.objects.create(
                planned_date=cart_serializer.validated_data['purchase_datetime'],
                subject=subject,
                detail=detail,
                status=action_type.default_status,
                type=action_type
            )
            action.contacts.add(contact)
            action.save()

            action.sale.analysis_code = SaleAnalysisCode.objects.get_or_create(name=u"Internet")[0]

            action.sale.delivery_point = delivery_point
            action.sale.save()

            warnings = []
            is_empty = True
            # for each line add a sale item
            for index, item in enumerate(cart_serializer.validated_data['items']):

                quantity = Decimal(u'{0}'.format(item['quantity']))

                try:
                    store_item = StoreItem.objects.get(id=item['id'])
                except StoreItem.DoesNotExist:
                    # ignore if not existing
                    continue

                if not store_item.available:
                    warnings.append(
                        _(u"{0} is currently not available. It has been removed from your cart").format(
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
                        order_index=index+1
                    )

            #Done
            if is_empty:
                action.delete()

                return Response({
                    'ok': False,
                    'message': _(u'Your cart is empty. Your articles are not available'),
                    'warnings': warnings,
                })
            else:

                action.sale.save()

                confirm_cart_to_user(profile, action)
                notify_cart_to_admin(profile, action)

                return Response({
                    'ok': True,
                    'warnings': warnings,
                    'deliveryDate': action.planned_date,
                    'deliveryPlace': action.sale.delivery_point.name,
                })
        else:
            return Response(
                {
                    'ok': False,
                    'message': u', '.join([u'{0}: {1}'.format(*err) for err in cart_serializer.errors.items()])
                }
            )


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
                    'message': u', '.join([u'{0}: {1}'.format(*err) for err in favorite_serializer.errors.items()])
                }
            )

    def get(self, request):
        """return a new list of favorites"""

        # Check that the user has a valid profile
        self.get_profile(request)

        favorites = self.request.user.favorite_set.all()
        favorites_serializer = serializers.FavoriteItemSerializer([fav.item for fav in favorites], many=True)
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
            if sale_item.item and sale_item.item.id not in already_in:
                already_in.add(sale_item.item.id)
                store_items.append(sale_item.item)

        last_sales_serializer = serializers.StoreItemSerializer(store_items, many=True)

        return Response(last_sales_serializer.data)
