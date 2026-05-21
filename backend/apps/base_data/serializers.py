"""序列化器 — Material, BOMItem, WorkCenter, Route, RouteStep, Equipment"""

from rest_framework import serializers
from .models import Material, BOMItem, WorkCenter, Route, RouteStep, Equipment


# ---------------------------------------------------------------------------
# Material
# ---------------------------------------------------------------------------

class MaterialSerializer(serializers.ModelSerializer):
    """物料完整序列化器"""

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class MaterialSimpleSerializer(serializers.ModelSerializer):
    """物料精简序列化器（仅含 id、编码、名称、单位），用于下拉选择"""

    class Meta:
        model = Material
        fields = ['id', 'material_code', 'material_name', 'unit']


# ---------------------------------------------------------------------------
# BOMItem
# ---------------------------------------------------------------------------

class BOMItemSerializer(serializers.ModelSerializer):
    """物料清单（BOM）序列化器：包含父/子物料的编码和名称"""

    # 关联字段：自动获取父物料和子物料的编码及名称
    parent_material_code = serializers.CharField(source='parent_material.material_code', read_only=True)
    parent_material_name = serializers.CharField(source='parent_material.material_name', read_only=True)
    child_material_code = serializers.CharField(source='child_material.material_code', read_only=True)
    child_material_name = serializers.CharField(source='child_material.material_name', read_only=True)

    class Meta:
        model = BOMItem
        fields = '__all__'


# ---------------------------------------------------------------------------
# WorkCenter
# ---------------------------------------------------------------------------

class WorkCenterSerializer(serializers.ModelSerializer):
    """工作中心序列化器：包含所属车间名称"""

    # 关联字段：自动获取所属车间名称
    workshop_name = serializers.CharField(source='workshop.name', read_only=True)

    class Meta:
        model = WorkCenter
        fields = '__all__'


# ---------------------------------------------------------------------------
# Route & RouteStep
# ---------------------------------------------------------------------------

class RouteStepSerializer(serializers.ModelSerializer):
    """工艺步骤序列化器"""

    class Meta:
        model = RouteStep
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    """工艺路线序列化器：嵌套包含所有工艺步骤"""

    # 嵌套序列化：只读方式展示该路线下的所有步骤
    steps = RouteStepSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = '__all__'


# ---------------------------------------------------------------------------
# Equipment
# ---------------------------------------------------------------------------

class EquipmentSerializer(serializers.ModelSerializer):
    """设备序列化器：包含所属工作中心名称"""

    # 关联字段：自动获取所属工作中心名称
    work_center_name = serializers.CharField(source='work_center.name', read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'
