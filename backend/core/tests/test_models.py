"""Unit tests for core models"""
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import UserProfile, Category, Professional, Article, Comment


class UserProfileModelTest(TestCase):
    """Tests for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertFalse(profile.is_professional)
        self.assertEqual(profile.theme, 'light')
    
    def test_user_profile_str(self):
        """Test user profile string representation"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "testuser's Profile")
    
    def test_profile_theme_choice(self):
        """Test profile theme choices"""
        profile = UserProfile.objects.create(user=self.user, theme='dark')
        self.assertEqual(profile.theme, 'dark')


class CategoryModelTest(TestCase):
    """Tests for Category model"""
    
    def test_create_category(self):
        """Test creating a category"""
        category = Category.objects.create(
            name='Software Development',
            description='Software development related'
        )
        self.assertEqual(category.name, 'Software Development')
        self.assertEqual(str(category), 'Software Development')
    
    def test_category_get_initials(self):
        """Test category initials generation"""
        category = Category.objects.create(name='Software Development')
        self.assertEqual(category.get_initials(), 'SD')
    
    def test_category_get_initials_single_word(self):
        """Test category initials with single word"""
        category = Category.objects.create(name='Design')
        self.assertEqual(category.get_initials(), 'D')
    
    def test_category_get_initials_empty(self):
        """Test category initials with empty name"""
        category = Category.objects.create(name='')
        self.assertEqual(category.get_initials(), '?')


class ProfessionalModelTest(TestCase):
    """Tests for Professional model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='professional',
            email='pro@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Engineering')
    
    def test_create_professional(self):
        """Test creating a professional"""
        professional = Professional.objects.create(
            user=self.user,
            field=self.category,
            subfield='Civil Engineering',
            location='Nairobi'
        )
        self.assertEqual(professional.user, self.user)
        self.assertEqual(professional.field, self.category)
        self.assertFalse(professional.is_verified)
    
    def test_professional_str(self):
        """Test professional string representation"""
        professional = Professional.objects.create(
            user=self.user,
            field=self.category
        )
        self.assertIn('professional', str(professional))
    
    def test_follower_count(self):
        """Test follower count property"""
        professional = Professional.objects.create(
            user=self.user,
            field=self.category
        )
        # Create another user to follow
        follower = User.objects.create_user(
            username='follower',
            email='follower@example.com',
            password='testpass123'
        )
        professional.followers.add(follower)
        self.assertEqual(professional.follower_count, 1)
    
    def test_average_rating_no_reviews(self):
        """Test average rating with no reviews"""
        professional = Professional.objects.create(
            user=self.user,
            field=self.category
        )
        self.assertEqual(professional.average_rating, 0)
    
    def test_professional_clean_sets_default_category(self):
        """Test that clean sets default category"""
        professional = Professional.objects.create(
            user=self.user,
            field=None
        )
        # Should not raise error and should set a category
        professional.clean()
        self.assertIsNotNone(professional.field)


class ArticleModelTest(TestCase):
    """Tests for Article model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Technology')
        self.professional = Professional.objects.create(
            user=self.user,
            field=self.category
        )
    
    def test_create_article(self):
        """Test creating an article"""
        article = Article.objects.create(
            author=self.professional,
            title='Test Article',
            content='This is a test article content'
        )
        self.assertEqual(article.title, 'Test Article')
        self.assertTrue(article.is_published)
        self.assertEqual(article.views, 0)
    
    def test_article_str(self):
        """Test article string representation"""
        article = Article.objects.create(
            author=self.professional,
            title='My Test Article',
            content='Content'
        )
        self.assertEqual(str(article), 'My Test Article')
    
    def test_like_count(self):
        """Test like count property"""
        article = Article.objects.create(
            author=self.professional,
            title='Test Article',
            content='Content'
        )
        user = User.objects.create_user(
            username='liker',
            email='liker@example.com',
            password='testpass123'
        )
        article.likes.add(user)
        self.assertEqual(article.like_count, 1)


class CommentModelTest(TestCase):
    """Tests for Comment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='General')
        self.professional = Professional.objects.create(
            user=self.user,
            field=self.category
        )
        self.article = Article.objects.create(
            author=self.professional,
            title='Test Article',
            content='Content'
        )
    
    def test_create_comment(self):
        """Test creating a comment"""
        comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            content='This is a test comment'
        )
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertIsNone(comment.parent)
    
    def test_comment_str(self):
        """Test comment string representation"""
        comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            content='A very long comment content that exceeds twenty characters'
        )
        self.assertIn('commenter', str(comment))
    
    def test_reply_comment(self):
        """Test creating a reply to a comment"""
        parent_comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            content='Parent comment'
        )
        reply = Comment.objects.create(
            article=self.article,
            user=self.user,
            content='Reply comment',
            parent=parent_comment
        )
        self.assertEqual(reply.parent, parent_comment)
        self.assertEqual(parent_comment.replies.count(), 1)
    
    def test_like_count(self):
        """Test like count property"""
        comment = Comment.objects.create(
            article=self.article,
            user=self.user,
            content='Comment'
        )
        liker = User.objects.create_user(
            username='liker',
            email='liker@example.com',
            password='testpass123'
        )
        comment.likes.add(liker)
        self.assertEqual(comment.like_count, 1)
