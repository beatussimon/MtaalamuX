"""Core models for MtaalamuX platform"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


# =============================================================================
# USER TIERS (Non-negotiable)
# =============================================================================

class UserTier:
    """User tier constants"""
    BASIC = 'basic'
    PLUS = 'plus'
    PREMIUM = 'premium'

    CHOICES = [
        (BASIC, 'Basic'),
        (PLUS, 'Plus'),
        (PREMIUM, 'Premium'),
    ]


class VerificationLevel:
    """Verification level constants"""
    NONE = None
    GREEN = 'green'
    GOLD = 'gold'

    CHOICES = [
        (NONE, 'None'),
        (GREEN, 'Green Checkmark'),
        (GOLD, 'Gold Checkmark'),
    ]


# =============================================================================
# USER PROFILE
# =============================================================================

class UserProfile(models.Model):
    """Extended user profile with additional attributes"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tier = models.CharField(
        max_length=20,
        choices=UserTier.CHOICES,
        default=UserTier.BASIC
    )
    bio = models.TextField(max_length=1000, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='default_avatar.svg', blank=True)
    interests = models.CharField(max_length=200, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def is_basic(self):
        return self.tier == UserTier.BASIC

    @property
    def is_plus(self):
        return self.tier == UserTier.PLUS

    @property
    def is_premium(self):
        return self.tier == UserTier.PREMIUM

    @property
    def can_initiate_consultation(self):
        """Basic users cannot initiate consultations"""
        return self.tier in [UserTier.PLUS, UserTier.PREMIUM]

    @property
    def can_post_content(self):
        """Only premium users can post articles/research"""
        return self.tier == UserTier.PREMIUM

    @property
    def can_sell_items(self):
        """Only premium users can sell digital items/merch"""
        return self.tier == UserTier.PREMIUM

    @property
    def display_tier(self):
        """UI display name for tier"""
        if self.tier == UserTier.BASIC:
            return "Basic"
        elif self.tier == UserTier.PLUS:
            return "Plus"
        else:
            return "Premium"


# =============================================================================
# CATEGORY
# =============================================================================

class Category(models.Model):
    """Professional categories"""
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_initials(self):
        """Get initials from category name"""
        if self.name:
            parts = self.name.split()
            if len(parts) > 1:
                return (parts[0][0] + parts[1][0]).upper()
            elif parts:
                return parts[0][0].upper()
        return "?"


# =============================================================================
# PROFESSIONAL (Verified Experts)
# =============================================================================

class Professional(models.Model):
    """Professional user profile - verified experts"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='professional')
    field = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='professionals'
    )
    subfield = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    skills = models.JSONField(default=list, blank=True)
    photo = models.ImageField(upload_to='professionals/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='hero_images/', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    # Verification system (non-negotiable)
    is_verified = models.BooleanField(default=False)
    verification_level = models.CharField(
        max_length=10,
        choices=VerificationLevel.CHOICES,
        default=VerificationLevel.NONE
    )
    verification_notes = models.TextField(blank=True)  # Admin notes
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_professionals'
    )
    
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    cv = models.FileField(upload_to='verification/cvs/', blank=True, null=True)
    certificates = models.FileField(upload_to='verification/certificates/', blank=True, null=True)
    
    # Featured status
    is_featured = models.BooleanField(default=False)
    featured_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Professional'
        verbose_name_plural = 'Professionals'

    def clean(self):
        """Set default category if not provided"""
        if self.field is None:
            self.field = Category.objects.first() or Category.objects.create(name="General")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        field_name = self.field.name if self.field else 'Uncategorized'
        return f"{self.user.username} - {field_name}"

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

    @property
    def article_count(self):
        return self.articles.filter(is_published=True).count()

    @property
    def research_count(self):
        return self.research_posts.filter(status='published').count()

    @property
    def has_green_checkmark(self):
        return self.verification_level == VerificationLevel.GREEN

    @property
    def has_gold_checkmark(self):
        return self.verification_level == VerificationLevel.GOLD

    @property
    def has_verification(self):
        return self.verification_level in [VerificationLevel.GREEN, VerificationLevel.GOLD]

    @property
    def display_verification(self):
        """Return verification display for UI"""
        if self.verification_level == VerificationLevel.GREEN:
            return "🟢 Verified Professional"
        elif self.verification_level == VerificationLevel.GOLD:
            return "🟡 Premium Expert"
        return "Verification pending"


# =============================================================================
# PORTFOLIO ITEMS
# =============================================================================

class PortfolioItem(models.Model):
    """Portfolio items for professionals"""
    professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='portfolio'
    )
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    file = models.FileField(upload_to='portfolio/', blank=True)
    image = models.ImageField(upload_to='portfolio/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'

    def __str__(self):
        return self.title


# =============================================================================
# INTERNAL MESSAGING (Core - Consultation Engine)
# =============================================================================

class Conversation(models.Model):
    """Consultation-threaded conversations"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    ]
    
    participants = models.ManyToManyField(User, related_name='conversations')
    subject = models.CharField(max_length=200)
    consultation_type = models.CharField(max_length=50, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_conversations'
    )

    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.subject} - {self.created_at}"


