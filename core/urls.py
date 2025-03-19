from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='home'),
    path('professionals/', views.ProfessionalListView.as_view(), name='professional_list'),
    path('professionals/<int:pk>/', views.ProfessionalDetailView.as_view(), name='professional_detail'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    path('become-professional/', views.become_professional, name='become_professional'),
    path('add-portfolio/', views.add_portfolio, name='add_portfolio'),
    path('messages/', views.messages, name='messages'),
    path('messages/<int:recipient_id>/', views.messages, name='messages_with'),
    path('post-article/', views.post_article, name='post_article'),
    path('follow/<int:professional_id>/', views.toggle_follow, name='toggle_follow'),
    path('review/<int:professional_id>/', views.review_service, name='review_service'),
    path('post-job/', views.post_job, name='post_job'),
    path('accounts/professionals/', RedirectView.as_view(url='/professionals/', permanent=True), name='redirect_professionals'),
]

accounts_urlpatterns = [
    path('signup/', views.signup, name='signup'),
]

urlpatterns += accounts_urlpatterns