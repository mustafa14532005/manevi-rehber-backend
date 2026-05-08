from rest_framework import serializers
from premium.models import SubscriptionPlan, Subscription, PaymentTransaction


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for Subscription Plan"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "name_tr",
            "price",
            "currency",
            "duration_days",
            "features",
            "is_active",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription"""
    plan = SubscriptionPlanSerializer(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "plan",
            "status",
            "started_at",
            "expires_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class SubscribeRequestSerializer(serializers.Serializer):
    """Serializer for Subscribe Request"""
    plan_id = serializers.IntegerField(required=True)
    payment_method = serializers.CharField(required=False, default="card")


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Payment Transaction"""
    
    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "user",
            "subscription",
            "transaction_type",
            "amount",
            "currency",
            "payment_provider",
            "payment_id",
            "payment_status",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