class Message(models.Model):
    """User messages within consultation threads"""
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    content = models.TextField()
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)  # File size in bytes
    image = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def save(self, *args, **kwargs):
        """Track file size on save"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


# =============================================================================
# ARTICLES (Expert Content)
# =============================================================================

class Article(models.Model):
    """Articles published by verified professionals"""
    author = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='articles'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/', blank=True)
    category = models.ForeignKey(
        'Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='articles'
    )
    publish_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True)
    shares = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def engagement_score(self):
        """Calculate engagement score for ranking"""
        return (self.like_count * 2) + self.views + (self.shares * 3)


# =============================================================================
# RESEARCH (Expert Content)
# =============================================================================

class Research(models.Model):
    """Research posts published by verified professionals"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    author = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='research_posts'
    )
    title = models.CharField(max_length=200)
    abstract = models.TextField(max_length=1000)
    content = models.TextField()
    document = models.FileField(upload_to='research/documents/', blank=True, null=True)
    image = models.ImageField(upload_to='research/images/', blank=True)
    category = models.ForeignKey(
        'Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='research'
    )
    tags = models.JSONField(default=list, blank=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_research', blank=True)
    shares = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Research'
        verbose_name_plural = 'Research Papers'
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def engagement_score(self):
        """Calculate engagement score for ranking"""
        return (self.like_count * 3) + (self.views * 2) + (self.shares * 5)


# =============================================================================
# COMMENTS
# =============================================================================

class Comment(models.Model):
    """Comments on articles and research"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    research = models.ForeignKey(Research, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    )
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def target_object(self):
        """Get the parent object (article or research)"""
        if self.article:
            return self.article
        return self.research


# =============================================================================
# REVIEWS
# =============================================================================

class ServiceReview(models.Model):
    """Reviews for professional services"""
    professional = models.ForeignKey(
        Professional, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    response = models.TextField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service Review'
        verbose_name_plural = 'Service Reviews'
        unique_together = ('professional', 'reviewer')

    def __str__(self):
        return f"{self.reviewer.username}'s review of {self.professional.user.username}"


# =============================================================================
# FAVORITES & FOLLOWS
# =============================================================================

class Favorite(models.Model):
    """User favorites (professionals they follow)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        unique_together = ('user', 'professional')

    def __str__(self):
        return f"{self.user.username} favorites {self.professional.user.username}"


# =============================================================================
# NOTIFICATIONS
# =============================================================================

class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('consultation', 'Consultation'),
        ('message', 'Message'),
        ('article', 'Article'),
        ('research', 'Research'),
        ('follow', 'Follow'),
        ('review', 'Review'),
        ('upgrade', 'Upgrade'),
        ('verification', 'Verification'),
        ('job', 'Job'),
        ('payment', 'Payment'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


# =============================================================================
# ACTIVITY LOG
# =============================================================================

class ActivityLog(models.Model):
    """User activity logging"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action}"


# =============================================================================
# JOBS (Internal job postings)
# =============================================================================

class Job(models.Model):
    """Internal job postings"""
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    )
    
    professional = models.ForeignKey(
        Professional, 
        null=True, 
        on_delete=models.CASCADE, 
        related_name='jobs'
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_jobs', 
        null=True, 
        blank=True
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    documents = GenericRelation('JobDocument', related_query_name='job')

    class Meta:
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# =============================================================================
# CONSULTATION SYSTEM (Core Product)
# =============================================================================

class Consultation(models.Model):
    """Consultation requests between users and experts"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consultations_as_client'
    )
    expert = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)  # Default 1 hour
    
    # Payment tracking
    is_paid = models.BooleanField(default=False)
    payment_proof = models.FileField(upload_to='consultation_payments/', blank=True, null=True)
    payment_verified = models.BooleanField(default=False)
    
    # Consultation details
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    meeting_link = models.CharField(max_length=500, blank=True, null=True)
    
    # Feedback
    client_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    client_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client.username} - {self.expert.user.username}: {self.title}"

    @property
    def is_active(self):
        return self.status in ['pending', 'accepted', 'in_progress']


class ConsultationMessage(models.Model):
    """Messages within consultation threads"""
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='consultation_messages/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message in {self.consultation.title}"


