# app/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import User

from app.models import Vendor, Product, Order, OrderItem, UserVendorRole
from app.serializers import (
    AssignRoleSerializer,
    VendorSerializer,
    ProductSerializer,
    OrderSerializer,
    UserVendorRoleSerializer,
)

def get_user_role(user, vendor):
    try:
        role = UserVendorRole.objects.get(user=user, vendor=vendor).role
        return role
    except UserVendorRole.DoesNotExist:
        return None

def is_owner(user, vendor):
    return get_user_role(user, vendor) == UserVendorRole.ROLE_OWNER

def is_staff(user, vendor):
    return get_user_role(user, vendor) == UserVendorRole.ROLE_STAFF

def is_customer(user, vendor):
    return get_user_role(user, vendor) == UserVendorRole.ROLE_CUSTOMER


class VendorListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vendor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()  

class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_vendor(self):
        return Vendor.objects.get(id=self.kwargs["vendor_id"])

    def get_queryset(self):
        vendor = self.get_vendor()
        return Product.objects.filter(vendor=vendor)

    def perform_create(self, serializer):
        vendor = self.get_vendor()
        user = self.request.user

        if not (is_owner(user, vendor) or is_staff(user, vendor)):
            raise PermissionError("You do not have permission to add products.")

        serializer.save(vendor=vendor) 


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_vendor(self):
        return Vendor.objects.get(id=self.kwargs["vendor_id"])

    def get_queryset(self):
        vendor = self.get_vendor()
        return Product.objects.filter(vendor=vendor)

    def perform_update(self, serializer):
        vendor = self.get_vendor()
        user = self.request.user

        if not (is_owner(user, vendor) or is_staff(user, vendor)):
            raise PermissionError("You cannot update this product.")

        serializer.save()

    def perform_destroy(self, instance):
        vendor = self.get_vendor()
        user = self.request.user

        if not is_owner(user, vendor):
            raise PermissionError("Only owner can delete products.")

        instance.delete()

class OrderListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_vendor(self):
        return Vendor.objects.get(id=self.kwargs["vendor_id"])

    def get_queryset(self):
        vendor = self.get_vendor()
        user = self.request.user
        role = get_user_role(user, vendor)

        if role in [UserVendorRole.ROLE_OWNER, UserVendorRole.ROLE_STAFF]:
            return Order.objects.filter(vendor=vendor)

        return Order.objects.filter(vendor=vendor, customer=user)

    def perform_create(self, serializer):
        vendor = self.get_vendor()
        user = self.request.user

        if not is_customer(user, vendor):
            raise PermissionError("Only customers can place orders.")

        serializer.save(customer=user)

class OrderDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_vendor(self):
        return Vendor.objects.get(id=self.kwargs["vendor_id"])

    def get_queryset(self):
        vendor = self.get_vendor()
        return Order.objects.filter(vendor=vendor)

    def perform_update(self, serializer):
        vendor = self.get_vendor()
        user = self.request.user

        if not (is_owner(user, vendor) or is_staff(user, vendor)):
            raise PermissionError("You cannot update this order.")

        serializer.save()

class AssignVendorRoleAPIView(generics.GenericAPIView):
    serializer_class = AssignRoleSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, vendor_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        role = serializer.validated_data["role"]

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            owner_role = UserVendorRole.objects.get(user=request.user, vendor=vendor).role
            if owner_role != UserVendorRole.ROLE_OWNER:
                return Response(
                    {"error": "Only vendor owner can assign roles"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except UserVendorRole.DoesNotExist:
            return Response(
                {"error": "You don't belong to this vendor"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        vendor_role, created = UserVendorRole.objects.update_or_create(
            user=target_user,
            vendor=vendor,
            defaults={"role": role}
        )

        return Response(
            {
                "message": "Role assigned successfully",
                "user": target_user.email,
                "vendor": vendor.store_name,
                "role": vendor_role.role,
            },
            status=status.HTTP_200_OK
        )
