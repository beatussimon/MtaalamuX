from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Professional, UserProfile, Article, Comment
from .forms import UserProfileForm


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.professional = Professional.objects.create(user=self.user, field=self.category)

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Test Category')

    def test_professional_str(self):
        self.assertEqual(str(self.professional), f"{self.user.username} - {self.category}")

    def test_user_profile_str(self):
        self.assertEqual(str(self.user_profile), self.user.username)

    def test_article_creation(self):
        article = Article.objects.create(
            author=self.professional,
            title='Test Article',
            content='Test content'
        )
        self.assertEqual(article.title, 'Test Article')
        self.assertEqual(str(article), 'Test Article')

    def test_comment_creation(self):
        article = Article.objects.create(
            author=self.professional,
            title='Test Article',
            content='Test content'
        )
        comment = Comment.objects.create(
            article=article,
            user=self.user,
            content='Test comment'
        )
        self.assertEqual(comment.content, 'Test comment')
        self.assertEqual(str(comment), f"{self.user.username} - Test comment")


class ViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.professional = Professional.objects.create(user=self.user, field=self.category)

    def test_home_view(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Find Your Perfect Expert')

    def test_professional_list_view(self):
        response = self.client.get(reverse('core:professional_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Experts')


class FormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user_profile = UserProfile.objects.create(user=self.user)

    def test_user_profile_form_valid(self):
        form_data = {
            'bio': 'Test bio',
            'interests': 'Test interests',
            'theme': 'light'
        }
        form = UserProfileForm(data=form_data, instance=self.user_profile)
        self.assertTrue(form.is_valid())
