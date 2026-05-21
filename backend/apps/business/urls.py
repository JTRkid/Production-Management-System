"""业务管理模块 — 路由配置（客户、销售订单、供应商、采购订单）"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SalesOrderViewSet, SupplierViewSet, PurchaseOrderViewSet

router = DefaultRouter()
router.register('customers', CustomerViewSet, basename='customer')
router.register('sales-orders', SalesOrderViewSet, basename='sales-order')
router.register('suppliers', SupplierViewSet, basename='supplier')
router.register('purchase-orders', PurchaseOrderViewSet, basename='purchase-order')

urlpatterns = [
    path('', include(router.urls)),
]
