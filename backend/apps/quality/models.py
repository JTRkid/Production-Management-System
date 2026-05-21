"""质量管理模块 — InspectionStandard / InspectionRecord 模型

管理产品质量检验标准和检验记录。
InspectionStandard 定义每个产品的检验项目和合格标准；
InspectionRecord 记录每次检验的实际执行结果。
"""

from django.db import models


class InspectionStandard(models.Model):
    """检验标准模型，定义产品的质量检验项目和判定标准。

    每个产品可以有多个检验项目（如尺寸、外观、性能），每个项目有对应的标准和公差。
    """

    # 关联的产品物料
    product = models.ForeignKey(
        'base_data.Material',
        on_delete=models.CASCADE,
        related_name='inspection_standards',
        verbose_name='产品'
    )
    # 检验项目名称，如"外径尺寸"、"表面粗糙度"
    item_name = models.CharField('检验项目', max_length=64)
    # 检验标准的详细描述，说明合格条件
    standard_desc = models.TextField('标准描述')
    # 允许的公差范围，如"+/-0.5mm"、"±1%"
    tolerance = models.CharField('公差范围', max_length=128, blank=True, default='')
    # 是否启用该检验标准
    is_active = models.BooleanField('启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'qc_standard'  # 数据库表名
        verbose_name = '检验标准'
        verbose_name_plural = verbose_name
        ordering = ['product', 'item_name']  # 按产品和检验项目排序

    def __str__(self):
        """返回产品和检验项目名称"""
        return f'{self.product} - {self.item_name}'


class InspectionRecord(models.Model):
    """检验记录模型，记录每次质量检验的执行结果。

    检验类型说明（INSPECTION_TYPE_CHOICES）：
        in_process - 过程检：生产过程中的中间检验
        final      - 终检：产品完工后的最终检验

    检验结果说明（RESULT_CHOICES）：
        pass       - 合格：检验通过
        fail       - 不合格：检验未通过，需返工或报废
        concession - 让步接收：虽不完全达标但可接受使用
    """

    # 检验类型选项
    INSPECTION_TYPE_CHOICES = [
        ('in_process', '过程检'),
        ('final', '终检'),
    ]

    # 检验结果选项
    RESULT_CHOICES = [
        ('pass', '合格'),
        ('fail', '不合格'),
        ('concession', '让步接收'),
    ]

    # 关联的生产工单，删除工单时置空
    work_order = models.ForeignKey(
        'work_order.WorkOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inspections',
        verbose_name='工单'
    )
    # 检验类型：过程检或终检
    inspection_type = models.CharField('检验类型', max_length=16, choices=INSPECTION_TYPE_CHOICES)
    # 被检验的产品物料
    product = models.ForeignKey(
        'base_data.Material',
        on_delete=models.PROTECT,
        related_name='inspections',
        verbose_name='产品'
    )
    # 执行检验的质检员
    inspector = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='inspections',
        verbose_name='检验员'
    )
    # 抽样检验的数量
    sample_quantity = models.IntegerField('抽检数量')
    # 合格的产品数量
    pass_quantity = models.IntegerField('合格数量')
    # 不良品数量
    defect_quantity = models.IntegerField('不良数量', default=0)
    # 不良明细，JSON 格式存储各类缺陷的数量
    defect_details = models.JSONField(
        '不良明细',
        null=True,
        blank=True,
        help_text='格式: [{"defect_type": "缺陷类型", "count": 数量}]'
    )
    # 最终检验结果
    result = models.CharField('检验结果', max_length=16, choices=RESULT_CHOICES)
    # 检验报告唯一编号
    report_no = models.CharField('报告编号', max_length=32)
    # 检验执行时间，自动填充
    inspected_at = models.DateTimeField('检验时间', auto_now_add=True)

    class Meta:
        db_table = 'qc_record'  # 数据库表名
        verbose_name = '检验记录'
        verbose_name_plural = verbose_name
        ordering = ['-inspected_at']  # 按检验时间倒序，最新记录在前

    def __str__(self):
        """返回报告编号和检验结果"""
        return f'{self.report_no} ({self.get_result_display()})'
