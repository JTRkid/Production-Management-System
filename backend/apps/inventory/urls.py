"""库存管理模块 — 路由"""

from rest_framework.routers import DefaultRouter

from .views import WarehouseViewSet, InventoryViewSet, InventoryTransactionViewSet

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'transactions', InventoryTransactionViewSet, basename='inventory-transaction')

urlpatterns = router.urls
