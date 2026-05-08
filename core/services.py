"""
External API Services for Manevi Rehber.

Services:
- Aladhan API: Prayer times
- Quran.com API: Quran verses
- Hadith API: Hadith collections
"""

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AladhanService:
    """
    Service for Aladhan Prayer Times API.
    Docs: https://aladhan.com/prayer-times-api
    """
    BASE_URL = settings.ALADHAN_BASE_URL
    CACHE_TIMEOUT = 86400  # 24 hours
    
    @classmethod
    def get_prayer_times_by_city(cls, city: str, country: str, date: str = None):
        """
        Get prayer times for a city on a specific date.
        
        Args:
            city: City name
            country: Country name
            date: Date in DD-MM-YYYY format (default: today)
        
        Returns:
            dict: Prayer times data
        """
        if not date:
            date = datetime.now().strftime("%d-%m-%Y")
        
        cache_key = f"prayer_times_{city}_{country}_{date}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/timingsByCity",
                params={
                    "city": city,
                    "country": country,
                    "date": date,
                    "method": 2,  # Diyanet İşleri Başkanlığı
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            if data["code"] == 200:
                result = {
                    "date": data["data"]["date"]["readable"],
                    "timings": data["data"]["timings"],
                    "meta": data["data"]["meta"],
                }
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
                return result
            else:
                logger.error(f"Aladhan API error: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Aladhan API request failed: {e}")
            return None
    
    @classmethod
    def get_prayer_times_by_coordinates(cls, latitude: float, longitude: float, date: str = None):
        """
        Get prayer times by GPS coordinates.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            date: Date in DD-MM-YYYY format (default: today)
        
        Returns:
            dict: Prayer times data
        """
        if not date:
            date = datetime.now().strftime("%d-%m-%Y")
        
        cache_key = f"prayer_times_{latitude}_{longitude}_{date}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/timings",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "date": date,
                    "method": 2,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            if data["code"] == 200:
                result = {
                    "date": data["data"]["date"]["readable"],
                    "timings": data["data"]["timings"],
                    "meta": data["data"]["meta"],
                }
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
                return result
            else:
                logger.error(f"Aladhan API error: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Aladhan API request failed: {e}")
            return None
    
    @classmethod
    def get_qibla_direction(cls, latitude: float, longitude: float):
        """
        Get Qibla direction from a location.
        
        Args:
            latitude: Latitude
            longitude: Longitude
        
        Returns:
            float: Qibla direction in degrees
        """
        cache_key = f"qibla_{latitude}_{longitude}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/qibla/{latitude}/{longitude}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            
            if data["code"] == 200:
                direction = data["data"]["direction"]
                cache.set(cache_key, direction, 86400 * 30)  # Cache for 30 days
                return direction
            else:
                logger.error(f"Aladhan Qibla API error: {data}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Aladhan Qibla API request failed: {e}")
            return None


class QuranService:
    """
    Service for QuranEnc API.
    Docs: https://quranenc.com/
    """
    BASE_URL = settings.QURAN_API_BASE_URL
    TRANSLATION = getattr(settings, "QURAN_API_TRANSLATION", "turkish_shaban")
    CACHE_TIMEOUT = 604800  # 7 days
    
    @classmethod
    def get_verse_by_key(cls, verse_key: str, language: str = "tr"):
        """
        Get a specific verse by its key (e.g., "1:1", "2:255").
        
        Args:
            verse_key: Verse key in format "chapter:verse"
            language: Language code for translation (default: Turkish)
        
        Returns:
            dict: Verse data
        """
        cache_key = f"verse_{verse_key}_{language}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            chapter, verse = verse_key.split(":")
            response = requests.get(
                f"{cls.BASE_URL}/{cls.TRANSLATION}/{chapter}/{verse}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            result_data = data.get("result") or {}
            translation = result_data.get("translation", "")
            sura_name = result_data.get("sura_name") or result_data.get("sura_name_en")
            ayah = result_data.get("aya") or verse

            result = {
                "verse_key": f"{chapter}:{ayah}",
                "chapter_id": int(chapter),
                "verse_number": int(ayah),
                "translation_tr": translation,
                "chapter_name": f"{sura_name} - Ayet {ayah}" if sura_name else f"Sure {chapter} - Ayet {ayah}",
            }
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result
                
        except requests.RequestException as e:
            logger.error(f"Quran API request failed: {e}")
            return None
    
    @classmethod
    def get_daily_verse(cls):
        """
        Get a random verse for daily display.
        Uses verse of the day or random selection.
        
        Returns:
            dict: Verse data
        """
        # Try to get verse 1:1 (Al-Fatiha) as default daily verse
        # In production, you'd rotate this daily
        today = timezone.now().date()
        day_number = today.timetuple().tm_yday
        
        # Use day number to select a verse (simple rotation)
        chapter = (day_number % 114) + 1  # 114 chapters in Quran
        verse = (day_number % 20) + 1  # Max 20 verses per day rotation
        
        verse_key = f"{chapter}:{verse}"
        return cls.get_verse_by_key(verse_key)
    
    @classmethod
    def get_chapter_info(cls, chapter_id: int):
        """
        Get chapter (Surah) information.
        
        Args:
            chapter_id: Chapter number (1-114)
        
        Returns:
            dict: Chapter info
        """
        cache_key = f"chapter_info_{chapter_id}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        logger.warning("QuranEnc API does not provide chapter info")
        return None


class HadithService:
    """
    Service for fawazahmed0 Hadith API.
    Docs: https://github.com/fawazahmed0/hadith-api
    """
    BASE_URL = settings.HADITH_API_BASE_URL
    DEFAULT_COLLECTION = getattr(settings, "HADITH_DEFAULT_COLLECTION", "tur-bukhari")
    CACHE_TIMEOUT = 604800  # 7 days
    
    @classmethod
    def get_hadith_by_collection(cls, collection: str, limit: int = 10):
        """
        Get hadiths from a specific collection.
        
        Args:
            collection: Collection name (e.g., "bukhari", "muslim")
            limit: Number of hadiths to return
        
        Returns:
            list: Hadiths data
        """
        cache_key = f"hadith_{collection}_{limit}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            response = requests.get(
                f"{cls.BASE_URL}/editions/{collection}.json",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            hadiths = data.get("hadiths") or []
            result = []
            for hadith in hadiths[:limit]:
                result.append({
                    "collection": collection,
                    "hadith_number": hadith.get("hadithnumber") or hadith.get("number"),
                    "translation_tr": hadith.get("text", ""),
                    "chapter": hadith.get("chapter", ""),
                })
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result
                
        except requests.RequestException as e:
            logger.error(f"Hadith API request failed: {e}")
            return None
    
    @classmethod
    def get_random_hadith(cls, collection: str = "bukhari"):
        """
        Get a random hadith for daily display.
        
        Returns:
            dict: Single hadith data
        """
        if not collection or collection == "bukhari":
            collection = cls.DEFAULT_COLLECTION

        hadiths = cls.get_hadith_by_collection(collection, limit=300)
        if hadiths:
            import random
            return random.choice(hadiths)
        return None


# Service instances
aladhan_service = AladhanService()
quran_service = QuranService()
hadith_service = HadithService()
