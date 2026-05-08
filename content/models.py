from django.db import models


class Verse(models.Model):
    """
    Stores Quran verses (Ayet) with Turkish translation.
    Data is synced from Quran.com API.
    """
    verse_key = models.CharField(max_length=20, unique=True)  # e.g., "1:1", "2:255"
    chapter_id = models.IntegerField()  # Surah number
    verse_number = models.IntegerField()  # Verse number in chapter
    
    # Arabic text
    text_uthmani = models.TextField()
    
    # Turkish translation
    translation_tr = models.TextField()
    
    # Metadata
    chapter_name = models.CharField(max_length=100, blank=True)  # Surah name
    juz_number = models.IntegerField(blank=True, null=True)
    page_number = models.IntegerField(blank=True, null=True)
    
    # For daily verse feature
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "verses"
        verbose_name = "Verse"
        verbose_name_plural = "Verses"
        ordering = ["chapter_id", "verse_number"]
        indexes = [
            models.Index(fields=["chapter_id", "verse_number"]),
            models.Index(fields=["verse_key"]),
        ]
    
    def __str__(self):
        return f"{self.chapter_name} - {self.verse_number}"


class Hadith(models.Model):
    """
    Stores Hadith collections with Turkish translation.
    Data is synced from Hadith API.
    """
    collection = models.CharField(max_length=50)  # e.g., "Bukhari", "Muslim", "Tirmidhi"
    hadith_number = models.CharField(max_length=20)  # Hadith number in collection
    
    # Arabic text (optional)
    arabic_text = models.TextField(blank=True)
    
    # Turkish translation
    translation_tr = models.TextField()
    
    # Chapter/Book info
    chapter = models.CharField(max_length=200, blank=True)
    
    # Metadata
    narrator = models.CharField(max_length=100, blank=True)  # Ravisi
    grade = models.CharField(max_length=50, blank=True)  # Derece (Sahih, Hasan, etc.)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "hadiths"
        verbose_name = "Hadith"
        verbose_name_plural = "Hadiths"
        ordering = ["collection", "hadith_number"]
        indexes = [
            models.Index(fields=["collection", "hadith_number"]),
        ]
    
    def __str__(self):
        return f"{self.collection} - {self.hadith_number}"


class Dua(models.Model):
    """
    Stores Dua (prayers/supplications) with Turkish translation.
    Can be manually added or synced from external sources.
    """
    title = models.CharField(max_length=200)  # Dua title
    title_arabic = models.CharField(max_length=200, blank=True)
    
    # Content
    content_arabic = models.TextField()  # Arabic text
    translation_tr = models.TextField()  # Turkish translation
    transliteration = models.TextField(blank=True)  # Latin characters with pronunciation
    
    # Category
    category = models.CharField(max_length=100, blank=True)  # e.g., "Sabah", "Akşam", "Yolculuk"
    
    # Reference
    reference = models.CharField(max_length=200, blank=True)  # Source reference
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "duas"
        verbose_name = "Dua"
        verbose_name_plural = "Duas"
        ordering = ["category", "title"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]
    
    def __str__(self):
        return self.title


class DailyContent(models.Model):
    """
    Tracks daily verse and hadith selections.
    """
    date = models.DateField(unique=True)
    verse = models.ForeignKey(Verse, on_delete=models.SET_NULL, null=True, blank=True, related_name="daily_verse")
    hadith = models.ForeignKey(Hadith, on_delete=models.SET_NULL, null=True, blank=True, related_name="daily_hadith")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "daily_contents"
        verbose_name = "Daily Content"
        verbose_name_plural = "Daily Contents"
        ordering = ["-date"]
    
    def __str__(self):
        return str(self.date)
