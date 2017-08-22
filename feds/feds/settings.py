"""
Django settings for feds project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import datetime
import os

# See https://simpleisbetterthancomplex.com/tips/2016/09/06/
# django-tip-14-messages-framework.html
from django.contrib.messages import constants as messages

from .secrets import secret_db_password, secret_key, secret_allowed_hosts, \
    secret_db_name, secret_db_user

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secret_key()
# SECRET_KEY = os.environ['feds_secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = secret_allowed_hosts()

# For debug toolbar.
# https://stackoverflow.com/questions/26898597/django-debug-toolbar-and-docker
# import subprocess
#
# route = subprocess.Popen(('ip', 'route'), stdout=subprocess.PIPE)
# network = subprocess.check_output(
#     ('grep', '-Po', 'src \K[\d.]+\.'), stdin=route.stdout).decode().rstrip()
# route.wait()
# network_gateway = network + '1'
# INTERNAL_IPS = [network_gateway]
# INTERNAL_IPS.append('0.0.0.0:8000')


# INTERNAL_IPS = ('127.0.0.1', '0.0.0.0:8000', )

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    # 'debug_toolbar',
    'django_docutils',
    'sitepages',
    'accounts',
    'helpers',
    'projects',
    'fieldspecs',
    'fieldsettings',
    'businessareas',
    'contact',
]

MIDDLEWARE = [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'feds.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'feds.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': secret_db_name(),
        'USER': secret_db_user(),
        'PASSWORD': secret_db_password(),
        'HOST': 'db'
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

# Auth system stuff
# Where to go after login
LOGIN_REDIRECT_URL = 'home'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# Places besides apps that static files come from
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "templates/static"),
]


# TODO: replace this with something better.
STATIC_ROOT = '/var/www/html/feds/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads/')
MEDIA_URL = '/uploads/'

# Project convenience settings.
FEDS_REST_HELP_URL = 'http://docutils.sourceforge.net/docs/user/rst' \
                     '/quickref.html'

# Aggregate machine name separator
FEDS_AGGREGATE_MACHINE_NAME_SEPARATOR = ' '

# Settings groups.
FEDS_BASIC_SETTING_GROUP = 'setting'
FEDS_ANOMALY_GROUP = 'anomaly'

FEDS_SETTING_GROUPS = (
    (FEDS_BASIC_SETTING_GROUP, 'Basic setting'),
    (FEDS_ANOMALY_GROUP, 'Anomaly'),
)

# Types of fields that can be in notional tables.
# These are NOT settings, but types of notional fields,
# like CName, and InvoiceDate.
FEDS_PRIMARY_KEY_NOTIONAL_FIELD = 'pk'
FEDS_FOREIGN_KEY_NOTIONAL_FIELD = 'fk'
FEDS_TEXT_NOTIONAL_FIELD = 'text'
FEDS_ZIP_NOTIONAL_FIELD = 'zip'
FEDS_PHONE_NOTIONAL_FIELD = 'phone'
FEDS_EMAIL_NOTIONAL_FIELD = 'email'
FEDS_DATE_NOTIONAL_FIELD = 'date'
FEDS_CHOICE_NOTIONAL_FIELD = 'choice'
FEDS_CURRENCY_NOTIONAL_FIELD = 'currency'
FEDS_INT_NOTIONAL_FIELD = 'int'

FEDS_NOTIONAL_FIELD_TYPES = (
    (FEDS_PRIMARY_KEY_NOTIONAL_FIELD, 'Primary key'),
    (FEDS_FOREIGN_KEY_NOTIONAL_FIELD, 'Foreign key'),
    (FEDS_TEXT_NOTIONAL_FIELD, 'Text'),
    (FEDS_ZIP_NOTIONAL_FIELD, "Zip code"),
    (FEDS_PHONE_NOTIONAL_FIELD, "Phone"),
    (FEDS_EMAIL_NOTIONAL_FIELD, "Email address"),
    (FEDS_DATE_NOTIONAL_FIELD, 'Date'),
    (FEDS_CHOICE_NOTIONAL_FIELD, 'Choice from a list'),
    (FEDS_CURRENCY_NOTIONAL_FIELD, 'Currency'),
    (FEDS_INT_NOTIONAL_FIELD, 'Integer'),
)

# Setting types.
FEDS_DATE_RANGE_SETTING = 'daterange'
FEDS_BOOLEAN_SETTING = 'boolean'
FEDS_INTEGER_SETTING = 'int'
FEDS_CHOICE_SETTING = 'choice'
FEDS_CURRENCY_SETTING = 'currency'
FEDS_FLOAT_SETTING = 'float'
FEDS__SETTING = ''

FEDS_SETTING_TYPES = (
    (FEDS_DATE_RANGE_SETTING, 'Date range (start and end)'),
    (FEDS_BOOLEAN_SETTING, 'Boolean (on or off)'),
    (FEDS_INTEGER_SETTING, 'Integer'),
    (FEDS_CHOICE_SETTING, 'Choice from a list'),
    (FEDS_CURRENCY_SETTING, 'Currency'),
    (FEDS_FLOAT_SETTING, 'Float'),
)

# Name of value param for all setting types.
FEDS_VALUE_PARAM = 'value'

# Settings constants

# Name of param that specifies the machine name of a setting.
FEDS_MACHINE_NAME_PARAM = 'machinename'

# Names of params that give start and end date.
FEDS_START_DATE_PARAM = 'startdate'
FEDS_END_DATE_PARAM = 'enddate'
# Dates are year, month, day.
FEDS_MIN_START_DATE = datetime.date(2000, 1, 1)
FEDS_MIN_END_DATE = datetime.date(2000, 2, 1)
# Labels to use for, e.g., boolean values.
FEDS_LABEL = 'label'
# Param for the value of a boolean label.
# FEDS_BOOLEAN_VALUE_PARAM = 'value'
FEDS_BOOLEAN_VALUE_TRUE = 'true'
FEDS_BOOLEAN_VALUE_FALSE = 'false'
# Names of properties for integers.
# FEDS_INTEGER_VALUE_PARAM = 'value'
FEDS_MIN = 'min'
FEDS_MAX = 'max'
# Default number of customers per project.
FEDS_DEFAULT_NUMBER_CUSTOMERS = 20
# Default average number of invoices per customer.
FEDS_DEFAULT_AVG_INVOICES_PER_CUSTOMER = 5

# Name of the param that stores choices.
FEDS_CHOICES_PARAM = 'choices'
# Name of the param that stores choice made.
# FEDS_CHOICE_VALUE_PARAM = 'choice'

# Choices of stat distributions.
FEDS_NORMAL_DISTRIBUTION = 'normal'
FEDS_SKEWED_DISTRIBUTION = 'skewed'
FEDS_STAT_DISTRIBUTION_CHOCIES = (
    (FEDS_NORMAL_DISTRIBUTION, 'Normal'),
    (FEDS_SKEWED_DISTRIBUTION, 'Skewed')
)
# Name of the param that stores a distribution.
# FEDS_DISTRIBUTION_VALUE_PARAM = 'distribution'

# Normal distribution mean.
FEDS_NORMAL_DISTRIBUTION_MEAN_TOTAL_BEFORE_TAX_DEFAULT = 800

# Name of param that gives Python visibility function.
FEDS_PYTHON_VISIBILITY_FUNCTION_PARAM = 'pythonvisfunction'

# Stuff for floats.
FEDS_FLOAT_DECIMALS_PARAM = 'decimals'
FEDS_FLOAT_DECIMALS_DEFAULT = 2

FEDS_SALES_TAX_SETTING_DEFAULT = 0.06

FEDS_CASH = 'cash'
FEDS_CREDIT = 'credit'

FEDS_PAYMENT_TYPES = (
    (FEDS_CASH, 'Cash'),
    (FEDS_CREDIT, 'Credit')
)

FEDS_WORKING_DAYS_WEEKDAYS = 'weekdays'
FEDS_WORKING_DAYS_MON_SAT = 'monsat'
FEDS_WORKING_DAYS_ALL_WEEK = 'allweek'

FEDS_WORKING_DAYS = (
    (FEDS_WORKING_DAYS_WEEKDAYS, 'Weekdays (Mon. - Fri.)'),
    (FEDS_WORKING_DAYS_MON_SAT, 'Mon. - Sat.'),
    (FEDS_WORKING_DAYS_ALL_WEEK, 'All week')
)

FEDS_NUMBER_STYLE_SIMPLE = 'simple'
FEDS_NUMBER_STYLE_COMPLEX = 'complex'
FEDS_NUMBER_STYLE = (
    (FEDS_NUMBER_STYLE_SIMPLE, 'Simple'),
    (FEDS_NUMBER_STYLE_COMPLEX, 'Complex'),
)

FEDS_EXPORT_TABLES_JOINED = 'joined'
FEDS_EXPORT_TABLES_SEPARATE = 'separate'
FEDS_EXPORT_TABLES = (
    (FEDS_EXPORT_TABLES_JOINED, 'Joined'),
    (FEDS_EXPORT_TABLES_SEPARATE, 'Separate'),
)

