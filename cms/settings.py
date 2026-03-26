from pathlib import Path
from django.contrib.messages import constants as messages
import os
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# ========================
# CORE SETTINGS
# ========================

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is required")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".vercel.app",
    ".now.sh",
    ".up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
    "https://*.vercel.app",
]

# ========================
# APPLICATIONS
# ========================

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # your apps
    "cms",
    "accounts",
    "users",
    "articles",
    "blog",
    "package",
    "testimonials",
    "social",
    "nearby",
    "services",
    "faq",
    "menu",
    "offers",
    "preferences",
    "features",
    "popup",
    "location",
    "media_manager",
    "api",
    "core",

    # third-party
    "ckeditor",
    "ckeditor_uploader",
    "rest_framework",
    "corsheaders",
    "widget_tweaks",
]

# DEV ONLY APPS
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

# ========================
# MIDDLEWARE
# ========================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# DEV ONLY MIDDLEWARE
if DEBUG:
    MIDDLEWARE.insert(0, "django_browser_reload.middleware.BrowserReloadMiddleware")

# ========================
# JAZZMIN
# ========================

JAZZMIN_SETTINGS = {
    "site_title": "PYTHON CMS",
    "site_header": "PYTHON CMS",
    "site_brand": "PYTHON CMS",
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}

# ========================
# URL / TEMPLATES
# ========================

ROOT_URLCONF = "cms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.sidebar_menu",
            ],
        },
    },
]

WSGI_APPLICATION = "cms.wsgi.application"

# ========================
# DATABASE
# ========================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is required in production")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )
}

# ========================
# PASSWORD VALIDATION
# ========================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================
# LOGGING (SERVERLESS SAFE)
# ========================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# ========================
# CORS
# ========================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
]

# ========================
# INTERNATIONALIZATION
# ========================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========================
# STATIC FILES
# ========================

# STATIC FILES
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # collectstatic will copy everything here
STATICFILES_DIRS = [BASE_DIR / "static"]  # your source static files

# Use WhiteNoise for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media (optional, Vercel not good for uploaded files)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ========================
# CKEDITOR
# ========================

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_RESTRICT_BY_DATE = False

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 400,
        "width": "100%",
        "allowedContent": True,
        "extraPlugins": "uploadimage,image2,sourcearea",
    }
}

# ========================
# REST FRAMEWORK
# ========================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

# ========================
# AUTH REDIRECTS
# ========================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# ========================
# MESSAGES
# ========================

MESSAGE_TAGS = {
    messages.ERROR: "error",
    messages.SUCCESS: "success",
}

# ========================
# SECURITY (IMPORTANT)
# ========================

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG