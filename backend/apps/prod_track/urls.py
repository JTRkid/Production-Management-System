"""生产追踪模块 — 路由"""

from rest_framework.routers import DefaultRouter

from .views import WorkReportViewSet

router = DefaultRouter()
router.register(r'work-reports', WorkReportViewSet, basename='workreport')

urlpatterns = router.urls
