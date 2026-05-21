"""业务管理视图 — Customer, SalesOrder, Supplier, PurchaseOrder"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Customer, SalesOrder, Supplier, PurchaseOrder
from .serializers import (
    CustomerSerializer,
    SalesOrderSerializer,
    SalesOrderCreateSerializer,
    SupplierSerializer,
    PurchaseOrderSerializer,
    PurchaseOrderCreateSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    """客户管理：增删改查、按等级/状态筛选"""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filterset_fields = ['customer_level', 'is_active']
    search_fields = ['customer_code', 'customer_name', 'contact_person', 'contact_phone']
    ordering_fields = ['customer_code', 'customer_name', 'created_at']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class SalesOrderViewSet(viewsets.ModelViewSet):
    """销售订单管理：增删改查、审批、取消"""

    queryset = SalesOrder.objects.select_related(
        'customer', 'product', 'sales_person', 'approved_by', 'created_by',
    ).all()
    filterset_fields = ['status', 'customer']
    search_fields = ['so_no', 'customer__customer_name', 'product__material_name']
    ordering_fields = ['so_no', 'scheduled_date', 'created_at', 'total_amount']

    def get_serializer_class(self):
        """创建时使用 SalesOrderCreateSerializer，其余使用 SalesOrderSerializer"""
        if self.action == 'create':
            return SalesOrderCreateSerializer
        return SalesOrderSerializer

    def perform_create(self, serializer):
        # 自动将当前登录用户设为创建人
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        """审批销售订单：仅草稿状态可审批，记录审批人和时间"""
        order = self.get_object()
        if order.status != 'draft':
            return Response({'code': 400, 'message': '仅草稿状态可审批'}, status=400)
        order.status = 'approved'
        order.approved_by = request.user
        order.approved_at = timezone.now()
        order.save()
        return Response({'code': 200, 'message': '审批成功'})

    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None):
        """取消销售订单：已取消或已完成的订单不可取消"""
        order = self.get_object()
        if order.status in ('cancelled', 'completed'):
            return Response({'code': 400, 'message': '已取消或已完成的订单不可取消'}, status=400)
        order.status = 'cancelled'
        order.save()
        return Response({'code': 200, 'message': '订单已取消'})


class SupplierViewSet(viewsets.ModelViewSet):
    """供应商管理：增删改查"""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filterset_fields = ['is_active']
    search_fields = ['supplier_code', 'supplier_name', 'contact_person', 'contact_phone', 'supply_category']
    ordering_fields = ['supplier_code', 'supplier_name', 'created_at']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """采购订单管理：增删改查、审批、收货"""

    queryset = PurchaseOrder.objects.select_related(
        'supplier', 'material', 'buyer', 'approved_by', 'created_by',
    ).all()
    filterset_fields = ['status', 'supplier']
    search_fields = ['po_no', 'supplier__supplier_name', 'material__material_name']
    ordering_fields = ['po_no', 'ordered_date', 'expected_date', 'created_at', 'total_amount']

    def get_serializer_class(self):
        """创建时使用 PurchaseOrderCreateSerializer，其余使用 PurchaseOrderSerializer"""
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        # 自动将当前登录用户设为创建人
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        """审批采购订单：仅草稿状态可审批，记录审批人和时间"""
        order = self.get_object()
        if order.status != 'draft':
            return Response({'code': 400, 'message': '仅草稿状态可审批'}, status=400)
        order.status = 'approved'
        order.approved_by = request.user
        order.approved_at = timezone.now()
        order.save()
        return Response({'code': 200, 'message': '审批成功'})

    @action(methods=['post'], detail=True)
    def receive(self, request, pk=None):
        """采购收货：累加已收货数量，自动更新订单状态"""
        order = self.get_object()
        if order.status not in ('approved', 'ordered', 'partial_received'):
            return Response({'code': 400, 'message': '当前状态不可收货'}, status=400)
        received_qty = request.data.get('received_quantity', 0)
        try:
            received_qty = int(received_qty)
        except (TypeError, ValueError):
            return Response({'code': 400, 'message': '收货数量无效'}, status=400)
        if received_qty <= 0:
            return Response({'code': 400, 'message': '收货数量必须大于0'}, status=400)
        order.received_quantity += received_qty
        if order.received_quantity >= order.order_quantity:
            order.received_quantity = order.order_quantity
            order.status = 'received'
        elif order.received_quantity > 0:
            order.status = 'partial_received'
        order.save()
        return Response({
            'code': 200,
            'message': '收货成功',
            'data': {'received_quantity': order.received_quantity},
        })
