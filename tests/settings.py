#-*- coding: utf-8 -*-

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3', 
        'NAME':     'smsgateway_test',
        'USER':     '', 
        'PASSWORD': '', 
        'HOST':     '', 
        'PORT':     '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Brussels'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

STATIC_URL = ''

SECRET_KEY = 'vbtge3@fn!73i&1h)g=0&)*b*uc_4+&ury)x)8a*a+-f0fpxe5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
)

ROOT_URLCONF = 'smsgateway.tests.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(os.path.dirname(__file__), "..", "templates"),
)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'smsgateway',
    'smsgateway.tests',
]

SMSGATEWAY_HOOK = {
    'SIM': {
        'TOPUP': 'mvne.telco.direct_debit.utils.incoming_topup_sms',
        '*': 'mvne.activation.utils.incoming_sms'
    }
}

SMSGATEWAY_ACCOUNTS = {
     '__default__': 'smpp',
    'smpp': {
        'backend': 'smpp',
        'host': 'localhost',
        'port': '2775',
        'system_id': 'smppclient1',
        'password': 'pwd1',
        'system_type': 'www',
    },
    'redistore': {
        'backend': 'redistore',
        'host': 'localhost',
        'port': 6379,
        'dbn': 2,
        'key_prefix': 'test'
    } 
}

SMSGATEWAY_BACKENDS = (
    'smsgateway.backends.redistore.RedistoreBackend',
    'smsgateway.backends.smpp.SMPPBackend',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple' 
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'smsgateway.backends': {
            'handlers': ['console'],
            'level': 'CRITICAL',
        },
        'smsgateway.smpplib.client': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}
