# Prolance — Production Deployment & Operations Guide

> **Mandatory Deployment Handoff Specification for Prolance Freelancer Marketplace**

---

## A. Technology & Architecture Overview

Prolance operates as an integrated, monolithic Django 5.x web application:
- **Serving Architecture**: HTTP requests are processed through a WSGI application server (Gunicorn in production) managed by Django's request-response lifecycle.
- **HTML & Interactivity**: Server-rendered HTML utilizing Django Templates, styled with a pre-compiled Tailwind CSS bundle (`static/css/output.css`) and augmented with vanilla JavaScript and Lucide icons.
- **Static Asset Delivery**: Handled in-process using **WhiteNoise** (`whitenoise.middleware.WhiteNoiseMiddleware` with `CompressedManifestStaticFilesStorage`). Assets are collected at build time into `STATIC_ROOT = BASE_DIR / 'staticfiles'` and served with optimal cache-control headers directly through WSGI without requiring a separate Nginx container.
- **Database Engine**: **SQLite 3**, configured to point dynamically to a persistent storage directory via the `SQLITE_DIR` environment variable, ensuring zero data loss across deployments when hosted on persistent-disk cloud platforms.

---

## B. Exact Project Directory Structure

```text
ProLance/
├── accounts/                  # Auth, roles, FreelancerProfile, ClientProfile
├── core/                      # Landing page, role dashboards, seed command
├── notifications/             # Notification center & global context processors
├── projects/                  # Catalog, categories, skills, saved projects
├── proposals/                 # Proposals, atomic hiring transactions
├── reviews/                   # Peer reviews, ratings, trust & safety reports
├── workspace/                 # Deliverables, milestones, direct chat messages
├── prolance_config/           # Settings, WSGI, main URL router
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/                 # Reusable template components and views
├── static/                    # CSS input/output, local Lucide JS
├── render.yaml                # Render Infrastructure as Code Blueprint
├── requirements.txt           # Production Python dependencies
├── package.json               # Tailwind CLI build scripts
├── tailwind.config.js         # Neo-brutalist theme configuration
├── manage.py
├── .env.example               # Safe environment template
├── .gitignore                 # Exclusion rules for secrets & build output
├── README.md
├── DEPLOYMENT_GUIDE.md
├── FEATURE_CHECKLIST.md
└── TEST_REPORT.md
```

---

## C. Environment Variables Specification

Configure these environment variables in your deployment dashboard (e.g. Render Web Service Environment settings):

| Variable Name | Required? | Default Value | Description & Production Guidance |
| :--- | :---: | :--- | :--- |
| `SECRET_KEY` | **Yes** | None (Random) | Cryptographic signing key. Generate a 50+ character string. Never commit this to Git. |
| `DEBUG` | **Yes** | `False` | Set strictly to `False` in production to prevent stack trace leaks and enforce security headers. |
| `ALLOWED_HOSTS` | **Yes** | `.onrender.com` | Comma-separated domains allowed to serve requests (e.g. `prolance.onrender.com,yourdomain.com`). |
| `CSRF_TRUSTED_ORIGINS`| **Yes** | `https://*.onrender.com` | Full URLs including scheme (`https://prolance.onrender.com`) required by Django 4+ CSRF protection. |
| `SQLITE_DIR` | **Yes** (on Render) | `/var/data` | Path to persistent disk mount point where `db.sqlite3` is permanently stored. |
| `SECURE_SSL_REDIRECT` | Optional | `True` | Enforces HTTPS redirection for all incoming web requests. |
| `EMAIL_BACKEND` | Optional | `console.EmailBackend` | Email delivery backend. For production emails, configure SMTP (`django.core.mail.backends.smtp.EmailBackend`). |

---

## D. Local Setup Instructions

```bash
# 1. Create and activate a clean Python virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 2. Install Python and frontend dependencies
pip install -r requirements.txt
npm install

# 3. Create .env file
cp .env.example .env

# 4. Run migrations
python manage.py migrate

# 5. Populate initial database with seed data (Admin + Demo Accounts + Projects)
python manage.py seed_marketplace

# 6. Compile Tailwind CSS
npm run build:css

# 7. Run automated tests to verify stability
python manage.py test

# 8. Start local server
python manage.py runserver
```

---

## E. GitHub Preparation & Safe Version Control

Ensure you never commit local databases, secret keys, or virtual environments to Git:

```bash
# Initialize git if not already initialized
git init

# Verify .gitignore covers db.sqlite3, media/, staticfiles/, and .env
git status

# Stage project files
git add .

# Initial commit
git commit -m "feat: complete Prolance marketplace with neo-brutalist UI and tests"

# Add your GitHub remote and push
git remote add origin https://github.com/<your-username>/prolance.git
git branch -M main
git push -u origin main
```

---

## F. Primary Production Target: Render Deployment

Render is the designated host for Prolance because it natively supports persistent disks attached to Python web services running SQLite.

### Recommended Render Configuration
1. **Service Type**: **Web Service**
2. **Environment**: **Python**
3. **Region**: Oregon or Frankfurt
4. **Plan**: **Starter** ($7/mo) — *A paid plan is required by Render to attach a Persistent Disk.*
5. **Build Command**:
   ```bash
   pip install -r requirements.txt && npm install && npm run build:css && python manage.py collectstatic --noinput && python manage.py migrate
   ```
6. **Start Command**:
   ```bash
   gunicorn prolance_config.wsgi:application
   ```

