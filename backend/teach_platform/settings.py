"""Django 项目配置文件 — 数据库、JWT、CORS、Channels 等

环境变量说明（不设置时使用开发默认值）：
  DJANGO_SECRET_KEY   — 生产环境必须设置
  DJANGO_DEBUG        — 生产环境设为 False
  DJANGO_ALLOWED_HOSTS — 逗号分隔的域名列表
  MYSQL_HOST          — 设置后切换到 MySQL，不设置则用 SQLite
  MYSQL_PORT / MYSQL_DATABASE / MYSQL_USER / MYSQL_PASSWORD
  REDIS_URL           — 设置后启用 Redis Channel Layer
  CORS_ALLOWED_ORIGINS — 逗号分隔的前端域名
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥 — 生产环境必须通过环境变量注入
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-prod-mgmt-secret-key-change-in-production-2026',
)

# 调试模式 — 生产环境设为 DJANGO_DEBUG=False
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

# 允许的主机 — 生产环境设置实际域名，如 "your.com,www.your.com"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')
    if h.strip()
]

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

# Database — 设置 MYSQL_HOST 环境变量后自动切换 MySQL，否则使用 SQLite（开发）
if os.environ.get('MYSQL_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('MYSQL_DATABASE', 'prod_mgmt'),
            'USER': os.environ.get('MYSQL_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ['MYSQL_HOST'],
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
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

# CORS — 生产环境通过 CORS_ALLOWED_ORIGINS 环境变量限制来源
_cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', '')
if _cors_origins:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(',') if o.strip()]
else:
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

# Channels — 设置 REDIS_URL 后自动切换 Redis，否则使用内存（开发/单进程）
_redis_url = os.environ.get('REDIS_URL')
if _redis_url:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [_redis_url]},
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# Scoring machine API key
SCORING_MACHINE_API_KEY = os.environ.get(
    'SCORING_MACHINE_API_KEY', 'scoring-machine-secret-key-2026'
)
