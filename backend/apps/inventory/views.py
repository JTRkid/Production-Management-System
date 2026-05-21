"""库存管理模块 — 视图"""

import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Warehouse, Inventory, InventoryTransaction
from .serializers import (
    WarehouseSerializer,
    InventorySerializer,
    InventoryTransactionSerializer,
)


class WarehouseViewSet(viewsets.ModelViewSet):
    """仓库管理：增删改查"""

    queryset = Warehouse.objects.select_related('keeper').all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['warehouse_type', 'is_active']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class InventoryViewSet(viewsets.ModelViewSet):
    """库存管理：增删改查，按仓库/物料筛选"""

    queryset = Inventory.objects.select_related('material', 'warehouse').all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['warehouse', 'material']
    search_fields = ['material__material_name']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """库存流水管理：增删改查、入库操作、出库操作"""

    queryset = InventoryTransaction.objects.select_related('material', 'warehouse', 'operator').all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['warehouse', 'transaction_type']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    def perform_create(self, serializer):
        # 自动将当前登录用户设为操作人
        serializer.save(operator=self.request.user)

    @action(methods=['post'], detail=False)
    def inbound(self, request):
        """入库操作: 创建入库流水并更新库存"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        material = validated_data.get('material')
        warehouse = validated_data.get('warehouse')
        quantity = validated_data.get('quantity')
        location = validated_data.get('location') or ''
        transaction_type = validated_data.get('transaction_type', 'purchase_in')

        with transaction.atomic():
            # 生成流水号
            transaction_no = f"IN{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

            trans = InventoryTransaction.objects.create(
                transaction_no=transaction_no,
                transaction_type=transaction_type,
                material=material,
                quantity=quantity,
                warehouse=warehouse,
                source_doc_type=validated_data.get('source_doc_type', ''),
                source_doc_id=validated_data.get('source_doc_id'),
                operator=request.user,
                remark=validated_data.get('remark', ''),
            )

            # 更新库存
            inventory, _ = Inventory.objects.get_or_create(
                material=material,
                warehouse=warehouse,
                location=location,
                defaults={'quantity': 0, 'locked_quantity': 0},
            )
            inventory.quantity += quantity
            inventory.save(update_fields=['quantity', 'updated_at'])

        return Response(
            {'code': 200, 'data': InventoryTransactionSerializer(trans).data},
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['post'], detail=False)
    def outbound(self, request):
        """出库操作: 校验库存并创建出库流水"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        material = validated_data.get('material')
        warehouse = validated_data.get('warehouse')
        quantity = validated_data.get('quantity')
        location = validated_data.get('location') or ''
        transaction_type = validated_data.get('transaction_type', 'material_out')

        with transaction.atomic():
            # 查询库存
            try:
                inventory = Inventory.objects.get(
                    material=material,
                    warehouse=warehouse,
                    location=location,
                )
            except Inventory.DoesNotExist:
                return Response(
                    {'code': 400, 'message': '库存记录不存在，无法出库'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            available = inventory.quantity - inventory.locked_quantity
            if available < quantity:
                return Response(
                    {'code': 400, 'message': f'库存不足，可用数量: {available}, 申请数量: {quantity}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 生成流水号
            transaction_no = f"OUT{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

            trans = InventoryTransaction.objects.create(
                transaction_no=transaction_no,
                transaction_type=transaction_type,
                material=material,
                quantity=quantity,
                warehouse=warehouse,
                source_doc_type=validated_data.get('source_doc_type', ''),
                source_doc_id=validated_data.get('source_doc_id'),
                operator=request.user,
                remark=validated_data.get('remark', ''),
            )

            # 扣减库存
            inventory.quantity -= quantity
            inventory.save(update_fields=['quantity', 'updated_at'])

        return Response(
            {'code': 200, 'data': InventoryTransactionSerializer(trans).data},
            status=status.HTTP_201_CREATED,
        )
