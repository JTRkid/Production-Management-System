"""库存管理模块 — Warehouse / Inventory / InventoryTransaction 模型

管理仓库、库存和出入库流水。
Warehouse 定义仓库基本信息；Inventory 记录每个仓库中每种物料的库存数量；
InventoryTransaction 记录所有出入库操作的流水明细。
"""

from django.db import models


class Warehouse(models.Model):
    """仓库模型，定义系统中的仓库信息。

    仓库类型说明（WAREHOUSE_TYPE_CHOICES）：
        raw      - 原料仓：存放采购入库的原材料
        finished - 成品仓：存放完工待发货的成品
        spare    - 备件仓：存放设备维修备件和辅助材料
    """

    # 仓库类型选项
    WAREHOUSE_TYPE_CHOICES = [
        ('raw', '原料仓'),
        ('finished', '成品仓'),
        ('spare', '备件仓'),
    ]

    # 仓库名称，如"1号原料仓"、"成品仓库"
    name = models.CharField('仓库名称', max_length=64)
    # 仓库唯一编码
    code = models.CharField('仓库编码', max_length=16, unique=True)
    # 仓库类型：原料仓/成品仓/备件仓
    warehouse_type = models.CharField('仓库类型', max_length=16, choices=WAREHOUSE_TYPE_CHOICES, default='raw')
    # 负责该仓库的仓管员，删除用户时置空
    keeper = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='warehouses',
        verbose_name='仓管员'
    )
    # 是否启用该仓库
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        db_table = 'inv_warehouse'  # 数据库表名
        verbose_name = '仓库'
        verbose_name_plural = verbose_name

    def __str__(self):
        """返回仓库编码和名称"""
        return f'{self.code} - {self.name}'


class Inventory(models.Model):
    """库存模型，记录每种物料在每个仓库的库存数量。

    同一物料在同一仓库不同库位的库存分开记录。
    locked_quantity 表示已被订单锁定、不可再分配的数量。
    """

    # 库存对应的物料
    material = models.ForeignKey(
        'base_data.Material',
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name='物料'
    )
    # 库存所在的仓库
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name='仓库'
    )
    # 仓库内的具体库位编码，如"A-01-03"
    location = models.CharField('库位', max_length=64, blank=True, default='')
    # 当前可用库存数量
    quantity = models.DecimalField('库存数量', max_digits=12, decimal_places=4, default=0)
    # 已被订单/工单锁定的数量，不可用于其他分配
    locked_quantity = models.DecimalField('锁定数量', max_digits=12, decimal_places=4, default=0)
    # 最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'inv_inventory'  # 数据库表名
        verbose_name = '库存'
        verbose_name_plural = verbose_name
        unique_together = [('material', 'warehouse', 'location')]  # 同一物料在同一仓库同一库位只能有一条记录
        ordering = ['material', 'warehouse', 'location']  # 按物料、仓库、库位排序

    def __str__(self):
        """返回物料@仓库[库位]:数量 格式"""
        return f'{self.material} @ {self.warehouse.name} [{self.location or "-"}] : {self.quantity}'


class InventoryTransaction(models.Model):
    """库存流水模型，记录每一次出入库操作的明细。

    交易类型说明（TRANSACTION_TYPE_CHOICES）：
        purchase_in  - 采购入库：原材料采购到货入库
        produce_in   - 生产入库：半成品/成品生产完工入库
        material_out - 原料出库：原材料领料出库投入生产
        sale_out     - 销售出库：成品发货出库给客户
        return_in    - 退货入库：客户退货或生产退料入库
        other        - 其他：盘点调整、损耗等其他出入库
    """

    # 交易类型选项
    TRANSACTION_TYPE_CHOICES = [
        ('purchase_in', '采购入库'),
        ('produce_in', '生产入库'),
        ('material_out', '原料出库'),
        ('sale_out', '销售出库'),
        ('return_in', '退货入库'),
        ('other', '其他'),
    ]

    # 流水唯一编号
    transaction_no = models.CharField('流水号', max_length=32, unique=True)
    # 交易类型：入库或出库的具体类型
    transaction_type = models.CharField('交易类型', max_length=16, choices=TRANSACTION_TYPE_CHOICES)
    # 涉及的物料
    material = models.ForeignKey(
        'base_data.Material',
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='物料'
    )
    # 交易数量，正数表示入库，负数表示出库
    quantity = models.DecimalField('数量', max_digits=12, decimal_places=4)
    # 涉及的仓库
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='仓库'
    )
    # 来源单据类型，如"purchase_order"、"sales_order"、"work_order"
    source_doc_type = models.CharField('来源单据类型', max_length=32, blank=True, default='')
    # 来源单据的ID，配合 source_doc_type 定位来源单据
    source_doc_id = models.BigIntegerField('来源单据ID', null=True, blank=True)
    # 执行该操作的用户
    operator = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name='操作人'
    )
    # 操作备注说明
    remark = models.CharField('备注', max_length=256, blank=True, default='')
    # 流水创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'inv_transaction'  # 数据库表名
        verbose_name = '库存流水'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']  # 按创建时间倒序，最新流水在前

    def __str__(self):
        """返回流水号-交易类型(数量)格式"""
        return f'{self.transaction_no} - {self.get_transaction_type_display()} ({self.quantity})'
