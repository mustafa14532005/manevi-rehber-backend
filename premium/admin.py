from django.contrib import admin
from premium.models import SubscriptionPlan, Subscription, PaymentTransaction


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name_tr", "price", "currency", "duration_days", "is_active"]
    list_filter = ["is_active", "currency"]
    search_fields = ["name", "name_tr"]
    ordering = ["price"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Plan Info", {
            "fields": ("name", "name_tr", "is_active")
        }),
        ("Pricing", {
            "fields": ("price", "currency", "duration_days")
        }),
        ("Features", {
            "fields": ("features",),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "started_at", "expires_at"]
    list_filter = ["status", "plan"]
    search_fields = ["user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Subscription Info", {
            "fields": ("user", "plan", "status")
        }),
        ("Dates", {
            "fields": ("started_at", "expires_at", "cancelled_at")
        }),
        ("Payment", {
            "fields": ("payment_provider", "payment_id"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "transaction_type", "amount", "currency", "payment_status", "created_at"]
    list_filter = ["transaction_type", "payment_status"]
    search_fields = ["user__email", "payment_id"]
    ordering = ["-created_at"]
    readonly_fields = ["all_fields"]
    
    def all_fields(self, obj):
        return ", ".join([f.name for f in obj._meta.fields])
    all_fields.short_description = "All Fields"
