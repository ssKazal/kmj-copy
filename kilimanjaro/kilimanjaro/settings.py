import os
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)
KILIMANJARO_LOG = config("KILIMANJARO_LOG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

AUTH_USER_MODEL = "user.User"

FRONT_END_DOMAIN = config("FRONT_END_DOMAIN", default="http://example.com")
FRONT_END_ACC_VERIFICATION_URL = config(
    "FRONT_END_ACC_VERIFICATION_URL", default="/verify-acc"
)
FRONT_END_RESET_PASSWORD_URL = config(
    "FRONT_END_RESET_PASSWORD_URL", default="/reset-pass"
)

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "user.authentication.CustomAuthBackend",  # make sure the first one is the custom
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "channels",
    "djmoney",
    "rest_framework",
    "django_filters",
    "phonenumber_field",
    # Custom apps
    "user",
    "core",
    "country",
    "notification",
    "contact_us",
    "occupation",
    "certification",
    "portfolio",
    "favorite",
    "skilled_worker",
    "customer",
    "chat",
    # coz customized import.html
    "import_export",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom
    "core.utils.middlewares.ClientAPIVerification",
    "core.utils.middlewares.ForceAccountVerification",
]

ROOT_URLCONF = "kilimanjaro.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.utils.context_processors.supported_currencies",
            ],
        },
    },
]

# WSGI_APPLICATION = 'kilimanjaro.wsgi.application'

# Channels
ASGI_APPLICATION = "kilimanjaro.asgi.application"

REDIS_HOST = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT = config("REDIS_PORT", default=6379)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (REDIS_HOST, REDIS_PORT)
            ],  # while deploying Host&Port need to change
        },
    },
}

# redis caches with django-redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://redis:{REDIS_PORT}/",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

CACHE_TTL = 60 * 43800

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default=""),
        "USER": config("DB_USER", default=""),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default=""),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# Default DATA_UPLOAD_MAX_MEMORY_SIZE is 2.5 MB, that raise error while upload large file
DATA_UPLOAD_MAX_MEMORY_SIZE = 1 * 1024 * 1024 * 1024  # 1GB

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = "en-GB"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "kilimanjaro/media")

STATICFILES_DIRS = (os.path.join(BASE_DIR, "kilimanjaro", "static"),)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "kilimanjaro", "static_root")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

SITE_HOST = config("SITE_HOST", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# JWT TOKEN LIFETIME
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="emailproviderusername")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="emailpassword")
EMAIL_USE_TLS = True
FROM_EMAIL = config("FROM_EMAIL", default="mail_address")

# twilio
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_NUMBER = config("TWILIO_NUMBER", default="")

RMQ_USER = config("RMQ_USER", default='')
RMQ_PASSWORD = config("RMQ_PASSWORD", default='')

# CELERY STUFF
CELERY_BROKER_URL = f"amqp://{RMQ_USER}:{RMQ_PASSWORD}@rabbitmq//"
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_RESULT_PERSISTANT = False
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"

EMAIL_VALIDITY_TIME = 24 * 60  # 24hrs
SMS_VALIDITY_TIME = 60  # 1hr
TOKEN_REQUEST_TIMEOUT = 1  # 1min

# currencies that would be supported
SKILLED_WORKER_SUPPORTED_CURRENCY = ["XAF", "GMD"]
CUSTOMER_SUPPORTED_CURRENCY = ["EUR", "GBP", "GMD", "USD", "XAF"]

if DEBUG:
    DEBUG_TOOLBAR_INTERNAL_IP = config("DEBUG_TOOLBAR_INTERNAL_IP", default="127.0.0.1")
    INTERNAL_IPS = [DEBUG_TOOLBAR_INTERNAL_IP]
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]


if KILIMANJARO_LOG:
    #  logging
    import logging

    INSTALLED_APPS += ["nplusone.ext.django"]
    MIDDLEWARE += [
        "core.logging.middleware.LoggingMiddleware",
        "nplusone.ext.django.NPlusOneMiddleware",
    ]
    NPLUSONE_LOGGER = logging.getLogger("nplusone")
    NPLUSONE_LOG_LEVEL = logging.WARN
    COMMON_FORMAT = "%(levelname)s %(asctime)s %(module)s %(process)d %(pathname)s %(funcName)s %(message)s"
 
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        
        # describe the exact format of that text
        "formatters": {
            "console": {
                "format": COMMON_FORMAT
            },
            "common": {
                "format": COMMON_FORMAT,
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            "request_track": {
                "format":  COMMON_FORMAT + "%(log_data)s %(request_data)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            "notification": {
                "format":  COMMON_FORMAT + "%(response_dict)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            "email_send": {
                "format":  "%(levelname)s %(asctime)s %(subject)s %(to_email)s %(message)s %(reason_of_fail)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            "sms_send": {
                "format":  "%(levelname)s %(asctime)s %(recipient_number)s %(message)s %(reason_of_fail)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
        },

        # describes a particular logging behavior, such as writing a message to the screen, to a file, or to a network socket.
        "handlers": {
            "common": {
                "class": "logging.FileHandler",
                "formatter": "common",
                "filename": os.path.join(BASE_DIR, "core/logging/save_log.log"),
            },
            "console": {
                "class": "logging.StreamHandler", 
                "formatter": "console"
            },
            "request_track": {
                "class": "logging.FileHandler",
                "formatter": "request_track",
                "filename": os.path.join(BASE_DIR, "core/logging/save_log.log"),
            },
            "notification": {
                "class": "logging.FileHandler",
                "formatter": "notification",
                "filename": os.path.join(BASE_DIR, "core/logging/save_log.log"),
            },
            "email_send": {
                "class": "logging.FileHandler",
                "formatter": "email_send",
                "filename": os.path.join(BASE_DIR, "core/logging/celery_log.log"),
            },
            "sms_send": {
                "class": "logging.FileHandler",
                "formatter": "sms_send",
                "filename": os.path.join(BASE_DIR, "core/logging/celery_log.log"),
            },
        },

        # Entry point of the logging system
        "loggers": {
            'request_track': { # Stop SQL debug from logging to main logger
                'handlers': ['request_track'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False
            },
            'notification': { # Stop SQL debug from logging to main logger
                'handlers': ['notification'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False
            },
            'email_send': { # Stop SQL debug from logging to main logger
                'handlers': ['email_send'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False
            },
            'sms_send': { # Stop SQL debug from logging to main logger
                'handlers': ['sms_send'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False
            },
            '': { # Stop SQL debug from logging to main logger
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
                'propagate': False
            },
            "nplusone": {
                "handlers": ["console"],
                "level": "WARN",
            },
        },
    }