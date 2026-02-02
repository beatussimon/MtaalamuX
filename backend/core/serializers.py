"""Serializers for MtaalamuX API"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    UserProfile, Category, Professional, PortfolioItem, Message,
    Article, Comment, ServiceReview, Favorite, Notification,
    ActivityLog, Job, ExternalJob, UpgradeRequest, FAQ,
    Feedback, JobDocument, Badge, Research, Consultation,
    ConsultationTask, ConsultationApplication, ConsultationMessage,
    Conversation, PaymentMethod, PaymentRecord, DigitalItem,
    MerchItem, Purchase, VerificationRequest, TopExpert,
    FeaturedContent, UserTier, VerificationLevel, SiteSettings
)


# =============================================================================
# USER & PROFILE SERIALIZERS
# =============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields don't match"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Auto-create user profile for new users
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    user = UserSerializer(read_only=True)
    is_basic = serializers.BooleanField(read_only=True)
    is_plus = serializers.BooleanField(read_only=True)
    is_premium = serializers.BooleanField(read_only=True)
    can_initiate_consultation = serializers.BooleanField(read_only=True)
    can_post_content = serializers.BooleanField(read_only=True)
    can_sell_items = serializers.BooleanField(read_only=True)
    display_tier = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'interests', 'theme']


# =============================================================================
# CATEGORY SERIALIZERS
# =============================================================================

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    initials = serializers.SerializerMethodField()
    professional_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'description', 'initials', 'professional_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_initials(self, obj):
        return obj.get_initials()
    
    def get_professional_count(self, obj):
        return obj.professionals.filter(is_verified=True).count()


class CategorySimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for category (nested representations)"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'image']


# =============================================================================
# PROFESSIONAL SERIALIZERS
# =============================================================================

class ProfessionalSerializer(serializers.ModelSerializer):
    """Serializer for Professional model"""
    user = UserSerializer(read_only=True)
    field = CategorySimpleSerializer(read_only=True)
    field_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='field', write_only=True, allow_null=True)
    follower_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    article_count = serializers.IntegerField(read_only=True)
    research_count = serializers.IntegerField(read_only=True)
    has_green_checkmark = serializers.BooleanField(read_only=True)
    has_gold_checkmark = serializers.BooleanField(read_only=True)
    has_verification = serializers.BooleanField(read_only=True)
    display_verification = serializers.CharField(read_only=True)
    
    class Meta:
        model = Professional
        fields = [
            'id', 'user', 'field', 'field_id', 'subfield', 'location', 'skills',
            'photo', 'hero_image', 'bio', 'is_verified', 'verification_level',
            'verification_notes', 'verified_at', 'followers', 'follower_count',
            'average_rating', 'article_count', 'research_count',
            'has_green_checkmark', 'has_gold_checkmark', 'has_verification',
            'display_verification', 'is_featured', 'featured_at',
            'linkedin_url', 'twitter_url', 'github_url', 'website_url',
            'cv', 'certificates', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_verified', 'verification_level', 
                           'verification_notes', 'verified_at', 'verified_by',
                           'followers', 'created_at', 'updated_at']


class ProfessionalListSerializer(serializers.ModelSerializer):
    """Serializer for listing professionals"""
    user = UserSerializer(read_only=True)
    field = CategorySimpleSerializer(read_only=True)
    followers_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()
    has_verification = serializers.SerializerMethodField()
    
    class Meta:
        model = Professional
        fields = [
            'id', 'user', 'field', 'subfield', 'location', 'skills',
            'photo', 'bio', 'is_verified', 'verification_level', 'has_verification',
            'followers_count', 'avg_rating', 'article_count', 'is_featured'
        ]
    
    def get_followers_count(self, obj):
        # Use annotation if available, otherwise use model property
        if hasattr(obj, '_followers_count'):
            return obj._followers_count
        return obj.follower_count
    
    def get_avg_rating(self, obj):
        # Use annotation if available, otherwise use model property
        if hasattr(obj, '_avg_rating'):
            return obj._avg_rating
        return obj.average_rating
    
    def get_article_count(self, obj):
        # Use model property directly
        return obj.article_count
    
    def get_has_verification(self, obj):
        return obj.has_verification


class ProfessionalMiniSerializer(serializers.ModelSerializer):
    """Mini serializer for professionals (embedded use)"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Professional
        fields = ['id', 'user', 'photo', 'bio', 'is_verified', 'verification_level']


