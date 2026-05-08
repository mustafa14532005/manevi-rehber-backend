from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model for Manevi Rehber app.
    Phone number is used as the primary identifier for authentication.
    """
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    
    # Premium status
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(blank=True, null=True)
    
    # Preferences
    city = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="Türkiye")
    notifications_enabled = models.BooleanField(default=True)
    location_enabled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.email or self.phone or self.username
    
    @property
    def is_premium_active(self) -> bool:
        """Check if premium subscription is still active"""
        if not self.is_premium or not self.premium_expires_at:
            return False
        from django.utils import timezone
        return timezone.now() < self.premium_expires_at
