from django.contrib import admin
from prayer_times.models import PrayerTimeCache, UserPrayerLocation


@admin.register(PrayerTimeCache)
class PrayerTimeCacheAdmin(admin.ModelAdmin):
    list_display = ["city", "country", "date", "ogle", "ikindi", "aksam"]
    list_filter = ["city", "country", "date"]
    search_fields = ["city", "country"]
    ordering = ["-date", "city"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Location", {
            "fields": ("city", "country", "date")
        }),
        ("Prayer Times", {
            "fields": (
                "imsak",
                "gunes",
                "ogle",
                "ikindi",
                "aksam",
                "yatsi",
            )
        }),
        ("Metadata", {
            "fields": ("method", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(UserPrayerLocation)
class UserPrayerLocationAdmin(admin.ModelAdmin):
    list_display = ["user", "city", "country", "is_default", "created_at"]
    list_filter = ["country", "is_default"]
    search_fields = ["user__email", "city"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]
