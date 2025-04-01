from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        unread_count = 0
    return {'unread_notifications': unread_count}


# core/context_processors.py
from .models import Notification, UserProfile

def common_context(request):
    context = {
        'unread_notifications': 0,
        'site_theme': 'light'  # Default theme
    }
    if request.user.is_authenticated:
        context['unread_notifications'] = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        try:
            # Check if userprofile exists and get theme preference
            profile = request.user.userprofile
            if profile.theme in ['light', 'dark']: # Validate theme value
                 context['site_theme'] = profile.theme
        except UserProfile.DoesNotExist:
            pass # User has no profile yet, use default theme
    return context