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
    path('profile/', views.user_profile, name='user_profile'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    path('become-professional/', views.become_professional, name='become_professional'),
    path('add-portfolio/', views.add_portfolio, name='add_portfolio'),
    path('messages/', views.messages, name='messages'),
    path('messages/<int:recipient_id>/', views.messages, name='messages_with'),
    path('post-article/', views.post_article, name='post_article'),
    path('follow/<int:professional_id>/', views.toggle_follow, name='toggle_follow'),
    path('review/<int:professional_id>/', views.review_service, name='review_service'),
    path('post-job/', views.post_job, name='post_job'),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('upgrade/', views.upgrade, name='upgrade'),
    path('faq/', views.faq, name='faq'),
    path('feedback/', views.feedback, name='feedback'),
    path('notifications/', views.notifications, name='notifications'),
    #path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/assign-helper/', views.assign_helper, name='assign_helper'),
    path('admin/upload-job/', views.admin_upload_job, name='admin_upload_job'),
    path('admin/verify-professional/<int:professional_id>/', views.verify_professional, name='verify_professional'),
    path('accounts/professionals/', RedirectView.as_view(url='/professionals/', permanent=True), name='redirect_professionals'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/verify-upgrade/<int:upgrade_id>/', views.verify_upgrade, name='verify_upgrade'),
    path('signup/', views.signup, name='signup'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
]

accounts_urlpatterns = [
    path('signup/', views.signup, name='signup'),
]

urlpatterns += accounts_urlpatterns