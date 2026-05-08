from django.db import models
from users.models import User


class SubscriptionPlan(models.Model):
    """
    Subscription plans for Premium membership.
    """
    name = models.CharField(max_length=100)  # e.g., "Monthly", "Yearly"
    name_tr = models.CharField(max_length=100)  # Turkish name
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price in TRY
    currency = models.CharField(max_length=3, default="TRY")
    
    # Duration
    duration_days = models.IntegerField()  # e.g., 30 for monthly, 365 for yearly
    
    # Features
    features = models.JSONField(default=list)  # List of features
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "subscription_plans"
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ["price"]
    
    def __str__(self):
        return f"{self.name_tr} - {self.price} {self.currency}"


class Subscription(models.Model):
    """
    User's active subscription.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
        ("pending", "Pending"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    
    # Payment info
    payment_provider = models.CharField(max_length=50, blank=True)  # e.g., "stripe", "iyzico"
    payment_id = models.CharField(max_length=100, blank=True)  # External payment ID
    
    # Dates
    started_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "expires_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name_tr} - {self.status}"


class PaymentTransaction(models.Model):
    """
    Records all payment transactions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_transactions")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, related_name="transactions")
    
    TRANSACTION_TYPE_CHOICES = [
        ("payment", "Payment"),
        ("refund", "Refund"),
        ("cancel", "Cancel"),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="TRY")
    
    # Payment info
    payment_provider = models.CharField(max_length=50, blank=True)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=50, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "payment_transactions"
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["payment_id"]),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount} {self.currency}"
