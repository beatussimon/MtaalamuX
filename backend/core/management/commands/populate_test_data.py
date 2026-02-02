"""Django management command to populate database with test data"""
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from core.models import (
    UserProfile, Category, Professional, PortfolioItem,
    Conversation, Message, Article, Research, Comment, ServiceReview,
    UserTier, VerificationLevel
)


class Command(BaseCommand):
    help = 'Populate database with realistic test data'

    def __init__(self):
        super().__init__()
        self.faker = Faker()

        # Professional categories
        self.categories_data = [
            {'name': 'Computer Science', 'description': 'Study of computation, algorithms, and computer systems'},
            {'name': 'Data Science', 'description': 'Extracting insights from structured and unstructured data'},
            {'name': 'Artificial Intelligence', 'description': 'Development of intelligent systems and machine learning'},
            {'name': 'Cybersecurity', 'description': 'Protection of systems, networks, and data from digital attacks'},
            {'name': 'Software Engineering', 'description': 'Design, development, and maintenance of software systems'},
            {'name': 'Web Development', 'description': 'Building and maintaining websites and web applications'},
            {'name': 'Mobile Development', 'description': 'Creating applications for mobile devices'},
            {'name': 'Cloud Computing', 'description': 'On-demand computing resources and services over the internet'},
            {'name': 'DevOps', 'description': 'Practices combining software development and IT operations'},
            {'name': 'Blockchain Technology', 'description': 'Decentralized ledger technology and cryptocurrencies'},
            {'name': 'Digital Marketing', 'description': 'Marketing using digital channels and platforms'},
            {'name': 'Product Management', 'description': 'Managing product lifecycle and strategy'},
            {'name': 'UX/UI Design', 'description': 'Designing user interfaces and experiences'},
            {'name': 'Business Analysis', 'description': 'Analyzing business needs and requirements'},
            {'name': 'Project Management', 'description': 'Planning and executing projects successfully'},
        ]

        # Skills by category
        self.skills_by_category = {
            'Computer Science': ['Algorithms', 'Data Structures', 'Operating Systems', 'Computer Networks', 'Compilers'],
            'Data Science': ['Python', 'R', 'Machine Learning', 'Statistics', 'Data Visualization', 'SQL', 'Big Data'],
            'Artificial Intelligence': ['Deep Learning', 'Neural Networks', 'NLP', 'Computer Vision', 'Reinforcement Learning'],
            'Cybersecurity': ['Network Security', 'Penetration Testing', 'Cryptography', 'Security Auditing', 'Incident Response'],
            'Software Engineering': ['System Design', 'Testing', 'Code Review', 'Agile', 'CI/CD'],
            'Web Development': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Django', 'REST APIs'],
            'Mobile Development': ['Swift', 'Kotlin', 'React Native', 'Flutter', 'iOS', 'Android'],
            'Cloud Computing': ['AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker', 'Serverless'],
            'DevOps': ['Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Ansible', 'GitLab CI'],
            'Blockchain Technology': ['Solidity', 'Smart Contracts', 'Ethereum', 'Hyperledger', 'Web3'],
            'Digital Marketing': ['SEO', 'SEM', 'Social Media Marketing', 'Content Marketing', 'Analytics'],
            'Product Management': ['Product Strategy', 'Roadmapping', 'User Research', 'A/B Testing', 'Stakeholder Management'],
            'UX/UI Design': ['Figma', 'Sketch', 'User Research', 'Prototyping', 'Design Systems', 'Usability Testing'],
            'Business Analysis': ['Requirements Gathering', 'Process Modeling', 'SQL', 'Data Analysis', 'BA Tools'],
            'Project Management': ['PMP', 'Scrum', 'Kanban', 'Risk Management', 'Stakeholder Management'],
        }

        # Article topics
        self.article_topics = [
            'The Future of AI in Healthcare',
            'Best Practices for Cloud Security',
            'Machine Learning for Beginners',
            'DevOps Transformation Strategies',
            'Blockchain Beyond Cryptocurrency',
            'UX Design Trends for 2024',
            'Data Engineering Best Practices',
            'Cybersecurity in Remote Work Era',
            'Microservices Architecture Guide',
            'The Rise of Low-Code Platforms',
        ]

        # Research topics
        self.research_topics = [
            'Optimizing Neural Networks for Edge Devices',
            'Privacy-Preserving Machine Learning Techniques',
            'Scalable Distributed Systems Design',
            'Automated Software Testing Methodologies',
            'Quantum-Resistant Cryptographic Algorithms',
            'Natural Language Processing Advancements',
            'Real-Time Data Streaming Architectures',
            'Security Vulnerabilities in IoT Devices',
            'Energy-Efficient Computing Paradigms',
            'Human-Computer Interaction Research',
        ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)',
        )
        parser.add_argument(
            '--professionals',
            type=int,
            default=20,
            help='Number of professionals to create (default: 20)',
        )
        parser.add_argument(
            '--articles',
            type=int,
            default=30,
            help='Number of articles to create (default: 30)',
        )
        parser.add_argument(
            '--research',
            type=int,
            default=15,
            help='Number of research papers to create (default: 15)',
        )
        parser.add_argument(
            '--conversations',
            type=int,
            default=25,
            help='Number of conversations to create (default: 25)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        num_users = options['users']
        num_professionals = options['professionals']
        num_articles = options['articles']
        num_research = options['research']
        num_conversations = options['conversations']

        self.stdout.write('Creating categories...')
        categories = self.create_categories()

        self.stdout.write('Creating users...')
        users = self.create_users(num_users)

        self.stdout.write('Creating professionals...')
        professionals = self.create_professionals(num_professionals, categories, users)

        self.stdout.write('Creating portfolio items...')
        self.create_portfolio_items(professionals)

        self.stdout.write('Creating articles...')
        self.create_articles(num_articles, professionals, categories, users)

        self.stdout.write('Creating research papers...')
        self.create_research(num_research, professionals, categories, users)

        self.stdout.write('Creating conversations and messages...')
        self.create_conversations(num_conversations, users, professionals)

        self.stdout.write('Creating reviews...')
        self.create_reviews(professionals, users)

        self.stdout.write(self.style.SUCCESS(f'Successfully populated database with:'))
        self.stdout.write(f'  - {len(categories)} categories')
        self.stdout.write(f'  - {len(users)} users')
        self.stdout.write(f'  - {len(professionals)} professionals')
        self.stdout.write(f'  - {num_articles} articles')
        self.stdout.write(f'  - {num_research} research papers')
        self.stdout.write(f'  - {num_conversations} conversations with messages')
        self.stdout.write(f'  - Reviews')

    def clear_data(self):
        """Clear all data from the database"""
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Comment.objects.all().delete()
        ServiceReview.objects.all().delete()
        Article.objects.all().delete()
        Research.objects.all().delete()
        PortfolioItem.objects.all().delete()
        Professional.objects.all().delete()
        UserProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Category.objects.all().delete()

    def create_categories(self):
        """Create professional categories"""
        categories = []
        for cat_data in self.categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
        return categories

    def create_users(self, count):
        """Create regular users with profiles"""
        users = []
        tier_weights = [(UserTier.BASIC, 50), (UserTier.PLUS, 30), (UserTier.PREMIUM, 20)]

        for i in range(count):
            # Generate fake user data
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@{self.faker.domain_name()}"

            # Ensure unique username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password='Testpass123!',
                first_name=first_name,
                last_name=last_name,
            )

            # Create user profile
            tier = random.choices(
                [t[0] for t in tier_weights],
                weights=[t[1] for t in tier_weights]
            )[0]

            profile = UserProfile.objects.create(
                user=user,
                tier=tier,
                bio=self.faker.paragraph(nb_sentences=3),
                interests=', '.join(self.faker.words(nb=5)),
                theme=random.choice(['light', 'dark']),
            )
            users.append(user)

        # Create a demo admin user
        if not User.objects.filter(username='demoadmin').exists():
            demo_admin = User.objects.create_superuser(
                username='demoadmin',
                email='admin@mtaalamux.com',
                password='Demoadmin123!',
                first_name='Demo',
                last_name='Admin',
            )
            UserProfile.objects.create(
                user=demo_admin,
                tier=UserTier.PREMIUM,
                bio='Platform administrator',
            )
            users.append(demo_admin)

        # Create demo users
        demo_users = ['demouser', 'demoprofessional']
        for demo_username in demo_users:
            if not User.objects.filter(username=demo_username).exists():
                first_name = 'Demo'
                last_name = demo_username.title().replace('demo', '')
                demo_user = User.objects.create_user(
                    username=demo_username,
                    email=f"{demo_username}@mtaalamux.com",
                    password='Demo123!',
                    first_name=first_name,
                    last_name=last_name,
                )

                tier = UserTier.PLUS if 'plus' in demo_username else UserTier.BASIC
                UserProfile.objects.create(
                    user=demo_user,
                    tier=tier,
                    bio=self.faker.paragraph(nb_sentences=3),
                )
                users.append(demo_user)

        return users

    def create_professionals(self, count, categories, users):
        """Create verified professionals"""
        professionals = []
        basic_profiles = UserProfile.objects.filter(tier=UserTier.BASIC)

        for i in range(count):
            if not basic_profiles.exists():
                break

            # Get a basic user who doesn't have a professional profile
            profile = basic_profiles.exclude(
                user__professional__isnull=False
            ).first()

            if not profile:
                break

            category = random.choice(categories)
            available_skills = self.skills_by_category.get(category.name, ['General Skills'])
            num_skills = min(random.randint(3, 6), len(available_skills))
            skills = random.sample(available_skills, k=num_skills)

            professional = Professional.objects.create(
                user=profile.user,
                field=category,
                subfield=self.faker.job(),
                location=f"{self.faker.city()}, {self.faker.country()}",
                skills=skills,
                bio=self.faker.paragraph(nb_sentences=5),
                is_verified=True,
                verification_level=random.choice([VerificationLevel.GREEN, VerificationLevel.GOLD]),
                verified_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                linkedin_url=self.faker.url(),
                twitter_url=self.faker.url(),
                is_featured=random.random() < 0.2,
            )

            # Upgrade profile to premium
            profile.tier = UserTier.PREMIUM
            profile.save()

            professionals.append(professional)

            # Add some followers
            potential_followers = random.sample(
                users,
                k=random.randint(5, min(30, len(users)))
            )
            for follower in potential_followers:
                if follower != profile.user:
                    professional.followers.add(follower)

        return professionals

    def create_portfolio_items(self, professionals):
        """Create portfolio items for professionals"""
        portfolio_titles = [
            'E-Commerce Platform Redesign',
            'Mobile Banking App',
            'Machine Learning Pipeline',
            'Cloud Migration Project',
            'API Gateway Implementation',
            'Data Visualization Dashboard',
            'Security Audit Report',
            'IoT Monitoring System',
            'Content Management System',
            'Social Media Analytics Tool',
        ]

        for professional in professionals:
            num_items = random.randint(2, 5)
            selected_titles = random.sample(portfolio_titles, k=num_items)

            for title in selected_titles:
                PortfolioItem.objects.create(
                    professional=professional,
                    title=title,
                    description=self.faker.paragraph(nb_sentences=2),
                )

    def create_articles(self, count, professionals, categories, users):
        """Create articles"""
        article_contents = [
            """In today's rapidly evolving technological landscape, artificial intelligence continues to transform industries across the globe. From healthcare to finance, AI-powered solutions are revolutionizing how we approach complex problems.

            Machine learning algorithms have become increasingly sophisticated, enabling systems to learn from data and make predictions with unprecedented accuracy. This has opened up new possibilities for automation, personalization, and decision-making.

            However, with great power comes great responsibility. Organizations must carefully consider the ethical implications of AI deployment, ensuring fairness, transparency, and accountability in their systems.""",

            """Cloud computing has fundamentally changed how businesses operate in the modern world. The ability to scale resources on-demand, reduce infrastructure costs, and deploy applications globally has made cloud platforms essential for organizations of all sizes.

            Major cloud providers offer a wide range of services, from basic compute and storage to advanced machine learning and analytics capabilities. This democratization of technology has leveled the playing field, allowing startups to compete with established enterprises.

            As we move forward, cloud-native architectures and serverless computing are becoming the norm, enabling developers to focus on writing code rather than managing infrastructure.""",

            """Cybersecurity threats continue to evolve in sophistication and scale. Organizations face constant challenges from nation-state actors, cybercriminals, and hacktivists seeking to exploit vulnerabilities for financial gain or ideological reasons.

            A comprehensive security strategy must address multiple layers of defense, including network security, application security, data protection, and user education. Zero-trust architectures are gaining traction as traditional perimeter-based defenses prove insufficient.

            Regular security assessments, penetration testing, and incident response planning are essential components of a robust security program.""",

            """User experience design has become a critical differentiator in today's competitive marketplace. Companies that prioritize user-centric design see higher customer satisfaction, increased engagement, and improved business outcomes.

            Understanding user needs through research, testing, and iteration is fundamental to creating products that resonate with their intended audience. Design systems help maintain consistency while enabling rapid iteration.

            The future of UX lies in personalization, accessibility, and creating seamless experiences across all touchpoints.""",

            """DevOps practices have transformed software development and operations, enabling teams to deliver value faster while maintaining high quality standards. Continuous integration and continuous deployment (CI/CD) pipelines have become industry standards.

            Infrastructure as code allows teams to manage and provision infrastructure through code, ensuring consistency and enabling version control. Automated testing and monitoring provide rapid feedback and early detection of issues.

            The cultural shift towards collaboration, shared responsibility, and continuous improvement is what makes DevOps truly powerful.""",
        ]

        published_professionals = [p for p in professionals if p.article_count > 0]

        for i in range(count):
            if not published_professionals:
                break

            author = random.choice(published_professionals)
            category = random.choice(categories)
            title = f"{random.choice(self.article_topics)}: {self.faker.sentence(nb_words=6)}"

            article = Article.objects.create(
                author=author,
                title=title,
                content=random.choice(article_contents),
                category=category,
                is_published=True,
                is_featured=random.random() < 0.15,
                views=random.randint(50, 5000),
                shares=random.randint(0, 100),
            )

            # Add likes from random users
            num_likes = random.randint(5, min(30, len(users)))
            likers = random.sample(users, k=num_likes)
            article.likes.set(likers)

            # Add comments
            num_comments = random.randint(0, 10)
            for _ in range(num_comments):
                commenter = random.choice(users)
                Comment.objects.create(
                    article=article,
                    user=commenter,
                    content=self.faker.paragraph(nb_sentences=2),
                )

    def create_research(self, count, professionals, categories, users):
        """Create research papers"""
        research_contents = [
            """Abstract:
This research presents a novel approach to optimizing neural network architectures for edge computing devices. We propose a method for efficient model compression that maintains accuracy while significantly reducing computational requirements.

Introduction:
Edge computing has emerged as a critical paradigm for deploying machine learning models in resource-constrained environments. However, deploying deep learning models on edge devices remains challenging due to memory and computational limitations.

Methodology:
Our approach combines pruning, quantization, and knowledge distillation techniques to achieve optimal compression ratios. We evaluate our method on multiple benchmark datasets and compare against existing approaches.

Results:
Experimental results demonstrate that our proposed method achieves comparable accuracy to full-precision models while reducing model size by up to 90% and inference time by 85%.

Conclusion:
This research provides a practical framework for deploying efficient neural networks on edge devices, enabling new applications in IoT, mobile computing, and embedded systems.""",

            """Abstract:
We present a comprehensive study on privacy-preserving machine learning techniques for sensitive data analysis. Our research addresses the critical challenge of training ML models without exposing underlying training data.

Introduction:
The increasing demand for data-driven insights must be balanced with privacy concerns and regulatory requirements such as GDPR and HIPAA. This has led to growing interest in privacy-preserving machine learning approaches.

Methodology:
We evaluate federated learning, differential privacy, and secure multi-party computation techniques across various ML tasks and datasets. Our study includes both theoretical analysis and empirical evaluation.

Results:
Our findings indicate that combining multiple privacy-preserving techniques can achieve strong privacy guarantees with minimal impact on model performance. Federated learning shows particular promise for cross-organizational collaboration.

Conclusion:
Privacy-preserving ML represents a crucial direction for responsible AI development, enabling organizations to derive value from data while respecting individual privacy rights.""",

            """Abstract:
This paper explores the design principles and implementation strategies for scalable distributed systems. We examine common patterns, anti-patterns, and best practices drawn from industry experience and academic research.

Introduction:
Distributed systems form the backbone of modern internet services, enabling scalability, reliability, and performance at unprecedented scales. However, designing and implementing distributed systems remains challenging due to inherent complexity.

Methodology:
We analyze production systems from major technology companies and derive patterns based on observed success factors and common failure modes.

Results:
Key findings include the importance of graceful degradation, effective caching strategies, and robust failure handling mechanisms. We provide practical recommendations for each layer of the system architecture.

Conclusion:
By following established design principles and learning from real-world implementations, organizations can build distributed systems that meet the demands of modern applications.""",
        ]

        published_professionals = [p for p in professionals if p.research_count > 0]

        for i in range(count):
            if not published_professionals:
                break

            author = random.choice(published_professionals)
            category = random.choice(categories)
            title = f"{random.choice(self.research_topics)}: A Comprehensive Study"

            research = Research.objects.create(
                author=author,
                title=title,
                abstract=self.faker.paragraph(nb_sentences=3),
                content=random.choice(research_contents),
                category=category,
                tags=random.sample(self.faker.words(10), k=5),
                status='published',
                is_featured=random.random() < 0.2,
                views=random.randint(100, 3000),
                shares=random.randint(0, 50),
            )

            # Add likes
            num_likes = random.randint(3, min(20, len(users)))
            likers = random.sample(users, k=num_likes)
            research.likes.set(likers)

            # Add comments
            num_comments = random.randint(0, 5)
            for _ in range(num_comments):
                commenter = random.choice(users)
                Comment.objects.create(
                    research=research,
                    user=commenter,
                    content=self.faker.paragraph(nb_sentences=2),
                )

    def create_conversations(self, count, users, professionals):
        """Create conversations and messages"""
        conversation_subjects = [
            'Consultation on AI Implementation',
            'Cloud Migration Strategy Discussion',
            'Cybersecurity Assessment Request',
            'Web Development Project Inquiry',
            'Data Science Collaboration',
            'Mobile App Development',
            'DevOps Pipeline Setup',
            'UX Design Feedback',
            'Research Collaboration Opportunity',
            'Technical Mentorship Request',
            'System Architecture Review',
            'Product Strategy Discussion',
            'Career Guidance Session',
            'Code Review Assistance',
            'Technology Selection Advice',
        ]

        consultation_types = ['general', 'technical', 'career', 'project', 'research']

        for i in range(count):
            # Select participants
            num_participants = random.randint(2, min(4, len(users)))
            participants = random.sample(users, k=num_participants)

            # Create conversation
            conversation = Conversation.objects.create(
                subject=random.choice(conversation_subjects),
                consultation_type=random.choice(consultation_types),
                status=random.choice(['active', 'completed']),
                created_by=participants[0],
            )
            conversation.participants.set(participants)

            # Add messages
            num_messages = random.randint(3, 15)
            current_time = datetime.now() - timedelta(days=random.randint(1, 30))

            for j in range(num_messages):
                sender = random.choice(participants)
                message_content = self.faker.paragraph(nb_sentences=random.randint(1, 4))

                # Add some variation to simulate real conversation
                if j == 0:
                    message_content = f"Hi! I'm interested in discussing {conversation.subject.lower()}. Could you share your insights on this topic?"
                elif j == num_messages - 1:
                    message_content = f"Thank you for the detailed explanation. This has been very helpful!"

                message = Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    content=message_content,
                    timestamp=current_time,
                    is_read=random.random() < 0.7,
                )

                current_time += timedelta(hours=random.randint(1, 48))

    def create_reviews(self, professionals, users):
        """Create service reviews for professionals"""
        review_comments = [
            "Excellent work! Very professional and knowledgeable. Would highly recommend.",
            "Great experience working with this professional. Delivered beyond expectations.",
            "Very helpful consultation. Provided valuable insights that helped our project succeed.",
            "Professional and responsive. Would definitely work with again.",
            "Outstanding expertise in the field. Solved our complex problems efficiently.",
            "Great communication throughout the project. Very satisfied with the results.",
            "Exceptional quality of work. Exceeded all expectations.",
            "Very knowledgeable and patient. Explained complex concepts clearly.",
            "Professional delivery and excellent results. Thank you for the great collaboration.",
            "Top-notch expertise and great to work with. Highly recommended!",
        ]

        for professional in professionals:
            num_reviews = random.randint(3, min(10, len(users)))
            reviewers = random.sample(
                [u for u in users if u != professional.user],
                k=min(num_reviews, len(users) - 1)
            )

            for reviewer in reviewers:
                ServiceReview.objects.create(
                    professional=professional,
                    reviewer=reviewer,
                    rating=random.randint(4, 5),
                    comment=random.choice(review_comments),
                    response=random.choice([
                        "Thank you for your kind words! It was a pleasure working with you.",
                        "I appreciate your feedback. Happy to have helped!",
                        "Thank you! Feel free to reach out if you need anything else.",
                        "Great working with you too! Looking forward to future collaborations.",
                        "",
                    ]),
                )
