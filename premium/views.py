from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from premium.models import SubscriptionPlan, Subscription, PaymentTransaction
from premium.serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    SubscribeRequestSerializer,
    PaymentTransactionSerializer,
)
from users.models import User


class SubscriptionPlanListView(generics.ListAPIView):
    """
    List available subscription plans.
    GET /api/premium/plans/
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """
    Get a specific subscription plan.
    GET /api/premium/plans/<id>/
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionView(generics.GenericAPIView):
    """
    Get user's subscription status.
    GET /api/premium/subscription/
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            subscription = Subscription.objects.get(user=request.user)
            return Response(SubscriptionSerializer(subscription).data)
        except Subscription.DoesNotExist:
            return Response({
                "status": "not_subscribed",
                "is_premium": False,
            })


class SubscribeView(generics.GenericAPIView):
    """
    Subscribe to a premium plan.
    POST /api/premium/subscribe/
    """
    serializer_class = SubscribeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data["plan_id"]
        
        # Get plan
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"error": "Plan not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Get or create subscription
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={
                "plan": plan,
                "status": "active",
            }
        )
        
        if not created:
            # Update existing subscription
            subscription.plan = plan
            subscription.status = "active"
            subscription.save()
        
        # Update user premium status
        user = request.user
        user.is_premium = True
        user.premium_expires_at = timezone.now() + timedelta(days=plan.duration_days)
        user.save()
        
        # Update subscription dates
        subscription.started_at = timezone.now()
        subscription.expires_at = user.premium_expires_at
        subscription.save()
        
        # Create payment transaction (mock)
        PaymentTransaction.objects.create(
            user=user,
            subscription=subscription,
            transaction_type="payment",
            amount=plan.price,
            currency=plan.currency,
            payment_provider="mock",
            payment_status="completed",
        )
        
        return Response({
            "message": "Successfully subscribed to premium",
            "subscription": SubscriptionSerializer(subscription).data,
            "expires_at": user.premium_expires_at,
        })


class CancelSubscriptionView(generics.GenericAPIView):
    """
    Cancel user's subscription.
    POST /api/premium/cancel/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            subscription = Subscription.objects.get(user=request.user)
            subscription.status = "cancelled"
            subscription.cancelled_at = timezone.now()
            subscription.save()
            
            # Note: Keep premium status until expires_at
            
            return Response({
                "message": "Subscription cancelled",
                "expires_at": subscription.expires_at,
            })
        except Subscription.DoesNotExist:
            return Response(
                {"error": "No active subscription found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class PaymentHistoryView(generics.ListAPIView):
    """
    Get user's payment history.
    GET /api/premium/payments/
    """
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PaymentTransaction.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
