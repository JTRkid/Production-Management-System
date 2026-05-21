"""生产追踪模块 — 视图"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import WorkReport
from .serializers import WorkReportSerializer


class WorkReportViewSet(viewsets.ModelViewSet):
    """报工记录管理：增删改查、查看当前用户的报工记录"""

    queryset = WorkReport.objects.select_related('work_order', 'route_step', 'worker').all()
    serializer_class = WorkReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['work_order']
    ordering_fields = ['report_time', 'report_quantity']
    ordering = ['-report_time']

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
        # 自动将当前登录用户设为报工人
        serializer.save(worker=self.request.user)

    @action(methods=['get'], detail=False)
    def my_reports(self, request):
        """当前用户的报工记录"""
        queryset = self.filter_queryset(
            self.get_queryset().filter(worker=request.user)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})
