from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q #Count  # Add Count for annotation
from .models import Professional, Article, Message, UserProfile, Favorite,UpgradeRequest, Comment,FAQ, Feedback, ServiceReview, Notification, ActivityLog, Job, Category, Badge, AdminHelper, JobDocument, VerificationToken
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
from django.conf import settings
from django.db.models import Q, Count, F, FloatField, Value, Avg
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.core.exceptions import ObjectDoesNotExist

class ProfessionalListView(ListView):
    model = Professional
    template_name = 'core/professional_list.html'
    context_object_name = 'professionals'
    paginate_by = 12

    # --- get_queryset remains the same as your last working version ---
    def get_queryset(self):
        # (Keep the combined search logic from the previous "perfect search" answer)
        queryset = Professional.objects.filter(is_verified=True)
        query = self.request.GET.get('q')
        category_name = self.request.GET.get('category')
        if category_name:
            queryset = queryset.filter(field__name__iexact=category_name)
        if query:
            field_q = Q(field__name__icontains=query)
            subfield_q = Q(subfield__icontains=query)
            location_q = Q(location__icontains=query)
            skills_q = Q(skills__icontains=query) # Basic skills search
            combined_q = field_q | subfield_q | location_q | skills_q
            queryset = queryset.filter(combined_q).distinct()
        queryset = queryset.annotate(
            follower_count_annotated=Count('followers', distinct=True),
            avg_rating_annotated=Coalesce(Avg('reviews__rating'), Value(0.0), output_field=FloatField())
        )
        professionals_list = list(queryset)
        for p in professionals_list:
            p._sort_score = (0.7 * p.follower_count_annotated) + (0.3 * p.avg_rating_annotated * 100)
        return sorted(professionals_list, key=lambda x: getattr(x, '_sort_score', 0), reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Pass full Category objects to the template ---
        context['categories'] = Category.objects.filter(
            professionals__is_verified=True # Only show relevant categories
        ).distinct().order_by('name') # Pass category objects

        # Manual pagination (needed because get_queryset returns a list)
        professionals_sorted = self.object_list
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

        # Keep selected_category as the NAME string for comparison with URL param
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
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if profile.is_professional:
        professional = Professional.objects.get(user=request.user)
        articles = professional.articles.all()
        messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
        reviews = professional.reviews.all()
        activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
        jobs = Job.objects.filter(professional=professional).order_by('-created_at')[:5]
        context = {'professional': professional, 'articles': articles, 'messages': messages, 'reviews': reviews, 'activities': activities, 'jobs': jobs}
    else:
        following = Professional.objects.filter(followers=request.user)
        feed = Article.objects.filter(author__in=following, is_published=True).order_by('-publish_date')[:10]
        messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')[:5]
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        favorites = Favorite.objects.filter(user=request.user)
        jobs = Job.objects.filter(client=request.user).order_by('-created_at')[:5]
        context = {'feed': feed, 'messages': messages, 'notifications': notifications, 'favorites': favorites, 'jobs': jobs}
    return render(request, 'core/dashboard.html', context)

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
def messages(request, recipient_id=None):
    if request.method == 'POST' and recipient_id:
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            recipient = get_object_or_404(User, id=recipient_id)
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            Notification.objects.create(user=recipient, message=f"New message from {request.user.username}", link="/messages/")
            ActivityLog.objects.create(user=request.user, action=f"Sent message to {recipient.username}")
            return redirect('core:messages_with', recipient_id=recipient_id)
    else:
        form = MessageForm()

    if recipient_id:
        recipient = get_object_or_404(User, id=recipient_id)
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=recipient)) | (Q(sender=recipient) & Q(recipient=request.user))
        ).order_by('timestamp')
    else:
        messages = None
        recipient = None
    inbox = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    sent = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'core/messages.html', {'form': form, 'messages': messages, 'inbox': inbox, 'sent': sent, 'recipient': recipient})

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
            user = form.save()
            # Create a UserProfile for the new user
            UserProfile.objects.create(user=user)
            # Log the user in after signup
            login(request, user)
            return redirect('core:dashboard')  # Redirect to dashboard after signup
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


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
        queryset = Job.objects.filter(status='open').select_related('professional').prefetch_related('documents')
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        location = self.request.GET.get('location')
        budget = self.request.GET.get('budget')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(professional__field__name__icontains=query)
            )
        if category:
            queryset = queryset.filter(professional__field__name__iexact=category)
        if location:
            queryset = queryset.filter(professional__location__icontains=location)
        if budget:
            try:
                budget_value = float(budget)
                queryset = queryset.filter(budget__lte=budget_value)
            except ValueError:
                pass

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = self.get_queryset()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(jobs, self.paginate_by)
        try:
            jobs_paginated = paginator.page(page)
        except PageNotAnInteger:
            jobs_paginated = paginator.page(1)
        except EmptyPage:
            jobs_paginated = paginator.page(paginator.num_pages)
        context['jobs'] = jobs_paginated
        context['categories'] = Category.objects.all()
        return context
    

