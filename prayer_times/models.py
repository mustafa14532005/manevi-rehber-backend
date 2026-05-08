from django.db import models
from users.models import User


class PrayerTimeCache(models.Model):
    """
    Caches prayer times from Aladhan API to reduce external API calls.
    Stores daily prayer times for each city.
    """
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Türkiye")
    date = models.DateField()
    
    # Prayer times
    imsak = models.CharField(max_length=10, blank=True)  # Fajr
    gunes = models.CharField(max_length=10, blank=True)  # Sunrise
    ogle = models.CharField(max_length=10, blank=True)  # Dhuhr
    ikindi = models.CharField(max_length=10, blank=True)  # Asr
    aksam = models.CharField(max_length=10, blank=True)  # Maghrib
    yatsi = models.CharField(max_length=10, blank=True)  # Isha
    
    # Metadata
    method = models.IntegerField(default=2)  # Diyanet İşleri Başkanlığı
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "prayer_time_caches"
        verbose_name = "Prayer Time Cache"
        verbose_name_plural = "Prayer Time Caches"
        unique_together = ["city", "country", "date"]
        indexes = [
            models.Index(fields=["city", "date"]),
            models.Index(fields=["date"]),
        ]
    
    def __str__(self):
        return f"{self.city} - {self.date}"
    
    @classmethod
    def get_today_prayer_times(cls, city: str, country: str = "Türkiye"):
        """Get today's prayer times for a city"""
        from django.utils import timezone
        today = timezone.now().date()
        return cls.objects.filter(
            city=city,
            country=country,
            date=today
        ).first()


class UserPrayerLocation(models.Model):
    """
    Stores user's saved prayer location (city/country or coordinates).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prayer_locations")
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Türkiye")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "user_prayer_locations"
        verbose_name = "User Prayer Location"
        verbose_name_plural = "User Prayer Locations"
    
    def __str__(self):
        return f"{self.user.email} - {self.city}"
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset other defaults for this user
        if self.is_default:
            UserPrayerLocation.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
