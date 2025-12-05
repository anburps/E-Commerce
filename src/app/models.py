from django.db import models
from accounts.models import User
# app/models.py

class Vendor(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_vendors')  
    store_name  = models.CharField(max_length=255)
    domain      = models.CharField(max_length=255, blank=True, null=True)
    subdomain   = models.CharField(max_length=255, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name


class UserVendorRole(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_STAFF = 'staff'
    ROLE_CUSTOMER = 'customer'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Store Owner'),
        (ROLE_STAFF, 'Staff'),
        (ROLE_CUSTOMER, 'Customer'),
    ]

    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_roles')
    vendor  = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='roles')
    role    = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'vendor')

    def __str__(self):
        return f"{self.user.email} → {self.vendor.store_name} ({self.role})"


class Product(models.Model):
    vendor      = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'name')

    def __str__(self):
        return f"{self.vendor.store_name} - {self.name}"

class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    customer        = models.ForeignKey( User, on_delete=models.CASCADE, related_name='orders' )
    vendor          = models.ForeignKey( Vendor, on_delete=models.CASCADE, related_name='orders' )
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_amount    = models.DecimalField(max_digits=10, decimal_places=2)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.vendor.store_name}"

class OrderItem(models.Model):
    order       = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product     = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity    = models.PositiveIntegerField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
