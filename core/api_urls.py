from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    me,
)
from prayer_times.views import (
    PrayerTimesView,
    PrayerTimesByCoordinatesView,
    PrayerTimesMonthlyView,
    UserPrayerLocationView,
    UserPrayerLocationDetailView,
    QiblaDirectionView,
)
from content.views import (
    DailyVerseView,
    DailyHadithView,
    DailyContentView,
    VerseListView,
    VerseDetailView,
    HadithListView,
    DuaListView,
    DuaDetailView,
    ContentSearchView,
)
from chat.views import (
    ChatView,
    ChatSessionListView,
    ChatSessionDetailView,
    ChatHistoryView,
    ChatHistoryClearView,
)
from premium.views import (
    SubscriptionPlanListView,
    SubscriptionPlanDetailView,
    SubscriptionView,
    SubscribeView,
    CancelSubscriptionView,
    PaymentHistoryView,
)

# API URLs
urlpatterns = [
    # Auth endpoints
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    
    # User endpoints
    path("user/me/", me, name="user-me"),
    path("user/profile/", ProfileView.as_view(), name="user-profile"),
    path("user/password/", ChangePasswordView.as_view(), name="user-change-password"),
    
    # Prayer times endpoints
    path("prayer-times/", PrayerTimesView.as_view(), name="prayer-times"),
    path("prayer-times/coordinates/", PrayerTimesByCoordinatesView.as_view(), name="prayer-times-coordinates"),
    path("prayer-times/monthly/", PrayerTimesMonthlyView.as_view(), name="prayer-times-monthly"),
    path("prayer-times/qibla/", QiblaDirectionView.as_view(), name="prayer-times-qibla"),
    path("prayer-times/locations/", UserPrayerLocationView.as_view(), name="prayer-times-locations"),
    path("prayer-times/locations/<int:pk>/", UserPrayerLocationDetailView.as_view(), name="prayer-times-location-detail"),
    
    # Content endpoints
    path("content/daily-verse/", DailyVerseView.as_view(), name="content-daily-verse"),
    path("content/daily-hadith/", DailyHadithView.as_view(), name="content-daily-hadith"),
    path("content/daily/", DailyContentView.as_view(), name="content-daily"),
    path("content/verses/", VerseListView.as_view(), name="content-verses"),
    path("content/verses/<str:verse_key>/", VerseDetailView.as_view(), name="content-verse-detail"),
    path("content/hadiths/", HadithListView.as_view(), name="content-hadiths"),
    path("content/duas/", DuaListView.as_view(), name="content-duas"),
    path("content/duas/<int:pk>/", DuaDetailView.as_view(), name="content-dua-detail"),
    path("content/search/", ContentSearchView.as_view(), name="content-search"),
    
    # Chat endpoints
    path("chat/", ChatView.as_view(), name="chat"),
    path("chat/sessions/", ChatSessionListView.as_view(), name="chat-sessions"),
    path("chat/sessions/<int:pk>/", ChatSessionDetailView.as_view(), name="chat-session-detail"),
    path("chat/history/", ChatHistoryView.as_view(), name="chat-history"),
    path("chat/history/clear/", ChatHistoryClearView.as_view(), name="chat-history-clear"),
    
    # Premium endpoints
    path("premium/plans/", SubscriptionPlanListView.as_view(), name="premium-plans"),
    path("premium/plans/<int:pk>/", SubscriptionPlanDetailView.as_view(), name="premium-plan-detail"),
    path("premium/subscription/", SubscriptionView.as_view(), name="premium-subscription"),
    path("premium/subscribe/", SubscribeView.as_view(), name="premium-subscribe"),
    path("premium/cancel/", CancelSubscriptionView.as_view(), name="premium-cancel"),
    path("premium/payments/", PaymentHistoryView.as_view(), name="premium-payments"),
]
