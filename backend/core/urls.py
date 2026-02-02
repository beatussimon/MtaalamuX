"""URL configuration for core app"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileViewSet, CategoryViewSet, ProfessionalViewSet,
    PortfolioItemViewSet, ConversationViewSet, MessageViewSet, ArticleViewSet, CommentViewSet,
    ServiceReviewViewSet, FavoriteViewSet, NotificationViewSet, JobViewSet,
    ExternalJobViewSet, UpgradeRequestViewSet, FAQViewSet, FeedbackViewSet,
    ResearchViewSet, HealthCheckView, HomepageView,
    ConsultationViewSet, ConsultationTaskViewSet, ConsultationApplicationViewSet,
    PaymentMethodViewSet, PaymentRecordViewSet, DigitalItemViewSet, MerchItemViewSet,
    PurchaseViewSet, VerificationRequestViewSet, TopExpertViewSet, FeaturedContentViewSet,
    ActivityLogViewSet, SiteSettingsViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'profiles', UserProfileViewSet, basename='profiles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'professionals', ProfessionalViewSet, basename='professionals')
router.register(r'portfolio', PortfolioItemViewSet, basename='portfolio')
router.register(r'conversations', ConversationViewSet, basename='conversations')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'articles', ArticleViewSet, basename='articles')
router.register(r'comments', CommentViewSet, basename='comments')
router.register(r'reviews', ServiceReviewViewSet, basename='reviews')
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'jobs', JobViewSet, basename='jobs')
router.register(r'external-jobs', ExternalJobViewSet, basename='external-jobs')
router.register(r'upgrade-requests', UpgradeRequestViewSet, basename='upgrade-requests')
router.register(r'faqs', FAQViewSet, basename='faqs')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'research', ResearchViewSet, basename='research')
router.register(r'consultations', ConsultationViewSet, basename='consultations')
router.register(r'consultation-tasks', ConsultationTaskViewSet, basename='consultation-tasks')
router.register(r'consultation-applications', ConsultationApplicationViewSet, basename='consultation-applications')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-methods')
router.register(r'payment-records', PaymentRecordViewSet, basename='payment-records')
router.register(r'digital-items', DigitalItemViewSet, basename='digital-items')
router.register(r'merch', MerchItemViewSet, basename='merch')
router.register(r'purchases', PurchaseViewSet, basename='purchases')
router.register(r'verification-requests', VerificationRequestViewSet, basename='verification-requests')
router.register(r'top-experts', TopExpertViewSet, basename='top-experts')
router.register(r'featured-content', FeaturedContentViewSet, basename='featured-content')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-logs')
router.register(r'site-settings', SiteSettingsViewSet, basename='site-settings')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('homepage/', HomepageView.as_view(), name='homepage'),
]
