"""Django Admin configuration for MtaalamuX"""
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Category, Professional, PortfolioItem, Message,
    Article, Comment, ServiceReview, Favorite, Notification,
    ActivityLog, Job, ExternalJob, UpgradeRequest, FAQ,
    Feedback, JobDocument, Badge, Research, Consultation,
    ConsultationTask, ConsultationApplication, ConsultationMessage,
    Conversation, PaymentMethod, PaymentRecord, DigitalItem,
    MerchItem, Purchase, VerificationRequest, TopExpert,
    FeaturedContent
)


# =============================================================================
# CATEGORY ADMIN
# =============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category Admin"""
    list_display = ['name', 'description', 'get_initials', 'professional_count', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    def get_initials(self, obj):
        return obj.get_initials()
    get_initials.short_description = 'Initials'
    
    def professional_count(self, obj):
        return obj.professionals.filter(is_verified=True).count()
    professional_count.short_description = 'Verified Professionals'


# =============================================================================
# PROFESSIONAL ADMIN
# =============================================================================

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    """Professional Admin"""
    list_display = ['user', 'field', 'location', 'is_verified', 'get_verification_level', 
                    'follower_count', 'article_count', 'created_at']
    list_filter = ['is_verified', 'verification_level', 'field', 'is_featured']
    search_fields = ['user__username', 'user__email', 'field__name']
    raw_id_fields = ['user', 'field', 'verified_by', 'followers']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_verification_level(self, obj):
        if obj.verification_level:
            return obj.get_verification_level_display()
        return 'None'
    get_verification_level.short_description = 'Verification'
    
    def follower_count(self, obj):
        return obj.follower_count
    follower_count.short_description = 'Followers'
    
    def article_count(self, obj):
        return obj.article_count
    article_count.short_description = 'Articles'


# =============================================================================
# ARTICLE & RESEARCH ADMIN
# =============================================================================

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Article Admin"""
    list_display = ['title', 'author', 'category', 'is_published', 'is_featured', 
                    'like_count', 'views', 'publish_date']
    list_filter = ['is_published', 'is_featured', 'category', 'publish_date']
    search_fields = ['title', 'content', 'author__user__username']
    raw_id_fields = ['author', 'category', 'likes']
    readonly_fields = ['publish_date', 'updated_at', 'views', 'likes', 'shares']
    
    def like_count(self, obj):
        return obj.like_count
    like_count.short_description = 'Likes'


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    """Research Admin"""
    list_display = ['title', 'author', 'category', 'status', 'is_featured',
                    'like_count', 'views', 'publish_date']
    list_filter = ['status', 'is_featured', 'category', 'publish_date']
    search_fields = ['title', 'abstract', 'content', 'author__user__username']
    raw_id_fields = ['author', 'category', 'likes']
    readonly_fields = ['publish_date', 'updated_at', 'views', 'likes', 'shares']
    
    def like_count(self, obj):
        return obj.like_count
    like_count.short_description = 'Likes'


# =============================================================================
# COMMENT ADMIN
# =============================================================================

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment Admin"""
    list_display = ['user', 'get_target', 'content_preview', 'created_at']
    list_filter = ['created_at', 'article', 'research']
    search_fields = ['content', 'user__username']
    raw_id_fields = ['user', 'article', 'research', 'parent', 'likes']
    
    def get_target(self, obj):
        if obj.article:
            return f"Article: {obj.article.title}"
        return f"Research: {obj.research.title}"
    get_target.short_description = 'On'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


# =============================================================================
# MESSAGE & CONVERSATION ADMIN
# =============================================================================

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation Admin"""
    list_display = ['subject', 'get_participants', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject']
    filter_horizontal = ['participants']
    
    def get_participants(self, obj):
        return ', '.join([p.username for p in obj.participants.all()[:3]])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message Admin"""
    list_display = ['sender', 'conversation', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp']
    search_fields = ['content', 'sender__username']
    raw_id_fields = ['sender', 'conversation', 'parent']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


# =============================================================================
# CONSULTATION ADMIN
# =============================================================================

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    """Consultation Admin"""
    list_display = ['title', 'client', 'expert', 'status', 'price', 
                    'is_paid', 'payment_verified', 'created_at']
    list_filter = ['status', 'is_paid', 'payment_verified', 'created_at']
    search_fields = ['title', 'description', 'client__username', 'expert__user__username']
    raw_id_fields = ['client', 'expert']


@admin.register(ConsultationTask)
class ConsultationTaskAdmin(admin.ModelAdmin):
    """Consultation Task Admin"""
    list_display = ['title', 'expert', 'category', 'budget', 'status', 'applicant_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'expert__user__username']
    raw_id_fields = ['expert', 'category']


@admin.register(ConsultationApplication)
class ConsultationApplicationAdmin(admin.ModelAdmin):
    """Consultation Application Admin"""
    list_display = ['task', 'applicant', 'status', 'proposed_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['cover_letter', 'applicant__username', 'task__title']
    raw_id_fields = ['task', 'applicant']


# =============================================================================
# PAYMENT ADMIN
# =============================================================================

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Payment Method Admin"""
    list_display = ['network', 'lipa_number', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'network']
    search_fields = ['network', 'lipa_number']
    fields = ['network', 'network_image', 'lipa_number', 'payment_instructions', 'is_active', 'order']


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    """Payment Record Admin"""
    list_display = ['user', 'payment_method', 'amount', 'transaction_reference', 
                    'status', 'verified_by', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_reference', 'phone_number']
    raw_id_fields = ['user', 'payment_method', 'verified_by']


# =============================================================================
# DIGITAL ITEMS & MERCH ADMIN
# =============================================================================

@admin.register(DigitalItem)
class DigitalItemAdmin(admin.ModelAdmin):
    """Digital Item Admin"""
    list_display = ['title', 'seller', 'category', 'price', 'status', 'sales_count', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'description', 'seller__user__username']
    raw_id_fields = ['seller']


@admin.register(MerchItem)
class MerchItemAdmin(admin.ModelAdmin):
    """Merch Item Admin"""
    list_display = ['title', 'seller', 'price', 'status', 'stock_quantity', 'is_in_stock', 'created_at']
    list_filter = ['status', 'color', 'created_at']
    search_fields = ['title', 'description', 'seller__user__username']
    raw_id_fields = ['seller']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Purchase Admin"""
    list_display = ['buyer', 'get_item', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['buyer__username']
    raw_id_fields = ['buyer', 'digital_item', 'merch_item']
    
    def get_item(self, obj):
        if obj.digital_item:
            return f"Digital: {obj.digital_item.title}"
        return f"Merch: {obj.merch_item.title}"
    get_item.short_description = 'Item'


# =============================================================================
# UPGRADE & VERIFICATION ADMIN
# =============================================================================

@admin.register(UpgradeRequest)
class UpgradeRequestAdmin(admin.ModelAdmin):
    """Upgrade Request Admin"""
    list_display = ['user', 'upgrade_type', 'status', 'requested_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'upgrade_type', 'requested_at']
    search_fields = ['user__username', 'notes']
    raw_id_fields = ['user', 'reviewed_by']
    readonly_fields = ['requested_at', 'updated_at']


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    """Verification Request Admin"""
    list_display = ['professional', 'requested_level', 'status', 'requested_at', 'reviewed_by', 'reviewed_at']
    list_filter = ['status', 'requested_level', 'requested_at']
    search_fields = ['professional__user__username', 'notes']
    raw_id_fields = ['professional', 'reviewed_by']
    readonly_fields = ['requested_at', 'updated_at']


# =============================================================================
# OTHER MODELS ADMIN
# =============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification Admin"""
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['message', 'title', 'user__username']
    raw_id_fields = ['user']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Favorite Admin"""
    list_display = ['user', 'professional', 'created_at']
    search_fields = ['user__username', 'professional__user__username']
    raw_id_fields = ['user', 'professional']


@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    """Service Review Admin"""
    list_display = ['professional', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['comment', 'professional__user__username', 'reviewer__username']
    raw_id_fields = ['professional', 'reviewer']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Activity Log Admin"""
    list_display = ['user', 'action', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'action']
    raw_id_fields = ['user']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Job Admin"""
    list_display = ['title', 'professional', 'client', 'status', 'budget', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description', 'professional__user__username']
    raw_id_fields = ['professional', 'client']


@admin.register(ExternalJob)
class ExternalJobAdmin(admin.ModelAdmin):
    """External Job Admin"""
    list_display = ['title', 'category', 'job_type', 'location', 'is_active', 'created_at']
    list_filter = ['job_type', 'is_active', 'category', 'created_at']
    search_fields = ['title', 'description']
    raw_id_fields = ['category', 'created_by']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Badge Admin"""
    list_display = ['user', 'tier', 'awarded_by', 'awarded_at']
    list_filter = ['tier', 'awarded_at']
    search_fields = ['user__username', 'description']
    raw_id_fields = ['user', 'awarded_by']


@admin.register(TopExpert)
class TopExpertAdmin(admin.ModelAdmin):
    """Top Expert Admin"""
    list_display = ['professional', 'rank', 'is_active', 'added_by', 'added_at']
    list_filter = ['is_active', 'added_at']
    search_fields = ['professional__user__username']
    raw_id_fields = ['professional', 'added_by']
    ordering = ['rank']


@admin.register(FeaturedContent)
class FeaturedContentAdmin(admin.ModelAdmin):
    """Featured Content Admin"""
    list_display = ['title', 'content_type', 'is_active', 'order', 'featured_at']
    list_filter = ['content_type', 'is_active', 'featured_at']
    search_fields = ['title', 'description']
    ordering = ['order', '-featured_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """FAQ Admin"""
    list_display = ['question', 'category', 'order', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['question', 'answer']
    ordering = ['order', 'category']


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Feedback Admin"""
    list_display = ['user', 'category', 'rating', 'is_resolved', 'submitted_at']
    list_filter = ['category', 'is_resolved', 'submitted_at']
    search_fields = ['message', 'user__username']
    raw_id_fields = ['user']


# =============================================================================
# PORTFOLIO ADMIN
# =============================================================================

@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    """Portfolio Item Admin"""
    list_display = ['title', 'professional', 'created_at']
    search_fields = ['title', 'description', 'professional__user__username']
    raw_id_fields = ['professional']


@admin.register(JobDocument)
class JobDocumentAdmin(admin.ModelAdmin):
    """Job Document Admin"""
    list_display = ['get_content_object', 'description', 'uploaded_at']
    search_fields = ['description']
    
    def get_content_object(self, obj):
        if obj.content_object:
            return str(obj.content_object)
        return 'Unlinked'
    get_content_object.short_description = 'Content Object'
