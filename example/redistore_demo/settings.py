#-*- coding: utf-8 -*-

import os

PRJ_PATH = os.path.abspath(os.path.curdir)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = DEBUG

ADMINS = (
    ("Alice Bloggs", "alice@example.com"),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   "django.db.backends.sqlite3",
        'NAME':     "redistore_demo.db",
        'USER':     "", 
        'PASSWORD': "", 
        'HOST':     "", 
        'PORT':     "",
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Europe/Brussels"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PRJ_PATH, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PRJ_PATH, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PRJ_PATH, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = "vbtge3@fn!73i&1h)g=0&)*b*uc_4+&ury)x)8a*a+-f0fpxe5"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = "urls"

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    'django.contrib.messages',
    "django.contrib.admin",

    "smsgateway",
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple' 
        }
    },
    'loggers': {
        'smsgateway': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

SMSGATEWAY_ACCOUNTS = {
    '__default__': 'redistore',
    'redistore': {
        'source_addr_ton': 0,
        'source_addr': 15185,
        'dest_addr_ton': 1,
        'backend': 'redistore',
        'host': 'localhost',
        'port': 6379,
        # 'dbn': 2,
        # 'key_prefix': 'test:',
        'dbn': 3,
        'pwd': None,
        'key_prefix': 'kpn:',
        'reply_signature': 'Mobile Vikings'
    } 
}

# When there are problems with the MobileWeb incoming urls, call 02 247 37 27

SMSGATEWAY_BACKENDS = (
    'smsgateway.backends.redistore.RedistoreBackend',
)

SMSGATEWAY_HOOK = {
    'SIM': {
        'TOPUP': 'mvne.telco.direct_debit.utils.incoming_topup_sms',
        '*': 'mvne.activation.utils.incoming_sms'
    }
}
