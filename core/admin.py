from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import (
    UserProfile, Category, Professional, PortfolioItem, Message, Article, Comment,
    ServiceReview, Favorite, Notification, ActivityLog, Job, ExternalJob, JobDocument,
    UpgradeRequest, FAQ, Feedback, CustomAdmin, AdminHelper, Badge
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_professional', 'bio', 'last_seen', 'theme')
    search_fields = ('user__username', 'bio', 'interests')
    list_filter = ('is_professional', 'last_seen', 'theme')
    list_per_page = 25
    raw_id_fields = ('user',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image')
    search_fields = ('name',)
    list_per_page = 25

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'field', 'subfield', 'location', 'is_verified', 'follower_count')
    search_fields = ('user__username', 'subfield', 'location', 'bio')
    list_filter = ('is_verified', 'field')
    list_per_page = 25
    raw_id_fields = ('user',)
    actions = ['verify_professionals']

    def verify_professionals(self, request, queryset):
        queryset.update(is_verified=True)
    verify_professionals.short_description = "Verify selected professionals"

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('professional', 'title', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at',)
    list_per_page = 25
    raw_id_fields = ('professional',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'is_read')
    search_fields = ('sender__username', 'recipient__username', 'content')
    list_filter = ('timestamp', 'is_read')
    list_per_page = 25
    raw_id_fields = ('sender', 'recipient')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'publish_date', 'is_published', 'views')
    search_fields = ('title', 'content', 'author__user__username', 'category__name')  # Updated to use category__name
    list_filter = ('is_published', 'publish_date', 'category')
    list_per_page = 25
    raw_id_fields = ('author',)
    actions = ['publish_articles']

    def publish_articles(self, request, queryset):
        queryset.update(is_published=True)
    publish_articles.short_description = "Publish selected articles"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at', 'like_count')
    search_fields = ('user__username', 'article__title', 'content')
    list_filter = ('created_at',)
    list_per_page = 25
    raw_id_fields = ('user', 'article')

@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ('professional', 'reviewer', 'rating', 'created_at')
    search_fields = ('professional__user__username', 'reviewer__username', 'comment')
    list_filter = ('rating', 'created_at')
    list_per_page = 25
    raw_id_fields = ('professional', 'reviewer')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'professional')
    search_fields = ('user__username', 'professional__user__username')
    list_per_page = 25
    raw_id_fields = ('user', 'professional')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'link', 'is_read', 'created_at')
    search_fields = ('user__username', 'message', 'link')
    list_filter = ('is_read', 'created_at')
    list_per_page = 25
    raw_id_fields = ('user',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    search_fields = ('user__username', 'action')
    list_filter = ('timestamp',)
    list_per_page = 25
    raw_id_fields = ('user',)

# Inline for JobDocument using GenericTabularInline
class JobDocumentInline(GenericTabularInline):
    model = JobDocument
    extra = 1

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'professional', 'client', 'status', 'created_at', 'budget')
    search_fields = ('title', 'description')
    list_filter = ('status', 'created_at')
    list_per_page = 25
    raw_id_fields = ('professional', 'client')
    inlines = [JobDocumentInline]

@admin.register(ExternalJob)
class ExternalJobAdmin(admin.ModelAdmin):
    list_display = ('title', 'job_type', 'category', 'location', 'created_at', 'created_by')
    search_fields = ('title', 'description', 'location')
    list_filter = ('job_type', 'category', 'created_at')
    list_per_page = 25
    raw_id_fields = ('created_by',)
    autocomplete_fields = ('category',)
    inlines = [JobDocumentInline]

@admin.register(JobDocument)
class JobDocumentAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'document', 'content_type', 'object_id')
    search_fields = ('content_object__title',)  # Search by the title of the related object
    list_filter = ('content_type',)
    list_per_page = 25

@admin.register(UpgradeRequest)
class UpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'upgrade_type', 'status', 'requested_at', 'updated_at')
    search_fields = ('user__username', 'upgrade_type')
    list_filter = ('status', 'upgrade_type', 'requested_at')
    list_per_page = 25
    raw_id_fields = ('user',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at')
    search_fields = ('question', 'answer')
    list_filter = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'submitted_at')
    search_fields = ('user__username', 'message')
    list_filter = ('submitted_at',)
    list_per_page = 25
    raw_id_fields = ('user',)

@admin.register(CustomAdmin)
class CustomAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    search_fields = ('user__username',)
    list_filter = ('is_active',)
    list_per_page = 25
    raw_id_fields = ('user',)
    class AdminHelperInline(admin.TabularInline):
        model = AdminHelper
        extra = 1
    inlines = [AdminHelperInline]

@admin.register(AdminHelper)
class AdminHelperAdmin(admin.ModelAdmin):
    list_display = ('custom_admin', 'user', 'task')
    search_fields = ('custom_admin__user__username', 'user__username', 'task')
    list_filter = ('task',)
    list_per_page = 25
    raw_id_fields = ('custom_admin', 'user')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier', 'awarded_at')
    search_fields = ('user__username', 'tier')
    list_filter = ('tier', 'awarded_at')
    list_per_page = 25
    raw_id_fields = ('user',)
