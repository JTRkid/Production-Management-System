"""种子数据 — 生产管理系统演示数据"""

import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teach_platform.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import random
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import date, datetime, timedelta

from apps.accounts.models import User, Workshop
from apps.base_data.models import Material, BOMItem, WorkCenter, Route, RouteStep, Equipment
from apps.business.models import Customer, SalesOrder, Supplier, PurchaseOrder
from apps.prod_plan.models import ProductionPlan
from apps.work_order.models import WorkOrder
from apps.prod_track.models import WorkReport
from apps.quality.models import InspectionStandard, InspectionRecord
from apps.inventory.models import Warehouse, Inventory, InventoryTransaction


def seed():
    print("开始填充种子数据...")

    # ── 1. 用户 ──
    admin = User.objects.get_or_create(username='admin', defaults={
        'name': '系统管理员', 'role': 'admin', 'password': make_password('123456'), 'is_superuser': True, 'is_staff': True,
    })[0]
    planner = User.objects.get_or_create(username='planner01', defaults={
        'name': '张计划', 'role': 'planner', 'password': make_password('123456'),
    })[0]
    director = User.objects.get_or_create(username='director01', defaults={
        'name': '李主任', 'role': 'workshop_director', 'password': make_password('123456'),
    })[0]
    foreman = User.objects.get_or_create(username='foreman01', defaults={
        'name': '王班长', 'role': 'foreman', 'password': make_password('123456'),
    })[0]
    worker = User.objects.get_or_create(username='worker01', defaults={
        'name': '赵工人', 'role': 'worker', 'password': make_password('123456'),
    })[0]
    inspector = User.objects.get_or_create(username='inspector01', defaults={
        'name': '陈质检', 'role': 'inspector', 'password': make_password('123456'),
    })[0]
    storekeeper = User.objects.get_or_create(username='storekeeper01', defaults={
        'name': '钱库管', 'role': 'storekeeper', 'password': make_password('123456'),
    })[0]
    salesman = User.objects.get_or_create(username='salesman01', defaults={
        'name': '孙销售', 'role': 'salesman', 'password': make_password('123456'),
    })[0]
    purchaser = User.objects.get_or_create(username='purchaser01', defaults={
        'name': '周采购', 'role': 'purchaser', 'password': make_password('123456'),
    })[0]

    # ── 2. 车间 ──
    ws1 = Workshop.objects.get_or_create(name='一车间（装配）', code='WS01', defaults={'manager': director})[0]
    ws2 = Workshop.objects.get_or_create(name='二车间（机加工）', code='WS02', defaults={'manager': director})[0]

    # ── 3. 物料 ──
    m_raw_1 = Material.objects.get_or_create(material_code='RAW001', defaults={
        'material_name': '钢板 Q235', 'specification': '2.0mm×1250mm', 'unit': 'kg', 'material_type': 'raw', 'unit_cost': 5.50,
    })[0]
    m_raw_2 = Material.objects.get_or_create(material_code='RAW002', defaults={
        'material_name': '电机 220V', 'specification': '1.5kW', 'unit': '台', 'material_type': 'raw', 'unit_cost': 320,
    })[0]
    m_semi = Material.objects.get_or_create(material_code='SEMI001', defaults={
        'material_name': '机壳组件', 'specification': '定制', 'unit': '套', 'material_type': 'semi', 'unit_cost': 80,
    })[0]
    m_finished = Material.objects.get_or_create(material_code='FIN001', defaults={
        'material_name': '小型搅拌机', 'specification': 'JB-200', 'unit': '台', 'material_type': 'finished', 'unit_cost': 650,
    })[0]

    # ── 4. BOM ──
    BOMItem.objects.get_or_create(parent_material=m_finished, child_material=m_semi, defaults={'quantity': 1, 'unit': '套'})
    BOMItem.objects.get_or_create(parent_material=m_finished, child_material=m_raw_2, defaults={'quantity': 1, 'unit': '台'})
    BOMItem.objects.get_or_create(parent_material=m_semi, child_material=m_raw_1, defaults={'quantity': 15, 'unit': 'kg'})

    # ── 5. 工作中心 ──
    wc1 = WorkCenter.objects.get_or_create(name='装配线', code='WC01', defaults={'workshop': ws1, 'capacity_per_day': 50})[0]
    wc2 = WorkCenter.objects.get_or_create(name='机加工中心', code='WC02', defaults={'workshop': ws2, 'capacity_per_day': 200})[0]

    # ── 6. 设备 ──
    Equipment.objects.get_or_create(code='EQ001', defaults={'name': '数控冲床', 'model': 'AMADA-255', 'work_center': wc2})
    Equipment.objects.get_or_create(code='EQ002', defaults={'name': '装配流水线', 'model': 'ZX-100', 'work_center': wc1})

    # ── 7. 工艺路线 ──
    route = Route.objects.get_or_create(product=m_finished, defaults={'route_name': '搅拌机标准工艺'})[0]
    RouteStep.objects.get_or_create(route=route, step_no=10, defaults={'step_name': '机加工', 'work_center': wc2, 'standard_hours': 2})
    RouteStep.objects.get_or_create(route=route, step_no=20, defaults={'step_name': '装配', 'work_center': wc1, 'standard_hours': 1.5})
    RouteStep.objects.get_or_create(route=route, step_no=30, defaults={'step_name': '测试', 'work_center': wc1, 'standard_hours': 0.5})

    # ── 8. 客户与供应商 ──
    customer = Customer.objects.get_or_create(customer_code='C001', defaults={
        'customer_name': '北方机械有限公司', 'contact_person': '刘经理', 'contact_phone': '13800001111',
    })[0]
    supplier = Supplier.objects.get_or_create(supplier_code='S001', defaults={
        'supplier_name': '通达钢材供应商', 'contact_person': '黄经理', 'supply_category': '钢材',
    })[0]
    supplier2 = Supplier.objects.get_or_create(supplier_code='S002', defaults={
        'supplier_name': '精工电机厂', 'contact_person': '吴经理', 'supply_category': '电机',
    })[0]

    # ── 9. 销售订单 ──
    SalesOrder.objects.get_or_create(so_no='SO202605001', defaults={
        'customer': customer, 'product': m_finished, 'order_quantity': 100, 'unit_price': 1200,
        'total_amount': 120000, 'scheduled_date': date(2026, 6, 15),
        'status': 'approved', 'sales_person': salesman, 'created_by': salesman,
    })

    # ── 10. 采购订单 ──
    PurchaseOrder.objects.get_or_create(po_no='PO202605001', defaults={
        'supplier': supplier, 'material': m_raw_1, 'order_quantity': 2000, 'unit_price': 5.2,
        'total_amount': 10400, 'ordered_date': date.today(), 'expected_date': date.today() + timedelta(days=15),
        'status': 'ordered', 'buyer': purchaser, 'created_by': purchaser,
    })

    # ── 11. 生产计划 ──
    plan = ProductionPlan.objects.get_or_create(plan_no='PL202605001', defaults={
        'plan_type': 'month', 'product': m_finished, 'plan_quantity': 100,
        'scheduled_start': date(2026, 5, 20), 'scheduled_end': date(2026, 6, 15),
        'status': 'approved', 'created_by': planner, 'approved_by': admin, 'approved_at': date.today(),
    })[0]

    # ── 12. 生产工单 ──
    WorkOrder.objects.get_or_create(wo_no='WO202605001', defaults={
        'production_plan': plan, 'product': m_finished, 'order_quantity': 50,
        'workshop': ws1, 'route': route, 'status': 'in_progress', 'created_by': planner,
    })
    WorkOrder.objects.get_or_create(wo_no='WO202605002', defaults={
        'production_plan': plan, 'product': m_finished, 'order_quantity': 50,
        'workshop': ws1, 'route': route, 'status': 'pending', 'created_by': planner,
    })

    # ── 13. 测试报表数据：仓库 ──
    wh_raw = Warehouse.objects.get_or_create(name='原料仓', code='WH01', defaults={'warehouse_type': 'raw', 'keeper': storekeeper})[0]
    wh_finished = Warehouse.objects.get_or_create(name='成品仓', code='WH02', defaults={'warehouse_type': 'finished', 'keeper': storekeeper})[0]

    # ── 14. 测试报表数据：更多工单 + 报工 + 检验 ──
    route_steps = list(RouteStep.objects.filter(route=route).order_by('step_no'))
    workers = [worker, foreman]

    # 过去 30 天生成数据
    for day_offset in range(30, -1, -1):
        d = date.today() - timedelta(days=day_offset)
        # 每天 1~3 个工单完成
        for i in range(random.randint(1, 3)):
            qty = random.randint(20, 60)
            done_qty = random.randint(qty - 5, qty)  # 有一些差数
            defect_qty = random.randint(0, min(3, done_qty // 10))
            wo_no = f'WO{d.strftime("%y%m%d")}{i+1:02d}'
            wo, created = WorkOrder.objects.get_or_create(wo_no=wo_no, defaults={
                'production_plan': plan, 'product': m_finished, 'order_quantity': qty,
                'workshop': ws1, 'route': route, 'priority': 'normal',
                'status': 'completed', 'completed_quantity': done_qty,
                'defect_quantity': defect_qty,
                'created_by': planner,
                'completed_at': timezone.make_aware(datetime.combine(d, datetime.min.time()) + timedelta(hours=16)),
            })
            if created:
                # 报工记录
                for step in route_steps:
                    WorkReport.objects.create(
                        work_order=wo, route_step=step, worker=random.choice(workers),
                        report_quantity=done_qty // len(route_steps),
                        defect_quantity=defect_qty // len(route_steps),
                        work_hours=float(step.standard_hours or 1.5) * random.uniform(0.8, 1.2),
                        report_time=timezone.make_aware(datetime.combine(d, datetime.min.time()) + timedelta(hours=10+step.step_no)),
                    )
                # 检验记录
                InspectionRecord.objects.create(
                    work_order=wo, inspection_type='final', product=m_finished,
                    inspector=inspector, sample_quantity=min(10, done_qty),
                    pass_quantity=done_qty - defect_qty, defect_quantity=defect_qty,
                    defect_details=[{'defect_type': '外观划痕', 'count': defect_qty}] if defect_qty else None,
                    result='pass' if defect_qty < 2 else 'concession',
                    report_no=f'QC{d.strftime("%y%m%d")}{i+1:02d}',
                    inspected_at=timezone.make_aware(datetime.combine(d, datetime.min.time()) + timedelta(hours=17)),
                )

    # ── 15. 检验标准 ──
    InspectionStandard.objects.get_or_create(product=m_finished, item_name='外观检查', defaults={
        'standard_desc': '表面无划痕、无锈蚀、涂层均匀', 'tolerance': '允许≤2处轻微划痕', 'is_active': True,
    })
    InspectionStandard.objects.get_or_create(product=m_finished, item_name='运转测试', defaults={
        'standard_desc': '额定转速下运转 5 分钟，无异响、无异常振动', 'tolerance': '噪声≤65dB', 'is_active': True,
    })
    InspectionStandard.objects.get_or_create(product=m_finished, item_name='绝缘电阻', defaults={
        'standard_desc': '使用 500V 兆欧表测量', 'tolerance': '≥2MΩ', 'is_active': True,
    })

    # ── 16. 库存数据 ──
    Inventory.objects.get_or_create(material=m_raw_1, warehouse=wh_raw, defaults={'quantity': 3500, 'locked_quantity': 500})
    Inventory.objects.get_or_create(material=m_raw_2, warehouse=wh_raw, defaults={'quantity': 200, 'locked_quantity': 50})
    Inventory.objects.get_or_create(material=m_finished, warehouse=wh_finished, defaults={'quantity': 45})

    # 出入库记录
    for i in range(5):
        d = date.today() - timedelta(days=i * 5)
        InventoryTransaction.objects.get_or_create(
            transaction_no=f'IN{d.strftime("%y%m%d")}01',
            defaults={'transaction_type': 'purchase_in', 'material': m_raw_1, 'quantity': 200,
                       'warehouse': wh_raw, 'operator': storekeeper, 'remark': f'采购入库-第{i+1}批'}
        )
        InventoryTransaction.objects.get_or_create(
            transaction_no=f'OUT{d.strftime("%y%m%d")}01',
            defaults={'transaction_type': 'produce_in', 'material': m_finished, 'quantity': 15,
                       'warehouse': wh_finished, 'source_doc_type': 'work_order', 'operator': storekeeper,
                       'remark': f'生产完工入库'}
        )

    # ── 17. 更多销售订单 ──
    for i, st in enumerate(['completed', 'shipped', 'completed']):
        SalesOrder.objects.get_or_create(so_no=f'SO20260400{i+1}', defaults={
            'customer': customer, 'product': m_finished, 'order_quantity': 30,
            'delivered_quantity': 30, 'unit_price': 1200, 'total_amount': 36000,
            'scheduled_date': date.today() - timedelta(days=(2-i)*10),
            'status': st, 'sales_person': salesman, 'created_by': salesman,
        })

    print("种子数据填充完成！")


if __name__ == '__main__':
    seed()
