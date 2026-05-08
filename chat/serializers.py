from rest_framework import serializers
from chat.models import ChatMessage, ChatSession


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for Chat Message"""
    
    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "role",
            "content",
            "token_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for Chat Session"""
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = [
            "id",
            "title",
            "is_active",
            "message_count",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def get_message_count(self, obj) -> int:
        return obj.messages.count()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for Chat Request"""
    message = serializers.CharField(required=True, max_length=4000)
    session_id = serializers.IntegerField(required=False)
