"""URL 路由 — base_data 应用"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MaterialViewSet,
    BOMItemViewSet,
    WorkCenterViewSet,
    RouteViewSet,
    RouteStepViewSet,
    EquipmentViewSet,
)

router = DefaultRouter()
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'bom-items', BOMItemViewSet, basename='bomitem')
router.register(r'work-centers', WorkCenterViewSet, basename='workcenter')
router.register(r'routes', RouteViewSet, basename='route')
router.register(r'route-steps', RouteStepViewSet, basename='routestep')
router.register(r'equipment', EquipmentViewSet, basename='equipment')

urlpatterns = [
    path('', include(router.urls)),
]
