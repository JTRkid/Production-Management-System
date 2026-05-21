"""视图 — Material, BOMItem, WorkCenter, Route, RouteStep, Equipment"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Material, BOMItem, WorkCenter, Route, RouteStep, Equipment
from .serializers import (
    MaterialSerializer,
    MaterialSimpleSerializer,
    BOMItemSerializer,
    WorkCenterSerializer,
    RouteSerializer,
    RouteStepSerializer,
    EquipmentSerializer,
)


# ---------------------------------------------------------------------------
# Material
# ---------------------------------------------------------------------------

class MaterialViewSet(viewsets.ModelViewSet):
    """物料管理：增删改查、获取启用物料列表"""

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['material_type', 'is_active']
    search_fields = ['material_code', 'material_name', 'specification']
    ordering_fields = ['material_code', 'material_name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['get'], detail=False)
    def active(self, request):
        """Return only active materials, using a lightweight serializer (for dropdowns)."""
        queryset = Material.objects.filter(is_active=True)
        serializer = MaterialSimpleSerializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


# ---------------------------------------------------------------------------
# BOMItem
# ---------------------------------------------------------------------------

class BOMItemViewSet(viewsets.ModelViewSet):
    """物料清单（BOM）管理：增删改查、获取 BOM 树形结构"""

    queryset = BOMItem.objects.select_related('parent_material', 'child_material').all()
    serializer_class = BOMItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent_material', 'child_material']
    search_fields = ['parent_material__material_name', 'child_material__material_name']
    ordering_fields = ['id']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['get'], detail=False, url_path='tree')
    def tree(self, request):
        """获取指定父物料的完整 BOM 树形结构（递归展开所有子物料）"""
        material_id = request.query_params.get('material_id')
        if not material_id:
            return Response({'code': 400, 'message': '缺少 material_id 参数'}, status=400)
        try:
            material = Material.objects.get(pk=material_id)
        except Material.DoesNotExist:
            return Response({'code': 404, 'message': '物料不存在'}, status=404)

        def build_tree(mat):
            items = BOMItem.objects.filter(parent_material=mat).select_related('child_material')
            return [{
                'id': item.id,
                'material': {
                    'id': item.child_material.id,
                    'material_code': item.child_material.material_code,
                    'material_name': item.child_material.material_name,
                    'unit': item.child_material.unit,
                },
                'quantity': float(item.quantity),
                'unit': item.unit,
                'process_step': item.process_step,
                'children': build_tree(item.child_material),
            } for item in items]

        tree_data = build_tree(material)
        return Response({'code': 200, 'data': tree_data})


# ---------------------------------------------------------------------------
# WorkCenter
# ---------------------------------------------------------------------------

class WorkCenterViewSet(viewsets.ModelViewSet):
    """工作中心管理：增删改查，关联所属车间"""

    queryset = WorkCenter.objects.select_related('workshop').all()
    serializer_class = WorkCenterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['workshop', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['code', 'name']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

class RouteViewSet(viewsets.ModelViewSet):
    """工艺路线管理：增删改查、获取工艺步骤列表"""

    queryset = Route.objects.select_related('product').prefetch_related('steps', 'steps__work_center').all()
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'is_active']
    search_fields = ['route_name', 'product__material_name', 'product__material_code']
    ordering_fields = ['route_name', 'created_at']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})

    @action(methods=['get'], detail=True)
    def steps(self, request, pk=None):
        """获取指定工艺路线的有序步骤列表"""
        route = self.get_object()
        steps_qs = RouteStep.objects.filter(
            route=route,
        ).select_related('work_center').order_by('step_no')
        serializer = RouteStepSerializer(steps_qs, many=True)
        return Response({'code': 200, 'data': serializer.data})


# ---------------------------------------------------------------------------
# RouteStep
# ---------------------------------------------------------------------------

class RouteStepViewSet(viewsets.ModelViewSet):
    """工艺步骤管理：增删改查，关联所属工艺路线和工作中心"""

    queryset = RouteStep.objects.select_related('route', 'work_center').all()
    serializer_class = RouteStepSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route', 'work_center']
    search_fields = ['step_name', 'route__route_name']
    ordering_fields = ['route', 'step_no']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})


# ---------------------------------------------------------------------------
# Equipment
# ---------------------------------------------------------------------------

class EquipmentViewSet(viewsets.ModelViewSet):
    """设备管理：增删改查，关联所属工作中心"""

    queryset = Equipment.objects.select_related('work_center').all()
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['work_center', 'status']
    search_fields = ['name', 'code', 'model']
    ordering_fields = ['code', 'name', 'purchase_date']

    def list(self, request, *args, **kwargs):
        # 重写 list 方法以统一返回格式为 {code, data}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 200, 'data': serializer.data})
