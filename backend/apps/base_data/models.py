"""基础数据管理 — Material, BOMItem, Route, RouteStep, WorkCenter, Equipment

管理生产系统的基础主数据，包括物料主数据、物料清单（BOM）、工艺路线、工作中心和设备。
这些数据是生产计划、工单和库存管理的基础。
"""

from django.db import models


class Material(models.Model):
    """物料主数据模型，存储所有物料（原材料、半成品、成品）的基本信息。

    物料类型说明（MATERIAL_TYPE_CHOICES）：
        raw      - 原材料：直接采购的基础材料，如钢材、塑料粒子
        semi     - 半成品：经过部分加工但尚未完工的中间产品
        finished - 成品：完工的最终产品，可直接销售给客户
    """

    # 物料类型选项
    MATERIAL_TYPE_CHOICES = [
        ('raw', '原材料'),
        ('semi', '半成品'),
        ('finished', '成品'),
    ]

    # 物料唯一编码，系统内标识物料的主键
    material_code = models.CharField('物料编码', max_length=64, unique=True)
    # 物料名称
    material_name = models.CharField('物料名称', max_length=128)
    # 物料的规格型号描述，如"100x50x2mm"
    specification = models.CharField('规格型号', max_length=256, blank=True, default='')
    # 计量单位，如"个"、"kg"、"米"
    unit = models.CharField('计量单位', max_length=16)
    # 物料类型：原材料/半成品/成品
    material_type = models.CharField('物料类型', max_length=16, choices=MATERIAL_TYPE_CHOICES)
    # 物料的单位成本（元），用于成本核算
    unit_cost = models.DecimalField('单位成本', max_digits=10, decimal_places=2, default=0)
    # 是否启用该物料，停用后不再出现在选择列表中
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'base_material'  # 数据库表名
        verbose_name = '物料'
        verbose_name_plural = '物料'

    def __str__(self):
        """返回物料编码和名称"""
        return f'{self.material_code} {self.material_name}'


class BOMItem(models.Model):
    """物料清单（BOM）明细模型，定义父物料由哪些子物料组成及用量。

    BOM 是生产的基础数据，描述产品的物料构成关系。
    例如：成品A = 原材料B x 2个 + 半成品C x 1个
    """

    # 父物料（成品或半成品），由哪些子物料组成
    parent_material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name='bom_children', verbose_name='父物料')
    # 子物料（原材料或半成品），构成父物料的组成部分
    child_material = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name='bom_parents', verbose_name='子物料')
    # 生产一个父物料所需的该子物料数量
    quantity = models.DecimalField('用量', max_digits=10, decimal_places=4)
    # 子物料的计量单位
    unit = models.CharField('单位', max_length=16)
    # 该子物料在第几道工序投入，可为空表示不限定工序
    process_step = models.IntegerField('工序序号', null=True, blank=True)

    class Meta:
        db_table = 'base_bom_item'  # 数据库表名
        verbose_name = 'BOM明细'
        verbose_name_plural = 'BOM明细'

    def __str__(self):
        """返回 父物料 -> 子物料 x数量 的格式"""
        return f'{self.parent_material} -> {self.child_material} x{self.quantity}'


class WorkCenter(models.Model):
    """工作中心模型，表示车间内执行特定生产任务的生产单元。

    一个车间可包含多个工作中心，每个工作中心有独立的日产能。
    工作中心是工艺路线中工序的执行场所。
    """

    # 工作中心名称，如"冲压线1号"、"CNC加工区"
    name = models.CharField('工作中心名称', max_length=128)
    # 工作中心唯一编码
    code = models.CharField('工作中心编码', max_length=32, unique=True)
    # 所属车间，删除车间时保护（PROTECT），防止误删
    workshop = models.ForeignKey(
        'accounts.Workshop', on_delete=models.PROTECT, related_name='work_centers', verbose_name='所属车间')
    # 每天的标准生产能力（件/天）
    capacity_per_day = models.IntegerField('日产能', default=0)
    # 是否启用该工作中心
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        db_table = 'base_work_center'  # 数据库表名
        verbose_name = '工作中心'
        verbose_name_plural = '工作中心'

    def __str__(self):
        """返回工作中心编码和名称"""
        return f'{self.code} {self.name}'


