"""Views for MtaalamuX API"""
from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F
from django.db.models.functions import Coalesce
from django.db.models import FloatField, ExpressionWrapper, IntegerField
from django.utils import timezone
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
from .serializers import (
    UserSerializer, UserCreateSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, CategorySerializer, CategorySimpleSerializer,
    ProfessionalSerializer, ProfessionalListSerializer, PortfolioItemSerializer,
    MessageSerializer, MessageCreateSerializer, ArticleSerializer,
    ArticleListSerializer, ArticleCreateSerializer, ArticleDetailSerializer,
    CommentSerializer, CommentCreateSerializer, ServiceReviewSerializer, ServiceReviewCreateSerializer,
    FavoriteSerializer, NotificationSerializer, JobSerializer, JobListSerializer,
    ExternalJobSerializer, ExternalJobListSerializer, UpgradeRequestSerializer,
    UpgradeRequestCreateSerializer, FAQSerializer, FeedbackSerializer,
    ResearchSerializer, ResearchListSerializer, ResearchCreateSerializer, ResearchDetailSerializer,
    ConsultationSerializer, ConsultationTaskSerializer, ConsultationApplicationSerializer,
    ConversationSerializer, MessageCreateSerializer, PaymentMethodSerializer,
    PaymentRecordSerializer, DigitalItemSerializer, MerchItemSerializer,
    PurchaseSerializer, VerificationRequestSerializer, VerificationRequestCreateSerializer,
    TopExpertSerializer, FeaturedContentSerializer, ConsultationMessageSerializer,
    ActivityLogSerializer, SiteSettingsSerializer
)
from .permissions import (
    IsOwnerOrReadOnly, IsProfessionalOrReadOnly, CanUpgradeUser,
    IsBasicUser, IsProfessionalUser, IsPremiumUser,
    CanPostContent, CanInitiateConsultation, CanSellItems,
    IsVerifiedExpert, IsGoldVerifiedExpert, IsStaffOrReadOnly
)
from .throttling import ArticleCreateThrottle, MessageThrottle, JobPostThrottle, ReviewThrottle


# =============================================================================
# USER VIEWS
# =============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        if self.action == 'me':
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get user profile"""
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update current user profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def tier_info(self, request):
        """Get current user tier info"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return Response({
            'tier': profile.tier,
            'display_tier': profile.display_tier,
            'is_basic': profile.is_basic,
            'is_plus': profile.is_plus,
            'is_premium': profile.is_premium,
            'can_initiate_consultation': profile.can_initiate_consultation,
            'can_post_content': profile.can_post_content,
            'can_sell_items': profile.can_sell_items,
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)


