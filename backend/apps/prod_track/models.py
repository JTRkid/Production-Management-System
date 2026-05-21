"""生产追踪模块 — WorkReport 模型

记录工人在生产过程中的报工信息，用于追踪生产进度和计算工时。
每条报工记录关联一个工单和一道工序，记录完成数量和工时。
"""

from django.db import models


class WorkReport(models.Model):
    """工作报工模型，记录工人的生产报工数据。

    工人在完成某道工序后提交报工，记录合格数量、不良数量和实际工时。
    报工数据用于更新工单的完成进度和工人工时统计。
    """

    # 关联的生产工单
    work_order = models.ForeignKey(
        'work_order.WorkOrder',
        on_delete=models.CASCADE,
        related_name='work_reports',
        verbose_name='工单'
    )
    # 报工对应的工艺步骤，删除工艺步骤时置空
    route_step = models.ForeignKey(
        'base_data.RouteStep',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_reports',
        verbose_name='工艺步骤'
    )
    # 执行报工的工人
    worker = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='work_reports',
        verbose_name='工人'
    )
    # 本次报工的合格产品数量
    report_quantity = models.IntegerField('合格数量')
    # 本次报工中产生的不良品数量
    defect_quantity = models.IntegerField('不良数量', default=0)
    # 本次报工消耗的实际工时（小时）
    work_hours = models.DecimalField('工时', max_digits=5, decimal_places=2, null=True, blank=True)
    # 报工提交的时间，自动填充
    report_time = models.DateTimeField('报工时间', auto_now_add=True)
    # 报工备注信息，如异常情况说明
    remark = models.CharField('备注', max_length=512, blank=True, default='')

    class Meta:
        db_table = 'prod_work_report'  # 数据库表名
        verbose_name = '工作报工'
        verbose_name_plural = verbose_name
        ordering = ['-report_time']  # 按报工时间倒序，最新报工在前

    def __str__(self):
        """返回工单号-工人姓名(合格数量)格式"""
        return f'{self.work_order.wo_no} - {self.worker.name} ({self.report_quantity})'
