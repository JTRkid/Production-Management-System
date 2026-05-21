"""生产计划模块 — 路由"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductionPlanViewSet

router = DefaultRouter()
router.register(r'production-plans', ProductionPlanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
