"""业务管理 — Customer, SalesOrder, Supplier, PurchaseOrder

包含客户（Customer）、销售订单（SalesOrder）、供应商（Supplier）、采购订单（PurchaseOrder）四个核心业务模型。
管理企业与客户、供应商之间的销售和采购业务流程。
"""

from django.db import models


class Customer(models.Model):
    """客户模型，存储客户基本信息和联系方式。

    客户等级分为 A/B/C 三级，用于区分客户重要程度。
    """

    # 客户等级选项：A级为重要客户，B级为一般客户，C级为普通客户
    CUSTOMER_LEVEL_CHOICES = [
        ('A', 'A级'),
        ('B', 'B级'),
        ('C', 'C级'),
    ]

    # 客户唯一编码，用于系统内部标识
    customer_code = models.CharField('客户编码', max_length=64, unique=True)
    # 客户公司或个人名称
    customer_name = models.CharField('客户名称', max_length=128)
    # 客户方联系人姓名
    contact_person = models.CharField('联系人', max_length=64, blank=True, default='')
    # 联系人电话号码
    contact_phone = models.CharField('联系电话', max_length=32, blank=True, default='')
    # 客户地址
    address = models.CharField('地址', max_length=256, blank=True, default='')
    # 客户等级，影响业务优先级和服务策略
    customer_level = models.CharField('客户等级', max_length=1, choices=CUSTOMER_LEVEL_CHOICES, default='C')
    # 是否启用该客户记录
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间，自动填充
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 最后更新时间，自动更新
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'biz_customer'  # 数据库表名
        verbose_name = '客户'
        verbose_name_plural = '客户'

    def __str__(self):
        """返回客户编码和名称"""
        return f'{self.customer_code} {self.customer_name}'


class SalesOrder(models.Model):
    """销售订单模型，记录客户下单信息和订单生命周期。

    状态流转：
        draft(草稿) → approved(已审批) → in_production(生产中) → shipped(已发货) → completed(已完成)
                                                                                   → cancelled(已取消)
    """

    # 销售订单状态选项
    STATUS_CHOICES = [
        ('draft', '草稿'),           # 订单刚创建，尚未提交审批
        ('approved', '已审批'),       # 订单已通过审批，等待安排生产
        ('in_production', '生产中'),  # 订单已排产，正在生产
        ('shipped', '已发货'),        # 货物已发出给客户
        ('completed', '已完成'),      # 订单全部完成，客户已签收
        ('cancelled', '已取消'),      # 订单被取消
    ]

    # 销售订单唯一编号
    so_no = models.CharField('销售订单号', max_length=64, unique=True)
    # 关联客户，删除客户时需先处理关联订单（PROTECT）
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name='sales_orders', verbose_name='客户')
    # 关联产品物料，删除物料时需先处理关联订单（PROTECT）
    product = models.ForeignKey(
        'base_data.Material', on_delete=models.PROTECT, related_name='sales_orders', verbose_name='产品')
    # 订单要求的产品数量
    order_quantity = models.IntegerField('订单数量')
    # 已发货的产品数量，随发货操作累加
    delivered_quantity = models.IntegerField('已发货数量', default=0)
    # 产品单价（元）
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    # 订单总金额（元），通常为 单价 * 数量
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2)
    # 客户要求的交付日期
    scheduled_date = models.DateField('计划交付日期')
    # 当前订单状态
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='draft')
    # 负责该订单的业务员
    sales_person = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='sales_orders_person', verbose_name='业务员')
    # 审批该订单的用户，未审批时为空
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='sales_orders_approved', verbose_name='审批人')
    # 审批时间
    approved_at = models.DateTimeField('审批时间', null=True, blank=True)
    # 创建该订单的用户
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='sales_orders_created', verbose_name='创建人')
    # 订单创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 订单最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'biz_sales_order'  # 数据库表名
        verbose_name = '销售订单'
        verbose_name_plural = '销售订单'
        ordering = ['-created_at']  # 按创建时间倒序，最新订单在前

    def __str__(self):
        """返回销售订单号"""
        return f'{self.so_no}'


class Supplier(models.Model):
    """供应商模型，存储供应商基本信息。

    用于采购业务，记录可供货的供应商联系方式和供货类别。
    """

    # 供应商唯一编码
    supplier_code = models.CharField('供应商编码', max_length=64, unique=True)
    # 供应商公司名称
    supplier_name = models.CharField('供应商名称', max_length=128)
    # 供应商方联系人
    contact_person = models.CharField('联系人', max_length=64, blank=True, default='')
    # 联系人电话
    contact_phone = models.CharField('联系电话', max_length=32, blank=True, default='')
    # 供应商提供的物料类别，如"钢材"、"电子元器件"
    supply_category = models.CharField('供货类别', max_length=128, blank=True, default='')
    # 是否启用该供应商
    is_active = models.BooleanField('是否启用', default=True)
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'biz_supplier'  # 数据库表名
        verbose_name = '供应商'
        verbose_name_plural = '供应商'

    def __str__(self):
        """返回供应商编码和名称"""
        return f'{self.supplier_code} {self.supplier_name}'


class PurchaseOrder(models.Model):
    """采购订单模型，记录向供应商采购物料的订单信息。

    状态流转：
        draft(草稿) → approved(已审批) → ordered(已下单) → partial_received(部分收货) → received(已收货)
                                                                                       → cancelled(已取消)
    """

    # 采购订单状态选项
    STATUS_CHOICES = [
        ('draft', '草稿'),               # 订单刚创建，尚未审批
        ('approved', '已审批'),           # 订单已审批通过
        ('ordered', '已下单'),            # 已向供应商发出采购订单
        ('partial_received', '部分收货'), # 部分物料已到货入库
        ('received', '已收货'),           # 全部物料已到货入库
        ('cancelled', '已取消'),          # 订单被取消
    ]

    # 采购订单唯一编号
    po_no = models.CharField('采购订单号', max_length=64, unique=True)
    # 关联供应商
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='purchase_orders', verbose_name='供应商')
    # 关联采购的物料
    material = models.ForeignKey(
        'base_data.Material', on_delete=models.PROTECT, related_name='purchase_orders', verbose_name='物料')
    # 采购数量
    order_quantity = models.IntegerField('订单数量')
    # 已收货入库的数量
    received_quantity = models.IntegerField('已收货数量', default=0)
    # 物料采购单价（元）
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    # 采购总金额（元）
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2)
    # 向供应商下单的日期
    ordered_date = models.DateField('下单日期')
    # 预计物料到货日期
    expected_date = models.DateField('预计到货日期')
    # 当前采购订单状态
    status = models.CharField('状态', max_length=16, choices=STATUS_CHOICES, default='draft')
    # 来源单据类型，如关联销售订单自动生成的采购单
    source_doc_type = models.CharField('来源单据类型', max_length=32, null=True, blank=True)
    # 来源单据的ID，配合 source_doc_type 定位来源
    source_doc_id = models.BigIntegerField('来源单据ID', null=True, blank=True)
    # 负责该采购订单的采购员
    buyer = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='purchase_orders', verbose_name='采购员')
    # 审批人
    approved_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='purchase_orders_approved', verbose_name='审批人')
    # 审批时间
    approved_at = models.DateTimeField('审批时间', null=True, blank=True)
    # 创建人
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='purchase_orders_created', verbose_name='创建人')
    # 创建时间
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    # 最后更新时间
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'biz_purchase_order'  # 数据库表名
        verbose_name = '采购订单'
        verbose_name_plural = '采购订单'
        ordering = ['-created_at']  # 按创建时间倒序排列

    def __str__(self):
        """返回采购订单号"""
        return f'{self.po_no}'
