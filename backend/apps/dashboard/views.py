"""报表看板 — 聚合查询 API"""

from datetime import date, datetime, timedelta
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import User
from apps.business.models import SalesOrder
from apps.prod_plan.models import ProductionPlan
from apps.work_order.models import WorkOrder
from apps.quality.models import InspectionRecord


class DashboardViewSet(viewsets.ViewSet):
    """报表看板：提供总览、生产日报、工单完成率、质量趋势等聚合数据"""

    @action(methods=['get'], detail=False)
    def overview(self, request):
        """总览数据：工单统计、本月产量、不良率、待处理订单、本月销售额"""
        today = date.today()
        month_start = today.replace(day=1)

        wo_qs = WorkOrder.objects.all()
        total_wo = wo_qs.count()
        in_progress_wo = wo_qs.filter(status='in_progress').count()
        completed_wo = wo_qs.filter(status='completed').count()
        overdue_wo = wo_qs.filter(
            status__in=['dispatched', 'in_progress'],
        ).count()

        month_completed_qty = WorkOrder.objects.filter(
            status='completed', completed_at__gte=month_start
        ).aggregate(total=Sum('completed_quantity'))['total'] or 0

        month_inspections = InspectionRecord.objects.filter(inspected_at__gte=month_start)
        total_inspected = month_inspections.aggregate(n=Sum('sample_quantity'))['n'] or 0
        total_defects = month_inspections.aggregate(n=Sum('defect_quantity'))['n'] or 0
        defect_rate = round(total_defects / total_inspected * 100, 2) if total_inspected else 0

        pending_orders = SalesOrder.objects.filter(status='approved').count()
        month_sales_amount = SalesOrder.objects.filter(
            status__in=['completed', 'shipped'],
            updated_at__gte=month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        return Response({
            'code': 200,
            'data': {
                'total_wo': total_wo,
                'in_progress_wo': in_progress_wo,
                'completed_wo': completed_wo,
                'overdue_wo': overdue_wo,
                'month_completed_qty': month_completed_qty,
                'defect_rate': defect_rate,
                'pending_orders': pending_orders,
                'month_sales_amount': float(month_sales_amount),
            },
        })

    @action(methods=['get'], detail=False)
    def prod_daily(self, request):
        """生产日报"""
        today = date.today()
        day_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))

        # 当日开工工单
        started_wo = WorkOrder.objects.filter(started_at__gte=day_start).count()

        # 当日完工工单
        completed_today = WorkOrder.objects.filter(
            status='completed', completed_at__gte=day_start
        )
        completed_wo = completed_today.count()
        actual_qty = completed_today.aggregate(total=Sum('completed_quantity'))['total'] or 0
        defect_qty = completed_today.aggregate(total=Sum('defect_quantity'))['total'] or 0
        qualified_qty = actual_qty - defect_qty

        # 当日计划产量（从生产计划获取当日计划数，取正在进行中的工单总数）
        plan_qty = WorkOrder.objects.filter(
            status__in=['dispatched', 'in_progress']
        ).aggregate(total=Sum('order_quantity'))['total'] or 0

        # 在线工人数（有报工记录的）
        online_workers = User.objects.filter(
            work_reports__report_time__gte=day_start
        ).distinct().count()

        # 设备稼动率（当日有报工的工作中心 / 已有工单的工作中心）
        active_centers = WorkOrder.objects.filter(
            work_reports__report_time__gte=day_start
        ).values('route__steps__work_center').distinct().count()
        total_centers = WorkOrder.objects.exclude(
            route__isnull=True
        ).values('route__steps__work_center').distinct().count()
        utilization_rate = min(round(active_centers / total_centers * 100, 1), 100) if total_centers else 0

        return Response({
            'code': 200,
            'data': {
                'date': str(today),
                'plan_qty': plan_qty,
                'actual_qty': actual_qty,
                'qualified_qty': qualified_qty,
                'defect_qty': defect_qty,
                'started_wo': started_wo,
                'completed_wo': completed_wo,
                'utilization_rate': utilization_rate,
                'online_workers': online_workers,
            },
        })

    @action(methods=['get'], detail=False)
    def completion_rate(self, request):
        """工单完成率（近30天）"""
        days = 30
        total_all = WorkOrder.objects.count()
        result = []
        for i in range(days):
            d = date.today() - timedelta(days=i)
            day_end = timezone.make_aware(datetime.combine(d + timedelta(days=1), datetime.min.time()))

            completed = WorkOrder.objects.filter(
                status='completed', completed_at__lt=day_end
            ).count()
            rate = round(completed / total_all * 100, 1) if total_all else 0

            result.append({
                'date': str(d),
                'total_wo': total_all,
                'completed_wo': completed,
                'completion_rate': rate,
            })

        return Response({'code': 200, 'data': result[::-1]})

    @action(methods=['get'], detail=False)
    def quality_trend(self, request):
        """近30天不良率趋势"""
        days = 30
        result = []
        for i in range(days):
            d = date.today() - timedelta(days=i)
            ins = InspectionRecord.objects.filter(inspected_at__date=d)
            total = ins.aggregate(n=Sum('sample_quantity'))['n'] or 0
            defect = ins.aggregate(n=Sum('defect_quantity'))['n'] or 0
            rate = round(defect / total * 100, 2) if total else 0
            result.append({'date': str(d), 'defect_rate': rate, 'total_inspected': total})

        return Response({'code': 200, 'data': result[::-1]})
