"""生产计划模块 — 序列化器"""

from rest_framework import serializers
from .models import ProductionPlan


class ProductionPlanSerializer(serializers.ModelSerializer):
    """生产计划序列化器（详情/列表），包含关联名称的只读字段"""

    # 关联字段：自动获取产品名称、创建人姓名、审批人姓名
    product_name = serializers.CharField(source='product.material_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.name', read_only=True)

    class Meta:
        model = ProductionPlan
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProductionPlanCreateSerializer(serializers.ModelSerializer):
    """生产计划创建序列化器：plan_no/created_by 由后端自动生成"""

    class Meta:
        model = ProductionPlan
        fields = [
            'plan_no', 'plan_type', 'product', 'plan_quantity',
            'status', 'scheduled_start', 'scheduled_end',
        ]
