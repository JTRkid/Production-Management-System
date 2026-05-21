"""Django 项目配置文件 — 数据库、JWT、CORS、Channels 等"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# WARNING: 生产环境请更换为强随机密钥并移出代码仓库
SECRET_KEY = 'django-insecure-prod-mgmt-secret-key-change-in-production-2026'

# WARNING: 生产环境必须设为 False
DEBUG = True

# WARNING: 生产环境应限制为实际域名
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    # Local apps
    'apps.accounts',
    'apps.sys_admin',
    'apps.business',
    'apps.base_data',
    'apps.prod_plan',
    'apps.work_order',
    'apps.prod_track',
    'apps.quality',
    'apps.inventory',
    'apps.dashboard',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'teach_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'teach_platform.wsgi.application'
ASGI_APPLICATION = 'teach_platform.asgi.application'

# Database - SQLite (本地开发)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
# WARNING: 生产环境应限制为实际前端域名，而非允许所有来源
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework — 全局默认配置
REST_FRAMEWORK = {
    # 认证：JWT Token（通过 Authorization: Bearer <token> 传递）
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 权限：默认需要登录，公开接口在视图中用 permission_classes=[AllowAny] 覆盖
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # 分页：PageNumberPagination，前端通过 ?page=1&page_size=10 控制
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # 过滤：DjangoFilterBackend（精确过滤）+ SearchFilter（模糊搜索）+ OrderingFilter（排序）
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Channels
# WARNING: InMemoryChannelLayer 仅适用于开发/单进程，生产环境应使用 Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Scoring machine API key
# WARNING: 生产环境应使用强随机密钥并通过环境变量注入
SCORING_MACHINE_API_KEY = 'scoring-machine-secret-key-2026'
