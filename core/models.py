from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import DetailView
import uuid
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_professional = models.BooleanField(default=False)
    bio = models.TextField(max_length=1000, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='default_avatar.jpg')
    interests = models.CharField(max_length=200, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Add the image field - allow it to be blank/null for fallback
    image = models.ImageField(
        upload_to='category_images/', # Store images in MEDIA_ROOT/category_images/
        blank=True,
        null=True,
        help_text="Optional: Image representing this category (e.g., an icon)."
    )

    def __str__(self):
        return self.name

    # Optional helper method for initials
    def get_initials(self):
        if self.name:
            # Simple first letter initial
            # return self.name[0].upper()
            # --- OR ---
            # Initials from first 1 or 2 words (e.g., "SD" for "Software Development")
            parts = self.name.split()
            if len(parts) > 1:
                return (parts[0][0] + parts[1][0]).upper()
            elif parts:
                return parts[0][0].upper()
        return "?" # Fallback if name is empty



from django.core.exceptions import ValidationError

class Professional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional')
    field = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='professionals')
    subfield = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills = models.JSONField(default=list)
    photo = models.ImageField(upload_to='professionals/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='hero_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    cv = models.FileField(upload_to='verification/cvs/', blank=True, null=True)
    certificates = models.FileField(upload_to='verification/certificates/', blank=True, null=True)

    def clean(self):
        from .utils import get_default_category
        if self.field is None:
            self.field = get_default_category()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.field if self.field else 'Uncategorized'}"

    def post_count(self):
        return self.articles.count()

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

class PortfolioItem(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='portfolio')
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    file = models.FileField(upload_to='portfolio/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    file = models.FileField(upload_to='messages/', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class Article(models.Model):
    author = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    publish_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    shares = models.PositiveIntegerField(default=0)

    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # For edits
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')  # For replies
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"
    
    @property
    def like_count(self):
        return self.likes.count()

class ServiceReview(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(max_length=500, blank=True)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'professional')

# In core/models.py

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    # Add this field:
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        # Optional: you could include the link in the string representation if helpful
        return f"Notification for {self.user.username}: {self.message}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class Job(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    )
    professional = models.ForeignKey('Professional', null=True, on_delete=models.CASCADE, related_name='jobs')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_jobs', null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    documents = GenericRelation('JobDocument', related_query_name='job')

    def __str__(self):
        return self.title

class ExternalJob(models.Model):
    JOB_TYPE_CHOICES = (
        ('public', 'Public Sector (Government)'),
        ('private', 'Private Sector'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='public')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='external_jobs')
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='external_jobs_created')
    documents = GenericRelation('JobDocument', related_query_name='external_job')
    apply_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct link to the external application page, if available.")

    def __str__(self):
        return self.title
    
class ProfessionalDetailView(DetailView):
    model = Professional
    template_name = 'your_template.html'  # Replace with your template

    def get_queryset(self):
        # Include related fields that *do* have setters, but *exclude* M2M
        field_names = [
            field.name
            for field in Professional._meta.get_fields()
            if not field.many_to_many and (not field.is_relation or field.one_to_one or hasattr(field, "field"))  # Key change
        ]
        return super().get_queryset().only(*field_names)
    

class UpgradeRequest(models.Model):
    UPGRADE_TYPES = (
        ('premium_profile', 'Premium Profile'),
        ('featured_article', 'Featured Article'),
        ('job_boost', 'Job Boost'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upgrade_requests')
    upgrade_type = models.CharField(max_length=50, choices=UPGRADE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_upgrade_type_display()} ({self.status})"
    

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'}"
    

class CustomAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_admin')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Custom Admin: {self.user.username}"

class AdminHelper(models.Model):
    TASKS = (
        ('upload_jobs', 'Upload Jobs'),
        ('manage_users', 'Manage Users'),
        ('verify_professionals', 'Verify Professionals'),
        ('manage_articles', 'Manage Articles'),
    )
    custom_admin = models.ForeignKey(CustomAdmin, on_delete=models.CASCADE, related_name='helpers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='helper_tasks')
    task = models.CharField(max_length=50, choices=TASKS)

    def __str__(self):
        return f"{self.user.username} - {self.get_task_display()}"
    
class JobDocument(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    document = models.FileField(upload_to='job_documents/')

    def __str__(self):
        if self.content_object:
            return f"Document for {self.content_object.title}"
        return "Document (unlinked)"

#For badges
class Badge(models.Model):
    TIER_CHOICES = (
        ('verified_user', 'Verified User'),
        ('verified_professional', 'Verified Professional'),
        ('premium_user', 'Premium User'),
        ('premium_professional', 'Premium Professional'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    tier = models.CharField(max_length=50, choices=TIER_CHOICES)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_tier_display()}"
    

class VerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.username}"