"""
Django settings for driverapp project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os

from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY",'SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "DEBUG")


ALLOWED_HOSTS = ["*",'127.0.0.1','localhost','192.168.100.5']

CSRF_TRUSTED_ORIGINS = ['https://ubintax.com']

CORS_ORIGIN_ALLOW_ALL = True  
# Allow all origins to access your API
CORS_ALLOWED_ORIGINS = [
    # "https://www.ubintax.com",
    "http://localhost:3000",  # React Native development server URL
    "http://127.0.0.1:8081",  # Alternative localhost URL
    "http://192.168.100.5:8000",  # Alternative localhost URL
    # Add your production URLs here
    'http://localhost',
    # 'http://172.20.10.3:8000',
    # 'https://4cb6-154-161-162-196.ngrok-free.app',

]

# If you want to allow all origins, use the following setting
CORS_ALLOW_ALL_ORIGINS = True

# Application definition

INSTALLED_APPS = [
    "daphne",
    'channels',
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'accounts',
    'corsheaders', 
    'chat',
    'food',
    'ride.apps.RideConfig', 
    'pharmacy.apps.PharmacyConfig', 
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'chat.middleware.TokenAuthMiddlewareStack',
]

ROOT_URLCONF = 'driverapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'driverapp.wsgi.application'
ASGI_APPLICATION = 'driverapp.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get("MYSQL_DATABASE", "ridderapp"),
        'USER': os.environ.get("MYSQL_USER", "rider_user"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD", "securepassword"),
        'HOST': os.environ.get("MYSQL_HOST", "db"),  # 'db' is the Docker service name
        'PORT': os.environ.get("MYSQL_PORT", "3306"),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }



 
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'django--db',              # your actual DB name
#         'USER': 'root',            # your DB user
#         'PASSWORD': 'yawigo',             # your DB password
#         'HOST': '34.10.38.34',            # Cloud SQL public IP
#         'PORT': '3306',                   # ✅ MySQL default port
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'django--db',              # your actual DB name
#         'USER': 'root',            # your DB user
#         'PASSWORD': '',             # your DB password
#         'HOST': '127.0.0.1',            # Cloud SQL public IP
#         'PORT': '3306',                   # ✅ MySQL default port
#     }
# }
# 

# if os.getenv("GAE_ENV", "").startswith("standard"):
    # Production (App Engine uses socket)
# DATABASES = {
#     "default": {
#     "ENGINE": "django.db.backends.postgresql_psycopg2",
#     "HOST": "/cloudsql/circular-music-463403-p3:us-central:django-db",
#     "NAME": "django-db",
#     "USER": "django_user",
#     "PASSWORD": "yawigo",
#     "PORT": "5432",
# }
# }
# else:
#     # Local (via TCP using proxy)
#      DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static')
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'accounts.CustomUser'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Replace with your email host
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "EMAIL_HOST_USER"),  # Replace with your email
EMAIL_HOST_PASSWORD =  os.environ.get("EMAIL_HOST_PASSWORD", "EMAIL_HOST_PASSWORD"),  # Replace with your email password


# settings.py
ASGI_APPLICATION = 'driverapp.asgi.application'

# Channels
CHANNEL_LAYERS = {
	'default': {
		'BACKEND': 'channels_redis.core.RedisChannelLayer',
		'CONFIG': {
			'hosts': [('redis', 6379)]
			# 'hosts': [('127.0.0.1', 6379)]
		},
       
 
	}
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,  # Adjust this to your needs
}


# FILE_UPLOAD_HANDLERS = [
#     'django.core.files.uploadhandler.TemporaryFileUploadHandler',
#     'django.core.files.uploadhandler.MemoryFileUploadHandler',
# ]


# Optionally, you can increase the max upload size if the image is large
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # Example: 10MB

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(weeks=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# TWILIO_ACCOUNT_SID = 'baabcff8-2553-477b-a5b9-9ff179788989'
# TWILIO_AUTH_TOKEN = '975655e042f7c2907273b7978e195c26-746c53cc-5443-4a7a-a269-b9520da9a9a3'
# TWILIO_PHONE_NUMBER = '447860099299'


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
