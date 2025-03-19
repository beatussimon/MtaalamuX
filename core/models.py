from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.generic import DetailView


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

class Professional(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    field = models.CharField(max_length=100)
    subfield = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    skills = models.CharField(max_length=255, default="")  # Changed to CharField
    bio = models.TextField()
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    credentials_file = models.FileField(upload_to='credentials/', blank=True, null=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    availability = models.CharField(max_length=100, blank=True)
    social_links = models.JSONField(default=dict)
    badges = models.JSONField(default=list)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateTimeField(blank=True, null=True)
    # follower_count = models.PositiveIntegerField(default=0)  <- REMOVE THIS LINE

    def __str__(self):
        return f"{self.user.username} - {self.field}"
    
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
    category = models.CharField(max_length=100)
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
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

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

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=200)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class Job(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='open')
    created_at = models.DateTimeField(auto_now_add=True)


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