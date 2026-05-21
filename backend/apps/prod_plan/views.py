"""生产计划模块 — 视图"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ProductionPlan
from .serializers import ProductionPlanSerializer, ProductionPlanCreateSerializer


class ProductionPlanViewSet(viewsets.ModelViewSet):
    """生产计划管理：增删改查、审批、下发、取消"""

    queryset = ProductionPlan.objects.select_related('product', 'created_by', 'approved_by').all()
    filterset_fields = ['status', 'plan_type']
    search_fields = ['plan_no', 'product__material_name']
    ordering_fields = ['-created_at', 'scheduled_start', 'scheduled_end']

    def get_serializer_class(self):
        """创建时使用 ProductionPlanCreateSerializer，其余使用 ProductionPlanSerializer"""
        if self.action == 'create':
            return ProductionPlanCreateSerializer
        return ProductionPlanSerializer

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
        # 自动将当前登录用户设为创建人
        serializer.save(created_by=self.request.user)

    @action(methods=['post'], detail=True)
    def approve(self, request, pk=None):
        """审批生产计划：记录审批人和审批时间"""
        plan = self.get_object()
        plan.status = 'approved'
        plan.approved_by = request.user
        plan.approved_at = timezone.now()
        plan.save()
        return Response({'code': 200, 'message': '审批成功'})

    @action(methods=['post'], detail=True)
    def release(self, request, pk=None):
        """下发生产计划：将状态改为已下发"""
        plan = self.get_object()
        plan.status = 'released'
        plan.save()
        return Response({'code': 200, 'message': '已下发'})

    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None):
        """取消生产计划"""
        plan = self.get_object()
        plan.status = 'cancelled'
        plan.save()
        return Response({'code': 200, 'message': '已取消'})
