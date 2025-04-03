from django import forms
from django.core.validators import FileExtensionValidator
from .models import Professional, PortfolioItem, Message, Article, ServiceReview, UserProfile, Job, Category

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'interests', 'theme']

class ProfessionalForm(forms.ModelForm):
    skills = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Python,Django,JavaScript'}),
        required=False,
        help_text="Enter skills as a comma-separated list."
    )
    new_field = forms.CharField(
        label="New Field (if not in list)",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter a new field if not listed'})
    )
    cv = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        required=True
    )
    certificates = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        required=True
    )
    hero_image = forms.ImageField(  # New field for hero image
        label="Hero Image (Cover Photo)",
        required=False,
        help_text="Upload a cover image for your profile page (optional). Recommended size: 1200x500px.",
    )

    class Meta:
        model = Professional
        fields = [
            'field', 'new_field', 'subfield', 'location', 'skills', 'photo', 'hero_image', 'bio',  # Added hero_image
            'linkedin_url', 'twitter_url', 'github_url', 'website_url',
            'cv', 'certificates'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
            'field': forms.Select(choices=[]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].choices = [(None, 'Select a field')] + [(category.id, category.name) for category in Category.objects.all()]
        self.fields['field'].required = False

    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        new_field = cleaned_data.get('new_field')

        if not field and not new_field:
            raise forms.ValidationError("Please select a field or enter a new one.")
        if field and new_field:
            raise forms.ValidationError("Please either select a field or enter a new one, not both.")

        if new_field:
            category, created = Category.objects.get_or_create(name=new_field.strip())
            cleaned_data['field'] = category

        return cleaned_data

    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        if skills:
            return [skill.strip() for skill in skills.split(',') if skill.strip()]
        return []

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'file']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...', 'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control file-input'}),
        }
        labels = {
            'content': '',  # Remove label for cleaner look
            'file': '',     # Remove label
        }

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
        fields = ['professional', 'title', 'description', 'budget', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['professional'].required = False
        self.fields['status'].required = False
        self.fields['budget'].required = False