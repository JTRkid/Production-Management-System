"""工单管理模块 — 视图"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import WorkOrder
from .serializers import WorkOrderSerializer, WorkReportSerializer


class WorkOrderViewSet(viewsets.ModelViewSet):
    """工单管理：增删改查、派工、开工、完工、关闭、报工"""

    queryset = WorkOrder.objects.select_related(
        'production_plan', 'product', 'workshop', 'route', 'created_by',
    ).all()
    serializer_class = WorkOrderSerializer
    filterset_fields = ['status', 'priority', 'workshop']
    search_fields = ['wo_no', 'product__material_name']
    ordering_fields = ['created_at', 'priority']

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

    @action(methods=['post'], detail=True, url_path='dispatch')
    def dispatch_order(self, request, pk=None):
        """派工：将工单状态改为已派工"""
        order = self.get_object()
        order.status = 'dispatched'
        order.save()
        return Response({'code': 200, 'message': '已派工'})

    @action(methods=['post'], detail=True)
    def start(self, request, pk=None):
        """开工：将工单状态改为生产中，记录开始时间"""
        order = self.get_object()
        order.status = 'in_progress'
        order.started_at = timezone.now()
        order.save()
        return Response({'code': 200, 'message': '生产已开始'})

    @action(methods=['post'], detail=True)
    def complete(self, request, pk=None):
        """完工：将工单状态改为已完成，记录完成时间"""
        order = self.get_object()
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        return Response({'code': 200, 'message': '已完成'})

    @action(methods=['post'], detail=True)
    def close(self, request, pk=None):
        """关闭工单：将工单状态改为已关闭"""
        order = self.get_object()
        order.status = 'closed'
        order.save()
        return Response({'code': 200, 'message': '已关闭'})

    @action(methods=['post'], detail=True)
    def report(self, request, pk=None):
        """报工：为指定工单提交生产报工记录"""
        order = self.get_object()
        serializer = WorkReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(work_order=order)
        return Response({'code': 200, 'message': '报工成功', 'data': serializer.data})
