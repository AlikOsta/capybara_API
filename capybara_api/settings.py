
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = [
    '217.114.2.208', 
    '127.0.0.1', 
    'localhost', 
    'capybaramarket.ru',
    'www.capybaramarket.store'
    ]


CSRF_TRUSTED_ORIGINS = [
    'https://capybaramarket.ru',
    'http://capybaramarket.ru', 
    'https://217.114.2.208', 
    'http://217.114.2.208',
    'https://127.0.0.1',
    'https://localhost',
    'http://localhost',
    'http://127.0.0.1',
    'http://www.capybaramarket.store',
    'https://www.capybaramarket.store',
    ]

INSTALLED_APPS = [
    'corsheaders',
    'django_cleanup.apps.CleanupConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'capybara_tg_user',
    'capybara_tg_bot',
    'capybara_products',
    'capybara_categories',
    'capybara_countries',
    'capybara_currencies',
    'capybara_premium',
    'drf_yasg',
    
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'capybara_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'capybara_api.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',    
        'NAME': os.getenv("NAME_SQL"),                          
        'USER': os.getenv("USER_SQL"),                             
        'PASSWORD': os.getenv('PASSWORD_SQL'),                       
        'HOST': os.getenv('HOST_SQL'),                          
        'PORT': os.getenv("PORT_SQL"),                               
    }
}

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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'capybara_tg_user.TelegramUser'

BASE_MINIAPP_URL = os.getenv("BASE_URL")

PHOTO_START = os.getenv("PHOTO_START")

PHOTO_HELP = os.getenv("PHOTO_HELP")

PHOTO_INFO = os.getenv("PHOTO_INFO")

PHOTO_ERROR = os.getenv("PHOTO_ERROR")

SAPPORT_URL = os.getenv("SAPPORT_URL")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") 

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static_src',
]

STATIC_ROOT = '/home/al/capybara_API/static'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/home/al/capybara_API/media'

ALLOWED_IMAGE_TYPES = [
    'image/jpeg',               
    'image/png',                
    'image/webp',                
    'image/svg+xml',             
]


MAX_IMAGE_SIZE = 5 * 1024 * 1024 

REST_FRAMEWORK = {
        'DEFAULT_RENDERER_CLASSES': [
            "rest_framework.renderers.JSONRenderer",
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
        'capybara_tg_user.authentication.JWTAuthenticationFromCookie',
        ),
}

CORS_ALLOW_ALL_ORIGINS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_errors.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

AUTH_USER_MODEL = 'capybara_tg_user.TelegramUser'

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "https://capybaramarket.ru",
    "http://capybaramarket.ru",
]