# =============================================================================
# PORTFOLIO SERIALIZERS
# =============================================================================

class PortfolioItemSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioItem model"""
    professional_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='professional', write_only=True)
    
    class Meta:
        model = PortfolioItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# =============================================================================
# CONVERSATION & MESSAGE SERIALIZERS
# =============================================================================

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, source='participants', write_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_ids', 'subject', 
            'consultation_type', 'status', 'created_at', 'updated_at',
            'created_by', 'last_message', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                sender__in=obj.participants.exclude(id=request.user.id),
                is_read=False
            ).count()
        return 0


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['id', 'sender', 'conversation', 'timestamp', 'is_read']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ['content', 'file', 'image', 'parent']
    
    def validate_file(self, value):
        """Validate file size against settings"""
        from .models import SiteSettings
        if value:
            max_size = SiteSettings.get_message_file_size_limit()
            if value.size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                raise serializers.ValidationError(
                    f'File size exceeds maximum allowed ({max_size_mb:.1f}MB)'
                )
        return value
    
    def validate_image(self, value):
        """Validate image size against settings"""
        from .models import SiteSettings
        if value:
            max_size = SiteSettings.get_max_image_size()
            if value.size > max_size:
                max_size_mb = max_size / (1024 * 1024)
                raise serializers.ValidationError(
                    f'Image size exceeds maximum allowed ({max_size_mb:.1f}MB)'
                )
        return value


# =============================================================================
# ARTICLE SERIALIZERS
# =============================================================================

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    author = ProfessionalSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    engagement_score = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'image', 'category', 'category_id',
            'publish_date', 'is_published', 'is_featured', 'views', 'likes', 'shares',
            'like_count', 'is_liked', 'comments_count', 'engagement_score', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'publish_date', 'views', 'likes', 'shares', 'updated_at']
    
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False
    
    def get_comments_count(self, obj):
        return obj.comments.count()


class ArticleListSerializer(serializers.ModelSerializer):
    """Serializer for listing articles"""
    author = ProfessionalMiniSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'image', 'category',
            'publish_date', 'is_published', 'is_featured', 'views', 
            'like_count', 'is_liked', 'shares'
        ]
    
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating articles"""
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'category', 'is_published']


# =============================================================================
# RESEARCH SERIALIZERS
# =============================================================================

class ResearchSerializer(serializers.ModelSerializer):
    """Serializer for Research model"""
    author = ProfessionalSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    engagement_score = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Research
        fields = [
            'id', 'author', 'title', 'abstract', 'content', 'document', 'image',
            'category', 'category_id', 'tags', 'publish_date', 'status',
            'is_featured', 'views', 'likes', 'shares', 'like_count',
            'is_liked', 'engagement_score', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'publish_date', 'views', 'likes', 'shares', 'updated_at']
    
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False


class ResearchListSerializer(serializers.ModelSerializer):
    """Serializer for listing research"""
    author = ProfessionalMiniSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Research
        fields = [
            'id', 'author', 'title', 'abstract', 'image', 'category',
            'publish_date', 'status', 'is_featured', 'views',
            'like_count', 'is_liked', 'shares'
        ]
    
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False


class ResearchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating research"""
    
    class Meta:
        model = Research
        fields = ['title', 'abstract', 'content', 'document', 'image', 'category', 'tags', 'status']


# =============================================================================
# COMMENT SERIALIZERS
# =============================================================================

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = UserSerializer(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'research', 'user', 'content', 'created_at', 'updated_at',
            'parent', 'likes', 'like_count', 'is_liked', 'replies'
        ]
        read_only_fields = ['id', 'article', 'research', 'user', 'created_at', 'updated_at', 'likes']
    
    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False
    
    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = Comment
        fields = ['content', 'parent']


# =============================================================================
# REVIEW SERIALIZERS
# =============================================================================

class ServiceReviewSerializer(serializers.ModelSerializer):
    """Serializer for ServiceReview model"""
    reviewer = UserSerializer(read_only=True)
    professional = ProfessionalSerializer(read_only=True)
    
    class Meta:
        model = ServiceReview
        fields = '__all__'
        read_only_fields = ['id', 'reviewer', 'professional', 'created_at', 'updated_at']


class ServiceReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


# =============================================================================
# FAVORITE SERIALIZERS
# =============================================================================

class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for Favorite model"""
    professional = ProfessionalListSerializer(read_only=True)
    professional_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='professional', write_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'professional', 'professional_id', 'created_at']
        read_only_fields = ['id', 'created_at']


