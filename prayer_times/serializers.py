from rest_framework import serializers
from prayer_times.models import PrayerTimeCache, UserPrayerLocation


class PrayerTimeSerializer(serializers.ModelSerializer):
    """Serializer for Prayer Times"""
    
    class Meta:
        model = PrayerTimeCache
        fields = [
            "id",
            "city",
            "country",
            "date",
            "imsak",
            "gunes",
            "ogle",
            "ikindi",
            "aksam",
            "yatsi",
            "method",
        ]


class PrayerTimeDailySerializer(serializers.Serializer):
    """Serializer for daily prayer times response"""
    date = serializers.DateField()
    city = serializers.CharField()
    country = serializers.CharField()
    timings = serializers.DictField()
    next_prayer = serializers.CharField()
    time_to_next_prayer = serializers.CharField()


class UserPrayerLocationSerializer(serializers.ModelSerializer):
    """Serializer for User Prayer Location"""
    
    class Meta:
        model = UserPrayerLocation
        fields = [
            "id",
            "city",
            "country",
            "latitude",
            "longitude",
            "is_default",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
