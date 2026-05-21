"""业务管理序列化器 — Customer, SalesOrder, Supplier, PurchaseOrder"""

from rest_framework import serializers
from django.utils import timezone
from .models import Customer, SalesOrder, Supplier, PurchaseOrder


class CustomerSerializer(serializers.ModelSerializer):
    """客户信息序列化器"""

    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SalesOrderSerializer(serializers.ModelSerializer):
    """销售订单序列化器（详情/列表），包含关联名称的只读字段"""

    # 关联字段：自动获取客户名称、产品名称、销售员姓名、创建人姓名
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    product_name = serializers.CharField(source='product.material_name', read_only=True)
    sales_person_name = serializers.CharField(source='sales_person.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = SalesOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    """销售订单创建序列化器 — so_no/total_amount/created_by 由后端自动生成"""

    class Meta:
        model = SalesOrder
        fields = [
            'customer', 'product', 'order_quantity',
            'unit_price', 'scheduled_date', 'sales_person',
        ]

    def create(self, validated_data):
        # 自动生成订单号
        last = SalesOrder.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        validated_data['so_no'] = f'SO{seq:06d}'
        # 自动计算总金额
        validated_data['total_amount'] = validated_data['order_quantity'] * validated_data['unit_price']
        return super().create(validated_data)


class SupplierSerializer(serializers.ModelSerializer):
    """供应商信息序列化器"""

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """采购订单序列化器（详情/列表），包含关联名称的只读字段"""

    # 关联字段：自动获取供应商名称、物料名称、采购员姓名、创建人姓名
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """采购订单创建序列化器 — po_no/total_amount/created_by 由后端自动生成"""

    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'material', 'order_quantity',
            'unit_price', 'expected_date', 'buyer',
        ]

    def create(self, validated_data):
        # 自动生成采购单号（PO + 6位序号）
        last = PurchaseOrder.objects.order_by('-id').first()
        seq = (last.id + 1) if last else 1
        validated_data['po_no'] = f'PO{seq:06d}'
        # 自动计算总金额 = 数量 * 单价
        validated_data['total_amount'] = validated_data['order_quantity'] * validated_data['unit_price']
        # 自动设置下单日期为当前日期
        validated_data['ordered_date'] = timezone.now().date()
        return super().create(validated_data)
