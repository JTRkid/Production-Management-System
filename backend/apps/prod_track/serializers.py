"""生产追踪模块 — 序列化器"""

from rest_framework import serializers

from .models import WorkReport


class WorkReportSerializer(serializers.ModelSerializer):
    """报工记录序列化器：包含关联的工单号、报工人姓名、工序步骤名称"""

    # 关联字段：自动获取工单号、报工人姓名、工序步骤名称
    work_order_wo_no = serializers.CharField(source='work_order.wo_no', read_only=True)
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    route_step_name = serializers.CharField(source='route_step.step_name', read_only=True, allow_null=True)

    class Meta:
        model = WorkReport
        fields = '__all__'
        read_only_fields = ['report_time']
