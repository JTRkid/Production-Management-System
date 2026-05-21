"""质量管理模块 — 序列化器"""

from rest_framework import serializers

from .models import InspectionStandard, InspectionRecord


class InspectionStandardSerializer(serializers.ModelSerializer):
    """检验标准序列化器：包含关联产品名称"""

    # 关联字段：自动获取产品物料名称
    product_name = serializers.CharField(source='product.material_name', read_only=True)

    class Meta:
        model = InspectionStandard
        fields = '__all__'
        read_only_fields = ['created_at']


class InspectionRecordSerializer(serializers.ModelSerializer):
    """检验记录序列化器：包含关联产品名称、检验员姓名、工单号"""

    # 关联字段：自动获取产品名称、检验员姓名、关联工单号
    product_name = serializers.CharField(source='product.material_name', read_only=True)
    inspector_name = serializers.CharField(source='inspector.name', read_only=True)
    work_order_wo_no = serializers.CharField(source='work_order.wo_no', read_only=True, allow_null=True)

    class Meta:
        model = InspectionRecord
        fields = '__all__'
        read_only_fields = ['inspected_at']
