# 🎯 Nexara Platform - Multi-Sector Compliance & Workflow Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0%2B-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Nexara** is an enterprise-grade, multi-tenant compliance and workflow automation platform designed for regulated sectors. It provides secure user authentication, multi-tenant isolation, dynamic workflow orchestration with LangGraph, Human-In-The-Loop (HITL) decision points, and sector-specific business logic.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Database Models](#database-models)
- [Workflow Engine](#workflow-engine)
- [Multi-Tenancy](#multi-tenancy)
- [Security](#security)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [Support](#support)

---

## Overview

Nexara Platform is built for organizations that need to:
- Manage complex compliance workflows across multiple sectors
- Execute deterministic business rules with AI-powered decision points
- Isolate data across multiple tenants securely
- Integrate human oversight into automated processes
- Scale business logic without code changes

The platform uses **LangGraph** for workflow orchestration, **Django** for the API layer, and **PostgreSQL** (via Supabase) for secure multi-tenant data storage.

### Current Focus
**Finance & Wealth Management** — Portfolio compliance workflows with policy evaluation, suitability checks, and human approval gates.

---

## Key Features

### 🔐 Security & Authentication
- ✅ **Secure Registration & Login** — Email-based registration with password hashing
- ✅ **Token-based Authentication** — Django REST Framework Token authentication
- ✅ **Protected Routes** — Role-based access control (RBAC)
- ✅ **Multi-Tenant Isolation** — Tenant-aware ORM queries, zero data leakage
- ✅ **CSRF Protection** — Django middleware protection on all forms
- ✅ **Responsive UI** — Mobile-friendly authentication pages with dark mode

### ⚙️ Workflow Orchestration
- ✅ **LangGraph-Powered Workflows** — State machines for complex business logic
- ✅ **Dynamic Node Registry** — Register custom nodes for any sector
- ✅ **HITL Integration** — Pause workflows for human decision points
- ✅ **Workflow Versioning** — Immutable templates with version control
- ✅ **Async Execution** — Celery task queue for long-running workflows

### 📊 Multi-Sector Support
- ✅ **Sector-Aware Logic** — Finance, IT, HR, Legal, Healthcare, and more
- ✅ **Finance Module** (Complete) — Portfolio compliance, policy evaluation, reporting
- ✅ **Extensible Architecture** — Add new sectors without modifying core

### 🏢 Multi-Tenancy
- ✅ **Complete Tenant Isolation** — Row-level security with automatic filtering
- ✅ **Tenant Membership** — RBAC with Admin, Reviewer, Analyst, Viewer roles
- ✅ **Per-Tenant Configurations** — Workflow and policy overrides

### 📱 Frontend
- ✅ **Registration Form** — Full Name, Email, Password validation
- ✅ **Login Form** — Email & password authentication
- ✅ **Protected Dashboard** — User info display and logout
- ✅ **Responsive Design** — Works on desktop, tablet, mobile
- ✅ **Real-time Validation** — Client-side form validation with error messages
- ✅ **Dark Mode Support** — Accessibility and eye-friendly interface

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/CSS/JS)                    │
│  - Registration/Login Forms                                      │
│  - Protected Dashboard                                           │
│  - Real-time Validation                                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    Django REST API Layer                         │
│  - Authentication (Register, Login, Logout, Me)                 │
│  - Tenant Management                                            │
│  - Workflow Execution                                           │
│  - Decision Submission (HITL)                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Nexara Core Services                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Workflow Engine (LangGraph)                                │ │
│  │ - Workflow Execution                                       │ │
│  │ - Node Registry                                            │ │
│  │ - Graph Building & Compilation                            │ │
│  │ - HITL Pause Points                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Multi-Tenancy & RBAC                                       │ │
│  │ - Tenant Isolation                                         │ │
│  │ - User Membership & Roles                                  │ │
│  │ - Permission Checks                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Business Domain Models (Finance)                           │ │
│  │ - Client Management                                        │ │
│  │ - Portfolio Management                                     │ │
│  │ - Instrument Registry                                      │ │
│  │ - Workflow Templates                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│              Data & Background Jobs                             │
│  - PostgreSQL (Supabase) - Persistent Data                     │
│  - SQLite (Dev) - Local Development                            │
│  - Redis - Cache & Message Broker                              │
│  - Celery - Async Task Queue                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Core language | 3.10+ |
| **Django** | Web framework | 6.0+ |
| **Django REST Framework** | API layer | 3.14+ |
| **LangGraph** | Workflow orchestration | Latest |
| **Celery** | Async task queue | 5.3+ |
| **PostgreSQL** | Production database | 13+ |
| **SQLite** | Development database | 3.9+ |
| **Redis** | Cache & message broker | 6.0+ |
| **Anthropic** | AI/LLM integration | Latest |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Markup |
| **CSS3** | Styling (Gradient, Animations, Dark Mode) |
| **Vanilla JavaScript** | Client-side logic (no framework) |
| **Responsive Design** | Mobile-first approach |

### DevOps & Infrastructure
| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerization (Redis, databases) |
| **Supabase** | PostgreSQL hosting + Auth (future) |
| **ASGI/Uvicorn** | Production server |

---

## Project Structure

```
Nexara/
├── 📄 manage.py                       # Django management script
├── 📄 db.sqlite3                      # SQLite database (dev only)
├── 📄 .env                            # Environment variables
├── 📄 .gitignore                      # Git ignore rules
│
├── 📁 nexara_platform/                # Main project configuration
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # URL routing
│   ├── wsgi.py                        # WSGI entry point
│   ├── asgi.py                        # ASGI entry point
│   └── celery.py                      # Celery configuration
│
├── 📁 core/                           # Core app (multi-tenancy, auth, RBAC)
│   ├── models.py                      # Tenant, User, Membership models
│   ├── views.py                       # Auth views (register, login, dashboard)
│   ├── serializers.py                 # DRF serializers
│   ├── urls.py                        # Core URL routes
│   ├── auth_decorators.py             # Auth protection decorators
│   ├── middleware.py                  # Tenant middleware
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App configuration
│   └── migrations/                    # Database migrations
│
├── 📁 engine/                         # Workflow engine app
│   ├── models.py                      # WorkflowTemplate, WorkflowRun, Agent
│   ├── views.py                       # Workflow APIs
│   ├── services.py                    # Workflow execution service
│   ├── graph.py                       # LangGraph builder
│   ├── tasks.py                       # Celery tasks
│   ├── urls.py                        # Engine URL routes
│   ├── nodes/                         # Node implementations
│   │   ├── base.py                    # BaseNode class
│   │   ├── common.py                  # Common nodes (evaluate, decision, gate)
│   │   └── finance.py                 # Finance-specific nodes
│   └── migrations/                    # Database migrations
│
├── 📁 domains/                        # Business domain models (Finance)
│   ├── models.py                      # Client, Portfolio, Instrument
│   ├── views.py                       # Domain APIs
│   ├── serializers.py                 # Domain serializers
│   ├── urls.py                        # Domain URL routes
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App configuration
│   └── migrations/                    # Database migrations
│
├── 📁 sectors/                        # Sector registry & config
│   ├── models.py                      # Sector configuration
│   ├── views.py                       # Sector APIs
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App configuration
│   └── migrations/                    # Database migrations
│
├── 📁 templates/                      # HTML templates
│   ├── base.html                      # Base template
│   └── core/
│       ├── register.html              # Registration form
│       ├── login.html                 # Login form
│       └── dashboard.html             # Protected dashboard
│
├── 📁 static/                         # Static files (CSS, JS, images)
│   ├── css/
│   │   └── auth.css                   # Authentication styling
│   └── js/
│       └── auth.js                    # Authentication logic
│
├── 📁 staticfiles/                    # Collected static files (production)
│
├── 📖 README.md                       # This file
├── 📖 AUTHENTICATION.md               # Auth system documentation
├── 📖 QUICK_START.md                  # Quick start guide
├── 📖 IMPLEMENTATION_SUMMARY.md       # Implementation details
├── 📖 AUTHENTICATION_SYSTEM.md        # Auth system notes
└── 📖 requirements.txt                # Python dependencies
```

---

## Installation

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Git**
- **PostgreSQL** (for production, optional for dev)
- **Redis** (for Celery tasks)
- **Docker** (optional, for containerized services)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/nexara.git
cd nexara
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy `.env.example` to `.env` (or create `.env` from the template):

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for dev, PostgreSQL for prod)
USE_SUPABASE=False
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_password
SUPABASE_DB_HOST=db.your-project.supabase.co
SUPABASE_DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Anthropic API (for AI features)
ANTHROPIC_API_KEY=your-api-key

# Nexara Settings
INTERNAL_API_SECRET=nexara-dev-secret
HITL_TIMEOUT_SECONDS=86400
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

---

## Configuration

### Database Setup

#### Development (SQLite)
No additional setup needed. SQLite is included with Django.

#### Production (PostgreSQL/Supabase)

1. Create a Supabase project: https://supabase.com
2. Get connection details from Supabase dashboard
3. Update `.env`:
   ```env
   USE_SUPABASE=True
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=postgres
   SUPABASE_DB_PASSWORD=your_password
   SUPABASE_DB_HOST=db.your-project.supabase.co
   ```
4. Run migrations: `python manage.py migrate`

### Redis Setup

#### Docker (Recommended)
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Local Installation
```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Django Settings

Key settings in `nexara_platform/settings.py`:

- **INSTALLED_APPS** — Core, Engine, Domains, Sectors apps
- **MIDDLEWARE** — CORS, Security, Auth, Tenant middleware
- **REST_FRAMEWORK** — Token authentication, pagination
- **DATABASES** — SQLite or PostgreSQL
- **TEMPLATES** — Template directory configuration
- **STATIC_FILES** — Static files configuration

---

## Running the Application

### Development Server

```bash
# Navigate to project directory
cd /path/to/nexara

# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Run development server
python manage.py runserver

# Server will be available at http://localhost:8000
```

### Background Tasks (Celery)

In a separate terminal:

```bash
# Install Celery (if not already installed)
pip install celery

# Start Celery worker
celery -A nexara_platform worker -l info
```

### Admin Dashboard

- Open: http://localhost:8000/admin/
- Login with superuser credentials created earlier
- Manage users, tenants, workflows, etc.

### Test Application

1. **Registration:**
   - Open: http://localhost:8000/register/
   - Fill in form and create account
   - Success message appears

2. **Login:**
   - Open: http://localhost:8000/login/
   - Enter registered email and password
   - Redirected to dashboard

3. **Dashboard:**
   - Open: http://localhost:8000/dashboard/
   - View user information
   - Test protected API endpoints

---

## API Endpoints

### Authentication

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---|
| POST | `/api/auth/register/` | Create new account | ❌ |
| POST | `/api/auth/login/` | Authenticate user | ❌ |
| POST | `/api/auth/logout/` | Logout user | ✅ |
| GET | `/api/auth/me/` | Get current user | ✅ |

### Tenants

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---|
| GET/POST | `/api/tenants/` | List/create tenants | ✅ |
| GET/PATCH | `/api/tenants/<slug>/` | Get/update tenant | ✅ |
| GET | `/api/tenants/<slug>/members/` | List tenant members | ✅ |

### Workflows

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---|
| POST | `/api/engine/workflows/execute/` | Execute workflow | ✅ |
| GET | `/api/engine/workflows/<run_id>/` | Get workflow status | ✅ |
| POST | `/api/engine/workflows/<run_id>/hitl/` | Submit HITL decision | ✅ |

### Finance (Domains)

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---|
| GET/POST | `/api/domains/clients/` | List/create clients | ✅ |
| GET/POST | `/api/domains/portfolios/` | List/create portfolios | ✅ |
| GET/POST | `/api/domains/instruments/` | List/create instruments | ✅ |

---

## Authentication

The platform uses **Django REST Framework Token Authentication**:

### Registration Flow

1. User visits `/register/`
2. Fills in Full Name, Email, Password
3. Submits form → `POST /api/auth/register/`
4. Server validates, hashes password, creates user
5. Success message → Redirects to login

### Login Flow

1. User visits `/login/`
2. Enters Email and Password
3. Submits form → `POST /api/auth/login/`
4. Server authenticates user
5. Creates/retrieves auth token
6. Token stored in localStorage
7. Redirects to dashboard

### Making Authenticated Requests

**From JavaScript:**
```javascript
const token = localStorage.getItem('authToken');
fetch('/api/protected/', {
    headers: {
        'Authorization': `Token ${token}`,
        'X-CSRFToken': getCookie('csrftoken'),
    }
});
```

**From Python:**
```python
import requests
headers = {'Authorization': f'Token {token}'}
response = requests.get('/api/protected/', headers=headers)
```

### Protecting Routes

**HTML Views:**
```python
from core.auth_decorators import login_required_view

@login_required_view
def my_page(request):
    return render(request, 'my_page.html')
```

**API Views:**
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_api(request):
    return Response({'data': 'protected'})
```

---

## Database Models

### Core Models

#### Tenant
```python
- id (UUID)
- name (CharField)
- sector (Choices: finance, it, hr, legal, healthcare, etc.)
- slug (SlugField - unique)
- is_active (BooleanField)
- created_at / updated_at (DateTimeField)
```

#### User (Django built-in)
```python
- id (Integer)
- username (CharField)
- email (EmailField)
- password (Hashed)
- first_name / last_name (CharField)
```

#### TenantMembership
```python
- id (Integer)
- user (OneToOneField → User)
- tenant (ForeignKey → Tenant)
- role (Choices: admin, reviewer, analyst, viewer)
- created_at (DateTimeField)
```

### Engine Models

#### WorkflowTemplate
```python
- code (CharField)
- version (IntegerField)
- name (CharField)
- description (TextField)
- sector (CharField)
- graph_json (JSONField)
- is_active (BooleanField)
- created_at (DateTimeField)
```

#### WorkflowRun
```python
- id (UUID)
- agent (ForeignKey → Agent)
- template (ForeignKey → WorkflowTemplate)
- template_version (IntegerField)
- status (Choices: pending, running, waiting, completed, failed)
- input_data (JSONField)
- output_data (JSONField)
- current_node (CharField)
- created_at / updated_at (DateTimeField)
- tenant (ForeignKey → Tenant)
```

### Finance Models (Domains)

#### Client
```python
- id (UUID)
- full_name (CharField)
- email (EmailField)
- risk_profile (Choices: conservative, moderate, aggressive)
- risk_tolerance (IntegerField 0-100)
- is_active (BooleanField)
- tenant (ForeignKey → Tenant)
```

#### Portfolio
```python
- id (UUID)
- client (ForeignKey → Client)
- name (CharField)
- description (TextField)
- is_active (BooleanField)
- tenant (ForeignKey → Tenant)
```

#### Instrument
```python
- instrument_uid (CharField - unique)
- name (CharField)
- ticker (CharField)
- asset_class (Choices: equity, fixed_income, etf, cash, alternative)
- risk_score (IntegerField 0-100)
- currency (CharField)
- is_active (BooleanField)
- tenant (ForeignKey → Tenant)
```

---

## Workflow Engine

### How It Works

1. **Trigger:** User calls `/api/engine/workflows/execute/` with agent code
2. **Template:** Engine retrieves workflow template for that agent
3. **Graph:** LangGraph compiles the workflow as a state machine
4. **Execution:** Nodes execute sequentially, passing data through state
5. **HITL:** Workflow pauses at `human_decision` node
6. **Decision:** User submits decision via `/api/engine/workflows/<run_id>/hitl/`
7. **Resume:** Workflow continues to completion
8. **Output:** Results stored in WorkflowRun.output_data

### Finance Workflow Example

```
portfolio_import
    ↓
compute_metrics
    ↓
concentration_check (detects over-concentration)
    ↓
suitability_check (matches client risk profile)
    ↓
evaluate_policies (applies compliance rules)
    ↓
human_decision ← HITL PAUSE POINT
    ↓
approval_gate (checks decision)
    ↓
generate_report
    ↓
END
```

### Adding a Custom Node

```python
from engine.nodes import register_node, BaseNode

@register_node(
    code='my_custom_node',
    sectors=['finance'],
    retry_policy='bounded'
)
class MyCustomNode(BaseNode):
    def execute(self, input_data: dict, context: dict) -> dict:
        # Your logic here
        return {'result': 'success'}
```

---

## Multi-Tenancy

### Tenant Isolation

Every database query automatically filters by current tenant:

```python
# Automatic tenant filtering (no manual WHERE needed)
from domains.models import Client

# Only gets clients in current tenant
clients = Client.objects.all()  # Query is auto-filtered!
```

### How It Works

1. `TenantMiddleware` extracts tenant from user's membership
2. Stores tenant in context variable
3. `TenantAwareManager` filters every query by tenant
4. Zero chance of data leakage between tenants

### Tenant Membership Roles

| Role | Permissions |
|------|------------|
| **Admin** | Full access, manage users |
| **Reviewer** | HITL decision authority |
| **Analyst** | Trigger workflows, read data |
| **Viewer** | Read-only access |

---

## Security

### Implementation Details

✅ **Password Hashing**
- Uses PBKDF2 algorithm (Django built-in)
- Never stores plain-text passwords
- Validated against Django's password validators

✅ **CSRF Protection**
- Django middleware prevents cross-site requests
- Forms include CSRF token
- API calls require CSRF header

✅ **Token Authentication**
- Tokens created on successful login
- Stored securely, never exposed in plain text
- Unique per user, revocable

✅ **Multi-Tenant Isolation**
- Automatic row-level filtering
- Users can only see their tenant's data
- No cross-tenant data access possible

✅ **Input Validation**
- Django ORM prevents SQL injection
- Serializers validate all inputs
- Client-side validation for UX

✅ **Rate Limiting**
- Can be added via django-ratelimit
- Prevents brute force attacks
- Configurable per endpoint

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Change `DJANGO_SECRET_KEY` to strong random string
- [ ] Use `HTTPS` only (SSL certificates)
- [ ] Store secrets in environment variables
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable CORS only for known domains
- [ ] Set up logging and monitoring
- [ ] Implement rate limiting
- [ ] Enable email verification
- [ ] Set up automated backups
- [ ] Use strong database passwords
- [ ] Configure firewall rules

---

## Contributing

We welcome contributions! Here's how to get started:

### 1. Fork & Clone

```bash
git clone https://github.com/yourusername/nexara.git
cd nexara
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write clean, documented code
- Follow PEP 8 style guide
- Add tests for new features

### 4. Test Locally

```bash
# Run tests
python manage.py test

# Check code style
flake8 .
black --check .
```

### 5. Commit & Push

```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Open PR on GitHub
- Describe changes and rationale
- Link related issues

---

## Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Multi-tenant architecture
- [x] User authentication (register/login)
- [x] Workflow engine with LangGraph
- [x] HITL decision points
- [x] Finance domain models
- [x] Dashboard & UI

### Phase 2: Enhancements 🚀 (Next)
- [ ] Email verification on registration
- [ ] Password reset / forgot password
- [ ] Rate limiting (brute force protection)
- [ ] Audit logging (who did what, when)
- [ ] Advanced reporting & analytics
- [ ] Webhook support for external systems

### Phase 3: Scaling 📈 (Future)
- [ ] Additional sectors (IT, HR, Legal)
- [ ] Advanced RBAC (granular permissions)
- [ ] OAuth2 / SAML integration
- [ ] Two-factor authentication (2FA)
- [ ] API key management
- [ ] Custom workflow builder UI
- [ ] Real-time notifications (WebSocket)
- [ ] Mobile app (iOS/Android)

### Phase 4: Enterprise 🏢 (Long-term)
- [ ] Multi-region deployment
- [ ] Advanced security (encryption, key management)
- [ ] Compliance certifications (SOC2, ISO27001)
- [ ] Premium support
- [ ] SLA guarantees
- [ ] Custom integration services

---

## Support

### Documentation

- **[AUTHENTICATION.md](AUTHENTICATION.md)** — Complete auth system documentation
- **[QUICK_START.md](QUICK_START.md)** — Quick setup and testing guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** — Implementation details

### Getting Help

1. **Check Documentation** — Most answers are in README or dedicated docs
2. **Search Issues** — Your question might be answered in GitHub Issues
3. **Create Issue** — Describe problem, include error logs, reproduction steps
4. **Contact Support** — Email or Discord (links in repo)

### Reporting Bugs

Please include:
- Python & Django versions
- Database (SQLite or PostgreSQL)
- Error message & traceback
- Steps to reproduce
- Expected vs actual behavior

### Feature Requests

Please include:
- Clear description of feature
- Use case / why it's needed
- Proposed implementation (optional)
- Related issues or PRs

---

## File Descriptions

### Core Files

| File | Purpose |
|------|---------|
| `manage.py` | Django management script (migrations, server, shell) |
| `requirements.txt` | Python dependencies |
| `.env` | Environment variables (secrets, API keys) |
| `.gitignore` | Git ignore patterns |

### Configuration

| File | Purpose |
|------|---------|
| `nexara_platform/settings.py` | Django settings (DB, apps, middleware) |
| `nexara_platform/urls.py` | URL routing configuration |
| `nexara_platform/wsgi.py` | WSGI entry point (production) |
| `nexara_platform/asgi.py` | ASGI entry point (async) |
| `nexara_platform/celery.py` | Celery task queue config |

### Apps

| App | Purpose |
|-----|---------|
| `core/` | Multi-tenancy, authentication, RBAC |
| `engine/` | Workflow orchestration engine |
| `domains/` | Business domain models (Finance) |
| `sectors/` | Sector registry & configuration |

### Frontend

| File | Purpose |
|------|---------|
| `templates/core/register.html` | User registration form |
| `templates/core/login.html` | User login form |
| `templates/core/dashboard.html` | User dashboard |
| `static/css/auth.css` | Authentication styling |
| `static/js/auth.js` | Authentication logic |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | This file (project overview) |
| `AUTHENTICATION.md` | Auth system documentation |
| `QUICK_START.md` | Quick start guide |
| `IMPLEMENTATION_SUMMARY.md` | Implementation details |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Changelog

### v1.0.0 (2026-05-29)
- ✨ Initial release
- ✨ Multi-tenant architecture
- ✨ User authentication (register/login/logout)
- ✨ Workflow engine with LangGraph
- ✨ HITL decision points
- ✨ Finance domain models
- ✨ Protected dashboard
- ✨ Comprehensive documentation

---

## Quick Links

- 🌐 **Website:** https://nexara.io
- 📖 **Documentation:** [AUTHENTICATION.md](AUTHENTICATION.md), [QUICK_START.md](QUICK_START.md)
- 🐛 **Issue Tracker:** https://github.com/yourusername/nexara/issues
- 💬 **Discussions:** https://github.com/yourusername/nexara/discussions
- 📧 **Email:** support@nexara.io
- 💼 **LinkedIn:** [Nexara Company](https://linkedin.com/company/nexara)

---

**Made with ❤️ by the Nexara Team**

© 2024 Nexara Platform. All rights reserved.
