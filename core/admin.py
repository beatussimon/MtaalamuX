from django.contrib import admin
from .models import UserProfile, Professional, PortfolioItem, Message, Article, Comment, ServiceReview, Favorite, Notification, ActivityLog, Job

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_professional', 'last_seen', 'theme')

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'field', 'subfield', 'is_verified', 'follower_count', 'post_count')
    actions = ['verify_professional']
    
    def verify_professional(self, request, queryset):
        queryset.update(is_verified=True, verified_date=timezone.now())
    verify_professional.short_description = "Mark as Verified"

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_date', 'is_published', 'views', 'like_count')

admin.site.register(PortfolioItem)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(ServiceReview)
admin.site.register(Favorite)
admin.site.register(Notification)
admin.site.register(ActivityLog)
admin.site.register(Job)