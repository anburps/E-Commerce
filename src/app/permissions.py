from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import UserVendorRole


def claim(request, key):
    """read vendor_id / role from JWT token"""
    token = request.auth
    if not token:
        return None
    return token.get(key)


class ProductPermission(BasePermission):
    """
    - Owner + Staff → Full CRUD
    - Customer → Read-only
    """

    def has_permission(self, request, view):
        role = claim(request, "role")
        if not role:
            return False

        if request.method in SAFE_METHODS:
            return True

        return role in ["Store Owner", "Staff"]

    def has_object_permission(self, request, view, obj):
        vendor_id = claim(request, "vendor_id")
        role = claim(request, "role")

        if obj.vendor_id != vendor_id:
            return False

        if request.method in SAFE_METHODS:
            return True

        return role in ["Store Owner", "Staff"]


class OrderPermission(BasePermission):
    """
    - Owner + Staff: Can read/update vendor orders
    - Customer: Only own orders
    """

    def has_permission(self, request, view):
        return claim(request, "vendor_id") is not None

    def has_object_permission(self, request, view, obj):
        vendor_id = claim(request, "vendor_id")
        role = claim(request, "role")

        if vendor_id != obj.vendor_id:
            return False

        if role in ["Store Owner", "Staff"]:
            return True

        return obj.customer_id == request.user.id
