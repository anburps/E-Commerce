from django.urls import path
from app.views import (
    VendorListCreateAPIView,

    ProductListCreateAPIView,
    ProductDetailAPIView,

    OrderListCreateAPIView,
    OrderDetailAPIView,

    AssignVendorRoleAPIView,
)


urlpatterns = [

    path('vendors/', VendorListCreateAPIView.as_view(), name='vendor-list-create'),

    path('vendors/<int:vendor_id>/products/',ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('vendors/<int:vendor_id>/products/<int:pk>/',ProductDetailAPIView.as_view(),name='product-detail' ),

    path('vendors/<int:vendor_id>/orders/',OrderListCreateAPIView.as_view(),name='order-list-create' ),
    path('vendors/<int:vendor_id>/orders/<int:pk>/',OrderDetailAPIView.as_view(),name='order-detail' ),

    path('vendors/<int:vendor_id>/',AssignVendorRoleAPIView.as_view(),name='assign-vendor-role' ),

]
