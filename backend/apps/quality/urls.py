"""质量管理模块 — 路由"""

from rest_framework.routers import DefaultRouter

from .views import InspectionStandardViewSet, InspectionRecordViewSet

router = DefaultRouter()
router.register(r'standards', InspectionStandardViewSet, basename='inspection-standard')
router.register(r'records', InspectionRecordViewSet, basename='inspection-record')

urlpatterns = router.urls
