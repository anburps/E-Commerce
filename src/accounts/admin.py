from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(profile)
class profileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    list_filter = ('user', 'phone_number')
    search_fields = ('user', 'phone_number')
    ordering = ('user',)

