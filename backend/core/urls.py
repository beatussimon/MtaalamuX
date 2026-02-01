"""URL configuration for core app"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileViewSet, CategoryViewSet, ProfessionalViewSet,
    PortfolioItemViewSet, MessageViewSet, ArticleViewSet, CommentViewSet,
    ServiceReviewViewSet, FavoriteViewSet, NotificationViewSet, JobViewSet,
    ExternalJobViewSet, UpgradeRequestViewSet, FAQViewSet, FeedbackViewSet,
    HealthCheckView
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'profiles', UserProfileViewSet, basename='profiles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'professionals', ProfessionalViewSet, basename='professionals')
router.register(r'portfolio', PortfolioItemViewSet, basename='portfolio')
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

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
