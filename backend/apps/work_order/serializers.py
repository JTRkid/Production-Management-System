"""工单管理模块 — 序列化器"""

from rest_framework import serializers
from .models import WorkOrder
from apps.prod_track.models import WorkReport


class WorkOrderSerializer(serializers.ModelSerializer):
    """工单序列化器（详情/列表），包含关联名称的只读字段"""

    # 关联字段：自动获取产品名称、车间名称、创建人姓名
    product_name = serializers.CharField(source='product.material_name', read_only=True)
    workshop_name = serializers.CharField(source='workshop.name', read_only=True)
    # SerializerMethodField：工艺路线名称可能为空，需要自定义获取逻辑
    route_name = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    # SerializerMethodField：生产计划单号可能为空（工单可不关联计划），需要自定义获取逻辑
    plan_no = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']

    def get_route_name(self, obj):
        """获取工艺路线名称，无关联时返回 None"""
        return obj.route.route_name if obj.route else None

    def get_plan_no(self, obj):
        """获取关联生产计划的单号，无关联时返回 None"""
        return obj.production_plan.plan_no if obj.production_plan else None


class WorkReportSerializer(serializers.ModelSerializer):
    """工单内嵌报工序列化器：用于工单详情页的报工操作"""

    class Meta:
        model = WorkReport
        fields = ['route_step', 'worker', 'report_quantity', 'defect_quantity', 'work_hours', 'remark']