# =============================================================================
# NOTIFICATION SERIALIZERS
# =============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'user', 'notification_type', 'title', 'message', 'link', 'created_at']


# =============================================================================
# ACTIVITY LOG SERIALIZERS
# =============================================================================

class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model"""
    
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ['id', 'user', 'action', 'timestamp']


# =============================================================================
# JOB SERIALIZERS
# =============================================================================

class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    professional = ProfessionalSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='client', write_only=True, allow_null=True)
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['id', 'professional', 'client', 'created_at', 'updated_at']


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for listing jobs"""
    professional = ProfessionalListSerializer(read_only=True)
    
    class Meta:
        model = Job
        fields = ['id', 'professional', 'title', 'description', 'budget', 'status', 'created_at']


class ExternalJobSerializer(serializers.ModelSerializer):
    """Serializer for ExternalJob model"""
    category = CategorySimpleSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ExternalJob
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class ExternalJobListSerializer(serializers.ModelSerializer):
    """Serializer for listing external jobs"""
    category = CategorySimpleSerializer(read_only=True)
    
    class Meta:
        model = ExternalJob
        fields = ['id', 'title', 'description', 'budget', 'job_type', 'category', 'location', 
                  'apply_url', 'contact_email', 'contact_phone', 'provider_name', 'provider_url', 'created_at']


# =============================================================================
# CONSULTATION SERIALIZERS
# =============================================================================

class ConsultationSerializer(serializers.ModelSerializer):
    """Serializer for Consultation model"""
    client = UserSerializer(read_only=True)
    expert = ProfessionalSerializer(read_only=True)
    expert_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='expert', write_only=True)
    
    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ['id', 'client', 'expert', 'created_at', 'updated_at']


class ConsultationMessageSerializer(serializers.ModelSerializer):
    """Serializer for ConsultationMessage model"""
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = ConsultationMessage
        fields = '__all__'
        read_only_fields = ['id', 'consultation', 'sender', 'created_at']


class ConsultationTaskSerializer(serializers.ModelSerializer):
    """Serializer for ConsultationTask model"""
    expert = ProfessionalSerializer(read_only=True)
    expert_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='expert', write_only=True)
    category = CategorySimpleSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True, allow_null=True)
    
    class Meta:
        model = ConsultationTask
        fields = '__all__'
        read_only_fields = ['id', 'expert', 'applicant_count', 'created_at', 'updated_at']


class ConsultationApplicationSerializer(serializers.ModelSerializer):
    """Serializer for ConsultationApplication model"""
    task = ConsultationTaskSerializer(read_only=True)
    task_id = serializers.PrimaryKeyRelatedField(queryset=ConsultationTask.objects.all(), source='task', write_only=True)
    applicant = UserSerializer(read_only=True)
    
    class Meta:
        model = ConsultationApplication
        fields = '__all__'
        read_only_fields = ['id', 'applicant', 'created_at', 'updated_at']


# =============================================================================
# PAYMENT SERIALIZERS
# =============================================================================

