from django.contrib import admin
from chat.models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ["role", "content", "created_at"]
    fields = ["role", "content", "created_at"]
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "is_active", "message_count", "updated_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user__email", "title"]
    ordering = ["-updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "content_preview", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["user__email", "content"]
    ordering = ["-created_at"]
    readonly_fields = ["user", "role", "content", "created_at"]
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content"
