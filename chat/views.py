from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from chat.models import ChatMessage, ChatSession
from chat.serializers import (
    ChatMessageSerializer,
    ChatSessionSerializer,
    ChatRequestSerializer,
)
from core.gemini_service import gemini_service


class ChatView(generics.GenericAPIView):
    """
    Send a message to AI assistant and get response.
    POST /api/chat/
    """
    serializer_class = ChatRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = serializer.validated_data["message"]
        session_id = serializer.validated_data.get("session_id")
        
        # Get or create chat session
        if session_id:
            session = ChatSession.objects.filter(
                id=session_id,
                user=request.user
            ).first()
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=message[:50] + "..." if len(message) > 50 else message,
            )
        
        if not session:
            return Response(
                {"error": "Session not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Save user message
        user_message = ChatMessage.objects.create(
            user=request.user,
            role="user",
            content=message,
            session=session,
        )
        
        # Get conversation history
        history = list(
            ChatMessage.objects.filter(
                session=session
            ).order_by("created_at")[:10].values("role", "content")
        )
        
        # Generate AI response
        ai_response = gemini_service.generate_response(message, history)
        
        # Save AI response
        assistant_message = ChatMessage.objects.create(
            user=request.user,
            role="assistant",
            content=ai_response,
        )
        
        # Update session
        session.updated_at = timezone.now()
        session.save()
        
        return Response({
            "message": ChatMessageSerializer(assistant_message).data,
            "session": ChatSessionSerializer(session).data,
        })


class ChatSessionListView(generics.ListAPIView):
    """
    List user's chat sessions.
    GET /api/chat/sessions/
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(
            user=self.request.user
        ).order_by("-updated_at")


class ChatSessionDetailView(generics.RetrieveDestroyAPIView):
    """
    Get/Delete a specific chat session.
    GET/DELETE /api/chat/sessions/<id>/
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


class ChatHistoryView(generics.GenericAPIView):
    """
    Get chat history for a session.
    GET /api/chat/history/?session_id=1
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")
        
        if not session_id:
            # Get all messages (no session filter)
            messages = ChatMessage.objects.filter(
                user=request.user
            ).order_by("-created_at")[:50]
        else:
            session = ChatSession.objects.filter(
                id=session_id,
                user=request.user
            ).first()
            
            if not session:
                return Response(
                    {"error": "Session not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            messages = ChatMessage.objects.filter(
                chatsession=session
            ).order_by("created_at")
        
        return Response({
            "messages": ChatMessageSerializer(messages, many=True).data,
        })


class ChatHistoryClearView(generics.GenericAPIView):
    """
    Clear chat history for a session or all sessions.
    DELETE /api/chat/history/?session_id=1
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")
        
        if session_id:
            # Clear specific session
            session = ChatSession.objects.filter(
                id=session_id,
                user=request.user
            ).first()
            
            if not session:
                return Response(
                    {"error": "Session not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            ChatMessage.objects.filter(session=session).delete()
            session.delete()
        else:
            # Clear all sessions
            ChatMessage.objects.filter(user=request.user).delete()
            ChatSession.objects.filter(user=request.user).delete()
        
        return Response({"message": "Chat history cleared"})
