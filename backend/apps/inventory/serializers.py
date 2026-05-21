"""库存管理模块 — 序列化器"""

from rest_framework import serializers

from .models import Warehouse, Inventory, InventoryTransaction


class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器：包含仓库管理员姓名"""

    # 关联字段：自动获取仓库管理员姓名，允许为空
    keeper_name = serializers.CharField(source='keeper.name', read_only=True, allow_null=True)

    class Meta:
        model = Warehouse
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器：包含物料编码、物料名称、仓库名称"""

    # 关联字段：自动获取物料编码、物料名称、仓库名称
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    material_code = serializers.CharField(source='material.material_code', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = Inventory
        fields = '__all__'


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """库存流水序列化器：包含物料名称、仓库名称、操作人姓名"""

    # 关联字段：自动获取物料名称、仓库名称、操作人姓名
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    operator_name = serializers.CharField(source='operator.name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = '__all__'
        read_only_fields = ['created_at']
