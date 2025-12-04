from django.contrib import admin
from .models import *

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'domain', 'subdomain')
    list_filter = ('name', 'contact_email', 'domain', 'subdomain')
    search_fields = ('name', 'contact_email', 'domain', 'subdomain')
    ordering = ('name',)

@admin.register(UserVendorRole)
class UserVendorRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor', 'role')
    list_filter = ('user', 'vendor', 'role')
    search_fields = ('user', 'vendor', 'role')
    ordering = ('user', 'vendor', 'role')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'name', 'description', 'price', 'stock', 'is_active')
    list_filter = ('vendor', 'name', 'description', 'price', 'stock', 'is_active')
    search_fields = ('vendor', 'name', 'description', 'price', 'stock', 'is_active')
    ordering = ('vendor', 'name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'vendor', 'status', 'total_amount', 'created_at')
    list_filter = ('customer', 'vendor', 'status', 'total_amount', 'created_at')
    search_fields = ('customer', 'vendor', 'status', 'total_amount', 'created_at')
    ordering = ('customer', 'vendor', 'status', 'total_amount', 'created_at')   

@admin.register(OrderItem)    
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order', 'product', 'quantity', 'price')
    search_fields = ('order', 'product', 'quantity', 'price')
    ordering = ('order', 'product', 'quantity', 'price')

