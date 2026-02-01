"""
Management command to set up Django Groups and Permissions for MtaalamuX RBAC.

This command creates:
1. Permission groups: Basic Users, Professional Users, Premium Users, Admins
2. Custom permissions for all models
3. Default payment methods for offline payments
4. Default FAQ entries
5. Default categories

Usage:
    python manage.py setup_groups_permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from core.models import (
    Category, PaymentMethod, FAQ, UserTier, VerificationLevel,
    UserProfile
)


class Command(BaseCommand):
    help = 'Set up Django Groups and Permissions for MtaalamuX RBAC'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-demo-data',
            action='store_true',
            help='Also create demo categories, payment methods, and FAQs',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting setup...'))
        
        with transaction.atomic():
            self.create_groups()
            self.create_custom_permissions()
            
            if options['with_demo_data']:
                self.create_categories()
                self.create_payment_methods()
                self.create_faqs()
        
        self.stdout.write(self.style.SUCCESS('Setup completed successfully!'))

    def create_groups(self):
        """Create permission groups for each user tier"""
        self.stdout.write('Creating permission groups...')
        
        # Basic Users Group - Read-only access
        basic_group, created = Group.objects.get_or_create(name='Basic Users')
        if created:
            self.stdout.write(f'  Created group: Basic Users')
        
        # Professional Users Group - Can initiate consultations
        professional_group, created = Group.objects.get_or_create(name='Professional Users')
        if created:
            self.stdout.write(f'  Created group: Professional Users')
        
        # Premium Users Group - Can post content and sell items
        premium_group, created = Group.objects.get_or_create(name='Premium Users')
        if created:
            self.stdout.write(f'  Created group: Premium Users')
        
        # Admins Group - Full access
        admin_group, created = Group.objects.get_or_create(name='Admins')
        if created:
            self.stdout.write(f'  Created group: Admins')
        
        # Super Admins - For superusers
        superadmin_group, created = Group.objects.get_or_create(name='Super Admins')
        if created:
            self.stdout.write(f'  Created group: Super Admins')

    def create_custom_permissions(self):
        """Create custom permissions for all models"""
        self.stdout.write('Creating custom permissions...')
        
        # Define all models that need permissions
        models = [
            ('article', 'Article'),
            ('research', 'Research'),
            ('professional', 'Professional'),
            ('consultation', 'Consultation'),
            ('consultationtask', 'Consultation Task'),
            ('conversation', 'Conversation'),
            ('message', 'Message'),
            ('digitalitem', 'Digital Item'),
            ('merchitem', 'Merch Item'),
            ('paymentmethod', 'Payment Method'),
            ('paymentrecord', 'Payment Record'),
            ('verificationrequest', 'Verification Request'),
            ('upgraderequest', 'Upgrade Request'),
            ('topexpert', 'Top Expert'),
            ('featuredcontent', 'Featured Content'),
            ('userprofile', 'User Profile'),
        ]
        
        # Content type for UserProfile
        userprofile_ct = ContentType.objects.get_for_model(UserProfile)
        
        # Get all permissions
        all_perms = Permission.objects.all()
        
        for model_name, model_label in models:
            try:
                ct = ContentType.objects.get(app_label='core', model=model_name)
                
                # Create custom permissions for each model
                for perm_type in ['can_view', 'can_create', 'can_edit', 'can_delete']:
                    perm_codename = f'{perm_type}_{model_name}'
                    perm_name = f'Can {perm_type.replace("_", " ").title()} {model_label}'
                    
                    if not Permission.objects.filter(codename=perm_codename).exists():
                        Permission.objects.create(
                            codename=perm_codename,
                            name=perm_name,
                            content_type=ct,
                        )
                        self.stdout.write(f'  Created permission: {perm_codename}')
            except ContentType.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Skipping {model_name} - not found'))
        
        self.stdout.write(self.style.SUCCESS('Custom permissions created!'))

    def create_categories(self):
        """Create default professional categories"""
        self.stdout.write('Creating default categories...')
        
        categories = [
            ('Technology', 'Software development, IT, and tech-related fields'),
            ('Business', 'Business consulting, management, and entrepreneurship'),
            ('Legal', 'Legal advice and consultation'),
            ('Health', 'Health and medical consultation'),
            ('Education', 'Educational consulting and tutoring'),
            ('Finance', 'Financial advice and investment consultation'),
            ('Engineering', 'Engineering and technical consultation'),
            ('Marketing', 'Marketing and brand consultation'),
            ('Design', 'Design and creative consultation'),
            ('Science', 'Scientific research and consultation'),
            ('Agriculture', 'Agricultural consultation'),
            ('Real Estate', 'Real estate consultation'),
            ('HR', 'Human resources and recruitment'),
            ('Other', 'Other professional fields'),
        ]
        
        for name, description in categories:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'  Created category: {name}')

    def create_payment_methods(self):
        """Create default payment methods for offline payments"""
        self.stdout.write('Creating payment methods...')
        
        payment_methods = [
            {
                'network': 'mpesa',
                'lipa_number': 'Lipa na M-Pesa 123456',
                'payment_instructions': 'Go to M-Pesa > Lipa na M-Pesa > Enter Business Number > Enter Amount > Enter PIN',
            },
            {
                'network': 'airtel',
                'lipa_number': 'Airtel Money 987654',
                'payment_instructions': 'Go to Airtel Money > Push Money > Enter Number > Enter Amount > Enter PIN',
            },
            {
                'network': 'tigo',
                'lipa_number': 'Tigo Pesa 555666',
                'payment_instructions': 'Go to Tigo Pesa > Make Payments > Enter Business Number > Enter Amount > Enter PIN',
            },
            {
                'network': 'halotel',
                'lipa_number': 'Halotel Money 777888',
                'payment_instructions': 'Go to Halotel Money > Payments > Enter Business Number > Enter Amount > Enter PIN',
            },
        ]
        
        for pm_data in payment_methods:
            pm, created = PaymentMethod.objects.get_or_create(
                network=pm_data['network'],
                defaults=pm_data
            )
            if created:
                network_name = dict(PaymentMethod.NETWORK_CHOICES).get(pm.network, pm.network)
                self.stdout.write(f'  Created payment method: {network_name}')

    def create_faqs(self):
        """Create default FAQ entries"""
        self.stdout.write('Creating FAQs...')
        
        faqs = [
            {
                'question': 'What is MtaalamuX?',
                'answer': 'MtaalamuX is a consultation platform that connects everyday users with verified experts for real consultation.',
                'category': 'general',
                'order': 1,
            },
            {
                'question': 'How do I become a verified expert?',
                'answer': 'To become a verified expert, you need to upgrade to Premium tier and submit your verification documents for admin review.',
                'category': 'verification',
                'order': 1,
            },
            {
                'question': 'What are the different user tiers?',
                'answer': 'MtaalamuX has three tiers: Basic (browse only), Professional (can initiate consultations), and Premium (verified experts who can post content and sell items).',
                'category': 'tiers',
                'order': 1,
            },
            {
                'question': 'How do I pay for consultations?',
                'answer': 'Payments are made offline via mobile money. We support M-Pesa, Airtel Money, Tigo Pesa, and Halotel Money.',
                'category': 'payments',
                'order': 1,
            },
            {
                'question': 'Can I refund a consultation?',
                'answer': 'Refunds are handled on a case-by-case basis. Please contact support if you need to request a refund.',
                'category': 'payments',
                'order': 2,
            },
        ]
        
        for faq_data in faqs:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
            if created:
                self.stdout.write(f'  Created FAQ: {faq.question}')
