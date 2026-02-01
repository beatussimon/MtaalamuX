"""Integration tests for API endpoints"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from core.models import UserProfile, Category, Professional, Article, Comment
from core.serializers import ArticleSerializer, CategorySerializer, ProfessionalSerializer


class CategoryAPITest(APITestCase):
    """Integration tests for Category API"""
    
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name='Software Development',
            description='Programming and software development'
        )
    
    def test_list_categories(self):
        """Test listing categories"""
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_category(self):
        """Test retrieving a single category"""
        response = self.client.get(f'/api/v1/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Software Development')
    
    def test_create_category_requires_auth(self):
        """Test that creating a category requires authentication"""
        response = self.client.post('/api/v1/categories/', {'name': 'New Category'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProfessionalAPITest(APITestCase):
    """Integration tests for Professional API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='professional',
            email='pro@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Engineering')
        self.professional = Professional.objects.create(
            user=self.user,
            field=self.category,
            is_verified=True
        )
    
    def test_list_professionals(self):
        """Test listing professionals"""
        response = self.client.get('/api/v1/professionals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_professional(self):
        """Test retrieving a single professional"""
        response = self.client.get(f'/api/v1/professionals/{self.professional.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'professional')
    
    def test_filter_by_category(self):
        """Test filtering professionals by category"""
        response = self.client.get('/api/v1/professionals/?category=Engineering')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_professionals(self):
        """Test searching professionals"""
        response = self.client.get('/api/v1/professionals/?q=Engineering')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_follow_professional(self):
        """Test following a professional"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/v1/professionals/{self.professional.id}/follow/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'followed')


class ArticleAPITest(APITestCase):
    """Integration tests for Article API"""
    
    def setUp(self):
        self.client = APIClient()
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
        self.article = Article.objects.create(
            author=self.professional,
            title='Test Article',
            content='This is test content',
            is_published=True
        )
    
    def test_list_articles(self):
        """Test listing articles"""
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_retrieve_article(self):
        """Test retrieving a single article"""
        response = self.client.get(f'/api/v1/articles/{self.article.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')
    
    def test_article_increment_views(self):
        """Test that viewing an article increments view count"""
        initial_views = self.article.views
        self.client.get(f'/api/v1/articles/{self.article.id}/')
        self.article.refresh_from_db()
        self.assertEqual(self.article.views, initial_views + 1)
    
    def test_like_article(self):
        """Test liking an article"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/v1/articles/{self.article.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'liked')
    
    def test_create_article_requires_auth(self):
        """Test that creating an article requires authentication"""
        response = self.client.post('/api/v1/articles/', {
            'title': 'New Article',
            'content': 'Content'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentAPITest(APITestCase):
    """Integration tests for Comment API"""
    
    def setUp(self):
        self.client = APIClient()
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
            content='Content',
            is_published=True
        )
    
    def test_list_comments(self):
        """Test listing comments for an article"""
        Comment.objects.create(
            article=self.article,
            user=self.user,
            content='Test comment'
        )
        response = self.client.get(f'/api/v1/articles/{self.article.id}/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_comment(self):
        """Test creating a comment"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f'/api/v1/articles/{self.article.id}/comments/',
            {'content': 'New comment'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)


class AuthenticationAPITest(APITestCase):
    """Integration tests for Authentication API"""
    
    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['username'], 'newuser')
    
    def test_user_login(self):
        """Test user login and token retrieval"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_refresh(self):
        """Test token refresh"""
        # First login to get tokens
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = login_response.data['refresh']
        
        # Refresh the token
        response = self.client.post('/api/v1/auth/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints require authentication"""
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_access_me(self):
        """Test authenticated user can access their profile"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')


class HealthCheckAPITest(APITestCase):
    """Integration tests for Health Check API"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
