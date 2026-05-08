from rest_framework import serializers
from content.models import Verse, Hadith, Dua, DailyContent


class VerseSerializer(serializers.ModelSerializer):
    """Serializer for Quran Verse"""
    
    class Meta:
        model = Verse
        fields = [
            "id",
            "verse_key",
            "chapter_id",
            "verse_number",
            "text_uthmani",
            "translation_tr",
            "chapter_name",
            "juz_number",
            "page_number",
        ]


class HadithSerializer(serializers.ModelSerializer):
    """Serializer for Hadith"""
    
    class Meta:
        model = Hadith
        fields = [
            "id",
            "collection",
            "hadith_number",
            "arabic_text",
            "translation_tr",
            "chapter",
            "narrator",
            "grade",
        ]


class DuaSerializer(serializers.ModelSerializer):
    """Serializer for Dua"""
    
    class Meta:
        model = Dua
        fields = [
            "id",
            "title",
            "title_arabic",
            "content_arabic",
            "translation_tr",
            "transliteration",
            "category",
            "reference",
        ]


class DailyContentSerializer(serializers.ModelSerializer):
    """Serializer for Daily Content (Verse + Hadith)"""
    verse = VerseSerializer(read_only=True)
    hadith = HadithSerializer(read_only=True)
    
    class Meta:
        model = DailyContent
        fields = [
            "id",
            "date",
            "verse",
            "hadith",
        ]
