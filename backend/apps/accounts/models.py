"""系统管理 — User 模型（生产管理系统角色体系）

包含用户（User）、车间（Workshop）、操作日志（OperationLog）三个核心模型。
User 继承自 AbstractUser，扩展了角色、手机号等字段，用于系统权限控制和操作审计。
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型，扩展 Django 内置用户，支持生产管理系统多角色权限。

    ROLE_CHOICES 说明：
        admin            - 系统管理员：拥有所有模块的最高权限
        planner          - 生产计划员：负责编制和管理生产计划
        workshop_director - 车间主任：管理车间日常生产事务
        foreman          - 班组长：管理班组工人、分配工单任务
        worker           - 工人：执行工单、报工操作
        inspector        - 质检员：执行质量检验、录入检验结果
        storekeeper      - 库管员：管理仓库出入库操作
        salesman         - 业务员：管理客户和销售订单
        purchaser        - 采购员：管理供应商和采购订单
    """

    # 角色选项，用于区分系统中不同岗位用户的权限范围
    ROLE_CHOICES = [
        ('admin', '系统管理员'),
        ('planner', '生产计划员'),
        ('workshop_director', '车间主任'),
        ('foreman', '班组长'),
        ('worker', '工人'),
        ('inspector', '质检员'),
        ('storekeeper', '库管员'),
        ('salesman', '业务员'),
        ('purchaser', '采购员'),
    ]

    # 用户真实姓名
    name = models.CharField('姓名', max_length=64)
    # 用户所属角色，决定其在系统中的操作权限
    role = models.CharField('角色', max_length=32, choices=ROLE_CHOICES, default='worker')
    # 用户手机号码，用于联系和通知
    phone = models.CharField('手机号', max_length=16, blank=True, default='')
    # 是否启用该用户账号，设为 False 可禁用用户登录
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        db_table = 'sys_user'  # 数据库表名
        verbose_name = '用户'

    def __str__(self):
        """返回 用户名(角色) 格式的字符串表示"""
        return f'{self.username} ({self.get_role_display()})'


class Workshop(models.Model):
    """车间模型，表示生产管理中的基本组织单元。

    每个车间可包含多个工作中心（WorkCenter），由一名负责人（车间主任）管理。
    """

    # 车间的显示名称，如"一车间"、"喷涂车间"
    name = models.CharField('车间名称', max_length=64)
    # 车间的唯一编码，用于系统内部标识
    code = models.CharField('车间编码', max_length=16, unique=True)
    # 车间负责人，关联到用户表；删除用户时置空
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='managed_workshops', verbose_name='负责人')
    # 是否启用该车间，设为 False 表示停用
    is_active = models.BooleanField('启用', default=True)
    # 记录创建时间，自动填充
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_workshop'  # 数据库表名
        verbose_name = '车间'

    def __str__(self):
        """返回车间编码和名称"""
        return f'{self.code} {self.name}'


class OperationLog(models.Model):
    """操作日志模型，记录用户在系统中的关键操作行为。

    用于安全审计和操作追溯，记录谁在什么时间做了什么操作。
    """

    # 操作类型选项，描述用户执行的操作分类
    ACTION_CHOICES = [
        ('login', '登录'),      # 用户登录系统
        ('create', '创建'),      # 新建数据记录
        ('update', '修改'),      # 修改已有数据
        ('delete', '删除'),      # 删除数据记录
        ('approve', '审批'),     # 审批流程操作
        ('export', '导出'),      # 导出数据/报表
    ]

    # 执行操作的用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作人')
    # 操作类型，取自 ACTION_CHOICES
    action = models.CharField('操作类型', max_length=16, choices=ACTION_CHOICES)
    # 操作对象的描述，如模型名称或具体记录标识
    target = models.CharField('操作对象', max_length=128)
    # 操作的详细描述信息
    detail = models.TextField('详情', blank=True, default='')
    # 操作者发起请求时的 IP 地址
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    # 操作发生的时间，自动填充
    created_at = models.DateTimeField('操作时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_operation_log'  # 数据库表名
        verbose_name = '操作日志'
        ordering = ['-created_at']  # 按操作时间倒序排列，最新的日志在前