### Persistent Disk Configuration (CRITICAL for SQLite)
1. In the Render Dashboard under **Disks**, click **Add Disk**.
2. **Name**: `prolance-data`
3. **Mount Path**: `/var/data`
4. **Size**: `1 GB` (sufficient for millions of SQLite records)
5. Add the Environment Variable in your Web Service:
   - **Key**: `SQLITE_DIR`
   - **Value**: `/var/data`

> **Why this is required**: Default web containers on cloud platforms have an ephemeral filesystem. Every time you redeploy or restart, ephemeral containers are destroyed and recreated. Mounting a persistent disk at `/var/data` ensures `db.sqlite3` survives reboots, redeployments, and scaling.

### One-Click Blueprint Option
Prolance includes a validated `render.yaml` blueprint in the repository root. When creating a project in Render, select **New -> Blueprint** and point to your GitHub repository; Render will automatically provision the web service, environment variables, and persistent disk.

---

## G. Vercel Compatibility Analysis

### Can Prolance be deployed directly to Vercel?
**No, not recommended with persistent SQLite.**

### Detailed Architectural Reason:
1. **Serverless Ephemeral Filesystem**: Vercel executes applications using AWS Lambda serverless functions. Each function has an ephemeral `/tmp` directory that is destroyed within minutes when the function goes idle.
2. **No Persistent Disk Support**: Vercel does not support attaching persistent block storage volumes. Any SQLite file written on Vercel is erased on the next cold start or concurrent request, causing total loss of users, projects, and proposals.
3. **Read-Only Code Bundle**: The application directory deployed on Vercel is strictly read-only.
4. **Unnecessary Splitting**: Forcing Prolance onto Vercel would necessitate splitting the monolithic Django templates into a separate client-side SPA and provisioning an external managed database (e.g. Supabase or Neon), which violates the project's strict architecture requirements.

### Recommendation:
Deploy the complete Django monolithic application on **Render** (as configured).

---

## H. Database Persistence, Backups & PostgreSQL Migration Pathway

### How to Back Up the Production SQLite Database on Render
1. **Render Shell Access**:
   Open the **Shell** tab in your Render dashboard:
   ```bash
   # Create a timestamped copy inside the persistent volume
   cp /var/data/db.sqlite3 /var/data/db_backup_$(date +%Y%m%d).sqlite3
   ```
2. **Download Local Backup**:
   Use Render's SSH access or an S3 sync cron script to archive `db.sqlite3`.

### Alternative PostgreSQL Migration Pathway
If your team transitions to a managed database in the future:
1. Install `psycopg2-binary`:
   ```bash
   pip install psycopg2-binary
   ```
2. Set `DATABASE_URL` in environment variables:
   `DATABASE_URL=postgres://user:password@host:port/dbname`
3. In `prolance_config/settings.py`, replace `DATABASES` with `dj-database-url`:
   ```python
   import dj_database_url
   DATABASES = {
       'default': dj_database_url.config(
           default=f'sqlite:///{sqlite_path}',
           conn_max_age=600
       )
   }
   ```
4. Run `python manage.py migrate` against the PostgreSQL database.

---

## I. Final Deployment Verification Checklist

Verify each of the following flows immediately after deployment:

- [ ] **Landing Page**: Renders cleanly with neo-brutalist styling, ticker ribbon, and live database counts.
- [ ] **Registration & Login**: Create a new test user; verify session cookies are set and HTTPS redirection works.
- [ ] **Client Project Creation**: Log in as a client and publish a project with budget and deadline validation.
- [ ] **Freelancer Bidding**: Log in as a freelancer, find the project, and submit a proposal.
- [ ] **Proposal Acceptance**: As the client, review proposals and accept the bid; verify atomic transition to *In Progress*.
- [ ] **Workspace & Chat**: Open the workspace room, send a message, and submit a mock deliverable.
- [ ] **Review Submission**: Mark the project completed and submit a 5-star peer review; verify rating updates on public profile.
- [ ] **Admin Moderation**: Access `/admin/` and verify content inspection.
- [ ] **Persistence Verification**: Trigger a manual redeploy in Render; verify all created users, projects, and messages remain intact.

---

## J. Troubleshooting Common Deployment Issues

### 1. `DisallowedHost at /`
- **Cause**: The incoming domain name is missing from `ALLOWED_HOSTS`.
- **Fix**: Update the `ALLOWED_HOSTS` environment variable to include your domain (e.g. `ALLOWED_HOSTS=prolance.onrender.com,.onrender.com`).

### 2. `Forbidden (403) CSRF verification failed`
- **Cause**: Origin not trusted by Django's CSRF protection.
- **Fix**: Add your exact HTTPS URL to `CSRF_TRUSTED_ORIGINS`:
  `CSRF_TRUSTED_ORIGINS=https://prolance.onrender.com`

### 3. Missing CSS / Broken Styling
- **Cause**: Tailwind was not compiled before `collectstatic`, or WhiteNoise storage is missing.
- **Fix**: Ensure your build command executes `npm run build:css && python manage.py collectstatic --noinput`.

### 4. Database Disappears After Redeployment
- **Cause**: SQLite database is being stored on the ephemeral container instead of the mounted persistent disk.
- **Fix**: Confirm that Render has an active Disk mounted at `/var/data` and that `SQLITE_DIR=/var/data` is set in Environment Variables.

### 5. `sqlite3.OperationalError: database is locked`
- **Cause**: Long-running background transactions with SQLite.
- **Fix**: The default SQLite timeout has been tuned to 20 seconds in `settings.py` (`'timeout': 20`).

