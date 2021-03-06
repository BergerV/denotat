"""
Django settings for djangodenotat project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

DEBUG = True

SITE_NAME = "Translator"

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dict'                      # Or path to database file if using sqlite3. dict3/4,
        # 'ENGINE': 'django.db.backends.mysql',
        # 'NAME': 'dict',
        # 'USER': 'root',
        # 'PASSWORD': '',
        # 'HOST': 'mysql',
        # 'PORT': 3306,
        # 'OPTIONS': {
        #     'charset': 'utf8mb4',
        #     "init_command": "SET foreign_key_checks = 0;",
        # }
    }
}


TIME_ZONE = 'Europe/Moscow'
USE_TZ = True
LANGUAGE_CODE = 'ru-RU'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # The HTTP 403 exception
    'djangodenotat.middleware.http.Http403Middleware',
)

ROOT_URLCONF = 'djangodenotat.urls'

WSGI_APPLICATION = 'djangodenotat.wsgi.application'

MEDIA_URL = '/upload/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'upload')

STATIC_URL = '/media/'
STATIC_ROOT = os.path.join(PROJECT_PATH, 'media')

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'djangodenotat/media'),
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ouydq@7m$ts3e-p_sj1nf*5-1xq+jtz6q223s)sk6+0p+0!81t'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangodenotat.languages',
    'djangodenotat.denotat',
)


DATE_FORMATS = ('%d.%m.%Y')
DATE_INPUT_FORMATS = ('%d.%m.%Y')