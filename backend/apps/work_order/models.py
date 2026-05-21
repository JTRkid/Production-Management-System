"""工单管理模块 — WorkOrder 模型

管理生产工单的创建、派工、执行和关闭全流程。
工单是车间执行生产任务的基本单元，由生产计划生成或手动创建。
"""

from django.db import models


class WorkOrder(models.Model):
    """工单模型，记录具体的生产任务信息和执行状态。

    优先级说明（PRIORITY_CHOICES）：
        normal - 普通：按正常排产顺序执行
        urgent - 紧急：需要优先安排生产和资源
        low    - 低：可延后处理的任务

    状态流转（STATUS_CHOICES）：
        pending(待派工) → dispatched(已派工) → in_progress(生产中) → completed(已完成) → closed(已关闭)
    """

    # 优先级选项
    PRIORITY_CHOICES = [
        ('normal', '普通'),
        ('urgent', '紧急'),
        ('low', '低'),
    ]

    # 工单状态选项
    STATUS_CHOICES = [
        ('pending', '待派工'),      # 工单已创建，等待分配给车间/班组
        ('dispatched', '已派工'),    # 工单已派发给车间，等待开工
        ('in_progress', '生产中'),   # 工单正在生产执行中
        ('completed', '已完成'),     # 工单生产任务已完成
        ('closed', '已关闭'),        # 工单已关闭归档
    ]

    # 工单唯一编号
    wo_no = models.CharField('工单号', max_length=32, unique=True)
    # 关联的生产计划，手动创建的工单可为空
    production_plan = models.ForeignKey(
        'prod_plan.ProductionPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name='生产计划'
    )
    # 需要生产的产品物料
    product = models.ForeignKey(
        'base_data.Material',
        on_delete=models.PROTECT,
        related_name='work_orders',
        verbose_name='产品'
    )
    # 工单要求生产的产品数量
    order_quantity = models.IntegerField('订单数量')
    # 已完工的合格产品数量
    completed_quantity = models.IntegerField('完成数量', default=0)
    # 生产过程中产生的不良品数量
    defect_quantity = models.IntegerField('不良数量', default=0)
    # 执行该工单的车间
    workshop = models.ForeignKey(
        'accounts.Workshop',
        on_delete=models.PROTECT,
        related_name='work_orders',
        verbose_name='车间'
    )
    # 该工单使用的工艺路线，决定生产工序流程
    route = models.ForeignKey(
        'base_data.Route',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        verbose_name='工艺路线'
    )
    # 工单优先级
    priority = models.CharField('优先级', max_length=8, choices=PRIORITY_CHOICES, default='normal')
    # 工单当前状态
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='pending')
    # 工单实际开始生产的时间
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    # 工单实际完成的时间
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    # 创建该工单的用户
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='work_orders_created',
        verbose_name='创建人'
    )
    # 工单创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 工单最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'work_order'  # 数据库表名
        verbose_name = '工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']  # 按创建时间倒序，最新工单在前

    def __str__(self):
        """返回工单号和当前状态"""
        return f'{self.wo_no} ({self.get_status_display()})'
