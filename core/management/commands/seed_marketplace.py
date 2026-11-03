from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User, FreelancerProfile, ClientProfile
from projects.models import Category, Skill, Project, SavedProject
from proposals.models import Proposal
from workspace.models import ProjectDeliverable, ProjectMessage
from reviews.models import Review
from notifications.models import Notification

class Command(BaseCommand):
    help = "Seeds database with realistic neo-brutalist marketplace data"

    def handle(self, *args, **options):
        self.stdout.write("Starting Prolance marketplace seeding...")

        # 1. Create Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@prolance.io',
                'full_name': 'Prolance System Administrator',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('adminpass123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / adminpass123"))

        # 2. Categories
        categories_data = [
            ('UI/UX Design', 'palette', 'yellow', 'Brand identity, design systems, design sprints, and responsive web styling.'),
            ('Web Development', 'code-2', 'mint', 'Full-stack web applications, APIs, database architectures, and reactive frontends.'),
            ('DevOps & Cloud', 'server', 'indigo', 'Infrastructure as Code, CI/CD automation pipelines, Docker orchestration, and cloud clusters.'),
            ('Mobile Engineering', 'smartphone', 'coral', 'Native iOS, Android, and universal cross-platform applications.'),
            ('AI & Machine Learning', 'sparkles', 'pink', 'LLM integrations, agentic pipelines, computer vision, and structured data intelligence.'),
            ('Cybersecurity & Audit', 'shield-check', 'lime', 'Penetration testing, source code audits, compliance reviews, and authentication security.'),
        ]

        category_objs = {}
        for name, icon, theme, desc in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'color_theme': theme, 'description': desc}
            )
            category_objs[name] = cat

        # 3. Skills
        skills_data = [
            ('Python', 'Web Development'),
            ('Django', 'Web Development'),
            ('Tailwind CSS', 'UI/UX Design'),
            ('Figma', 'UI/UX Design'),
            ('Design Systems', 'UI/UX Design'),
            ('Docker', 'DevOps & Cloud'),
            ('PostgreSQL', 'Web Development'),
            ('FastAPI', 'Web Development'),
            ('AWS', 'DevOps & Cloud'),
            ('Flutter', 'Mobile Engineering'),
            ('React Native', 'Mobile Engineering'),
            ('PyTorch', 'AI & Machine Learning'),
            ('LangChain', 'AI & Machine Learning'),
            ('AppSec', 'Cybersecurity & Audit'),
        ]

        skill_objs = {}
        for skill_name, cat_name in skills_data:
            sk, _ = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': category_objs.get(cat_name)}
            )
            skill_objs[skill_name] = sk

        # 4. Clients
        clients_data = [
            ('kristi_client', 'kristi@studio.design', 'Kristina Vance', 'Kristi Digital Studio', 'Creative Agency', 'Berlin, Germany', 'Digital product studio crafting growth engines and high-conversion brand experiences.'),
            ('acme_labs', 'founder@acmelabs.tech', 'David Chen', 'Acme Systems', 'B2B SaaS', 'San Francisco, CA', 'Building enterprise monitoring and real-time infrastructure platforms.'),
            ('fintech_corp', 'ops@fintechcorp.io', 'Sarah Jenkins', 'Apex Fintech Group', 'Financial Technology', 'London, UK', 'Next-generation compliance, algorithmic trade settlement, and payments.'),
        ]

        client_users = []
        for username, email, full_name, company, industry, location, bio in clients_data:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'full_name': full_name,
                    'role': User.ROLE_CLIENT,
                }
            )
            if created:
                u.set_password('clientpass123')
                u.save()
            cp, _ = ClientProfile.objects.get_or_create(
                user=u,
                defaults={
                    'company_name': company,
                    'industry': industry,
                    'location': location,
                    'bio': bio,
                }
            )
            client_users.append(u)

        # 5. Freelancers
        freelancers_data = [
            (
                'kristina_design', 'kristina@prolance.io', 'Kristina Kowalska',
                'Senior Growth Product Designer & Design System Mentor',
                '10+ years specializing in modern neo-brutalist interfaces, conversion architecture, and design systems for funded startups.',
                Decimal('85.00'), 8, 'https://kristi.digital', 'https://github.com/kristina-design', True,
                ['Figma', 'Design Systems', 'Tailwind CSS']
            ),
            (
                'marcus_dev', 'marcus@prolance.io', 'Marcus Thorne',
                'Full-Stack Django & Python Architect',
                'Senior software engineer dedicated to building resilient monolithic applications, clean database architectures, and fast REST APIs.',
                Decimal('75.00'), 6, 'https://marcusdev.io', 'https://github.com/marcusthorne', True,
                ['Python', 'Django', 'PostgreSQL', 'Tailwind CSS', 'Docker']
            ),
            (
                'elena_arch', 'elena@prolance.io', 'Elena Rostova',
                'DevSecOps Engineer & Cloud Infrastructure Specialist',
                'Automating high-reliability deployment pipelines with Docker, Kubernetes, and AWS infrastructure as code.',
                Decimal('95.00'), 7, 'https://elena-ops.dev', 'https://github.com/elena-ops', True,
                ['Docker', 'AWS', 'Python', 'AppSec']
            ),
            (
                'sam_mobile', 'sam@prolance.io', 'Samuel O’Connor',
                'Cross-Platform Mobile Engineer (Flutter & React Native)',
                'Delivering sleek, performance-critical native apps with zero lag and pixel-perfect design alignment.',
                Decimal('65.00'), 5, 'https://samuelmobile.app', 'https://github.com/samoconnor', False,
                ['Flutter', 'React Native', 'Figma']
            ),
        ]

        freelancer_users = {}
        for uname, uemail, ufullname, headline, bio, rate, yrs, port, gh, avail, skills in freelancers_data:
            fu, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'email': uemail,
                    'full_name': ufullname,
                    'role': User.ROLE_FREELANCER,
                }
            )
            if created:
                fu.set_password('freepass123')
                fu.save()
            fp, _ = FreelancerProfile.objects.get_or_create(
                user=fu,
                defaults={
                    'headline': headline,
                    'bio': bio,
                    'hourly_rate': rate,
                    'experience_years': yrs,
                    'portfolio_url': port,
                    'github_url': gh,
                    'is_available': avail,
                }
            )
            freelancer_users[uname] = fu

        # 6. Projects in various lifecycle stages
        now = timezone.now().date()
        kristina = freelancer_users['kristina_design']
        marcus = freelancer_users['marcus_dev']
        client_kristi = client_users[0]
        client_acme = client_users[1]
        client_fintech = client_users[2]

        # Project 1: OPEN project
        p1, _ = Project.objects.get_or_create(
            slug='neo-brutalist-fintech-design-system',
            defaults={
                'client': client_fintech,
                'title': 'Neo-Brutalist FinTech Design System & Component Library',
                'category': category_objs['UI/UX Design'],
                'project_type': Project.TYPE_FIXED,
                'budget_min': Decimal('2500.00'),
                'budget_max': Decimal('4500.00'),
                'deadline': now + timedelta(days=21),
                'status': Project.STATUS_OPEN,
                'description': (
                    "We require a comprehensive, high-contrast Neo-Brutalist design system for our algorithmic trade execution dashboard.\n\n"
                    "Scope of Work:\n"
                    "1. High-contrast color tokens and typography scale (Space Grotesk).\n"
                    "2. 40+ interactive UI components with 2.5px solid black borders and offset drop shadows.\n"
                    "3. Figma components with full AutoLayout and responsive variants.\n"
                    "4. Exported Tailwind CSS configuration and reusable HTML component snippets."
                )
            }
        )
        p1.required_skills.set([skill_objs['Figma'], skill_objs['Design Systems'], skill_objs['Tailwind CSS']])

        # Project 2: OPEN project
        p2, _ = Project.objects.get_or_create(
            slug='django-real-time-telemetry-broker',
            defaults={
                'client': client_acme,
                'title': 'Django Production Telemetry & Log Audit Pipeline',
                'category': category_objs['Web Development'],
                'project_type': Project.TYPE_FIXED,
                'budget_min': Decimal('1800.00'),
                'budget_max': Decimal('3200.00'),
                'deadline': now + timedelta(days=14),
                'status': Project.STATUS_OPEN,
                'description': (
                    "Seeking a senior Python/Django engineer to implement an internal telemetry ingestion service.\n\n"
                    "Deliverables:\n"
                    "- Resilient SQLite / PostgreSQL batch logging endpoints.\n"
                    "- Server-side permission guards and API authentication.\n"
                    "- Django admin views with filtering and CSV report export.\n"
                    "- 90%+ automated test coverage with Django TestCase."
                )
            }
        )
        p2.required_skills.set([skill_objs['Python'], skill_objs['Django'], skill_objs['PostgreSQL']])

        # Project 3: IN PROGRESS project (Marcus hired by Acme)
        p3, _ = Project.objects.get_or_create(
            slug='dockerized-saas-deployment-harness',
            defaults={
                'client': client_acme,
                'title': 'Dockerized SaaS Production Deployment Harness on Render',
                'category': category_objs['DevOps & Cloud'],
                'project_type': Project.TYPE_FIXED,
                'budget_min': Decimal('2000.00'),
                'budget_max': Decimal('2800.00'),
                'deadline': now + timedelta(days=10),
                'status': Project.STATUS_IN_PROGRESS,
                'hired_freelancer': marcus,
                'agreed_budget': Decimal('2600.00'),
                'description': (
                    "Setup automated Docker container orchestration, Render deployment scripts, persistent volume mounting for SQLite, and WhiteNoise static asset optimization."
                )
            }
        )
        p3.required_skills.set([skill_objs['Docker'], skill_objs['AWS'], skill_objs['Python']])

        # Project 4: COMPLETED project (Kristina hired by Kristi Studio)
        p4, _ = Project.objects.get_or_create(
            slug='brand-identity-editorial-web-experience',
            defaults={
                'client': client_kristi,
                'title': 'Brand Identity & Editorial Web Experience for Kristi.digital',
                'category': category_objs['UI/UX Design'],
                'project_type': Project.TYPE_FIXED,
                'budget_min': Decimal('3500.00'),
                'budget_max': Decimal('5000.00'),
                'deadline': now - timedelta(days=5),
                'status': Project.STATUS_COMPLETED,
                'hired_freelancer': kristina,
                'agreed_budget': Decimal('4800.00'),
                'description': (
                    "Develop an editorial neo-brutalist landing page and design language featuring pastel accent palettes, thick black borders, and hard offset shadows."
                )
            }
        )
        p4.required_skills.set([skill_objs['Design Systems'], skill_objs['Tailwind CSS'], skill_objs['Figma']])

        # 7. Proposals
        # Proposal for p1
        Proposal.objects.get_or_create(
            project=p1,
            freelancer=kristina,
            defaults={
                'proposed_budget': Decimal('3800.00'),
                'estimated_days': 16,
                'portfolio_link': 'https://kristi.digital',
                'cover_letter': (
                    "Hello Sarah! I have spearheaded design systems for 4 major FinTech brands. My approach is rooted in mathematical typography, high contrast, and accessible WCAG AAA color standards.\n\n"
                    "I will deliver a clean Figma library alongside ready-to-use Tailwind tokens in under 16 business days."
                ),
                'status': Proposal.STATUS_PENDING,
            }
        )

        Proposal.objects.get_or_create(
            project=p1,
            freelancer=marcus,
            defaults={
                'proposed_budget': Decimal('3200.00'),
                'estimated_days': 14,
                'portfolio_link': 'https://marcusdev.io',
                'cover_letter': (
                    "I can build the complete HTML5 and Tailwind CSS component bundle with clean semantic markup and zero extraneous JavaScript dependencies."
                ),
                'status': Proposal.STATUS_PENDING,
            }
        )

        # Proposal for p3 (Accepted)
        Proposal.objects.get_or_create(
            project=p3,
            freelancer=marcus,
            defaults={
                'proposed_budget': Decimal('2600.00'),
                'estimated_days': 8,
                'portfolio_link': 'https://github.com/marcusthorne',
                'cover_letter': "I have deployed multiple production Django applications on Render using persistent SQLite disk mounts and WhiteNoise.",
                'status': Proposal.STATUS_ACCEPTED,
            }
        )

        # Proposal for p4 (Accepted & Completed)
        Proposal.objects.get_or_create(
            project=p4,
            freelancer=kristina,
            defaults={
                'proposed_budget': Decimal('4800.00'),
                'estimated_days': 12,
                'portfolio_link': 'https://kristi.digital',
                'cover_letter': "Editorial neo-brutalist web design is my primary design signature.",
                'status': Proposal.STATUS_ACCEPTED,
            }
        )

        # 8. Workspace Deliverables & Messages for p3
        ProjectDeliverable.objects.get_or_create(
            project=p3,
            title='Initial Dockerfile & Render Blueprint Configuration',
            defaults={
                'submitted_by': marcus,
                'notes': 'Prepared multi-stage Docker build, gunicorn configuration, and render.yaml blueprint with disk mount specification.',
                'demo_url': 'https://github.com/marcusthorne/render-django-template',
                'status': ProjectDeliverable.STATUS_APPROVED,
                'client_feedback': 'Looks solid! Tested the container locally and migrations execute properly.',
            }
        )

        ProjectMessage.objects.get_or_create(
            project=p3,
            sender=client_acme,
            message="Welcome aboard Marcus! Let's ensure the persistent disk directory permissions are configured properly for SQLite.",
            defaults={'is_read': True}
        )

        ProjectMessage.objects.get_or_create(
            project=p3,
            sender=marcus,
            message="Thanks David! I've set up the SQLITE_DIR environment variable logic so the app automatically routes db.sqlite3 to the mounted volume.",
            defaults={'is_read': True}
        )

        # 9. Deliverables & Reviews for p4 (Completed)
        ProjectDeliverable.objects.get_or_create(
            project=p4,
            title='Final Figma Tokens & Tailwind Production Bundle',
            defaults={
                'submitted_by': kristina,
                'notes': 'All components delivered including responsive navbar, neo cards, ticker ribbons, and custom badges.',
                'demo_url': 'https://kristi.digital',
                'status': ProjectDeliverable.STATUS_APPROVED,
                'client_feedback': 'Exceptional execution. The neo-brutalist aesthetic exceeded our expectations.',
            }
        )

        Review.objects.get_or_create(
            project=p4,
            reviewer=client_kristi,
            reviewee=kristina,
            defaults={
                'rating': 5,
                'feedback': 'Kristina delivered phenomenal design work. Uncompromising attention to typography, border weight, and color theory. Highly recommended!',
            }
        )

        Review.objects.get_or_create(
            project=p4,
            reviewer=kristina,
            reviewee=client_kristi,
            defaults={
                'rating': 5,
                'feedback': 'Wonderful client with clear technical vision, prompt feedback, and immediate sign-off. Would gladly collaborate again.',
            }
        )

        # 10. Saved Projects
        SavedProject.objects.get_or_create(user=marcus, project=p1)
        SavedProject.objects.get_or_create(user=kristina, project=p2)

        # 11. Notifications
        Notification.objects.get_or_create(
            recipient=client_fintech,
            title="New Proposal Received",
            message="Kristina Kowalska submitted a $3800 proposal for 'Neo-Brutalist FinTech Design System'.",
            url=f"/proposals/project/{p1.slug}/",
            category='proposal'
        )

        Notification.objects.get_or_create(
            recipient=marcus,
            title="Congratulations! You Have Been Hired",
            message=f"Acme Systems accepted your proposal for '{p3.title}'. Workspace is open.",
            url=f"/workspace/{p3.slug}/",
            category='hire'
        )

        self.stdout.write(self.style.SUCCESS("Prolance marketplace database successfully seeded with realistic sample data!"))

