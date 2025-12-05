from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Vendor, Product, Order, UserVendorRole
from .serializers import VendorSerializer, ProductSerializer, OrderSerializer
from .permissions import ProductPermission, OrderPermission, claim
from accounts.models import User



class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def patch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            content_text = {
                "message": "Only superusers can update vendors."
            }
            return Response(content_text, status=status.HTTP_403_FORBIDDEN)
        else:
            content_text = {
                "message": "Vendor updated successfully."
            }
            return Response(content_text, status=status.HTTP_200_OK)
    

# -------------------
# PRODUCT VIEWS
# -------------------

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(vendor__user=user)
    

    def post(self, request, *args, **kwargs):
        user = request.user
        if Vendor.objects.filter(vendor_users__user=user,vendor_users__role__in=["owner", "staff"]):
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                content_text = {
                    "message": "Product created successfully.",
                    "product": serializer.data,
                    "status": status.HTTP_201_CREATED
                }
                return Response(content_text)
            else:
                content_text = {
                    "message": "Product could not be created.",
                    "status": status.HTTP_400_BAD_REQUEST
                }
                return Response(content_text)
        else:
            content_text = {
                "message": "You are not authorized to create a product.",
                "status": status.HTTP_403_FORBIDDEN
            }
            return Response(content_text)
    
    def list(self, request, *args, **kwargs):
        user = request.user
        if Vendor.objects.filter(vendor_users__user=user,vendor_users__role__in=["owner", "staff"]):

            queryset = self.get_queryset()

            serializer = self.get_serializer(queryset, many=True)

            if serializer:
                content_text = {
                    "message": "Products retrieved successfully.",
                    "products": serializer.data,
                    "status": status.HTTP_200_OK
                }
                return Response(content_text)
            else:
                content_text = {
                    "message": "Products could not be retrieved.",
                    "status": status.HTTP_400_BAD_REQUEST
                }
                return Response(content_text)
        else:
            content_text = {
                "message": "You are not authorized to view products.",
                "status": status.HTTP_403_FORBIDDEN
            }
            return Response(content_text)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()  

    def get_vendor(self, user):
        return Vendor.objects.filter(
            vendor_users__user=user,
            vendor_users__role__in=["owner", "staff"]
        ).first()

    def patch(self, request, *args, **kwargs):
        user = request.user

        vendor = self.get_vendor(user)
        if not vendor:
            return Response({
                "message": "You are not authorized to update this product."
            }, status=status.HTTP_403_FORBIDDEN)

        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Product updated successfully.",
            "product": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user

        vendor = self.get_vendor(user)
        if not vendor:
            return Response({
                "message": "You are not authorized to delete this product."
            }, status=status.HTTP_403_FORBIDDEN)

        product = self.get_object()
        product.delete()

        return Response({
            "message": "Product deleted successfully.",
            "product": serializer.data
        }, status=status.HTTP_200_OK)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # 1. Identify vendor & user role vendor/customer
    def get_vendor_role(self, user):
        return UserVendorRole.objects.filter(
            user=user,
            vendor__user=user  # vendor belongs to main owner
        ).first()

    # 2. List Orders
    def list(self, request, *args, **kwargs):
        user = request.user

        role_obj = UserVendorRole.objects.filter(user=user).first()
        if not role_obj:
            return Response({
                "message": "Role not assigned.",
                "status": status.HTTP_403_FORBIDDEN
            })

        role = role_obj.role
        vendor = role_obj.vendor

        # Staff/Owner → list all vendor orders
        if role in ["owner", "staff"]:
            queryset = Order.objects.filter(vendor=vendor)

        # Customer → only their orders
        else:
            queryset = Order.objects.filter(customer=user)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "message": "Orders retrieved successfully.",
            "orders": serializer.data,
            "status": status.HTTP_200_OK
        })

    # 3. Create Order
    def post(self, request, *args, **kwargs):
        user = request.user

        role_obj = UserVendorRole.objects.filter(user=user).first()
        if not role_obj:
            return Response({
                "message": "Role not assigned.",
                "status": status.HTTP_403_FORBIDDEN
            })

        role = role_obj.role
        vendor = role_obj.vendor

        # Only customers can place order
        if role != "customer":
            return Response({
                "message": "Only customers can create an order.",
                "status": status.HTTP_403_FORBIDDEN
            })

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(
                vendor=vendor,
                customer=user
            )

            return Response({
                "message": "Order created successfully.",
                "order": serializer.data,
                "status": status.HTTP_201_CREATED
            })

        return Response({
            "message": "Order could not be created.",
            "status": status.HTTP_400_BAD_REQUEST
        })

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_vendor_role(self, user):
        return UserVendorRole.objects.filter(user=user).first()

    def get_queryset(self):
        user = self.request.user
        role_obj = self.get_vendor_role(user)

        role = role_obj.role
        vendor = role_obj.vendor

        if role in ["owner", "staff"]:
            return Order.objects.filter(vendor=vendor)

        return Order.objects.filter(customer=user)

    # 1. Update Order
    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        order = self.get_object()

        role_obj = self.get_vendor_role(user)
        role = role_obj.role

        # Customer update only their order, cannot change status
        if role == "customer":
            data = request.data.copy()
            data.pop("status", None)

            serializer = self.get_serializer(order, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({
                    "message": "Order updated successfully.",
                    "order": serializer.data,
                    "status": status.HTTP_200_OK
                })

            return Response({
                "message": "Order update failed.",
                "status": status.HTTP_400_BAD_REQUEST
            })

        # Vendor owner/staff can update full order including status
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Order updated successfully.",
            "order": serializer.data,
            "status": status.HTTP_200_OK
        })

    # 2. Delete / Cancel Order
    def delete(self, request, pk, *args, **kwargs):
        user = request.user
        order = self.get_object()

        role_obj = self.get_vendor_role(user)
        role = role_obj.role

        # Customer → convert to cancelled instead of deleting
        if role == "customer":
            order.status = Order.STATUS_CANCELLED
            order.save()
            return Response({
                "message": "Order cancelled successfully.",
                "status": status.HTTP_200_OK
            })

        # Vendor → full delete allowed
        order.delete()

        return Response({
            "message": "Order deleted successfully.",
            "status": status.HTTP_200_OK
        })