# =============================================================================
# CATEGORY VIEWS
# =============================================================================

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model"""
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategorySerializer
        return CategorySimpleSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def with_professionals(self, request):
        """Get categories that have verified professionals"""
        categories = Category.objects.filter(
            professionals__is_verified=True
        ).distinct().annotate(
            professional_count=Count('professionals', filter=Q(professionals__is_verified=True))
        )
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


# =============================================================================
# PROFESSIONAL VIEWS
# =============================================================================

class ProfessionalViewSet(viewsets.ModelViewSet):
    """ViewSet for Professional model"""
    queryset = Professional.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProfessionalListSerializer
        return ProfessionalSerializer
    
    def get_queryset(self):
        try:
            queryset = Professional.objects.filter(is_verified=True)
            
            # Filter by category
            category = self.request.query_params.get('category')
            if category:
                queryset = queryset.filter(field__name__iexact=category)
            
            # Search
            query = self.request.query_params.get('q')
            if query:
                queryset = queryset.filter(
                    Q(field__name__icontains=query) |
                    Q(subfield__icontains=query) |
                    Q(location__icontains=query) |
                    Q(skills__icontains=query)
                ).distinct()
            
            # Filter by verification level
            verification = self.request.query_params.get('verification')
            if verification:
                queryset = queryset.filter(verification_level=verification)
            
            # Filter featured
            featured = self.request.query_params.get('featured')
            if featured and featured.lower() == 'true':
                queryset = queryset.filter(is_featured=True)
            
            # Annotate with counts using underscore prefix to avoid conflict with model properties
            # The serializer will check for these annotations first, then fall back to model properties
            queryset = queryset.annotate(
                _followers_count=Count('followers', distinct=True),
                _avg_rating=ExpressionWrapper(
                    Coalesce(Avg('reviews__rating'), 0.0),
                    output_field=FloatField()
                )
            )
            
            return queryset
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in ProfessionalViewSet.get_queryset: {str(e)}")
            return Professional.objects.none()
    
    def get_permissions(self):
        # Allow anyone to list and retrieve professionals (public read access)
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # Write operations require authentication
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        # Get or create professional for user
        professional, created = Professional.objects.get_or_create(
            user=self.request.user,
            defaults=serializer.validated_data
        )
        if not created:
            for key, value in serializer.validated_data.items():
                setattr(professional, key, value)
            professional.save()
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Follow a professional"""
        professional = self.get_object()
        if request.user in professional.followers.all():
            professional.followers.remove(request.user)
            return Response({'status': 'unfollowed'})
        professional.followers.add(request.user)
        return Response({'status': 'followed'})
    
    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """Get articles by this professional"""
        try:
            professional = get_object_or_404(Professional, pk=pk)
            articles = professional.articles.filter(is_published=True)
            serializer = ArticleListSerializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in articles endpoint: {str(e)}")
            # Return empty list instead of 500 error
            return Response([])
    
    @action(detail=True, methods=['get'])
    def research(self, request, pk=None):
        """Get research by this professional"""
        try:
            professional = get_object_or_404(Professional, pk=pk)
            research = professional.research_posts.filter(status='published')
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in research endpoint: {str(e)}")
            # Return empty list instead of 500 error
            return Response([])
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for this professional"""
        try:
            professional = get_object_or_404(Professional, pk=pk)
            reviews = professional.reviews.all()
            serializer = ServiceReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in reviews endpoint: {str(e)}")
            # Return empty list instead of 500 error
            return Response([])
    
    @action(detail=True, methods=['get'])
    def portfolio(self, request, pk=None):
        """Get portfolio items for this professional"""
        try:
            professional = get_object_or_404(Professional, pk=pk)
            portfolio = professional.portfolio.all()
            serializer = PortfolioItemSerializer(portfolio, many=True)
            return Response(serializer.data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in portfolio endpoint: {str(e)}")
            # Return empty list instead of 500 error
            return Response([])


# =============================================================================
# PORTFOLIO VIEWS
# =============================================================================

class PortfolioItemViewSet(viewsets.ModelViewSet):
    """ViewSet for PortfolioItem model"""
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemSerializer
    permission_classes = [IsAuthenticated, IsPremiumUser]
    
    def get_queryset(self):
        professional_id = self.kwargs.get('professional_pk')
        if professional_id:
            return PortfolioItem.objects.filter(professional_id=professional_id)
        return PortfolioItem.objects.all()
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        serializer.save(professional=professional)


# =============================================================================
# CONVERSATION & MESSAGE VIEWS
# =============================================================================

class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation model"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model"""
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]
    # Throttling disabled - not configured in settings
    # throttle_classes = [MessageThrottle]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id:
            return Message.objects.filter(conversation_id=conversation_id)
        # For direct messages, filter by conversations the user participates in
        return Message.objects.filter(
            Q(conversation__participants=self.request.user)
        )
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            # Check if user can message in this conversation
            if not self._can_message_in_conversation(conversation):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You do not have permission to send messages in this conversation.")
            serializer.save(conversation=conversation, sender=self.request.user)
        else:
            # For direct messages, create or get conversation
            recipient_id = self.request.data.get('recipient_id')
            if recipient_id:
                from django.contrib.auth.models import User
                recipient = get_object_or_404(User, id=recipient_id)
                # Check if user can initiate messaging with this recipient
                if not self._can_initiate_messaging_with(recipient):
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("You do not have permission to message this user.")
                # Find or create conversation between these users
                conversation = Conversation.objects.filter(
                    participants=self.request.user
                ).filter(
                    participants=recipient
                ).first()
                if not conversation:
                    conversation = Conversation.objects.create(
                        subject=f'Chat with {recipient.username}',
                        created_by=self.request.user
                    )
                    conversation.participants.add(self.request.user, recipient)
                serializer.save(conversation=conversation, sender=self.request.user)
            else:
                serializer.save(sender=self.request.user)

    def _can_initiate_messaging_with(self, recipient):
        """Check if user can initiate messaging with recipient (expert)"""
        # Must be Plus or Premium
        user_profile = self.request.user.userprofile
        if user_profile.is_basic:
            return False

        # Check if recipient is a professional
        try:
            professional = recipient.professional
        except:
            return False  # Not a professional

        if user_profile.is_premium:
            # Premium users can message if expert allows instant messaging or has consultation
            has_consultation = Consultation.objects.filter(
                client=self.request.user,
                expert=professional,
                status__in=['accepted', 'in_progress', 'completed']
            ).exists()
            return professional.allow_instant_messaging or has_consultation
        elif user_profile.is_plus:
            # Plus users can only message if they have an accepted consultation
            return Consultation.objects.filter(
                client=self.request.user,
                expert=professional,
                status__in=['accepted', 'in_progress', 'completed']
            ).exists()
        return False

    def _can_message_in_conversation(self, conversation):
        """Check if user can send messages in existing conversation"""
        # For now, allow if user is participant
        # Could add more checks later
        return conversation.participants.filter(id=self.request.user.id).exists()
    
    @action(detail=False, methods=['get'])
    def inbox(self, request):
        """Get inbox messages - actually returns conversations"""
        conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get total unread message count across all conversations"""
        count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def unread_conversations(self, request):
        """Get conversations with unread messages"""
        conversations = Conversation.objects.filter(
            participants=request.user,
            messages__is_read=False
        ).exclude(
            messages__sender=request.user
        ).distinct()
        serializer = ConversationSerializer(conversations, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get sent messages - returns user's messages across all conversations"""
        messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        """Get conversation with a specific user"""
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id required'}, status=400)
        
        # Find conversation between these users
        conversations = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user_id
        )
        
        if not conversations.exists():
            return Response([])
        
        messages = conversations.first().messages.all().order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark message as read with timestamp"""
        from django.utils import timezone
        message = self.get_object()
        if not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        return Response({'status': 'marked_read', 'read_at': message.read_at})
    
    @action(detail=True, methods=['post'])
    def mark_all_read(self, request, pk=None):
        """Mark all messages in a conversation as read"""
        conversation = self.get_object()
        from django.utils import timezone
        updated = Message.objects.filter(
            conversation=conversation,
            is_read=False
        ).exclude(sender=request.user).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'status': 'marked_read', 'count': updated})


# =============================================================================
# ARTICLE VIEWS
# =============================================================================

class ArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for Article model"""
    queryset = Article.objects.all()
    # Throttling disabled - not configured in settings
    # throttle_classes = [ArticleCreateThrottle]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.action == 'create':
            return ArticleCreateSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), CanPostContent()]
    
    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        
        # Filter featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        
        # Order by engagement
        sort = self.request.query_params.get('sort')
        if sort == 'popular':
            queryset = queryset.order_by('-views', '-like_count')
        else:
            queryset = queryset.order_by('-publish_date')
        
        return queryset
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        serializer.save(author=professional)
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count on retrieve"""
        import logging
        logger = logging.getLogger(__name__)
        try:
            instance = self.get_object()
            instance.views += 1
            instance.save(update_fields=['views'])
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error retrieving article: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def my_drafts(self, request):
        """Get unpublished articles for the current author"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            professional = Professional.objects.get(user=request.user)
            articles = Article.objects.filter(
                author=professional,
                is_published=False
            ).order_by('-updated_at')
            serializer = ArticleListSerializer(articles, many=True)
            return Response(serializer.data)
        except Professional.DoesNotExist:
            return Response({'error': 'You are not a professional'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like/unlike an article"""
        article = self.get_object()
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            return Response({'status': 'unliked', 'like_count': article.like_count})
        article.likes.add(request.user)
        return Response({'status': 'liked', 'like_count': article.like_count})
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share an article"""
        article = self.get_object()
        article.shares += 1
        article.save()
        return Response({'status': 'shared', 'shares': article.shares})
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or create comments for an article"""
        if request.method == 'GET':
            try:
                article = self.get_object()
                comments = article.comments.filter(parent__isnull=True)
                serializer = CommentSerializer(comments, many=True, context={'request': request})
                return Response(serializer.data)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error fetching article comments for id {pk}: {str(e)}")
                # Return empty list instead of 500 error
                return Response([])
        
        # POST - Create comment
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to post comments'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            article = self.get_object()
            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(article=article, user=request.user)
                return Response(CommentSerializer(comment, context={'request': request}).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating article comment: {str(e)}", exc_info=True)
            return Response({'error': 'Failed to create comment', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending articles"""
        articles = Article.objects.filter(
            is_published=True
        ).annotate(
            calculated_score=ExpressionWrapper(
                (Count('likes', distinct=True) * 2) + Count('views') + (Count('shares') * 3),
                output_field=IntegerField()
            )
        ).order_by('-calculated_score')[:10]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top(self, request):
        """Get top articles"""
        articles = Article.objects.filter(
            is_published=True, is_featured=True
        ).annotate(
            calculated_score=ExpressionWrapper(
                (Count('likes', distinct=True) * 2) + Count('views') + (Count('shares') * 3),
                output_field=IntegerField()
            )
        ).order_by('-calculated_score', '-publish_date')[:10]
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)


# =============================================================================
# RESEARCH VIEWS
# =============================================================================

class ResearchViewSet(viewsets.ModelViewSet):
    """ViewSet for Research model"""
    queryset = Research.objects.all()
    pagination_class = None  # Disable pagination to return 200 with empty list instead of 404
    # Throttling disabled - not configured in settings
    # throttle_classes = [ArticleCreateThrottle]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ResearchListSerializer
        if self.action == 'create':
            return ResearchCreateSerializer
        if self.action == 'retrieve':
            return ResearchDetailSerializer
        return ResearchSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), CanPostContent()]
    
    def get_queryset(self):
        queryset = Research.objects.filter(status='published')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        
        # Filter featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(abstract__icontains=query) |
                Q(content__icontains=query)
            )
        
        return queryset.order_by('-publish_date')
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        # Set initial status based on user tier - Premium users can publish directly
        user_profile = professional.user.userprofile
        initial_status = 'published' if user_profile.is_premium else 'draft'
        serializer.save(author=professional, status=initial_status)
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count on retrieve"""
        import logging
        logger = logging.getLogger(__name__)
        try:
            instance = self.get_object()
            instance.views += 1
            instance.save(update_fields=['views'])
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error retrieving research: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def my_drafts(self, request):
        """Get unpublished research for the current author"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            professional = Professional.objects.get(user=request.user)
            research = Research.objects.filter(
                author=professional,
                status__in=['draft', 'pending']
            ).order_by('-updated_at')
            serializer = ResearchListSerializer(research, many=True)
            return Response(serializer.data)
        except Professional.DoesNotExist:
            return Response({'error': 'You are not a professional'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit research for review"""
        research = self.get_object()
        if research.status != 'draft':
            return Response(
                {'error': 'Only draft research can be submitted for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        research.status = 'pending'
        research.save()
        return Response({'status': 'submitted', 'message': 'Research submitted for review'})
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish research (Premium users only or admin)"""
        research = self.get_object()
        user_profile = request.user.userprofile
        
        if not (user_profile.is_premium or request.user.is_staff):
            return Response(
                {'error': 'Only Premium users or admins can publish research directly'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        research.status = 'published'
        research.save()
        return Response({'status': 'published', 'message': 'Research published successfully'})
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like/unlike a research"""
        research = self.get_object()
        if request.user in research.likes.all():
            research.likes.remove(request.user)
            return Response({'status': 'unliked', 'like_count': research.like_count})
        research.likes.add(request.user)
        return Response({'status': 'liked', 'like_count': research.like_count})
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share a research"""
        research = self.get_object()
        research.shares += 1
        research.save()
        return Response({'status': 'shared', 'shares': research.shares})
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """Get or create comments for a research"""
        from .models import Comment
        
        if request.method == 'GET':
            try:
                research = self.get_object()
                comments = Comment.objects.filter(research=research, parent__isnull=True)
                serializer = CommentSerializer(comments, many=True, context={'request': request})
                return Response(serializer.data)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error fetching research comments for id {pk}: {str(e)}")
                # Return empty list instead of 500 error
                return Response([])
        
        # POST - Create comment
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to post comments'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            research = self.get_object()
            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(research=research, user=request.user)
                return Response(CommentSerializer(comment, context={'request': request}).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
    
    @action(detail=False, methods=['get'])
    def top(self, request):
        """Get top research"""
        research = Research.objects.filter(
            status='published', is_featured=True
        ).annotate(
            calculated_score=ExpressionWrapper(
                (Count('likes', distinct=True) * 3) + (Count('views') * 2) + Count('shares'),
                output_field=IntegerField()
            )
        ).order_by('-calculated_score')[:10]
        serializer = ResearchListSerializer(research, many=True)
        return Response(serializer.data)


# =============================================================================
# COMMENT VIEWS
# =============================================================================

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model"""
    queryset = Comment.objects.all()
    permission_classes = [AllowAny]  # Allow read access for all, write requires auth
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        research_id = self.kwargs.get('research_pk')
        if article_id:
            return Comment.objects.filter(article_id=article_id)
        if research_id:
            return Comment.objects.filter(research_id=research_id)
        return Comment.objects.all()
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to post comments'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        article_id = self.kwargs.get('article_pk')
        research_id = self.kwargs.get('research_pk')
        if article_id:
            article = get_object_or_404(Article, id=article_id)
            serializer.save(article=article, user=self.request.user)
        elif research_id:
            research = get_object_or_404(Research, id=research_id)
            serializer.save(research=research, user=self.request.user)
        else:
            serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Override create to handle unauthenticated users gracefully"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to post comments'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None, article_pk=None, research_pk=None):
        """Like/unlike a comment"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to like comments'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        comment = self.get_object()
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            return Response({'status': 'unliked', 'like_count': comment.like_count})
        comment.likes.add(request.user)
        return Response({'status': 'liked', 'like_count': comment.like_count})


# =============================================================================
# REVIEW VIEWS
# =============================================================================

class ServiceReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for ServiceReview model"""
    queryset = ServiceReview.objects.all()
    permission_classes = [IsAuthenticated]
    # Throttling disabled - not configured in settings
    # throttle_classes = [ReviewThrottle]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceReviewCreateSerializer
        return ServiceReviewSerializer
    
    def get_queryset(self):
        professional_id = self.kwargs.get('professional_pk')
        if professional_id:
            return ServiceReview.objects.filter(professional_id=professional_id)
        return ServiceReview.objects.all()
    
    def perform_create(self, serializer):
        professional_id = self.kwargs.get('professional_pk')
        professional = get_object_or_404(Professional, id=professional_id)
        serializer.save(professional=professional, reviewer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None, professional_pk=None):
        """Respond to a review (professional only)"""
        review = self.get_object()
        if review.professional.user != request.user:
            return Response(
                {'error': 'Only the professional can respond to reviews'},
                status=status.HTTP_403_FORBIDDEN
            )
        review.response = request.data.get('response', '')
        review.save()
        return Response(ServiceReviewSerializer(review).data)


# =============================================================================
# FAVORITE VIEWS
# =============================================================================

class FavoriteViewSet(viewsets.ModelViewSet):
    """ViewSet for Favorite model"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def professionals(self, request):
        """Get favorited professionals"""
        favorites = Favorite.objects.filter(user=request.user)
        professional_ids = favorites.values_list('professional_id', flat=True)
        professionals = Professional.objects.filter(id__in=professional_ids)
        serializer = ProfessionalListSerializer(professionals, many=True)
        return Response(serializer.data)


# =============================================================================
# NOTIFICATION VIEWS
# =============================================================================

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification model"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        from django.utils import timezone
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'status': 'all_marked_read'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read with timestamp"""
        from django.utils import timezone
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
        return Response({'status': 'marked_read', 'read_at': notification.read_at})


# =============================================================================
# JOB VIEWS
# =============================================================================

class JobViewSet(viewsets.ModelViewSet):
    """ViewSet for Job model"""
    queryset = Job.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Job.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Get jobs created by current user"""
        jobs = Job.objects.filter(client=request.user)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def accept_proposal(self, request, pk=None):
        """Accept a professional's proposal for a job"""
        job = self.get_object()
        if job.client != request.user:
            return Response(
                {'error': 'Only the job client can accept proposals'},
                status=status.HTTP_403_FORBIDDEN
            )
        proposal_id = request.data.get('proposal_id')
        if not proposal_id:
            return Response({'error': 'proposal_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update job status and assign professional
        job.professional_id = proposal_id
        job.status = 'in_progress'
        job.save()
        return Response({'status': 'accepted', 'message': 'Proposal accepted'})
    
    @action(detail=True, methods=['post'])
    def reject_proposal(self, request, pk=None):
        """Reject a professional's proposal for a job"""
        job = self.get_object()
        if job.client != request.user:
            return Response(
                {'error': 'Only the job client can reject proposals'},
                status=status.HTTP_403_FORBIDDEN
            )
        proposal_id = request.data.get('proposal_id')
        reason = request.data.get('reason', '')
        # Here you would create a rejection record
        return Response({'status': 'rejected', 'reason': reason})
    
    @action(detail=True, methods=['get'])
    def proposals(self, request, pk=None):
        """Get all proposals for a job"""
        job = self.get_object()
        if job.client != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        # Assuming there's a JobProposal model or similar
        # This is a placeholder
        return Response({'proposals': [], 'message': 'Proposals endpoint - implement JobProposal model'})


class ExternalJobViewSet(viewsets.ModelViewSet):
    """ViewSet for ExternalJob model"""
    queryset = ExternalJob.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExternalJobListSerializer
        return ExternalJobSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsStaffOrReadOnly()]
    
    def get_queryset(self):
        queryset = ExternalJob.objects.filter(is_active=True)
        
        # Filter by job type
        job_type = self.request.query_params.get('job_type')
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# =============================================================================
# CONSULTATION VIEWS
# =============================================================================

class ConsultationViewSet(viewsets.ModelViewSet):
    """ViewSet for Consultation model"""
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated, CanInitiateConsultation]
    
    def get_queryset(self):
        # Users can see their own consultations
        return Consultation.objects.filter(
            Q(client=self.request.user) |
            Q(expert__user=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        expert_id = serializer.validated_data.get('expert').id
        expert = get_object_or_404(Professional, id=expert_id)
        serializer.save(client=self.request.user, expert=expert)
    
    @action(detail=False, methods=['get'])
    def my_consultations(self, request):
        """Get consultations for current user"""
        consultations = Consultation.objects.filter(
            Q(client=request.user) | Q(expert__user=request.user)
        )
        serializer = ConsultationSerializer(consultations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def as_client(self, request):
        """Get consultations where user is client"""
        consultations = Consultation.objects.filter(client=request.user)
        serializer = ConsultationSerializer(consultations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def as_expert(self, request):
        """Get consultations where user is expert"""
        if hasattr(request.user, 'professional'):
            consultations = Consultation.objects.filter(expert=request.user.professional)
            serializer = ConsultationSerializer(consultations, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['post'])
    def message_expert(self, request):
        """Start a direct message conversation with an expert"""
        expert_id = request.data.get('expert_id')
        message = request.data.get('message')
        
        if not expert_id:
            return Response({'error': 'expert_id required'}, status=status.HTTP_400_BAD_REQUEST)
        if not message:
            return Response({'error': 'message required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            expert = Professional.objects.get(id=expert_id)
        except Professional.DoesNotExist:
            return Response({'error': 'Expert not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user can initiate consultation with this expert
        user_profile = request.user.userprofile
        if not user_profile.can_initiate_consultation:
            return Response(
                {'error': 'Only Plus and Premium users can message experts directly. Please upgrade your account.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Find or create conversation between these users
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=expert.user
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                subject=f'Consultation inquiry with {expert.user.username}',
                created_by=request.user
            )
            conversation.participants.add(request.user, expert.user)
        
        # Create the message
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=message
        )
        
        return Response({
            'status': 'message_sent',
            'conversation_id': conversation.id,
            'message': 'Your message has been sent to the expert'
        })


class ConsultationTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for ConsultationTask model"""
    queryset = ConsultationTask.objects.all()
    serializer_class = ConsultationTaskSerializer
    permission_classes = [IsAuthenticated, IsPremiumUser]
    
    def get_queryset(self):
        queryset = ConsultationTask.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        serializer.save(expert=professional)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks created by current user"""
        if hasattr(request.user, 'professional'):
            tasks = ConsultationTask.objects.filter(expert=request.user.professional)
            serializer = ConsultationTaskSerializer(tasks, many=True)
            return Response(serializer.data)
        return Response([])


class ConsultationApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for ConsultationApplication model"""
    queryset = ConsultationApplication.objects.all()
    serializer_class = ConsultationApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConsultationApplication.objects.filter(applicant=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        """Get applications by current user"""
        applications = ConsultationApplication.objects.filter(applicant=request.user)
        serializer = ConsultationApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get applications for tasks created by current user"""
        if hasattr(request.user, 'professional'):
            applications = ConsultationApplication.objects.filter(
                task__expert=request.user.professional
            )
            serializer = ConsultationApplicationSerializer(applications, many=True)
            return Response(serializer.data)
        return Response([])


# =============================================================================
# PAYMENT VIEWS
# =============================================================================

class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentMethod model"""
    queryset = PaymentMethod.objects.filter(is_active=True)
    serializer_class = PaymentMethodSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class PaymentRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for PaymentRecord model"""
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentRecord.objects.filter(user=self.request.user)


# =============================================================================
# DIGITAL ITEMS & MERCH VIEWS
# =============================================================================

class DigitalItemViewSet(viewsets.ModelViewSet):
    """ViewSet for DigitalItem model"""
    queryset = DigitalItem.objects.filter(status='published')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DigitalItemSerializer
        return DigitalItemSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), CanSellItems()]
    
    def get_queryset(self):
        queryset = DigitalItem.objects.filter(status='published')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        serializer.save(seller=professional)
    
    @action(detail=False, methods=['get'])
    def my_items(self, request):
        """Get items sold by current user"""
        if hasattr(request.user, 'professional'):
            items = DigitalItem.objects.filter(seller=request.user.professional)
            serializer = DigitalItemSerializer(items, many=True)
            return Response(serializer.data)
        return Response([])


class MerchItemViewSet(viewsets.ModelViewSet):
    """ViewSet for MerchItem model"""
    queryset = MerchItem.objects.filter(status='published', stock_quantity__gt=0)
    
    def get_serializer_class(self):
        return MerchItemSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), CanSellItems()]
    
    def get_queryset(self):
        queryset = MerchItem.objects.filter(status='published')
        
        # Filter by color
        color = self.request.query_params.get('color')
        if color:
            queryset = queryset.filter(color__iexact=color)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        serializer.save(seller=professional)
    
    @action(detail=False, methods=['get'])
    def my_items(self, request):
        """Get items sold by current user"""
        if hasattr(request.user, 'professional'):
            items = MerchItem.objects.filter(seller=request.user.professional)
            serializer = MerchItemSerializer(items, many=True)
            return Response(serializer.data)
        return Response([])


class PurchaseViewSet(viewsets.ModelViewSet):
    """ViewSet for Purchase model"""
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Purchase.objects.filter(buyer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_purchases(self, request):
        """Get purchases by current user"""
        purchases = Purchase.objects.filter(buyer=request.user)
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(serializer.data)


# =============================================================================
# UPGRADE & VERIFICATION VIEWS
# =============================================================================

class UpgradeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for UpgradeRequest model"""
    queryset = UpgradeRequest.objects.all()
    permission_classes = [IsAuthenticated, CanUpgradeUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UpgradeRequestCreateSerializer
        return UpgradeRequestSerializer
    
    def get_queryset(self):
        return UpgradeRequest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VerificationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for VerificationRequest model"""
    queryset = VerificationRequest.objects.all()
    permission_classes = [IsAuthenticated, IsPremiumUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VerificationRequestCreateSerializer
        return VerificationRequestSerializer
    
    def get_queryset(self):
        if hasattr(self.request.user, 'professional'):
            return VerificationRequest.objects.filter(professional=self.request.user.professional)
        return VerificationRequest.objects.none()
    
    def perform_create(self, serializer):
        professional = get_object_or_404(Professional, user=self.request.user)
        serializer.save(professional=professional)


# =============================================================================
# FAQ & FEEDBACK VIEWS
# =============================================================================

class FAQViewSet(viewsets.ModelViewSet):
    """ViewSet for FAQ model"""
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = FAQ.objects.filter(is_published=True)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset.order_by('order', 'created_at')


class FeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for Feedback model"""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Feedback.objects.filter(user=self.request.user)
        return Feedback.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class SiteSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for SiteSettings model"""
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """Get a setting by key"""
        key = request.query_params.get('key')
        if not key:
            return Response({'error': 'key parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            setting = SiteSettings.objects.get(key=key)
            serializer = self.get_serializer(setting)
            return Response(serializer.data)
        except SiteSettings.DoesNotExist:
            return Response({'value': None})


# =============================================================================
# TOP EXPERTS & FEATURED CONTENT VIEWS
# =============================================================================

class TopExpertViewSet(viewsets.ModelViewSet):
    """ViewSet for TopExpert model"""
    queryset = TopExpert.objects.filter(is_active=True)
    serializer_class = TopExpertSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        return TopExpert.objects.filter(is_active=True).order_by('rank')


class FeaturedContentViewSet(viewsets.ModelViewSet):
    """ViewSet for FeaturedContent model"""
    queryset = FeaturedContent.objects.filter(is_active=True)
    serializer_class = FeaturedContentSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        queryset = FeaturedContent.objects.filter(is_active=True)
        
        # Filter by content type
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        return queryset.order_by('order', '-featured_at')


# =============================================================================
# ACTIVITY LOG VIEWS
# =============================================================================

class ActivityLogViewSet(viewsets.ModelViewSet):
    """ViewSet for ActivityLog model"""
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)


# =============================================================================
# HEALTH CHECK
# =============================================================================

class HealthCheckView(views.APIView):
    """Health check endpoint"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat()
        })


# =============================================================================
# HOMEPAGE DATA
# =============================================================================

class HomepageView(views.APIView):
    """Homepage data endpoint - returns role-aware content"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        data = {
            'featured_experts': None,
            'top_research': None,
            'trending_articles': None,
            'statistics': {},
        }
        
        try:
            # Featured experts (verified professionals)
            # Using underscore prefix for annotations to avoid conflict with model properties
            featured_experts = Professional.objects.filter(
                is_verified=True, is_featured=True
            ).annotate(
                _followers_count=Count('followers', distinct=True),
                _avg_rating=Coalesce(Avg('reviews__rating'), 0.0, output_field=FloatField())
            ).order_by('-_followers_count')[:6]
            data['featured_experts'] = ProfessionalListSerializer(featured_experts, many=True).data
            
            # Top research - use database annotation instead of property
            # Note: views and shares are integer fields, likes is M2M
            top_research = Research.objects.filter(
                status='published'
            ).annotate(
                calculated_score=ExpressionWrapper(
                    (Count('likes', distinct=True) * 3) + (F('views') * 2) + F('shares'),
                    output_field=IntegerField()
                )
            ).order_by('-calculated_score')[:5]
            data['top_research'] = ResearchListSerializer(top_research, many=True).data
            
            # Trending articles - use database annotation instead of property
            # Note: views and shares are integer fields, likes is M2M
            trending_articles = Article.objects.filter(
                is_published=True
            ).annotate(
                calculated_score=ExpressionWrapper(
                    (Count('likes', distinct=True) * 2) + F('views') + (F('shares') * 3),
                    output_field=IntegerField()
                )
            ).order_by('-calculated_score')[:5]
            data['trending_articles'] = ArticleListSerializer(trending_articles, many=True).data
            
            # Statistics
            data['statistics'] = {
                'total_experts': Professional.objects.filter(is_verified=True).count(),
                'total_articles': Article.objects.filter(is_published=True).count(),
                'total_research': Research.objects.filter(status='published').count(),
                'total_consultations': Consultation.objects.count(),
            }
            
            # For authenticated users, add personalized data
            if request.user.is_authenticated:
                profile = getattr(request.user, 'profile', None)
                if profile:
                    data['user_tier'] = profile.tier
                    data['display_tier'] = profile.display_tier
                    
                    # Add ongoing consultations
                    ongoing = Consultation.objects.filter(
                        Q(client=request.user) | Q(expert__user=request.user),
                        status__in=['pending', 'accepted', 'in_progress']
                    ).count()
                    data['ongoing_consultations'] = ongoing
            
            return Response(data)
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in HomepageView: {str(e)}")
            # Return minimal safe data
            return Response({
                'featured_experts': [],
                'top_research': [],
                'trending_articles': [],
                'statistics': {
                    'total_experts': 0,
                    'total_articles': 0,
                    'total_research': 0,
                    'total_consultations': 0,
                },
                'error': 'Failed to load homepage data'
            }, status=500)
