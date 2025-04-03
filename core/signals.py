from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Professional
from .utils import get_default_category

@receiver(post_save, sender=UserProfile)
def create_professional_for_profile(sender, instance, created, **kwargs):
    if instance.is_professional and not hasattr(instance.user, 'professional'):
        # Create a Professional object if the user is marked as a professional
        Professional.objects.create(
            user=instance.user,
            field=get_default_category(),
            subfield='',
            location='',
            bio='',
            is_verified=False,
            # Remove follower_count=0 since it's a computed property
        )