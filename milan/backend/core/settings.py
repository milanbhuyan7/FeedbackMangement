import os
from pathlib import Path
from decouple import config
from datetime import timedelta
import dj_database_url

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Security
SECRET_KEY = config('SECRET_KEY', cast=str)  # No default for security

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = [
    'feedbackmangement.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Application definition
INSTALLED_APPS = [
    'daphne',  # Add daphne at the top
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # Add channels
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'feedback',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Database Configuration
DATABASE_URL = config(
    'DATABASE_URL', 
    default='postgresql://feedback_user:2YUjcbWrq9FmaPuSRCIQyqtilLxDAQvA@dpg-d1chjrndiees73c4pt50-a.oregon-postgres.render.com/feedback_grk6'
)

DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# Fallback to individual database settings if DATABASE_URL parsing fails
if not DATABASES['default']:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='feedback_grk6'),
            'USER': config('DB_USER', default='feedback_user'),
            'PASSWORD': config('DB_PASSWORD', default='2YUjcbWrq9FmaPuSRCIQyqtilLxDAQvA'),
            'HOST': config('DB_HOST', default='dpg-d1chjrndiees73c4pt50-a.oregon-postgres.render.com'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }

# Channels Configuration - Using In-Memory Channel Layer
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'feedback.User'

# Authentication Configuration - Use email as username
AUTHENTICATION_BACKENDS = [
    'feedback.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "https://feedback-mangement.vercel.app",
    "https://feedbackmangement.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only for development

# Additional CORS headers for WebSocket
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
]

# SSE Configuration
SSE_HEARTBEAT_INTERVAL = 30  # seconds

# Email Configuration (for future use)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@feedbacktool.com'

# Security Settings for Production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
