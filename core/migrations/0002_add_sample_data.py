from django.db import migrations
# Use apps.get_model instead of direct import for historical safety
# from django.contrib.auth.models import User
# from django.utils import timezone # Use django.utils.timezone below
import datetime
from django.contrib.auth.hashers import make_password # Import password hasher
from django.utils import timezone as django_timezone # Import timezone

def add_sample_data(apps, schema_editor):
    # Get historical models using apps.get_model
    User = apps.get_model('auth', 'User') # Correct way to get User in migrations
    UserProfile = apps.get_model('core', 'UserProfile')
    Category = apps.get_model('core', 'Category')
    Professional = apps.get_model('core', 'Professional')
    PortfolioItem = apps.get_model('core', 'PortfolioItem')
    Message = apps.get_model('core', 'Message')
    Article = apps.get_model('core', 'Article')
    Comment = apps.get_model('core', 'Comment')
    ServiceReview = apps.get_model('core', 'ServiceReview')
    Favorite = apps.get_model('core', 'Favorite')
    Notification = apps.get_model('core', 'Notification')
    ActivityLog = apps.get_model('core', 'ActivityLog')
    Job = apps.get_model('core', 'Job')
    JobDocument = apps.get_model('core', 'JobDocument')
    UpgradeRequest = apps.get_model('core', 'UpgradeRequest')
    FAQ = apps.get_model('core', 'FAQ')
    Feedback = apps.get_model('core', 'Feedback')
    CustomAdmin = apps.get_model('core', 'CustomAdmin')
    AdminHelper = apps.get_model('core', 'AdminHelper')
    Badge = apps.get_model('core', 'Badge')
    VerificationToken = apps.get_model('core', 'VerificationToken')

    # --- Create Users using correct get_or_create pattern ---
    users_data = [
        {'username': 'john_doe', 'email': 'john.doe@example.com', 'password': 'password123', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane_smith', 'email': 'jane.smith@example.com', 'password': 'password123', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'mike_pro', 'email': 'mike.pro@example.com', 'password': 'password123', 'first_name': 'Mike', 'last_name': 'Professional'},
        # Ensure admin has staff status if needed by CustomAdmin or other logic
        {'username': 'admin_user', 'email': 'admin@example.com', 'password': 'adminpass', 'first_name': 'Admin', 'last_name': 'User', 'is_staff': True},
    ]

    users = {} # Store user objects in a dict by username
    for data in users_data:
        username = data['username']
        raw_password = data.pop('password') # Get raw password
        is_staff_flag = data.get('is_staff', False) # Check if staff flag is set

        # Use username for lookup, other fields in defaults
        user_obj, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': data.get('email', ''),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'password': make_password(raw_password), # HASH the password
                'is_staff': is_staff_flag,
                'is_active': True, # Typically want sample users active
            }
        )
        users[username] = user_obj # Store the fetched/created user object

        if created:
            print(f"Created sample user: {username}")
        # Optional: If user existed, you might want to ensure password is correct
        # elif not user_obj.check_password(raw_password):
        #    user_obj.set_password(raw_password)
        #    user_obj.save()
        #    print(f"Password reset for existing user: {username}")
        else:
            print(f"Sample user '{username}' already exists.")


    # --- UserProfile ---
    # Apply the same pattern: use unique FK for lookup, others in defaults
    UserProfile.objects.get_or_create(
        user=users['john_doe'],
        defaults={'bio': "Software developer with a passion for open-source.", 'avatar': '', 'interests': "Python, AI", 'theme': 'dark'}
    )
    UserProfile.objects.get_or_create(
        user=users['jane_smith'],
        defaults={'bio': "Graphic designer specializing in branding.", 'avatar': '', 'interests': "Design, Illustration", 'theme': 'light'}
    )
    UserProfile.objects.get_or_create(
        user=users['mike_pro'],
        defaults={'is_professional': True, 'bio': "Experienced web developer.", 'avatar': '', 'interests': "Web Dev, JavaScript", 'theme': 'dark'}
    )
    UserProfile.objects.get_or_create(
        user=users['admin_user'],
        defaults={'bio': "Site administrator.", 'avatar': '', 'interests': "Management", 'theme': 'light'}
    )

    # --- Category ---
    # get_or_create is fine here since 'name' is the unique identifier being used
    categories = {
        "Software Development": Category.objects.get_or_create(name="Software Development")[0],
        "Graphic Design": Category.objects.get_or_create(name="Graphic Design")[0],
        "Digital Marketing": Category.objects.get_or_create(name="Digital Marketing")[0],
    }

    # --- Professional ---
    # Use user for lookup, rest in defaults
    professionals = {}
    prof_obj, _ = Professional.objects.get_or_create(
        user=users['mike_pro'], # Lookup by user (which is unique via OneToOne)
        defaults={
            'field': categories["Software Development"], 'subfield': "Frontend Development", 'location': "Nairobi, Kenya",
            'skills': ["HTML", "CSS", "React"], 'photo': 'professionals/mike.jpg', 'bio': "5+ years in web dev.",
            'is_verified': True, 'linkedin_url': "https://linkedin.com/in/mikepro", 'cv': 'verification/cvs/mike_cv.pdf'
        }
    )
    professionals['mike_pro'] = prof_obj

    prof_obj, _ = Professional.objects.get_or_create(
        user=users['jane_smith'], # Lookup by user
        defaults={
            'field': categories["Graphic Design"], 'subfield': "UI/UX Design", 'location': "Lagos, Nigeria",
            'skills': ["Photoshop", "Figma"], 'photo': 'professionals/jane.jpg', 'bio': "Creative designer with 3 years exp.",
            'is_verified': False, 'website_url': "https://janesmith.design"
        }
    )
    professionals['jane_smith'] = prof_obj

    # --- PortfolioItem ---
    # Lookup by professional and title (assuming this combo is unique enough for sample data)
    PortfolioItem.objects.get_or_create(
        professional=professionals['mike_pro'], title="E-commerce Website",
        defaults={
            'description': "Built with React and Django.", 'file': 'portfolio/ecommerce.zip',
            'created_at': django_timezone.now() - datetime.timedelta(days=30) # Use imported timezone
        }
    )
    PortfolioItem.objects.get_or_create(
        professional=professionals['jane_smith'], title="Brand Logo",
        defaults={
            'description': "Logo design for a startup.", 'file': 'portfolio/logo.pdf',
            'created_at': django_timezone.now() - datetime.timedelta(days=15)
        }
    )

    # --- Message ---
    # For things like messages, simple create might be okay unless you absolutely
    # need idempotency. Let's make it idempotent for safety.
    Message.objects.get_or_create(
        sender=users['john_doe'], recipient=users['mike_pro'], content="Hi Mike, can you help with a React project?",
        defaults={ # Use timestamp in defaults if creating
            'timestamp': django_timezone.now() - datetime.timedelta(hours=5), 'is_read': False
        }
    )
    Message.objects.get_or_create(
        sender=users['mike_pro'], recipient=users['john_doe'], content="Sure, let’s discuss details!",
        defaults={
             'file': 'messages/spec.pdf',
             'timestamp': django_timezone.now() - datetime.timedelta(hours=4), 'is_read': True
        }
    )


    # ... (Continue applying the correct get_or_create pattern for other models) ...
    # --- Article ---
    articles = {}
    art_obj, _ = Article.objects.get_or_create(
        author=professionals['mike_pro'], title="Mastering React Hooks",
        defaults={
            'content': "A deep dive into useEffect and useState...", 'image': 'articles/react_hooks.jpg',
            'category': "Software Development", 'publish_date': django_timezone.now() - datetime.timedelta(days=10),
            'views': 150, 'shares': 25
        }
    )
    articles['react_hooks'] = art_obj
    # Add likes separately after get_or_create
    art_obj.likes.add(users['john_doe'], users['jane_smith'])


    art_obj, _ = Article.objects.get_or_create(
        author=professionals['jane_smith'], title="Top 5 Design Trends in 2025",
        defaults={
            'content': "Exploring modern design aesthetics...", 'image': 'articles/design_trends.jpg',
            'category': "Graphic Design", 'publish_date': django_timezone.now() - datetime.timedelta(days=5),
            'views': 80, 'shares': 10
        }
    )
    articles['design_trends'] = art_obj


    # --- Comment ---
    # NOTE: Original had incorrect likes=[users[2]] inside get_or_create
    cmt_obj, _ = Comment.objects.get_or_create(
        article=articles['react_hooks'], user=users['jane_smith'], content="Great article, very insightful!",
        defaults={'created_at': django_timezone.now() - datetime.timedelta(days=9)}
    )

    cmt_obj, _ = Comment.objects.get_or_create(
        article=articles['design_trends'], user=users['john_doe'], content="Love the color palette ideas!",
        defaults={'created_at': django_timezone.now() - datetime.timedelta(days=4)}
    )
    # Add likes after creation/getting the object
    cmt_obj.likes.add(users['mike_pro'])

    # --- ServiceReview ---
    ServiceReview.objects.get_or_create(
        professional=professionals['mike_pro'], reviewer=users['john_doe'],
        defaults={
            'rating': 5, 'comment': "Mike delivered an amazing website!",
            'created_at': django_timezone.now() - datetime.timedelta(days=20)
        }
    )
    ServiceReview.objects.get_or_create(
        professional=professionals['jane_smith'], reviewer=users['mike_pro'], # user[2] is mike_pro
        defaults={
            'rating': 4, 'comment': "Great design, but took a bit long.",
            'created_at': django_timezone.now() - datetime.timedelta(days=10), 'response': "Thanks, working on speed!"
        }
    )

    # --- Favorite ---
    # get_or_create is correct here due to unique_together
    Favorite.objects.get_or_create(user=users['john_doe'], professional=professionals['jane_smith'])
    Favorite.objects.get_or_create(user=users['jane_smith'], professional=professionals['mike_pro'])

    # --- Notification ---
    # Make idempotent
    Notification.objects.get_or_create(
        user=users['john_doe'], message="Jane Smith liked your comment.",
        defaults={'created_at': django_timezone.now() - datetime.timedelta(hours=3)}
    )
    Notification.objects.get_or_create(
        user=users['mike_pro'], message="New job posted in your field!", # user[2] is mike_pro
        defaults={'created_at': django_timezone.now() - datetime.timedelta(hours=1), 'is_read': True}
    )

    # --- ActivityLog ---
    ActivityLog.objects.get_or_create(
        user=users['john_doe'], action="Logged in",
        defaults={'timestamp': django_timezone.now() - datetime.timedelta(hours=6)}
    )
    ActivityLog.objects.get_or_create(
        user=users['mike_pro'], action="Published article", # user[2] is mike_pro
        defaults={'timestamp': django_timezone.now() - datetime.timedelta(days=10)}
    )

    # --- Job ---
    jobs = {}
    job_obj, _ = Job.objects.get_or_create(
        professional=professionals['mike_pro'], title="Build a Portfolio Site",
        defaults={
            'client': users['john_doe'], 'description': "Need a responsive site.",
            'budget': 500.00, 'status': 'open', 'created_at': django_timezone.now() - datetime.timedelta(days=7)
        }
    )
    jobs['portfolio_site'] = job_obj

    job_obj, _ = Job.objects.get_or_create(
        professional=professionals['jane_smith'], title="Design a Logo",
        defaults={
             'description': "Startup needs branding.", # Removed client as it wasn't in original defaults
             'budget': 150.00, 'status': 'completed', 'created_at': django_timezone.now() - datetime.timedelta(days=14)
        }
    )
    jobs['logo_design'] = job_obj


    # --- JobDocument ---
    JobDocument.objects.get_or_create(job=jobs['portfolio_site'], document='job_documents/requirements.pdf')
    JobDocument.objects.get_or_create(job=jobs['logo_design'], document='job_documents/final_logo.pdf')

    # --- UpgradeRequest ---
    UpgradeRequest.objects.get_or_create(
        user=users['mike_pro'], upgrade_type='premium_profile', # user[2] is mike_pro
        defaults={'status': 'pending', 'requested_at': django_timezone.now() - datetime.timedelta(days=2)}
    )
    UpgradeRequest.objects.get_or_create(
        user=users['jane_smith'], upgrade_type='featured_article', # user[1] is jane_smith
        defaults={'status': 'verified', 'requested_at': django_timezone.now() - datetime.timedelta(days=5)}
    )

    # --- FAQ ---
    FAQ.objects.get_or_create(
        question="How do I become a verified professional?",
        defaults={'answer': "Submit your CV and certificates for review.", 'created_at': django_timezone.now() - datetime.timedelta(days=30)}
    )
    FAQ.objects.get_or_create(
        question="What is a premium profile?",
        defaults={'answer': "Unlock additional features like job boosts.", 'created_at': django_timezone.now() - datetime.timedelta(days=25)}
    )

    # --- Feedback ---
    Feedback.objects.get_or_create(
        user=users['john_doe'], message="Love the platform, but needs more categories!",
        defaults={'submitted_at': django_timezone.now() - datetime.timedelta(days=3)}
    )
    Feedback.objects.get_or_create(
        message="Great site, easy to use.", # Anonymous feedback needs a unique lookup if using get_or_create
        defaults={'submitted_at': django_timezone.now() - datetime.timedelta(days=1)}
    )


    # --- CustomAdmin ---
    custom_admin, _ = CustomAdmin.objects.get_or_create(user=users['admin_user'], defaults={'is_active': True}) # user[3] is admin_user


    # --- AdminHelper ---
    AdminHelper.objects.get_or_create(custom_admin=custom_admin, user=users['john_doe'], task='verify_professionals') # user[0]
    AdminHelper.objects.get_or_create(custom_admin=custom_admin, user=users['jane_smith'], task='manage_articles') # user[1]


    # --- Badge ---
    Badge.objects.get_or_create(user=users['mike_pro'], tier='verified_professional', defaults={'awarded_at': django_timezone.now() - datetime.timedelta(days=15)}) # user[2]
    Badge.objects.get_or_create(user=users['john_doe'], tier='premium_user', defaults={'awarded_at': django_timezone.now() - datetime.timedelta(days=5)}) # user[0]


    # --- VerificationToken ---
    VerificationToken.objects.get_or_create(
        user=users['mike_pro'], token="abc123xyz", # user[2]
        defaults={'created_at': django_timezone.now() - datetime.timedelta(days=1), 'expires_at': django_timezone.now() + datetime.timedelta(days=6)}
    )
    VerificationToken.objects.get_or_create(
        user=users['jane_smith'], token="def456uvw", # user[1]
        defaults={'created_at': django_timezone.now() - datetime.timedelta(days=2), 'expires_at': django_timezone.now() + datetime.timedelta(days=5)}
    )


# It's good practice to provide a way to reverse data migrations if possible,
# but for simple additions, a no-op is often acceptable.
# If reversing, you'd typically delete the objects based on the same lookups.
# def remove_sample_data(apps, schema_editor):
#    # ... delete logic ...
#    pass

class Migration(migrations.Migration):
    dependencies = [
        # Ensure dependency on the previous migration of the 'core' app
        ('core', '0001_initial'),
        # It's often safer to depend on the auth app's latest migration too,
        # in case its structure changed, although usually not strictly necessary for get_model
        ('auth', '0012_alter_user_first_name_max_length'), # Or replace 0012... with the actual latest auth migration you have
    ]

    operations = [
        # Use RunPython.noop for the reverse operation if you don't need to undo the data seeding
        migrations.RunPython(add_sample_data, reverse_code=migrations.RunPython.noop),
    ]