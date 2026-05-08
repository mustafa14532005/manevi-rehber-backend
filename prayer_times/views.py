from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from prayer_times.models import PrayerTimeCache, UserPrayerLocation
from prayer_times.serializers import (
    PrayerTimeSerializer,
    PrayerTimeDailySerializer,
    UserPrayerLocationSerializer,
)
from core.services import aladhan_service


class PrayerTimesBaseView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def _normalize_time(self, time_str: str) -> str:
        """Extract HH:MM from API time strings like '04:30 (+03)'"""
        if not time_str:
            return ""
        return time_str.strip().split(" ")[0]

    def _format_time_delta(self, delta: timedelta) -> str:
        """Format time delta as Turkish hours/minutes"""
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if hours > 0:
            return f"{hours} saat {minutes} dakika"
        return f"{minutes} dakika"

    def _get_next_prayer(self, timings: dict):
        """Calculate next prayer time based on local time"""
        now = timezone.localtime()
        today = now.date()

        prayers = [
            ("İmsak", timings.get("Fajr", "")),
            ("Güneş", timings.get("Sunrise", "")),
            ("Öğle", timings.get("Dhuhr", "")),
            ("İkindi", timings.get("Asr", "")),
            ("Akşam", timings.get("Maghrib", "")),
            ("Yatsı", timings.get("Isha", "")),
        ]

        for name, time_str in prayers:
            time_str = self._normalize_time(time_str)
            if not time_str:
                continue
            target_time = datetime.strptime(time_str, "%H:%M").time()
            target_dt = timezone.make_aware(datetime.combine(today, target_time))
            if target_dt > now:
                return name, self._format_time_delta(target_dt - now)

        # If all prayers passed, return İmsak for tomorrow
        first_time = self._normalize_time(prayers[0][1])
        if first_time:
            tomorrow = today + timedelta(days=1)
            target_time = datetime.strptime(first_time, "%H:%M").time()
            target_dt = timezone.make_aware(datetime.combine(tomorrow, target_time))
            return "İmsak", self._format_time_delta(target_dt - now)

        return "İmsak", ""


class PrayerTimesView(PrayerTimesBaseView):
    """
    Get today's prayer times for a city.
    GET /api/prayer-times/?city=Istanbul&country=Turkey
    """

    def get(self, request, *args, **kwargs):
        city = request.query_params.get("city", "Istanbul")
        country = request.query_params.get("country", "Turkey")
        date = request.query_params.get("date")
        
        # Fetch from external API
        data = aladhan_service.get_prayer_times_by_city(city, country, date)
        
        if not data:
            return Response(
                {"error": "Failed to fetch prayer times"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        
        # Save to cache
        today = timezone.now().date()
        timings = data["timings"]
        
        PrayerTimeCache.objects.update_or_create(
            city=city,
            country=country,
            date=today,
            defaults={
                "imsak": timings.get("Fajr", ""),
                "gunes": timings.get("Sunrise", ""),
                "ogle": timings.get("Dhuhr", ""),
                "ikindi": timings.get("Asr", ""),
                "aksam": timings.get("Maghrib", ""),
                "yatsi": timings.get("Isha", ""),
            }
        )
        
        # Get next prayer
        next_prayer, time_to_next = self._get_next_prayer(timings)
        
        return Response({
            "date": data["date"],
            "city": city,
            "country": country,
            "timings": {
                "İmsak": self._normalize_time(timings.get("Fajr")),
                "Güneş": self._normalize_time(timings.get("Sunrise")),
                "Öğle": self._normalize_time(timings.get("Dhuhr")),
                "İkindi": self._normalize_time(timings.get("Asr")),
                "Akşam": self._normalize_time(timings.get("Maghrib")),
                "Yatsı": self._normalize_time(timings.get("Isha")),
            },
            "next_prayer": next_prayer,
            "time_to_next_prayer": time_to_next,
        })


class PrayerTimesByCoordinatesView(PrayerTimesBaseView):
    """
    Get today's prayer times for coordinates.
    GET /api/prayer-times/coordinates/?latitude=41.0082&longitude=28.9784
    """

    def get(self, request, *args, **kwargs):
        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid latitude/longitude"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date = request.query_params.get("date")
        data = aladhan_service.get_prayer_times_by_coordinates(latitude, longitude, date)

        if not data:
            return Response(
                {"error": "Failed to fetch prayer times"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        timings = data["timings"]
        next_prayer, time_to_next = self._get_next_prayer(timings)

        return Response({
            "date": data["date"],
            "latitude": latitude,
            "longitude": longitude,
            "timings": {
                "İmsak": self._normalize_time(timings.get("Fajr")),
                "Güneş": self._normalize_time(timings.get("Sunrise")),
                "Öğle": self._normalize_time(timings.get("Dhuhr")),
                "İkindi": self._normalize_time(timings.get("Asr")),
                "Akşam": self._normalize_time(timings.get("Maghrib")),
                "Yatsı": self._normalize_time(timings.get("Isha")),
            },
            "next_prayer": next_prayer,
            "time_to_next_prayer": time_to_next,
        })


class PrayerTimesMonthlyView(generics.GenericAPIView):
    """
    Get monthly prayer times for a city.
    GET /api/prayer-times/monthly/?city=Istanbul&country=Turkey&month=4&year=2026
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        city = request.query_params.get("city", "Istanbul")
        country = request.query_params.get("country", "Turkey")
        month = request.query_params.get("month", timezone.now().month)
        year = request.query_params.get("year", timezone.now().year)
        
        try:
            response = aladhan_service.BASE_URL + "/calendarByCity"
            import requests
            res = requests.get(
                response,
                params={
                    "city": city,
                    "country": country,
                    "month": month,
                    "year": year,
                    "method": 2,
                },
                timeout=10,
            )
            data = res.json()
            
            if data["code"] == 200:
                return Response({
                    "month": data["data"][0]["date"]["month"]["en"],
                    "year": year,
                    "city": city,
                    "country": country,
                    "prayer_times": [
                        {
                            "date": d["date"]["readable"],
                            "timings": d["timings"],
                        }
                        for d in data["data"]
                    ],
                })
            else:
                return Response(
                    {"error": "Failed to fetch monthly prayer times"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class UserPrayerLocationView(generics.ListCreateAPIView):
    """
    Get/Create user's saved prayer locations.
    GET/POST /api/prayer-times/locations/
    """
    serializer_class = UserPrayerLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPrayerLocation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserPrayerLocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get/Update/Delete a specific prayer location.
    GET/PUT/DELETE /api/prayer-times/locations/<id>/
    """
    serializer_class = UserPrayerLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserPrayerLocation.objects.filter(user=self.request.user)


class QiblaDirectionView(generics.GenericAPIView):
    """
    Get Qibla direction for user's location.
    GET /api/prayer-times/qibla/?latitude=41.0082&longitude=28.9784
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        try:
            lat = float(request.query_params.get("latitude", 41.0082))
            lng = float(request.query_params.get("longitude", 28.9784))
            
            direction = aladhan_service.get_qibla_direction(lat, lng)
            
            if direction:
                return Response({
                    "latitude": lat,
                    "longitude": lng,
                    "qibla_direction": direction,
                })
            else:
                return Response(
                    {"error": "Failed to fetch Qibla direction"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
