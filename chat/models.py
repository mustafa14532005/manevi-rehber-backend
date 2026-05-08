from django.db import models
from users.models import User


class ChatSession(models.Model):
    """
    Groups chat messages into sessions/conversations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    title = models.CharField(max_length=200, blank=True)  # Auto-generated from first message
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "chat_sessions"
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"]),
            models.Index(fields=["user", "is_active"]),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.title or 'Untitled'} - {self.created_at}"


class ChatMessage(models.Model):
    """
    Stores chat messages between user and AI assistant (Gemini).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_messages")
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()  # Message content (can be markdown)
    
    # Metadata
    token_count = models.IntegerField(blank=True, null=True)  # Approximate token count
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "chat_messages"
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role} - {self.created_at}"
