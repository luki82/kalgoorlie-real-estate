"""
Django settings for core project.
"""
import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv 

# Load variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY CONFIGURATION ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-unsafe-key-for-dev')



# SECURITY: False in production (Render), True locally.
if os.environ.get('LIVE_MODE'):
    DEBUG = False
    print("🔴 DEBUG MODE IS OFF (Live Site)")
else:
    DEBUG = True
    print("🟢 DEBUG MODE IS ON (Local Computer)")

ALLOWED_HOSTS = [
    'auestate.com.au', 
    'www.auestate.com.au', 
    'auestate.onrender.com',
    'auestate.com',
    'www.auestate.com',
    '127.0.0.1',
    'localhost'
]

CSRF_TRUSTED_ORIGINS = [
    'https://auestate.com.au',
    'https://www.auestate.com.au',
]

# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third Party Apps
    'django_cleanup.apps.CleanupConfig',

    # Custom Apps
    'accounts',
    'pages',
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware', # Compresses content for speed
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'


# --- DATABASE ---
# If we are on Render, use their database. If on laptop, use SQLite.
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Perth' 
USE_I18N = True
USE_TZ = True


# --- STATIC & MEDIA FILES ---

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# User Uploads (Local default)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CUSTOM AUTH ---
AUTH_USER_MODEL = 'accounts.User' 
LOGIN_URL = 'admin:login'


# --- CACHE ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}


# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'admin@auestate.com.au'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')


# --- FILE STORAGE ---
# Static files (including the portfolio drawings) are served by WhiteNoise.
MEDIA_URL = '/media/'
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Put the PDFs for the Portfolio page in this folder (see portfolio_pdfs/README.txt)
PORTFOLIO_PDF_DIR = BASE_DIR / 'portfolio_pdfs'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