class JobDetailView(DetailView):
    model = Job
    template_name = 'core/job_detail.html'
    context_object_name = 'job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_apply'] = self.request.user.is_authenticated and self.request.user != self.object.professional.user
        if self.request.user.is_authenticated:
            context['has_applied'] = Message.objects.filter(
                sender=self.request.user,
                recipient=self.object.professional.user,
                content__contains=f"I'm interested in your job posting: {self.object.title}"
            ).exists()
        context['documents'] = self.object.documents.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated and request.user != self.object.professional.user:
            message_content = f"I'm interested in your job posting: {self.object.title}"
            Message.objects.create(
                sender=request.user,
                recipient=self.object.professional.user,
                content=message_content
            )
            Notification.objects.create(
                user=self.object.professional.user,
                message=f"{request.user.username} has applied for your job: {self.object.title}"
            )
            Notification.objects.create(
                user=request.user,
                message=f"You have applied for the job: {self.object.title}"
            )
        return redirect('core:job_detail', pk=self.object.id)


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

#For teh admin dashboard

def custom_admin_required(view_func):
    def check_custom_admin(user):
        return user.is_authenticated and hasattr(user, 'custom_admin') and user.custom_admin.is_active
    return user_passes_test(check_custom_admin)(view_func)

@custom_admin_required
def custom_admin_dashboard(request):
    professionals = Professional.objects.all()
    jobs = Job.objects.all()
    articles = Article.objects.all()
    users = User.objects.all()
    helpers = AdminHelper.objects.filter(custom_admin=request.user.custom_admin)

    context = {
        'professionals': professionals,
        'jobs': jobs,
        'articles': articles,
        'users': users,
        'helpers': helpers,
    }
    return render(request, 'core/custom_admin_dashboard.html', context)

@custom_admin_required
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
        return redirect('core:custom_admin_dashboard')
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'core/assign_helper.html', {'users': users})

@custom_admin_required
def admin_upload_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.professional = form.cleaned_data['professional']
            job.save()
            # Save documents if provided
            documents = request.FILES.getlist('documents')
            for doc in documents:
                JobDocument.objects.create(job=job, document=doc)
            return redirect('core:custom_admin_dashboard')
    else:
        form = JobForm()
    return render(request, 'core/admin_upload_job.html', {'form': form})

@custom_admin_required
def verify_professional(request, professional_id):
    professional = get_object_or_404(Professional, id=professional_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            professional.is_verified = True
            professional.save()
            # Award badge
            Badge.objects.get_or_create(user=professional.user, tier='verified_professional')
            Notification.objects.create(
                user=professional.user,
                message="Your professional profile has been verified! You have earned the 'Verified Professional' badge."
            )
        elif action == 'reject':
            professional.delete()
            Notification.objects.create(
                user=professional.user,
                message="Your professional profile verification was rejected."
            )
        return redirect('core:custom_admin_dashboard')
    return render(request, 'core/verify_professional.html', {'professional': professional})

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

@custom_admin_required
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
            user = form.save()
            # Create a verification token
            token = VerificationToken.objects.create(user=user)
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('core:verify_email', kwargs={'token': str(token.token)})
            )
            send_mail(
                'Verify Your Email - mtaalamuX',
                f'Please click the following link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            login(request, user)
            return redirect('core:setup_profile')
    else:
        form = UserCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def verify_email(request, token):
    try:
        verification_token = VerificationToken.objects.get(token=token)
        user = verification_token.user
        # Award Verified User badge
        Badge.objects.get_or_create(user=user, tier='verified_user')
        Notification.objects.create(
            user=user,
            message="Your email has been verified! You have earned the 'Verified User' badge."
        )
        verification_token.delete()
        return redirect('core:user_profile')
    except VerificationToken.DoesNotExist:
        return render(request, 'core/error.html', {'message': 'Invalid or expired verification token.'})
    
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