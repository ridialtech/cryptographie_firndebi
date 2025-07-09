import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = 'dummy-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = ['django.contrib.contenttypes', 'django.contrib.staticfiles', 'pdfsigner.api']
MIDDLEWARE = ['django.middleware.common.CommonMiddleware']
ROOT_URLCONF = 'pdfsigner.urls'
STATIC_URL = '/static/'
WSGI_APPLICATION = 'pdfsigner.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}
