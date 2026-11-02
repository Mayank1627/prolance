# Prolance — Freelancer Project Marketplace

> **"Where Direct Talent Meets Serious Projects."**  
> An authentic, monolithic full-stack marketplace built with Django 5, SQLite, and an editorial Neo-Brutalist design language.

---

## 1. Project Overview

**Prolance** is an academic software engineering project delivering a functional, production-ready freelance project marketplace. It establishes direct connections between clients and specialized talent (software engineers, UI/UX architects, cloud specialists).

### Core Capabilities
- **Role-Aware Authentication**: Built-in Django session authentication with strict server-side permission barriers distinguishing **Clients**, **Freelancers**, and **Platform Administrators**.
- **Project Discovery & Scoping**: Search by keyword, filter by categories, skills, and budget ranges, with server-side validation rejecting stale or conflicting deadlines.
- **Atomic Hiring Pipeline**: Database transactions (`select_for_update`) ensure that accepting a proposal locks the project to the chosen freelancer, auto-rejects competing bids, and prevents race conditions.
- **Dedicated Workspaces**: Private channels between the client and hired freelancer featuring milestone deliverable review workflows and project-scoped messaging.
- **Verified Peer Reviews**: Review and 1–5 star rating submission unlocked strictly upon project completion, calculating genuine profile reputation scores.
- **Trust & Safety Reporting**: Community moderation reporting pipeline for inappropriate listings and contract disputes.

---

## 2. Neo-Brutalist UI Design System

Derived directly from the reference visual specifications (`kristi.digital`, `Dodonut`, and `NEOX Studio`):

| Design Token | Specification | Implementation |
| :--- | :--- | :--- |
| **Canvas Background** | `#F7F4EB` | Warm off-white / editorial paper base |
| **Surface Cards** | `#FFFFFF` | Crisp white cards with 2.5px solid borders |
| **Stroke Borders** | `#121212` | Deep charcoal/black deliberate framing |
| **Hard Offset Shadows**| `box-shadow: 4px 4px 0px #121212` | Tactical mechanical depth with zero blur |
| **Primary Accent** | `#FFE600` (Canary Yellow) | High-contrast action triggers and key callouts |
| **Secondary Accent** | `#2DD4BF` (Mint Teal) | Active state indicators, badges, and approvals |
| **Supporting Accents**| `#6366F1` (Indigo), `#FF6B4A` (Coral)| Category distinction and alert notifications |
| **Typography** | `Space Grotesk` & `Plus Jakarta Sans` | High-legibility editorial sans-serif hierarchy |
| **Interactive Polish** | `-translate-x-0.5 -translate-y-0.5` | Tactile press-down effect on clicks |

---

## 3. Technology Stack

- **Backend**: Python 3.13, Django 5.x, Django ORM, ModelForms, Session-based Authentication (No JWT, no microservices, no separate SPA).
- **Frontend**: Django Templates, Tailwind CSS (standalone CLI / Node-based compiler + production bundle), Vanilla JavaScript, Lucide icons.
- **Database**: SQLite 3 with persistent disk support for Render, plus documented PostgreSQL transition path.
- **Static Asset Delivery**: WhiteNoise with gzip and caching headers.

---

## 4. Project Directory Structure

```text
ProLance/
├── accounts/               # Custom User model, Freelancer & Client profiles, talent directory
│   ├── forms.py            # UserRegistrationForm, UserLoginForm, ProfileForms
│   ├── models.py           # User(AbstractUser), FreelancerProfile, ClientProfile
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── projects/               # Project catalog, categories, skills, bookmarks
│   ├── forms.py            # ProjectForm with budget & deadline validation
│   ├── models.py           # Category, Skill, Project, SavedProject
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── proposals/              # Freelancer proposals & atomic client hiring transaction
│   ├── forms.py            # ProposalSubmissionForm
│   ├── models.py           # Proposal model
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── workspace/              # Project workspace rooms, deliverables, direct messaging
│   ├── forms.py            # DeliverableSubmissionForm, ProjectMessageForm
│   ├── models.py           # ProjectDeliverable, ProjectMessage
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── reviews/                # Verified peer ratings, reviews, and moderation reports
│   ├── forms.py            # ReviewForm, ReportForm
│   ├── models.py           # Review, Report
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── notifications/          # In-app notification center & global navbar badges
│   ├── context_processors.py
│   ├── models.py           # Notification
│   ├── urls.py
│   └── views.py
├── core/                   # Landing page, dashboards, and shared context
│   ├── context_processors.py
│   ├── management/commands/seed_marketplace.py  # Realistic database seed command
│   ├── urls.py
│   └── views.py
├── prolance_config/        # Project settings, WSGI, root URL routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/              # Reusable Django templates & UI components
│   ├── base.html
│   ├── components/         # Navbar, footer, project_card, pagination, messages
│   ├── accounts/           # Register, login, edit_profile, freelancer_detail
│   ├── projects/           # Browse, detail, form, saved_list
│   ├── proposals/          # Submit, client_proposals_list, confirm_hire
│   ├── workspace/          # Room, chat, deliverables
│   └── core/               # Landing, freelancer_dashboard, client_dashboard
├── static/                 # Static CSS, compiled output, Lucide JS
│   ├── css/input.css
│   ├── css/output.css
│   └── js/lucide.min.js
├── manage.py
├── package.json
├── tailwind.config.js
├── render.yaml             # Render deployment blueprint with disk mounting
├── requirements.txt
├── .env.example
├── DEPLOYMENT_GUIDE.md     # Production deployment instructions (Render & Vercel)
├── FEATURE_CHECKLIST.md    # Mapping of all features to implementation status
└── TEST_REPORT.md          # Automated test execution report (32 tests passing)
```

---

## 5. Local Setup & Quickstart

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Node.js 18+ (for Tailwind CSS asset compilation)

### Step 1: Clone & Create Virtual Environment
```bash
git clone <repository-url>
cd ProLance

python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS / Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
npm install
```

### Step 3: Configure Environment Variables
```bash
copy .env.example .env   # Windows
# or cp .env.example .env (Linux/macOS)
```

### Step 4: Run Migrations & Seed Database
```bash
python manage.py migrate
python manage.py seed_marketplace
```

### Step 5: Build Tailwind CSS
```bash
npm run build:css
```

### Step 6: Start Development Server
```bash
python manage.py runserver
```
Visit **`http://127.0.0.1:8000/`** in your browser.

---

## 6. Pre-Seeded Demonstration Accounts

The `seed_marketplace` command pre-populates realistic accounts:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `adminpass123` | Django Admin access at `/admin/` |
| **Client** | `acme_labs` | `clientpass123` | B2B SaaS client with active and open projects |
| **Client** | `fintech_corp` | `clientpass123` | Has open project receiving proposals |
| **Freelancer** | `marcus_dev` | `freepass123` | Full-stack Django architect, active workspace |
| **Freelancer** | `kristina_design` | `freepass123` | Growth UI/UX designer, 5.0 star rating, delivered contracts |

---

## 7. Running Automated Tests

Run the complete 32-test suite with:
```bash
python manage.py test
```
All tests run against a temporary in-memory database and verify authentication, project lifecycle, atomic hiring, workspace access control, and review validation.
