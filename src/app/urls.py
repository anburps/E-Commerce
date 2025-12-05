from django.urls import path
from .views import *


urlpatterns = [
    # URLs for Vendors
    path("vendors/<int:pk>/", VendorDetailView.as_view(), name="vendor-detail"),

    # URLs for Products
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<pk>/", ProductDetailView.as_view(), name="product-detail"),

    # URLs for Orders
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<pk>/", OrderDetailView.as_view(), name="order-detail"),
]