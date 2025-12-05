from django.db import models
from accounts.models import User

# The Vendor model represents a store or business that sells products.

class Vendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors',null=True,blank=False)
    domain = models.CharField(max_length=255, blank=True, null=True)
    subdomain = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name

# The UserVendorRole model represents the relationship between a user and a store or business.
class UserVendorRole(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_STAFF = 'staff'
    ROLE_CUSTOMER = 'customer'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Store Owner'),
        (ROLE_STAFF, 'Staff'),
        (ROLE_CUSTOMER, 'Customer'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_roles')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    class Meta:
        unique_together = ('user', 'vendor') 

    def __str__(self):
        return f"{self.user.email} - {self.vendor} ({self.role})"

# The Product model represents a product that is sold by a store or business.
class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vendor', 'name')

    def __str__(self):
        return f"{self.vendor} - {self.name}"

# The Order model represents an order placed by a customer for a product sold by a store or business.

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
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='orders')
    status  = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id}- {self.vendor.name}"

# The OrderItem model represents an item in an order

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.price}"