"""
Django settings for nexara_platform project.
Nexara Platform — Multi-Sector Compliance Engine
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-)t03p-hamockeaop_75f4_(nx%rft%xk29bd7gpea!b)ppc6l=')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ─── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # Nexara apps
    'core',       # multi-tenancy, auth, RBAC, Redis pub/sub
    'engine',     # workflow engine, node registry, HITL, SSE, decisions
    'domains',
    'domains.it',
    'domains.hr',
    'domains.legal',
    'domains.healthcare',
    'domains.insurance',
    'domains.education',
    'domains.government',
    'domains.energy',
    'domains.telecom',
    'domains.manufacturing',
    'domains.logistics',
    'domains.retail',
    'domains.cybersecurity',
    'sectors',    # sector registry & config
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',          # must be first
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TenantMiddleware',               # tenant isolation — after auth
]

ROOT_URLCONF = 'nexara_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nexara_platform.wsgi.application'

# ─── Database — Supabase (PostgreSQL) ─────────────────────────────────────────
# For local dev without Supabase yet, falls back to SQLite.
# Set USE_SUPABASE=True in .env when your Supabase project is ready.
USE_SUPABASE = os.getenv('USE_SUPABASE', 'False') == 'True'

if USE_SUPABASE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME':     os.getenv('SUPABASE_DB_NAME'),
            'USER':     os.getenv('SUPABASE_DB_USER'),
            'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD'),
            'HOST':     os.getenv('SUPABASE_DB_HOST'),
            'PORT':     os.getenv('SUPABASE_DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',           # Supabase requires SSL
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─── Django REST Framework ────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# ─── CORS ─────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'   # Next.js dev server
).split(',')
CORS_ALLOW_CREDENTIALS = True

# ─── Redis ────────────────────────────────────────────────────────────────────
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# ─── Celery ───────────────────────────────────────────────────────────────────
CELERY_BROKER_URL          = f'{REDIS_URL}/0'       # DB 0: task queue
CELERY_RESULT_BACKEND      = f'{REDIS_URL}/0'
CELERY_TASK_SERIALIZER     = 'json'
CELERY_RESULT_SERIALIZER   = 'json'
CELERY_ACCEPT_CONTENT      = ['json']
CELERY_TIMEZONE            = 'UTC'
CELERY_TASK_TRACK_STARTED  = True
CELERY_TASK_TIME_LIMIT     = 30 * 60               # 30 min hard limit per task

# Redis DB 1 is reserved for LangGraph runtime state (graph thread state)
LANGGRAPH_REDIS_URL = f'{REDIS_URL}/1'

# ─── Supabase client (used alongside Django ORM for Realtime/Auth/Storage) ───
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')       # anon/service key

# ─── Anthropic / LangGraph ────────────────────────────────────────────────────
ANTHROPIC_API_KEY  = os.getenv('ANTHROPIC_API_KEY', '')
LANGSMITH_API_KEY  = os.getenv('LANGSMITH_API_KEY', '')   # optional, for tracing

# ─── Nexara platform config ───────────────────────────────────────────────────
NEXARA = {
    # Internal API used by LangGraph to call back into Django
    'INTERNAL_API_BASE': os.getenv('INTERNAL_API_BASE', 'http://localhost:8000'),
    'INTERNAL_API_SECRET': os.getenv('INTERNAL_API_SECRET', 'change-me-in-production'),

    # LangGraph: runs in-process via SDK (no Docker image needed)
    'LANGGRAPH_MODE': 'inprocess',   # options: 'inprocess' | 'remote'
    'LANGGRAPH_REMOTE_URL': os.getenv('LANGGRAPH_REMOTE_URL', ''),

    # HITL timeout before auto-escalation (seconds)
    'HITL_TIMEOUT_SECONDS': int(os.getenv('HITL_TIMEOUT_SECONDS', 86400)),  # 24h default

    # Audit: content-addressed blob store backend
    'MEMORY_BACKEND': 'db',          # 'db' for now; 'supabase_storage' later
}

# ─── Password validation ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─── Static files ─────────────────────────────────────────────────────────────
STATIC_URL  = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Logging ──────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'nexara': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'nexara',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'nexara': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}