class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model"""
    
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentRecordSerializer(serializers.ModelSerializer):
    """Serializer for PaymentRecord model"""
    user = UserSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)
    
    class Meta:
        model = PaymentRecord
        fields = '__all__'
        read_only_fields = ['id', 'user', 'payment_method', 'verified_by', 'verified_at', 'created_at', 'updated_at']


# =============================================================================
# DIGITAL ITEMS & MERCH SERIALIZERS
# =============================================================================

class DigitalItemSerializer(serializers.ModelSerializer):
    """Serializer for DigitalItem model"""
    seller = ProfessionalSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='seller', write_only=True)
    
    class Meta:
        model = DigitalItem
        fields = '__all__'
        read_only_fields = ['id', 'seller', 'sales_count', 'created_at', 'updated_at']


class MerchItemSerializer(serializers.ModelSerializer):
    """Serializer for MerchItem model"""
    seller = ProfessionalSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(queryset=Professional.objects.all(), source='seller', write_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = MerchItem
        fields = '__all__'
        read_only_fields = ['id', 'seller', 'sales_count', 'created_at', 'updated_at', 'is_in_stock']


class PurchaseSerializer(serializers.ModelSerializer):
    """Serializer for Purchase model"""
    buyer = UserSerializer(read_only=True)
    
    class Meta:
        model = Purchase
        fields = '__all__'
        read_only_fields = ['id', 'buyer', 'created_at', 'updated_at']


# =============================================================================
# UPGRADE & VERIFICATION SERIALIZERS
# =============================================================================

class UpgradeRequestSerializer(serializers.ModelSerializer):
    """Serializer for UpgradeRequest model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UpgradeRequest
        fields = '__all__'
        read_only_fields = ['id', 'user', 'status', 'requested_at', 'updated_at', 'reviewed_by', 'reviewed_at']


class UpgradeRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating upgrade requests"""
    
    class Meta:
        model = UpgradeRequest
        fields = ['upgrade_type', 'notes', 'payment_method', 'payment_reference', 
                  'lawyer_confirmation_letter', 'supporting_documents']
    
    def validate(self, attrs):
        upgrade_type = attrs.get('upgrade_type')
        
        # Premium upgrades require lawyer confirmation letter
        if upgrade_type == 'premium':
            if not attrs.get('lawyer_confirmation_letter'):
                raise serializers.ValidationError({
                    'lawyer_confirmation_letter': 'Lawyer confirmation letter is required for Premium tier upgrades'
                })
        
        # Plus upgrades require payment
        if upgrade_type == 'plus':
            if not attrs.get('payment_method') or not attrs.get('payment_reference'):
                raise serializers.ValidationError({
                    'payment': 'Payment information is required for Plus tier upgrades'
                })
        
        return attrs


class VerificationRequestSerializer(serializers.ModelSerializer):
    """Serializer for VerificationRequest model"""
    professional = ProfessionalSerializer(read_only=True)
    
    class Meta:
        model = VerificationRequest
        fields = '__all__'
        read_only_fields = ['id', 'professional', 'status', 'requested_at', 'updated_at', 'reviewed_by', 'reviewed_at']


class VerificationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating verification requests"""
    
    class Meta:
        model = VerificationRequest
        fields = ['requested_level', 'notes', 'documents']


# =============================================================================
# FAQ & FEEDBACK SERIALIZERS
# =============================================================================

class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model"""
    
    class Meta:
        model = FAQ
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['id', 'user', 'submitted_at', 'updated_at']


class SiteSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SiteSettings model"""
    
    class Meta:
        model = SiteSettings
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']


# =============================================================================
# JOB DOCUMENT SERIALIZERS
# =============================================================================

class JobDocumentSerializer(serializers.ModelSerializer):
    """Serializer for JobDocument model"""
    
    class Meta:
        model = JobDocument
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at']


# =============================================================================
# BADGE SERIALIZERS
# =============================================================================

class BadgeSerializer(serializers.ModelSerializer):
    """Serializer for Badge model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Badge
        fields = '__all__'
        read_only_fields = ['id', 'awarded_at']


# =============================================================================
# TOP EXPERTS & FEATURED CONTENT SERIALIZERS
# =============================================================================

class TopExpertSerializer(serializers.ModelSerializer):
    """Serializer for TopExpert model"""
    professional = ProfessionalListSerializer(read_only=True)
    
    class Meta:
        model = TopExpert
        fields = '__all__'
        read_only_fields = ['id', 'added_at', 'updated_at']


class FeaturedContentSerializer(serializers.ModelSerializer):
    """Serializer for FeaturedContent model"""
    
    class Meta:
        model = FeaturedContent
        fields = '__all__'
        read_only_fields = ['id', 'featured_at']
