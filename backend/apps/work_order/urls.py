"""工单管理模块 — 路由"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet

router = DefaultRouter()
router.register(r'work-orders', WorkOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
