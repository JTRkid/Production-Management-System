"""生产计划模块 — ProductionPlan 模型

管理生产计划的编制、审批和下发流程。
生产计划是连接销售订单和生产工单的桥梁，将客户需求转化为可执行的生产任务。
"""

from django.db import models


class ProductionPlan(models.Model):
    """生产计划模型，记录产品的计划生产安排。

    计划类型说明（PLAN_TYPE_CHOICES）：
        month - 月计划：按月度编制的常规生产计划
        week  - 周计划：按周度编制的详细排产计划
        urgent - 急单：紧急插单，优先安排生产

    状态流转（STATUS_CHOICES）：
        draft(草稿) → approved(已审批) → released(已下发) → completed(已完成)
                                                         → cancelled(已取消)
    """

    # 计划类型选项
    PLAN_TYPE_CHOICES = [
        ('month', '月计划'),
        ('week', '周计划'),
        ('urgent', '急单'),
    ]

    # 计划状态选项
    STATUS_CHOICES = [
        ('draft', '草稿'),       # 计划刚创建，尚未审批
        ('approved', '已审批'),   # 计划已通过审批
        ('released', '已下发'),   # 计划已下发到车间执行
        ('completed', '已完成'),  # 计划对应的生产任务全部完成
        ('cancelled', '已取消'),  # 计划被取消
    ]

    # 生产计划唯一编号
    plan_no = models.CharField('计划编号', max_length=32, unique=True)
    # 计划类型：月计划/周计划/急单
    plan_type = models.CharField('计划类型', max_length=16, choices=PLAN_TYPE_CHOICES)
    # 计划生产的产品物料
    product = models.ForeignKey(
        'base_data.Material',
        on_delete=models.PROTECT,
        related_name='production_plans',
        verbose_name='产品'
    )
    # 计划生产的产品数量
    plan_quantity = models.IntegerField('计划数量')
    # 当前计划状态
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='draft')
    # 计划生产的开始日期
    scheduled_start = models.DateField('计划开始日期')
    # 计划生产的结束日期
    scheduled_end = models.DateField('计划结束日期')
    # 审批该计划的用户，未审批时为空
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_plans',
        verbose_name='审批人'
    )
    # 审批时间
    approved_at = models.DateTimeField('审批时间', null=True, blank=True)
    # 创建该计划的用户
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='created_plans',
        verbose_name='创建人'
    )
    # 计划创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 计划最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'prod_plan'  # 数据库表名
        verbose_name = '生产计划'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']  # 按创建时间倒序，最新计划在前

    def __str__(self):
        """返回计划编号和计划类型"""
        return f'{self.plan_no} - {self.get_plan_type_display()}'
