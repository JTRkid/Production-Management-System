"""用户认证与账号管理 — 路由配置"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginViewSet, UserViewSet, WorkshopViewSet, OperationLogViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('workshops', WorkshopViewSet, basename='workshop')
router.register('logs', OperationLogViewSet, basename='operation-log')

urlpatterns = [
    path('login/', LoginViewSet.as_view({'post': 'login'}), name='login'),
    path('change-password/', LoginViewSet.as_view({'post': 'change_password'}), name='change-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('', include(router.urls)),
]
