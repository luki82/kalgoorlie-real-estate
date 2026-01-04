"""
Django settings for core project.
"""
import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv # <--- Import this

# Load variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY CONFIGURATION ---
# SECURITY WARNING: keep the secret key used in production secret!
# We will use an Environment Variable for this later. 
# For now, this is okay ONLY for your local computer.
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'default-unsafe-key-for-dev')


# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# This logic means: If the environment says "False", it's False. Otherwise default to True.
#DEBUG = os.environ.get('DEBUG') == 'True'
if os.environ.get('RENDER'):
    DEBUG = False
else:
    DEBUG = True

#ALLOWED_HOSTS = [] # Add your domain (e.g., 'iioptions.com.au') here when live.
ALLOWED_HOSTS = [
    'auestate.com.au', 
    'www.auestate.com.au', 
    'your-render-app.onrender.com',
    # You can keep these here safely
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
    
    # Custom Apps (I added the missing ones back!)
    'accounts',
    'listings',
    #'realtors',  # ### Added back
   # 'contacts',  # ### Added back
    'pages',
    'payments',  # Assuming you are adding this new feature
]

MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware', # Compresses content for speed
    'django.middleware.security.SecurityMiddleware', # ### Removed duplicate line
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

# DATABASE CONFIGURATION
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

# ### Kalgoorlie Engineering Standard
# Changing from UTC to Perth time ensures your listing dates are accurate
TIME_ZONE = 'Australia/Perth' 

USE_I18N = True
USE_TZ = True


# --- STATIC & MEDIA FILES ---


# STATIC FILES CONFIGURATION
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Where files go on the server
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Where they are now

# Enable WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



# User Uploads
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- CUSTOM AUTH ---
# Ensure your 'accounts' app has a model named 'User' or this will crash!
AUTH_USER_MODEL = 'accounts.User' 
LOGIN_URL = 'login' 


# --- CACHE ---
# Simple development cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}




# 3 action to be done before going live!    
# 1 seceret key to be put in .env 
# turn of debug
# set up email , and payment intergration

# --- EMAIL CONFIGURATION (Gmail) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('wkop abmd llbq eagl')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# settings.py

# ... existing code ...

# EMAIL CONFIGURATION (Microsoft 365 / GoDaddy)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Your new professional email address
EMAIL_HOST_USER = 'admin@auestate.com.au'  # <--- CHANGE THIS to your actual email
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# SECURITY WARNING: Never type the actual password here!
# We will read it from the Render Environment instead.

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# ... existing code ...
