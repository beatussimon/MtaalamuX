from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q #Count  # Add Count for annotation
from .models import Professional, Article, Message, UserProfile, Favorite,UpgradeRequest, Comment,FAQ, Feedback, ServiceReview, Notification, ActivityLog, Job, Category, Badge, AdminHelper, JobDocument, ExternalJob
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


def custom_admin_or_helper_required(view_func):
    def check_user(user):
        if not user.is_authenticated:
            return False
        # Check if user is a custom admin
        if hasattr(user, 'custom_admin') and user.custom_admin.is_active:
            return True
        # Check if user is an assigned helper
        return AdminHelper.objects.filter(user=user, custom_admin__is_active=True).exists()
    
    decorated_view = user_passes_test(check_user, login_url='login')(view_func)
    return decorated_view


class ProfessionalListView(ListView):
    model = Professional
    template_name = 'core/professional_list.html'
    context_object_name = 'professionals'
    paginate_by = 12

    def get_queryset(self):
        # Base queryset: only verified professionals
        queryset = Professional.objects.filter(is_verified=True).select_related('field', 'user')

        # Apply filters
        query = self.request.GET.get('q')
        category_name = self.request.GET.get('category')
        if category_name:
            queryset = queryset.filter(field__name__iexact=category_name)
        if query:
            field_q = Q(field__name__icontains=query)
            subfield_q = Q(subfield__icontains=query)
            location_q = Q(location__icontains=query)
            skills_q = Q(skills__icontains=query)  # Assumes skills is a JSONField or text
            combined_q = field_q | subfield_q | location_q | skills_q
            queryset = queryset.filter(combined_q).distinct()

        # Annotate with follower count and average rating
        queryset = queryset.annotate(
            follower_count_annotated=Count('followers', distinct=True),
            avg_rating_annotated=Coalesce(Avg('reviews__rating'), Value(0.0), output_field=FloatField())
        )

        # Convert to list for custom sorting
        professionals_list = list(queryset)
        for p in professionals_list:
            p._sort_score = (0.7 * p.follower_count_annotated) + (0.3 * p.avg_rating_annotated * 100)

        # Sort by score
        return sorted(professionals_list, key=lambda x: getattr(x, '_sort_score', 0), reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Categories: only those with verified professionals
        context['categories'] = Category.objects.filter(
            professionals__is_verified=True
        ).distinct().order_by('name')

        # Manual pagination since queryset is a list
        professionals_sorted = self.get_queryset()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(professionals_sorted, self.paginate_by)
        try:
            professionals_paginated = paginator.page(page)
        except PageNotAnInteger:
            professionals_paginated = paginator.page(1)
        except EmptyPage:
            professionals_paginated = paginator.page(paginator.num_pages)

        context['professionals'] = professionals_paginated
        context['paginator'] = paginator
        context['is_paginated'] = paginator.num_pages > 1
        context['page_obj'] = professionals_paginated
        context['selected_category'] = self.request.GET.get('category', '')
        context['query'] = self.request.GET.get('q', '')

        return context


class ProfessionalDetailView(DetailView):
    model = Professional
    template_name = 'core/professional_detail.html'
    context_object_name = 'professional'

    def get_queryset(self):
        # Keep this simple as fixed before
        return Professional.objects.filter(is_verified=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['articles'] = self.object.articles.filter(is_published=True).order_by('-publish_date')[:5]
        context['is_following'] = self.request.user in self.object.followers.all() if self.request.user.is_authenticated else False

        # Use the correct related_name 'portfolio' here
        context['portfolio_items'] = self.object.portfolio.all() # <-- CORRECTED

        context['jobs'] = Job.objects.filter(professional=self.object, status='completed')[:3]
        context['badges'] = self.object.user.badges.all()
        # context['follower_count_display'] = self.object.follower_count # Optional

        return context
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
        <img src="{comment.user.userprofile.avatar.url if comment.user.userprofile.avatar else static('img/default_avatar.jpg')}" class="rounded-circle" alt="{comment.user.username}'s Avatar" style="width: 40px; height: 40px; object-fit: cover;">
        <div class="comment-body flex-grow-1">
            <p class="mb-1">
                {"<a href='" + url('core:professional_detail', args=[comment.user.professional.id]) + "' class='text-dark text-decoration-none fw-bold'>" + comment.user.username + "</a>" if comment.user.professional else f"<span class='text-dark fw-bold'>{comment.user.username}</span>"}
                <span class="text-muted small ms-2">{comment.created_at|timesince} ago</span>
                {" (Edited)" if comment.created_at != comment.updated_at else ""}
            </p>
            <p class="text-dark">{comment.content}</p>
            """
    if user.is_authenticated:
        html += f"""
            <div class="comment-actions d-flex gap-3 align-items-center">
                <form method="post" class="d-inline like-comment-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{self.request.COOKIES.get('csrftoken', '')}">
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
                <form method="post" class="d-inline delete-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{self.request.COOKIES.get('csrftoken', '')}">
                    <input type="hidden" name="delete_comment" value="true">
                    <input type="hidden" name="comment_id" value="{comment.id}">
                    <button type="submit" class="btn p-0 text-muted" title="Delete" onclick="return confirm('Are you sure?')">
                        <i class="fas fa-trash"></i>
                    </button>
                </form>
                """
        html += "</div>"
        if comment.user == user:
            html += f"""
            <form method="post" class="edit-form mt-2" style="display: none;" id="edit-form-{comment.id}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{self.request.COOKIES.get('csrftoken', '')}">
                <input type="hidden" name="edit_comment" value="true">
                <input type="hidden" name="comment_id" value="{comment.id}">
                <div class="input-group">
                    <input type="text" name="edit_comment" class="form-control" value="{comment.content}" required>
                    <button type="submit" class="btn btn-primary">Save</button>
                </div>
            </form>
            """
        html += f"""
        <form method="post" class="reply-form mt-2" style="display: none;" id="reply-form-{comment.id}">
            <input type="hidden" name="csrfmiddlewaretoken" value="{self.request.COOKIES.get('csrftoken', '')}">
            <input type="hidden" name="reply" value="true">
            <input type="hidden" name="parent_id" value="{comment.id}">
            <div class="input-group">
                <input type="text" name="reply" class="form-control" placeholder="Reply..." required>
                <button type="submit" class="btn btn-primary">Send</button>
            </div>
        </form>
        """
    for reply in comment.replies.all():
        html += f"""
        <div class="reply d-flex gap-3 mb-3 ms-4">
            <img src="{reply.user.userprofile.avatar.url if reply.user.userprofile.avatar else static('img/default_avatar.jpg')}" class="rounded-circle" alt="{reply.user.username}'s Avatar" style="width: 30px; height: 30px; object-fit: cover;">
            <div class="reply-body flex-grow-1">
                <p class="mb-1">
                    {"<a href='" + url('core:professional_detail', args=[reply.user.professional.id]) + "' class='text-dark text-decoration-none fw-bold'>" + reply.user.username + "</a>" if reply.user.professional else f"<span class='text-dark fw-bold'>{reply.user.username}</span>"}
                    <span class="text-muted small ms-2">{reply.created_at|timesince} ago</span>
                    {" (Edited)" if reply.created_at != reply.updated_at else ""}
                </p>
                <p class="text-dark">{reply.content}</p>
                """
        if user.is_authenticated:
            html += f"""
                <form method="post" class="d-inline like-comment-form">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{self.request.COOKIES.get('csrftoken', '')}">
                    <input type="hidden" name="like_comment" value="true">
                    <input type="hidden" name="comment_id" value="{reply.id}">
                    <button type="submit" class="btn p-0 text-muted" title="{'Unlike' if user in reply.likes.all() else 'Like'}">
                        <i class="fas fa-heart {'text-danger' if user in reply.likes.all() else 'text-muted'}"></i> {reply.like_count}
                    </button>
                </form>
                """
        html += "</div></div>"
    html += "</div></div>"
    return html

def url(view_name, args=None):
    from django.urls import reverse
    return reverse(view_name, args=args) if args else reverse(view_name)

def static(path):
    return f"/static/{path}"




@login_required
def setup_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Try to get the existing professional profile FOR THIS USER, if one exists
    try:
        existing_professional = Professional.objects.get(user=request.user)
    except Professional.DoesNotExist:
        existing_professional = None # No existing professional record found

    if request.method == 'POST':
        if profile.is_professional:
            # User is marked as professional. Handle update or creation of Professional model.
            if existing_professional:
                # UPDATE: Pass the existing instance to the form
                form = ProfessionalForm(request.POST, request.FILES, instance=existing_professional)
                log_action = "Updated professional profile"
            else:
                # CREATE: No existing instance found, create a new form
                # (This might happen if UserProfile.is_professional was set true elsewhere)
                form = ProfessionalForm(request.POST, request.FILES)
                log_action = "Created professional profile via setup"

            if form.is_valid():
                professional = form.save(commit=False) # Get instance, don't save yet
                professional.user = request.user     # Ensure user is set
                # Safely handle skills if the field exists in the form
                if 'skills' in form.cleaned_data:
                   professional.skills = form.cleaned_data['skills']
                professional.save()                 # Save the new or updated instance
                ActivityLog.objects.create(user=request.user, action=log_action)
                return redirect('core:dashboard')
            # If form is not valid, it will fall through and render below with errors

        else: # User is NOT marked as professional
            # Update the UserProfile model instance
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                ActivityLog.objects.create(user=request.user, action="Updated user profile")
                return redirect('core:dashboard')
            # If form is not valid, it will fall through and render below with errors

    else: # GET Request
        if profile.is_professional:
            if existing_professional:
                # Show form pre-filled with existing professional data
                form = ProfessionalForm(instance=existing_professional)
            else:
                 # Show blank professional form (if profile.is_professional is true but no record exists)
                 form = ProfessionalForm()
        else:
            # Show form pre-filled with UserProfile data
            form = UserProfileForm(instance=profile)

    return render(request, 'core/setup_profile.html', {'form': form, 'is_professional': profile.is_professional})



def get_default_category():
    """Helper function to return or create a default Category."""
    return Category.objects.first() or Category.objects.create(name="General")

@login_required
def dashboard(request):
    # Get or create UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Professional Dashboard
    if profile.is_professional:
        try:
            professional = Professional.objects.get(user=request.user)
        except Professional.DoesNotExist:
            # Create a Professional instance if it doesn’t exist
            professional = Professional.objects.create(
                user=request.user,
                field=get_default_category(),
                subfield='',
                location='',
                bio='',
                is_verified=False,
            )
            profile.is_professional = True
            profile.save()

        # Professional-specific data
        articles = Article.objects.filter(author=professional, is_published=True)[:5]
        messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
        reviews = ServiceReview.objects.filter(professional=professional)[:5]
        activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:5]
        # Internal jobs assigned to the professional
        jobs = Job.objects.filter(professional=professional).order_by('-created_at')[:5]
        # External jobs matching field/subfield
        external_jobs = ExternalJob.objects.filter(
            Q(category=professional.field) |
            Q(subfield__icontains=professional.subfield),
            professional__isnull=True  # Assuming ExternalJob can link to Professional (not in model yet)
        ).exclude(created_by=request.user).order_by('-created_at')[:5] if professional.field else ExternalJob.objects.none()

        context = {
            'profile': profile,
            'professional': professional,
            'articles': articles,
            'messages': messages,
            'reviews': reviews,
            'activities': activities,
            'jobs': jobs,
            'external_jobs': external_jobs,
        }

    # Client Dashboard
    else:
        following = Professional.objects.filter(followers=request.user)
        feed = Article.objects.filter(
            author__in=following, is_published=True
        ).order_by('-publish_date')[:5]
        messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        favorites = Favorite.objects.filter(user=request.user)[:5]
        # Internal jobs where user is the client
        jobs = Job.objects.filter(client=request.user).order_by('-created_at')[:5]
        # External jobs created by the user
        external_jobs = ExternalJob.objects.filter(created_by=request.user).order_by('-created_at')[:5]

        context = {
            'profile': profile,
            'feed': feed,
            'messages': messages,
            'notifications': notifications,
            'favorites': favorites,
            'jobs': jobs,
            'external_jobs': external_jobs,
        }

    return render(request, 'core/dashboard.html', context)


@login_required
def become_professional(request):
    if hasattr(request.user, 'professional'):
        return redirect('core:user_profile')

    if request.method == 'POST':
        form = ProfessionalForm(request.POST, request.FILES)
        if form.is_valid():
            professional = form.save(commit=False)
            professional.user = request.user
            professional.is_verified = False
            professional.save()
            Notification.objects.create(
                user=request.user,
                message="Your professional profile has been submitted for verification."
            )
            return redirect('core:user_profile')
    else:
        form = ProfessionalForm()
    return render(request, 'core/become_professional.html', {'form': form})

@login_required
def add_portfolio(request):
    professional = get_object_or_404(Professional, user=request.user)
    if request.method == 'POST':
        form = PortfolioItemForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.professional = professional
            portfolio.save()
            ActivityLog.objects.create(user=request.user, action=f"Added portfolio item: {portfolio.title}")
            return redirect('core:dashboard')
    else:
        form = PortfolioItemForm()
    return render(request, 'core/add_portfolio.html', {'form': form})

@login_required
def view_messages(request, recipient_id=None):
    if request.method == 'POST' and recipient_id:
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            recipient = get_object_or_404(User, id=recipient_id)
            if recipient == request.user:
                form.add_error(None, "You cannot send a message to yourself.")
            else:
                message = form.save(commit=False)
                message.sender = request.user
                message.recipient = recipient
                message.save()
                Notification.objects.create(user=recipient, message=f"New message from {request.user.username}", link=f"/messages/{recipient_id}/")
                ActivityLog.objects.create(user=request.user, action=f"Sent message to {recipient.username}")
                return redirect('core:messages_with', recipient_id=recipient_id)
    else:
        form = MessageForm()

    if recipient_id:
        recipient = get_object_or_404(User, id=recipient_id)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) |
            (Q(sender=recipient) & Q(recipient=request.user))
        ).select_related('sender', 'recipient').order_by('timestamp')
        messages.filter(recipient=request.user, is_read=False).update(is_read=True)
    else:
        messages = None
        recipient = None

    inbox = Message.objects.filter(recipient=request.user).select_related('sender').order_by('-timestamp')[:10]
    sent = Message.objects.filter(sender=request.user).select_related('recipient').order_by('-timestamp')[:10]

    return render(request, 'core/messages.html', {
        'form': form,
        'messages': messages,
        'inbox': inbox,
        'sent': sent,
        'recipient': recipient,
        'user': request.user
    })

@login_required
def post_article(request):
    professional = get_object_or_404(Professional, user=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = professional
            article.save()
            ActivityLog.objects.create(user=request.user, action=f"Posted article: {article.title}")
            return redirect('core:dashboard')
    else:
        form = ArticleForm()
    return render(request, 'core/post_article.html', {'form': form})

@login_required
def toggle_follow(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    if request.user in professional.followers.all():
        professional.followers.remove(request.user)
        ActivityLog.objects.create(user=request.user, action=f"Unfollowed {professional.user.username}")
    else:
        professional.followers.add(request.user)
        Notification.objects.create(user=professional.user, message=f"{request.user.username} followed you", link=f"/professionals/{professional.id}/")
        ActivityLog.objects.create(user=request.user, action=f"Followed {professional.user.username}")
    return redirect('core:professional_detail', pk=professional_id)

@login_required
def review_service(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    if request.method == 'POST':
        form = ServiceReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.professional = professional
            review.reviewer = request.user
            review.save()
            Notification.objects.create(user=professional.user, message=f"{request.user.username} reviewed your service", link=f"/professionals/{professional.id}/")
            ActivityLog.objects.create(user=request.user, action=f"Reviewed {professional.user.username}")
            return redirect('core:professional_detail', pk=professional_id)
    else:
        form = ServiceReviewForm()
    return render(request, 'core/review_service.html', {'form': form, 'professional': professional})

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.save()
            ActivityLog.objects.create(user=request.user, action=f"Posted job: {job.title}")
            return redirect('core:dashboard')
    else:
        form = JobForm()
    return render(request, 'core/post_job.html', {'form': form})

# Add the signup view
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create and save the user (they will be active by default)
            user = form.save()

            # Create the associated UserProfile
            UserProfile.objects.get_or_create(user=user)

            # Log the user in immediately after signup
            login(request, user)

            # Redirect to the dashboard or wherever you want logged-in users to go
            return redirect('core:dashboard')
        else:
            # Form is invalid, re-render the page with errors
            # You might want to add messages here using django.contrib.messages
            pass # Fall through to render the template with the form object containing errors

    else: # GET request
        form = UserCreationForm()

    return render(request, 'core/signup.html', {'form': form})  

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('core:home'))


@login_required
def user_profile(request):
    user = request.user
    try:
        professional = user.professional
    except Professional.DoesNotExist:
        professional = None

    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if professional:
            professional_form = ProfessionalForm(request.POST, request.FILES, instance=professional)
        else:
            professional_form = ProfessionalForm(request.POST, request.FILES)

        if user_form.is_valid() and (not professional or professional_form.is_valid()):
            user_profile = user_form.save(commit=False)
            user_profile.user = user
            user_profile.save()

            if professional_form:
                professional = professional_form.save(commit=False)
                professional.user = user
                # Handle skills manually since we’re using a custom input
                if 'skills' in request.POST:
                    professional.skills = [skill.strip() for skill in request.POST['skills'].split(',') if skill.strip()]
                professional.save()

            return redirect('core:user_profile')
    else:
        user_form = UserProfileForm(instance=user_profile)
        professional_form = ProfessionalForm(instance=professional) if professional else ProfessionalForm()

    return render(request, 'core/user_profile.html', {
        'user_form': user_form,
        'professional_form': professional_form,
        'professional': professional,
        'user_profile': user_profile,
    })

class JobListView(ListView):
    model = Job
    template_name = 'core/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        # Get internal jobs
        internal_jobs = Job.objects.all()
        # Get external jobs
        external_jobs = ExternalJob.objects.all()

        # Apply filters to internal jobs
        queryset = internal_jobs
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        location = self.request.GET.get('location')
        budget = self.request.GET.get('budget')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(professional__field__name__icontains=query)
            )
        if category:
            queryset = queryset.filter(professional__field__name=category)
        if location:
            queryset = queryset.filter(professional__location__icontains=location)
        if budget:
            queryset = queryset.filter(budget__lte=budget)

        # Apply filters to external jobs
        external_queryset = external_jobs
        if query:
            external_queryset = external_queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
        if category:
            external_queryset = external_queryset.filter(category__name=category)
        if location:
            external_queryset = external_queryset.filter(location__icontains=location)
        if budget:
            external_queryset = external_queryset.filter(budget__lte=budget)

        # Combine the two querysets into a list with a type flag
        combined_jobs = []
        for job in queryset:
            combined_jobs.append({'type': 'internal', 'job': job})
        for job in external_queryset:
            combined_jobs.append({'type': 'external', 'job': job})

        # Sort by created_at (newest first)
        combined_jobs.sort(key=lambda x: x['job'].created_at, reverse=True)
        return combined_jobs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context
    

class JobDetailView(DetailView):
    template_name = 'core/job_detail.html'
    context_object_name = 'job'

    def get_object(self):
        job_id = self.kwargs.get('pk')
        job_type = self.request.GET.get('type')

        if job_type == 'internal':
            return get_object_or_404(Job, id=job_id)
        else:
            return get_object_or_404(ExternalJob, id=job_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_type = self.request.GET.get('type')
        context['job_type'] = job_type

        # Documents are common to both Job and ExternalJob
        context['documents'] = self.object.documents.all()

        # Application logic only applies to internal jobs (since external jobs don't have a professional)
        if job_type == 'internal':
            context['can_apply'] = (
                self.request.user.is_authenticated and
                self.request.user != self.object.professional.user
            )
            if self.request.user.is_authenticated:
                context['has_applied'] = Message.objects.filter(
                    sender=self.request.user,
                    recipient=self.object.professional.user,
                    content__contains=f"I'm interested in your job posting: {self.object.title}"
                ).exists()
        else:
            context['can_apply'] = False  # External jobs don't support applications
            context['has_applied'] = False

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        job_type = self.request.GET.get('type')

        # Application logic only applies to internal jobs
        if job_type == 'internal':
            if request.user.is_authenticated and request.user != self.object.professional.user:
                message_content = f"I'm interested in your job posting: {self.object.title}"
                Message.objects.create(
                    sender=request.user,
                    recipient=self.object.professional.user,
                    content=message_content
                )
                Notification.objects.create(
                    user=self.object.professional.user,
                    message=f"{request.user.username} has applied for your job: {self.object.title}",
                    link=f"/jobs/{self.object.id}/?type=internal"
                )
                Notification.objects.create(
                    user=request.user,
                    message=f"You have applied for the job: {self.object.title}",
                    link=f"/jobs/{self.object.id}/?type=internal"
                )
                messages.success(request, "Your application has been submitted!")
            else:
                messages.error(request, "You cannot apply for this job.")
        else:
            messages.info(request, "Applications are not available for external jobs.")

        return redirect('core:job_detail', pk=self.object.id, type=job_type)


def faq(request):
    faqs = FAQ.objects.all()
    return render(request, 'core/faq.html', {'faqs': faqs})

def feedback(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            Feedback.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=message
            )
            return redirect('core:feedback')
    feedbacks = Feedback.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, 'core/feedback.html', {'feedbacks': feedbacks})

@login_required
def notifications(request):
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications_list, 10)  # 10 notifications per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'notifications': page_obj,
        'page_obj': page_obj,
        'site_theme': request.session.get('theme', 'light')
    }
    return render(request, 'core/notifications.html', context)

@login_required
def upgrade(request):
    if request.method == 'POST':
        upgrade_type = request.POST.get('upgrade_type')
        upgrade_request = UpgradeRequest.objects.create(
            user=request.user,
            upgrade_type=upgrade_type,
            status='pending'
        )
        Notification.objects.create(
            user=request.user,
            message=f"Your {upgrade_request.get_upgrade_type_display()} request has been submitted. Please follow the payment instructions."
        )
        return redirect('core:upgrade')
    upgrade_requests = UpgradeRequest.objects.filter(user=request.user).order_by('-requested_at')
    return render(request, 'core/upgrade.html', {'upgrade_requests': upgrade_requests})

@custom_admin_or_helper_required
def verify_upgrade(request, upgrade_id):
    upgrade_request = get_object_or_404(UpgradeRequest, id=upgrade_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            upgrade_request.status = 'verified'
            upgrade_request.save()
            # Award badge based on upgrade type
            if upgrade_request.upgrade_type == 'premium_profile':
                tier = 'premium_professional' if hasattr(upgrade_request.user, 'professional') else 'premium_user'
            elif upgrade_request.upgrade_type == 'featured_article':
                tier = 'premium_user'
            elif upgrade_request.upgrade_type == 'job_boost':
                tier = 'premium_user'
            Badge.objects.get_or_create(user=upgrade_request.user, tier=tier)
            Notification.objects.create(
                user=upgrade_request.user,
                message=f"Your {upgrade_request.get_upgrade_type_display()} has been verified! You have earned the '{tier.replace('_', ' ').title()}' badge."
            )
        elif action == 'reject':
            upgrade_request.status = 'rejected'
            upgrade_request.save()
            Notification.objects.create(
                user=upgrade_request.user,
                message=f"Your {upgrade_request.get_upgrade_type_display()} request was rejected."
            )
        return redirect('core:custom_admin_dashboard')
    return render(request, 'core/verify_upgrade.html', {'upgrade_request': upgrade_request})




#Additions for dignup 


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create and save the user (will be active by default)
                user = form.save()
                # Create the associated UserProfile
                UserProfile.objects.get_or_create(user=user)
                # Log the user in immediately
                login(request, user)
                # Add a success message
                messages.success(request, f"Welcome, {user.username}! Your account created successfully.")
                # Redirect to the dashboard (or setup_profile if preferred)
                return redirect('core:dashboard') # Or 'core:setup_profile'

            except Exception as e:
                messages.error(request, "An unexpected error occurred during signup.")
                # Consider logging the error 'e'
        else:
            # Form is invalid
            messages.error(request, "Please correct the errors below.")

    else: # GET request
        form = UserCreationForm()

    return render(request, 'core/signup.html', {'form': form})

    
def insights(request):
    # Get all categories for the filter dropdown
    categories = Category.objects.all()

    # Base queryset: only published articles
    articles = Article.objects.filter(is_published=True)

    # Search filter
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        articles = articles.filter(category=category_id)  # Fixed: Use 'category' instead of 'category_id'

    # Featured articles: top 3 by likes from filtered results
    featured_articles = articles.order_by('-likes')[:3]

    # All articles: ordered by publish date
    all_articles = articles.order_by('-publish_date')

    return render(request, 'core/insights.html', {
        'featured_articles': featured_articles,
        'all_articles': all_articles,
        'categories': categories,
        'site_theme': request.session.get('theme', 'light')
    })

@login_required
def clear_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        return redirect('core:notifications')
    return redirect('core:notifications')

@login_required
def delete_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.delete()
    return redirect('core:notifications')

@custom_admin_or_helper_required
def custom_admin_dashboard(request):
    professionals = Professional.objects.all()
    jobs = Job.objects.all()
    external_jobs = ExternalJob.objects.all()
    articles = Article.objects.all()
    users = User.objects.all()
    helpers = AdminHelper.objects.filter(custom_admin=request.user.custom_admin)
    pending_verifications = Professional.objects.filter(is_verified=False)
    pending_upgrades = UpgradeRequest.objects.filter(status='pending')

    context = {
        'users_count': users.count(),
        'professionals_count': professionals.count(),
        'jobs_count': jobs.count(),
        'external_jobs_count': external_jobs.count(),
        'articles_count': articles.count(),
        'all_users': users,
        'professionals': professionals,
        'pending_verifications': pending_verifications,
        'helpers': helpers,
        'pending_upgrades': pending_upgrades,
        'site_theme': request.session.get('theme', 'light')
    }
    return render(request, 'core/custom_admin_dashboard.html', context)

@custom_admin_or_helper_required
def assign_helper(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        task = request.POST.get('task')
        user = get_object_or_404(User, id=user_id)
        AdminHelper.objects.create(
            custom_admin=request.user.custom_admin,
            user=user,
            task=task
        )
        ActivityLog.objects.create(user=request.user, action=f"Assigned helper: {user.username} - {task}")
        return redirect('core:custom_admin_dashboard')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'core/assign_helper.html', {'users': users})

@custom_admin_or_helper_required
def admin_upload_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        job_type = request.POST.get('job_type')

        if form.is_valid():
            is_valid = True

            if job_type == 'internal':
                if not form.cleaned_data.get('professional'):
                    form.add_error('professional', "Professional is required for internal jobs.")
                    is_valid = False
                if not form.cleaned_data.get('status'):
                    form.add_error('status', "Status is required for internal jobs.")
                    is_valid = False
            else:
                location = request.POST.get('location', '').strip()
                if not location:
                    messages.error(request, "Location is required for external jobs.")
                    is_valid = False

            if is_valid:
                if job_type == 'internal':
                    job = form.save(commit=False)
                    job.professional = form.cleaned_data['professional']
                    job.save()
                    documents = request.FILES.getlist('documents')
                    for doc in documents:
                        JobDocument.objects.create(
                            content_type=ContentType.objects.get_for_model(Job),
                            object_id=job.id,
                            document=doc
                        )
                    ActivityLog.objects.create(user=request.user, action=f"Uploaded internal job: {job.title}")
                else:
                    category_id = request.POST.get('category')
                    category = None
                    if category_id:
                        try:
                            category = Category.objects.get(id=category_id)
                        except Category.DoesNotExist:
                            messages.error(request, "Invalid category selected.")
                            is_valid = False

                    if is_valid:
                        external_job = ExternalJob(
                            title=form.cleaned_data['title'],
                            description=form.cleaned_data['description'],
                            budget=form.cleaned_data.get('budget'),
                            job_type=job_type,
                            category=category,
                            location=location,
                            created_by=request.user
                        )
                        external_job.save()
                        documents = request.FILES.getlist('documents')
                        for doc in documents:
                            JobDocument.objects.create(
                                content_type=ContentType.objects.get_for_model(ExternalJob),
                                object_id=external_job.id,
                                document=doc
                            )
                        ActivityLog.objects.create(user=request.user, action=f"Uploaded {job_type} job: {external_job.title}")

                if is_valid:
                    messages.success(request, "Job uploaded successfully!")
                    return redirect('core:admin_upload_job')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm()

    return render(request, 'core/admin_upload_job.html', {
        'form': form,
        'job_types': [
            ('internal', 'Internal Job (Platform)'),
            ('public', 'Public Sector (Government)'),
            ('private', 'Private Sector'),
        ],
        'categories': Category.objects.all()  # Add categories to the context
    })

@custom_admin_or_helper_required
def verify_professional(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            professional.is_verified = True
            professional.save()
            Badge.objects.get_or_create(user=professional.user, tier='verified_professional')
            Notification.objects.create(
                user=professional.user,
                message="Your professional profile has been verified! You have earned the 'Verified Professional' badge.",
                link=f"/professionals/{professional.id}/"
            )
            ActivityLog.objects.create(user=request.user, action=f"Verified professional: {professional.user.username}")
        elif action == 'reject':
            professional.delete()
            Notification.objects.create(
                user=professional.user,
                message="Your professional profile verification was rejected."
            )
            ActivityLog.objects.create(user=request.user, action=f"Rejected professional: {professional.user.username}")
        return redirect('core:custom_admin_dashboard')
    return render(request, 'core/verify_professional.html', {'professional': professional})

@custom_admin_or_helper_required
def verify_upgrade(request, upgrade_id):
    upgrade_request = get_object_or_404(UpgradeRequest, id=upgrade_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            upgrade_request.status = 'verified'
            upgrade_request.save()
            if upgrade_request.upgrade_type == 'premium_profile':
                tier = 'premium_professional' if hasattr(upgrade_request.user, 'professional') else 'premium_user'
            elif upgrade_request.upgrade_type == 'featured_article':
                tier = 'premium_user'
            elif upgrade_request.upgrade_type == 'job_boost':
                tier = 'premium_user'
            Badge.objects.get_or_create(user=upgrade_request.user, tier=tier)
            Notification.objects.create(
                user=upgrade_request.user,
                message=f"Your {upgrade_request.get_upgrade_type_display()} has been verified! You have earned the '{tier.replace('_', ' ').title()}' badge.",
                link="/profile/"
            )
            ActivityLog.objects.create(user=request.user, action=f"Verified upgrade: {upgrade_request.user.username}")
        elif action == 'reject':
            upgrade_request.status = 'rejected'
            upgrade_request.save()
            Notification.objects.create(
                user=upgrade_request.user,
                message=f"Your {upgrade_request.get_upgrade_type_display()} request was rejected."
            )
            ActivityLog.objects.create(user=request.user, action=f"Rejected upgrade: {upgrade_request.user.username}")
        return redirect('core:custom_admin_dashboard')
    return render(request, 'core/verify_upgrade.html', {'upgrade_request': upgrade_request})

@custom_admin_or_helper_required
def export_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admin_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type', 'Count'])
    writer.writerow(['Users', User.objects.count()])
    writer.writerow(['Professionals', Professional.objects.count()])
    writer.writerow(['Jobs', Job.objects.count()])
    writer.writerow(['Articles', Article.objects.count()])
    ActivityLog.objects.create(user=request.user, action="Exported admin data as CSV")
    return response

@custom_admin_or_helper_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    action = "Deactivated" if not user.is_active else "Activated"
    ActivityLog.objects.create(user=request.user, action=f"{action} user: {user.username}")
    return redirect('core:custom_admin_dashboard')

@custom_admin_or_helper_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    ActivityLog.objects.create(user=request.user, action=f"Deleted user: {user.username}")
    return redirect('core:custom_admin_dashboard')

@custom_admin_or_helper_required
def remove_helper(request, helper_id):
    helper = get_object_or_404(AdminHelper, id=helper_id, custom_admin=request.user.custom_admin)
    helper.delete()
    ActivityLog.objects.create(user=request.user, action=f"Removed helper: {helper.user.username}")
    return redirect('core:custom_admin_dashboard')

@custom_admin_or_helper_required
def delete_professional(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    professional.delete()
    ActivityLog.objects.create(user=request.user, action=f"Deleted professional: {professional.user.username}")
    return redirect('core:custom_admin_dashboard')