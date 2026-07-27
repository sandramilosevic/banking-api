from os import getenv, path
from dotenv import load_dotenv
from .base import *  # noqa
from .base import BASE_DIR
from datetime import timedelta

local_env = path.join(BASE_DIR, ".env")

if path.isfile(local_env):
    load_dotenv(local_env)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG")

SITE_NAME = getenv("SITE_NAME")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

ADMIN_URL = getenv("ADMIN_URL")

EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")
DOMAIN = getenv("DOMAIN")

MAX_UPLOAD_SIZE = 1 * 1024 * 1024

csrf_origins = getenv("CSRF_TRUSTED_ORIGINS")
if not csrf_origins:
    raise ValueError("CSRF_TRUSTED_ORIGINS is not set in .env")

CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins.split(",") if o.strip()]

# how long user is lockout after multiple failed logins (production >= 10 mins)
LOCKOUT_DURATION = timedelta(minutes=1)

# failed logins before lockout
LOGIN_ATTEMPTS = 3

# Expiration time
OTP_EXPIRATION = timedelta(minutes=1)
