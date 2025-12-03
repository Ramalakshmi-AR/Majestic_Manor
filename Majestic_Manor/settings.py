"""
Django settings for Majestic_Manor project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env (useful locally, not on Render)
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --------------------------
# 🔐 SECURITY
# --------------------------
# SECRET_KEY = os.environ.get(
#     "SECRET_KEY",
#     "django-insecure-oz15$zv0dx5m7pm&23_9@a7mjglpv!#o%9s6j&js^6!wb2mfmb"
# )

# DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]   # Render needs '*'

# --------------------------
# 🔑 RAZORPAY KEYS
# --------------------------
# RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_RgQ7aqPF3uAVyp")
# RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "5Ktz63WjFVnzVBfhAXgNWCHR")

# --------------------------
# APPS
# --------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # your apps
    'book',
    'billing',
    'hospitality',
    'reporting',
    'contact',
    'about',
]

# --------------------------
# MIDDLEWARE
# --------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Majestic_Manor.urls"

# --------------------------
# TEMPLATES
# --------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "Majestic_Manor.wsgi.application"

# --------------------------
# DATABASE (sqlite works on Render free plan)
# --------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --------------------------
# STATIC & MEDIA
# --------------------------
STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# ⭐ Required for serving static files on Render
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------
# DEFAULT PRIMARY KEY
# --------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
