"""质量管理模块 — 视图"""

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .models import InspectionStandard, InspectionRecord
from .serializers import InspectionStandardSerializer, InspectionRecordSerializer


class InspectionStandardViewSet(viewsets.ModelViewSet):
    """检验标准管理：增删改查，关联产品物料"""

    queryset = InspectionStandard.objects.select_related('product').all()
    serializer_class = InspectionStandardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['product', 'is_active']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


class InspectionRecordViewSet(viewsets.ModelViewSet):
    """检验记录管理：增删改查，记录来料/过程/成品检验结果"""

    queryset = InspectionRecord.objects.select_related('work_order', 'product', 'inspector').all()
    serializer_class = InspectionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['work_order', 'inspection_type', 'result']

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
        # 自动将当前登录用户设为检验员
        serializer.save(inspector=self.request.user)
