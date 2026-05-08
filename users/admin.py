from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "is_premium", "city", "created_at"]
    list_filter = ["is_premium", "is_staff", "is_active"]
    search_fields = ["email", "username", "phone"]
    ordering = ["-created_at"]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Manevi Rehber", {
            "fields": (
                "phone",
                "avatar",
                "is_premium",
                "premium_expires_at",
                "city",
                "country",
                "notifications_enabled",
                "location_enabled",
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Manevi Rehber", {
            "fields": (
                "phone",
                "email",
                "city",
                "country",
            )
        }),
    )
