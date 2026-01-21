from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, F, FloatField, Value, Avg
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.db import models
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q, Count, F, FloatField, Value, Avg
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import csv
from .utils import get_default_category  # Import the function
from django.contrib import messages
from .models import Professional, Article, Message, UserProfile, Favorite, UpgradeRequest, Comment, FAQ, Feedback, ServiceReview, Notification, ActivityLog, Job, Category, Badge, AdminHelper, JobDocument, ExternalJob
from .forms import ProfessionalForm, PortfolioItemForm, MessageForm, ArticleForm, ServiceReviewForm, UserProfileForm, JobForm
from django.contrib.auth.forms import UserCreationForm  # For signup
from django.contrib.auth import login, logout  # To log in the user after signup
from django.contrib.auth.models import User  # For recipient lookup in messages view
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.db import models
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q, Count, F, FloatField, Value, Avg
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import csv
from .utils import get_default_category  # Import the function
from django.contrib import messages


class ArticleListView(ListView):
    model = Article
    template_name = 'core/home.html' # Assuming this maps to '/'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        # This is the main query for articles on the home page
        return Article.objects.filter(is_published=True).order_by('-publish_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Get Top Professionals (using the correct annotation pattern) ---
        # Start with the base queryset for verified professionals
        professionals_qs = Professional.objects.filter(is_verified=True)

        # Annotate with follower count and average rating using DB functions
        professionals_qs = professionals_qs.annotate(
            follower_count_annotated=Count('followers', distinct=True),
            avg_rating_annotated=Coalesce(
                Avg('reviews__rating'),     # Calculate Avg rating from related ServiceReviews
                Value(0.0),                 # Default to 0.0 if no reviews
                output_field=FloatField()
            )
        )

        # Fetch the annotated professionals into a Python list
        professionals_list = list(professionals_qs)

        # Calculate sort score in Python using the annotated values
        for professional in professionals_list:
            # Access the annotated values calculated by the database
            follower_count = professional.follower_count_annotated
            avg_rating = professional.avg_rating_annotated
            # Store the calculated score on a temporary attribute (e.g., _sort_score)
            professional._sort_score = (0.7 * follower_count) + (0.3 * avg_rating * 100)

        # Sort the list in Python based on the temporary score and take top 6
        context['top_professionals'] = sorted(
            professionals_list,
            key=lambda x: getattr(x, '_sort_score', 0), # Use getattr for safety
            reverse=True
        )[:6]

        # --- Recent jobs ---
        context['recent_jobs'] = Job.objects.filter(status='open').order_by('-created_at')[:5]

        return context

class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'core/article_detail.html'
    context_object_name = 'article'
    initial_comments_limit = 5

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        obj.views += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        context['articles'] = article.author.articles.filter(is_published=True).order_by('-publish_date')[:5]
        context['is_following'] = self.request.user in article.author.followers.all() if self.request.user.is_authenticated else False
        context['comments'] = article.comments.filter(parent__isnull=True).order_by('-created_at')[:self.initial_comments_limit]
        context['total_comments'] = article.comments.filter(parent__isnull=True).count()
        context['comments_limit'] = self.initial_comments_limit
        return context

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        user = request.user

        if 'comment' in request.POST:
            content = request.POST['comment'].strip()
            if content:
                comment = Comment.objects.create(article=article, user=user, content=content)
                Notification.objects.create(
                    user=article.author.user,
                    message=f"{user.username} commented on your article",
                    link=f"/articles/{article.id}/"
                )
        elif 'reply' in request.POST:
            content = request.POST['reply'].strip()
            parent_id = request.POST.get('parent_id')
            if content and parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
                comment = Comment.objects.create(article=article, user=user, content=content, parent=parent)
                Notification.objects.create(
                    user=parent.user,
                    message=f"{user.username} replied to your comment",
                    link=f"/articles/{article.id}/"
                )
        elif 'edit_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            content = request.POST['edit_comment'].strip()
            comment = get_object_or_404(Comment, id=comment_id, user=user)
            if content:
                comment.content = content
                comment.save()
        elif 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, user=user)
            comment.delete()
        elif 'like_comment' in request.POST:  # New: Like/Unlike comment
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id)
            if user in comment.likes.all():
                comment.likes.remove(user)
            else:
                comment.likes.add(user)
                Notification.objects.create(
                    user=comment.user,
                    message=f"{user.username} liked your comment",
                    link=f"/articles/{article.id}/"
                )

        return redirect('core:article_detail', pk=article.id)

    def get(self, request, *args, **kwargs):
        if 'load_more' in request.GET:
            article = self.get_object()
            offset = int(request.GET.get('offset', 0))
            limit = self.initial_comments_limit
            comments = article.comments.filter(parent__isnull=True).order_by('-created_at')[offset:offset + limit]
            comments_html = ""
            for comment in comments:
                comments_html += self.render_comment(comment)
            has_more = article.comments.filter(parent__isnull=True).count() > offset + limit
            return JsonResponse({'comments_html': comments_html, 'has_more': has_more})
        return super().get(request, *args, **kwargs)

    # core/views.py (partial update)
    def render_comment(self, comment):
        user = self.request.user
        html = f"""
        <div class="comment d-flex gap-3 mb-4" id="comment-{comment.id}">
            <img src="{comment.user.userprofile.avatar.url if comment.user.userprofile.avatar else '/static/img/default_avatar.svg'}" class="rounded-circle" alt="{comment.user.username}'s Avatar" style="width: 40px; height: 40px; object-fit: cover;">
            <div class="comment-body flex-grow-1">
                <p class="mb-1">
                    {"<a href='" + reverse('core:professional_detail', args=[comment.user.professional.id]) + "' class='text-dark text-decoration-none fw-bold'>" + comment.user.username + "</a>" if hasattr(comment.user, 'professional') else f"<span class='text-dark fw-bold'>{comment.user.username}</span>"}
                    <span class="text-muted small ms-2">{timesince(comment.created_at)} ago</span>
                    {" (Edited)" if comment.created_at != comment.updated_at else ""}
                </p>
                <p class="text-dark">{comment.content}</p>
                """
        if user.is_authenticated:
            html += f"""
                <div class="comment-actions d-flex gap-3 align-items-center">
                    <form method="post" class="d-inline like-comment-form">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{self.request.POST.get('csrfmiddlewaretoken', '')}">
                        <input type="hidden" name="like_comment" value="true">
                        <input type="hidden" name="comment_id" value="{comment.id}">
                        <button type="submit" class="btn p-0 text-muted" title="{'Unlike' if user in comment.likes.all() else 'Like'}">
                            <i class="fas fa-heart {'text-danger' if user in comment.likes.all() else 'text-muted'}"></i> {comment.like_count}
                        </button>
                    </form>
                    <button class="btn p-0 text-muted reply-btn" data-comment-id="{comment.id}" title="Reply">
                        <i class="fas fa-reply"></i>
                    </button>
                    """
            if comment.user == user:
                html += f"""
                    <button class="btn p-0 text-muted edit-btn" data-comment-id="{comment.id}" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn p-0 text-muted delete-btn" data-comment-id="{comment.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                    """
            html += """
                </div>
                """
        html += """
            </div>
        </div>
        """
        return html