class Route(models.Model):
    """工艺路线模型，定义产品从原材料到成品的加工路径。

    一条工艺路线包含多个工序步骤（RouteStep），按顺序排列。
    一个产品可以有多条工艺路线，但同一时间只有一条启用。
    """

    # 该工艺路线对应的成品物料
    product = models.ForeignKey(
        Material, on_delete=models.CASCADE, related_name='routes', verbose_name='产品')
    # 工艺路线名称，如"标准工艺"、"快速工艺"
    route_name = models.CharField('工艺路线名称', max_length=128)
    # 是否启用该工艺路线
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'base_route'  # 数据库表名
        verbose_name = '工艺路线'
        verbose_name_plural = '工艺路线'

    def __str__(self):
        """返回工艺路线名称和关联产品"""
        return f'{self.route_name} ({self.product})'


class RouteStep(models.Model):
    """工艺路线工序模型，定义工艺路线中的每一道具体工序。

    工序按 step_no 排序执行，每道工序指定在哪个工作中心完成，以及标准工时。
    """

    # 所属的工艺路线
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name='steps', verbose_name='工艺路线')
    # 工序序号，决定工序在工艺路线中的执行顺序
    step_no = models.IntegerField('工序序号')
    # 工序名称，如"下料"、"焊接"、"组装"
    step_name = models.CharField('工序名称', max_length=128)
    # 执行该工序的工作中心
    work_center = models.ForeignKey(
        WorkCenter, on_delete=models.PROTECT, related_name='route_steps', verbose_name='工作中心')
    # 完成该工序的标准工时（小时），用于产能计算和排产
    standard_hours = models.DecimalField(
        '标准工时(小时)', max_digits=5, decimal_places=2, null=True, blank=True)
    # 工序的详细说明，如操作要求、注意事项
    description = models.TextField('工序说明', blank=True, default='')

    class Meta:
        db_table = 'base_route_step'  # 数据库表名
        verbose_name = '工艺路线工序'
        verbose_name_plural = '工艺路线工序'
        ordering = ['route', 'step_no']  # 按工艺路线和工序序号排序

    def __str__(self):
        """返回工艺路线名称和工序信息"""
        return f'{self.route.route_name} - 工序{self.step_no}: {self.step_name}'


class Equipment(models.Model):
    """设备模型，记录生产设备的基本信息和状态。

    设备状态说明（STATUS_CHOICES）：
        normal      - 正常：设备可正常使用
        maintenance - 维修中：设备正在维修保养，暂不可用
        scrapped    - 已报废：设备已报废，不再使用
    """

    # 设备状态选项
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('maintenance', '维修中'),
        ('scrapped', '已报废'),
    ]

    # 设备名称，如"数控车床C6140"
    name = models.CharField('设备名称', max_length=128)
    # 设备唯一编码，贴在设备上的标识码
    code = models.CharField('设备编码', max_length=32, unique=True)
    # 设备型号规格
    model = models.CharField('设备型号', max_length=128, blank=True, default='')
    # 设备所属的工作中心，删除工作中心时置空
    work_center = models.ForeignKey(
        WorkCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipments', verbose_name='所属工作中心')
    # 设备当前状态
    status = models.CharField('设备状态', max_length=16, choices=STATUS_CHOICES, default='normal')
    # 设备购置日期，用于计算折旧和使用寿命
    purchase_date = models.DateField('购置日期', null=True, blank=True)

    class Meta:
        db_table = 'base_equipment'  # 数据库表名
        verbose_name = '设备'
        verbose_name_plural = '设备'

    def __str__(self):
        """返回设备编码和名称"""
        return f'{self.code} {self.name}'
