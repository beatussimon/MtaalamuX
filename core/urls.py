from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='home'),
    path('professionals/', views.ProfessionalListView.as_view(), name='professional_list'),
    path('professionals/<int:pk>/', views.ProfessionalDetailView.as_view(), name='professional_detail'),
    path('insights/', views.insights, name='insights'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    path('become-professional/', views.become_professional, name='become_professional'),
    path('add-portfolio/', views.add_portfolio, name='add_portfolio'),
    path('messages/', views.view_messages, name='messages'),
    path('messages/<int:recipient_id>/', views.view_messages, name='messages_with'),
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
    # path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('clear_notifications/', views.clear_notifications, name='clear_notifications'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('accounts/professionals/', RedirectView.as_view(url='/professionals/', permanent=True), name='redirect_professionals'),
    path('logout/', views.logout_view, name='logout'),
    #path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),

    # Admin dashboard paths
    path('admin-dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin/assign-helper/', views.assign_helper, name='assign_helper'),
    path('admin/upload-job/', views.admin_upload_job, name='admin_upload_job'),
    path('admin/verify-professional/<int:professional_id>/', views.verify_professional, name='verify_professional'),
    path('admin/verify-upgrade/<int:upgrade_id>/', views.verify_upgrade, name='verify_upgrade'),
    path('admin/export-data/', views.export_data, name='export_data'),
    path('admin/toggle-user/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin/remove-helper/<int:helper_id>/', views.remove_helper, name='remove_helper'),
    path('admin/delete-professional/<int:professional_id>/', views.delete_professional, name='delete_professional'),
]

accounts_urlpatterns = [
    path('signup/', views.signup, name='signup'),
]

urlpatterns += accounts_urlpatterns