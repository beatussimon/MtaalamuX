from django.contrib import admin
from .models import (
    UserProfile, Category, Professional, PortfolioItem, Message, Article, Comment,
    ServiceReview, Favorite, Notification, ActivityLog, Job, JobDocument, UpgradeRequest,
    FAQ, Feedback, CustomAdmin, AdminHelper, Badge, VerificationToken
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'last_seen')
    search_fields = ('user__username', 'bio')
    list_filter = ('last_seen', 'theme',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'field', 'subfield', 'location', 'is_verified')
    search_fields = ('user__username', 'subfield', 'location')
    list_filter = ('is_verified', 'field')
    actions = ['verify_professionals']

    def verify_professionals(self, request, queryset):
        queryset.update(is_verified=True)
    verify_professionals.short_description = "Verify selected professionals"

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('professional', 'title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'is_read')
    search_fields = ('sender__username', 'recipient__username', 'content')
    list_filter = ('timestamp', 'is_read')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_date', 'is_published')
    search_fields = ('title', 'content', 'author__user__username')
    list_filter = ('is_published', 'publish_date')
    actions = ['publish_articles']

    def publish_articles(self, request, queryset):
        queryset.update(is_published=True)
    publish_articles.short_description = "Publish selected articles"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    search_fields = ('user__username', 'article__title', 'content')
    list_filter = ('created_at',)

@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ('professional', 'reviewer', 'rating', 'created_at')
    search_fields = ('professional__user__username', 'reviewer__username', 'comment')
    list_filter = ('rating', 'created_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'professional')
    search_fields = ('user__username', 'professional__user__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read', 'created_at')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action')
    list_filter = ('timestamp',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional', 'status', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'created_at')
    # Define the inline class
    class JobDocumentInline(admin.TabularInline):
        model = JobDocument
        extra = 1  # Number of empty forms to display
    inlines = [JobDocumentInline]  # Reference the inline class

@admin.register(JobDocument)
class JobDocumentAdmin(admin.ModelAdmin):
    list_display = ('job', 'document')
    search_fields = ('job__title',)

@admin.register(UpgradeRequest)
class UpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'upgrade_type', 'status', 'requested_at')
    search_fields = ('user__username', 'upgrade_type')
    list_filter = ('status', 'upgrade_type', 'requested_at')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')
    list_filter = ('created_at',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'submitted_at')
    search_fields = ('user__username', 'message')
    list_filter = ('submitted_at',)

@admin.register(CustomAdmin)
class CustomAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    search_fields = ('user__username',)
    list_filter = ('is_active',)
    # Define the inline class
    class AdminHelperInline(admin.TabularInline):
        model = AdminHelper
        extra = 1
    inlines = [AdminHelperInline]

@admin.register(AdminHelper)
class AdminHelperAdmin(admin.ModelAdmin):
    list_display = ('custom_admin', 'user', 'task')
    search_fields = ('custom_admin__user__username', 'user__username', 'task')
    list_filter = ('task',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'awarded_at')
    search_fields = ('user__username', 'tier')
    list_filter = ('tier', 'awarded_at')

@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at')
    search_fields = ('user__username', 'token')
    list_filter = ('created_at', 'expires_at')