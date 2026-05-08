from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from content.models import Verse, Hadith, Dua, DailyContent
from content.serializers import (
    VerseSerializer,
    HadithSerializer,
    DuaSerializer,
    DailyContentSerializer,
)
from core.services import quran_service, hadith_service


class DailyVerseView(generics.GenericAPIView):
    """
    Get daily verse.
    GET /api/content/daily-verse/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        verse_data = quran_service.get_daily_verse()
        
        if not verse_data:
            return Response(
                {"error": "Failed to fetch daily verse"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            "translation_tr": verse_data.get("translation_tr", ""),
            "chapter_name": verse_data.get("chapter_name", ""),
            "verse_key": verse_data.get("verse_key", ""),
        })


class DailyHadithView(generics.GenericAPIView):
    """
    Get daily hadith.
    GET /api/content/daily-hadith/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        hadith_data = hadith_service.get_random_hadith()
        
        if not hadith_data:
            return Response(
                {"error": "Failed to fetch daily hadith"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({
            "translation_tr": hadith_data.get("translation_tr", ""),
            "collection": hadith_data.get("collection", ""),
            "hadith_number": hadith_data.get("hadith_number"),
        })


class DailyContentView(generics.GenericAPIView):
    """
    Get daily content (verse + hadith).
    GET /api/content/daily/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        verse_data = quran_service.get_daily_verse()
        hadith_data = hadith_service.get_random_hadith()

        if not verse_data and not hadith_data:
            return Response(
                {"error": "Failed to fetch daily content"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        response_payload = {
            "verse": None,
            "hadith": None,
        }

        if verse_data:
            response_payload["verse"] = {
                "translation_tr": verse_data.get("translation_tr", ""),
                "chapter_name": verse_data.get("chapter_name", ""),
                "verse_key": verse_data.get("verse_key", ""),
            }

        if hadith_data:
            response_payload["hadith"] = {
                "translation_tr": hadith_data.get("translation_tr", ""),
                "collection": hadith_data.get("collection", ""),
                "hadith_number": hadith_data.get("hadith_number"),
            }

        return Response(response_payload)


class VerseListView(generics.ListAPIView):
    """
    List verses with filtering.
    GET /api/content/verses/?chapter_id=1&search=rahman
    """
    queryset = Verse.objects.filter(is_active=True)
    serializer_class = VerseSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["chapter_id"]
    search_fields = ["translation_tr", "text_uthmani"]


class VerseDetailView(generics.RetrieveAPIView):
    """
    Get verse by verse_key.
    GET /api/content/verses/<verse_key>/
    """
    serializer_class = VerseSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "verse_key"
    
    def get_queryset(self):
        return Verse.objects.filter(is_active=True)


class HadithListView(generics.ListAPIView):
    """
    List hadiths with filtering.
    GET /api/content/hadiths/?collection=bukhari&search=sadaqah
    """
    queryset = Hadith.objects.filter(is_active=True)
    serializer_class = HadithSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["collection"]
    search_fields = ["translation_tr", "arabic_text"]


class DuaListView(generics.ListAPIView):
    """
    List duas with filtering.
    GET /api/content/duas/?category=sabah
    """
    queryset = Dua.objects.filter(is_active=True)
    serializer_class = DuaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category"]
    search_fields = ["title", "translation_tr"]


class DuaDetailView(generics.RetrieveAPIView):
    """
    Get dua by ID.
    GET /api/content/duas/<id>/
    """
    queryset = Dua.objects.filter(is_active=True)
    serializer_class = DuaSerializer
    permission_classes = [permissions.AllowAny]


class ContentSearchView(generics.GenericAPIView):
    """
    Search across all content (verses, hadiths, duas).
    GET /api/content/search/?q=merhamet
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", "")
        
        if not query or len(query) < 3:
            return Response({
                "verses": [],
                "hadiths": [],
                "duas": [],
            })
        
        # Search in verses
        verses = Verse.objects.filter(
            is_active=True,
            translation_tr__icontains=query
        )[:10]
        
        # Search in hadiths
        hadiths = Hadith.objects.filter(
            is_active=True,
            translation_tr__icontains=query
        )[:10]
        
        # Search in duas
        duas = Dua.objects.filter(
            is_active=True,
            translation_tr__icontains=query
        )[:10]
        
        return Response({
            "query": query,
            "results": {
                "verses": VerseSerializer(verses, many=True).data,
                "hadiths": HadithSerializer(hadiths, many=True).data,
                "duas": DuaSerializer(duas, many=True).data,
            },
        })


# Import timezone for views that need it
from django.utils import timezone
