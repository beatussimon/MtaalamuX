from django import forms
from .models import Professional, PortfolioItem, Message, Article, ServiceReview, UserProfile, Job

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'interests', 'theme']

class ProfessionalForm(forms.ModelForm):
    skills = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g., Python, Django'}), required=False)

    class Meta:
        model = Professional
        fields = ['field', 'subfield', 'location', 'bio', 'photo', 'credentials_file', 'social_links', 'availability', 'rate']

    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        return [skill.strip() for skill in skills.split(',')] if skills else []

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'file']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'image', 'category']

class ServiceReviewForm(forms.ModelForm):
    class Meta:
        model = ServiceReview
        fields = ['rating', 'comment']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'budget']