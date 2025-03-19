from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count  # Add Count for annotation
from .models import Professional, Article, Message, UserProfile, Favorite, Comment, ServiceReview, Notification, ActivityLog, Job
from .forms import ProfessionalForm, PortfolioItemForm, MessageForm, ArticleForm, ServiceReviewForm, UserProfileForm, JobForm
from django.contrib.auth.forms import UserCreationForm  # For signup
from django.contrib.auth import login  # To log in the user after signup
from django.contrib.auth.models import User  # For recipient lookup in messages view
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

class ProfessionalListView(ListView):
    model = Professional
    template_name = 'core/professional_list.html'
    context_object_name = 'professionals'
    paginate_by = 12

    def get_queryset(self):
        queryset = Professional.objects.filter(is_verified=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(field__icontains=query) | Q(subfield__icontains=query) | Q(location__icontains=query)
            )
            # Filter on the skills JSON field in Python
            professionals = [
                professional for professional in queryset
                if any(query.lower() in skill.lower() for skill in professional.skills)
            ]
        else:
            professionals = list(queryset)
        # Annotate with follower_count and sort
        for professional in professionals:
            professional.follower_count = professional.followers.count()
        return sorted(professionals, key=lambda x: x.follower_count, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Since get_queryset returns a list, we need to handle pagination manually
        professionals = self.get_queryset()
        page = self.request.GET.get('page', 1)
        paginator = Paginator(professionals, self.paginate_by)
        try:
            professionals_paginated = paginator.page(page)
        except PageNotAnInteger:
            professionals_paginated = paginator.page(1)
        except EmptyPage:
            professionals_paginated = paginator.page(paginator.num_pages)
        context['professionals'] = professionals_paginated
        return context

class ProfessionalDetailView(DetailView):
    model = Professional
    template_name = 'core/professional_detail.html'
    context_object_name = 'professional'

    def get_queryset(self):
        return Professional.objects.annotate(follower_count=Count('followers'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['articles'] = self.object.articles.filter(is_published=True).order_by('-publish_date')[:5]
        context['is_following'] = self.request.user in self.object.followers.all() if self.request.user.is_authenticated else False
        context['portfolio_items'] = self.object.portfolio_items.all()  # Adjust related_name as needed
        context['jobs'] = Job.objects.filter(professional=self.object, status='completed')[:3]
        return context
    
class ArticleListView(ListView):
    model = Article
    template_name = 'core/article_list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        queryset = Article.objects.filter(is_published=True)
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return queryset.order_by('-publish_date')

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'core/article_detail.html'
    context_object_name = 'article'

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = self.object.author.articles.filter(is_published=True).order_by('-publish_date')[:5]
        context['is_following'] = self.request.user in self.object.author.followers.all() if self.request.user.is_authenticated else False
        return context

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        if 'comment' in request.POST:
            Comment.objects.create(article=article, user=request.user, content=request.POST['comment'])
            Notification.objects.create(user=article.author.user, message=f"{request.user.username} commented on your article", link=f"/articles/{article.id}/")
        elif 'like' in request.POST:
            if request.user in article.likes.all():
                article.likes.remove(request.user)
            else:
                article.likes.add(request.user)
                Notification.objects.create(user=article.author.user, message=f"{request.user.username} liked your article", link=f"/articles/{article.id}/")
        elif 'share' in request.POST:
            article.shares += 1
            article.save()
        return redirect('core:article_detail', pk=article.id)

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
    if request.method == 'POST':
        if profile.is_professional:
            form = ProfessionalForm(request.POST, request.FILES)
            if form.is_valid():
                professional = form.save(commit=False)
                professional.user = request.user
                professional.skills = form.cleaned_data['skills']
                professional.save()
                ActivityLog.objects.create(user=request.user, action="Updated professional profile")
                return redirect('core:dashboard')
        else:
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                ActivityLog.objects.create(user=request.user, action="Updated user profile")
                return redirect('core:dashboard')
    else:
        form = ProfessionalForm() if profile.is_professional else UserProfileForm(instance=profile)
    return render(request, 'core/setup_profile.html', {'form': form, 'is_professional': profile.is_professional})

@login_required
def become_professional(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST' and not profile.is_professional:
        profile.is_professional = True
        profile.save()
        ActivityLog.objects.create(user=request.user, action="Became a professional")
        return redirect('core:setup_profile')
    return render(request, 'core/become_professional.html')

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