# =============================================================================
# CONSULTATION TASKS (Jobs)
# =============================================================================

class ConsultationTask(models.Model):
    """Consultation tasks/opportunities posted by experts"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    expert = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    is_remote = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Application tracking
    applicant_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Consultation Task'
        verbose_name_plural = 'Consultation Tasks'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ConsultationApplication(models.Model):
    """Applications for consultation tasks"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    task = models.ForeignKey(
        ConsultationTask,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_letter = models.TextField()
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} - {self.task.title}"


# =============================================================================
# OFFLINE PAYMENTS (Admin-Editable)
# =============================================================================

class PaymentMethod(models.Model):
    """Mobile payment methods for offline payments"""
    NETWORK_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel'),
        ('tigo', 'Tigo'),
        ('halotel', 'Halotel'),
    ]
    
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES, unique=True)
    network_image = models.ImageField(upload_to='payment_and_verification/', blank=True, null=True)
    lipa_number = models.CharField(max_length=50)  # e.g., "Lipa na M-Pesa 123456"
    payment_instructions = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['order', 'network']

    def __str__(self):
        return f"{self.get_network_display()} - {self.lipa_number}"

    @property
    def display_name(self):
        return f"{self.get_network_display()} ({self.lipa_number})"


class PaymentRecord(models.Model):
    """Record of payments made"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_records')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100)  # e.g., M-Pesa code
    phone_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Record'
        verbose_name_plural = 'Payment Records'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.transaction_reference})"


# =============================================================================
# SECONDARY MONETIZATION (Digital Items & Merch)
# =============================================================================

class DigitalItem(models.Model):
    """Digital items sold by premium experts"""
    CATEGORY_CHOICES = [
        ('book', 'Book'),
        ('guide', 'Guide'),
        ('pdf', 'PDF'),
        ('template', 'Template'),
        ('course', 'Course'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    seller = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='digital_items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='pdf')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='digital_items/')
    preview_image = models.ImageField(upload_to='digital_items/previews/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Digital Item'
        verbose_name_plural = 'Digital Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seller.user.username}: {self.title}"


class MerchItem(models.Model):
    """Merchandise sold by premium experts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('out_of_stock', 'Out of Stock'),
        ('archived', 'Archived'),
    ]
    
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('one_size', 'One Size'),
    ]
    
    seller = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='merch_items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='merch/')
    available_sizes = models.JSONField(default=list, blank=True)
    color = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    stock_quantity = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Merch Item'
        verbose_name_plural = 'Merch Items'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seller.user.username}: {self.title}"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class Purchase(models.Model):
    """Record of purchases (digital items and merch)"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    ]
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    digital_item = models.ForeignKey(
        DigitalItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases'
    )
    merch_item = models.ForeignKey(
        MerchItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'
        ordering = ['-created_at']

    def __str__(self):
        item_name = self.digital_item.title if self.digital_item else self.merch_item.title
        return f"{self.buyer.username}: {item_name}"


# =============================================================================
# EXTERNAL JOBS
# =============================================================================

class ExternalJob(models.Model):
    """External job postings from various sources"""
    JOB_TYPE_CHOICES = (
        ('public', 'Public Sector (Government)'),
        ('private', 'Private Sector'),
    )
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='public')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='external_jobs'
    )
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='external_jobs_created'
    )
    documents = GenericRelation('JobDocument', related_query_name='external_job')
    
    # Application and contact info
    apply_url = models.URLField(max_length=500, blank=True, null=True)
    contact_email = models.EmailField(max_length=254, blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    
    # Provider/source information
    provider_name = models.CharField(max_length=100, blank=True, null=True)
    provider_url = models.URLField(max_length=500, blank=True, null=True)
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'External Job'
        verbose_name_plural = 'External Jobs'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# =============================================================================
# UPGRADE REQUESTS
# =============================================================================

class UpgradeRequest(models.Model):
    """Tier upgrade requests"""
    UPGRADE_TYPES = (
        ('plus', 'Plus Tier'),
        ('premium', 'Premium Tier (Expert)'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='upgrade_requests'
    )
    upgrade_type = models.CharField(max_length=50, choices=UPGRADE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    # Payment information for instant upgrades (Plus)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_verified = models.BooleanField(default=False)
    
    # Document verification for Premium upgrades
    lawyer_confirmation_letter = models.FileField(
        upload_to='upgrade_documents/', 
        blank=True, 
        null=True,
        help_text='Letter from a licensed lawyer confirming expertise (required for Premium)'
    )
    supporting_documents = models.FileField(
        upload_to='upgrade_documents/', 
        blank=True, 
        null=True,
        help_text='Additional supporting documents'
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_upgrade_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Upgrade Request'
        verbose_name_plural = 'Upgrade Requests'
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_upgrade_type_display()} ({self.status})"
    
    @property
    def requires_verification(self):
        """Premium upgrades require document verification"""
        return self.upgrade_type == 'premium'
    
    @property
    def is_instant_upgrade(self):
        """Plus upgrades are instant with payment verification"""
        return self.upgrade_type == 'plus'


# =============================================================================
# VERIFICATION REQUESTS
# =============================================================================

class VerificationRequest(models.Model):
    """Verification requests for professionals"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='verification_requests'
    )
    requested_level = models.CharField(max_length=10, choices=VerificationLevel.CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    documents = models.FileField(upload_to='verification_requests/', blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_verification_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Verification Request'
        verbose_name_plural = 'Verification Requests'

    def __str__(self):
        return f"{self.professional.user.username} - {self.get_requested_level_display()} ({self.status})"


# =============================================================================
# FAQ & FEEDBACK
# =============================================================================

class FAQ(models.Model):
    """Frequently Asked Questions"""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=50, default='general')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question


class Feedback(models.Model):
    """User feedback / Contact form submissions"""
    FEEDBACK_CATEGORIES = [
        ('general', 'General Inquiry'),
        ('support', 'Technical Support'),
        ('billing', 'Billing & Payments'),
        ('verification', 'Verification'),
        ('upgrade', 'Account Upgrade'),
        ('consultation', 'Consultation Issues'),
        ('partnership', 'Partnership'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='feedbacks', 
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True)
    category = models.CharField(max_length=50, choices=FEEDBACK_CATEGORIES, default='general')
    status = models.CharField(max_length=20, choices=[('new', 'New'), ('in_progress', 'In Progress'), ('resolved', 'Resolved')], default='new')
    admin_response = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Feedback: {self.subject or self.message[:50]} from {self.user.username if self.user else self.name or 'Anonymous'}"


# =============================================================================
# JOB DOCUMENTS
# =============================================================================

class JobDocument(models.Model):
    """Generic document attachment for jobs"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    document = models.FileField(upload_to='job_documents/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Job Document'
        verbose_name_plural = 'Job Documents'

    def __str__(self):
        if self.content_object:
            return f"Document for {self.content_object.title}"
        return "Document (unlinked)"


# =============================================================================
# BADGES
# =============================================================================

class Badge(models.Model):
    """User badges"""
    TIER_CHOICES = (
        ('verified_user', 'Verified User'),
        ('verified_professional', 'Verified Professional'),
        ('premium_user', 'Premium User'),
        ('premium_professional', 'Premium Professional'),
        ('top_contributor', 'Top Contributor'),
        ('helpful_member', 'Helpful Member'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    tier = models.CharField(max_length=50, choices=TIER_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='awarded_badges'
    )

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'

    def __str__(self):
        return f"{self.user.username} - {self.tier}"


# =============================================================================
# TOP EXPERTS RANKING
# =============================================================================

class TopExpert(models.Model):
    """Curated top experts for homepage/sections"""
    professional = models.ForeignKey(
        Professional,
        on_delete=models.CASCADE,
        related_name='top_expert_rankings'
    )
    rank = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='added_top_experts'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Top Expert'
        verbose_name_plural = 'Top Experts'
        ordering = ['rank']

    def __str__(self):
        return f"#{self.rank} - {self.professional.user.username}"


# =============================================================================
# FEATURED CONTENT
# =============================================================================

class FeaturedContent(models.Model):
    """Featured articles, research, etc."""
    CONTENT_TYPES = [
        ('article', 'Article'),
        ('research', 'Research'),
    ]
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.PositiveIntegerField()  # ID of the article/research
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='featured/', blank=True, null=True)
    link = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    featured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Featured Content'
        verbose_name_plural = 'Featured Content'
        ordering = ['order', '-featured_at']


# =============================================================================
# SITE SETTINGS (Admin-editable instructions)
# =============================================================================

class SiteSettings(models.Model):
    """Site-wide settings and instructions editable via admin"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=[
        ('text', 'Plain Text'),
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
    ], default='text')
    description = models.CharField(max_length=200, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key, default=''):
        """Get a setting value by key"""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def get_message_file_size_limit(cls, default=10485760):  # Default 10MB
        """Get the maximum file size for message attachments in bytes"""
        try:
            return int(cls.objects.get(key='message_file_size_limit').value)
        except (cls.DoesNotExist, ValueError):
            return default
    
    @classmethod
    def get_max_image_size(cls, default=5242880):  # Default 5MB
        """Get the maximum image size for message images in bytes"""
        try:
            return int(cls.objects.get(key='max_image_size').value)
        except (cls.DoesNotExist, ValueError):
            return default


