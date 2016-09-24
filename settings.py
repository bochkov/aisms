import os


def rel(*x):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel('database.db'),
    }
}

TIME_ZONE = 'Asia/Yekaterinburg'
LANGUAGE_CODE = 'ru-ru'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

MEDIA_ROOT = rel('media')  # '/home/users2/b/bochkov/domains/aisms.demoland.ru/media/'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

SECRET_KEY = 't-+*#unnma&mb@vr-*cfy+@lg91q%tm$w)4e=t0-hj#plt8ers'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'aisms_project.urls'

TEMPLATE_DIRS = (
    'templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'aisms_project.aisms',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
