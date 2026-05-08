from django.contrib import admin
from content.models import Verse, Hadith, Dua, DailyContent


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = ["verse_key", "chapter_name", "verse_number", "is_active"]
    list_filter = ["chapter_id", "is_active"]
    search_fields = ["verse_key", "translation_tr", "text_uthmani"]
    ordering = ["chapter_id", "verse_number"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Verse Info", {
            "fields": ("verse_key", "chapter_id", "verse_number", "chapter_name")
        }),
        ("Content", {
            "fields": ("text_uthmani", "translation_tr")
        }),
        ("Metadata", {
            "fields": ("juz_number", "page_number", "is_active"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Hadith)
class HadithAdmin(admin.ModelAdmin):
    list_display = ["collection", "hadith_number", "chapter", "is_active"]
    list_filter = ["collection", "is_active"]
    search_fields = ["translation_tr", "arabic_text", "chapter"]
    ordering = ["collection", "hadith_number"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Hadith Info", {
            "fields": ("collection", "hadith_number", "chapter")
        }),
        ("Content", {
            "fields": ("arabic_text", "translation_tr", "narrator")
        }),
        ("Metadata", {
            "fields": ("grade", "is_active"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(Dua)
class DuaAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["title", "translation_tr", "content_arabic"]
    ordering = ["category", "title"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Dua Info", {
            "fields": ("title", "title_arabic", "category")
        }),
        ("Content", {
            "fields": ("content_arabic", "translation_tr", "transliteration")
        }),
        ("Reference", {
            "fields": ("reference", "is_active"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(DailyContent)
class DailyContentAdmin(admin.ModelAdmin):
    list_display = ["date", "verse", "hadith"]
    list_filter = ["date"]
    ordering = ["-date"]
    readonly_fields = ["created_at"]
