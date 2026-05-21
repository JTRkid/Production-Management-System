"""
项目根 URL 路由配置 — 生产管理系统

API 路由结构：
  /api/v1/auth/        — 登录/用户管理/车间/操作日志
  /api/v1/sys-admin/   — 系统管理（预留）
  /api/v1/business/    — 客户/销售订单/供应商/采购订单
  /api/v1/base-data/   — 物料/BOM/工艺路线/工作中心/设备
  /api/v1/prod-plan/   — 生产计划
  /api/v1/work-order/  — 生产工单
  /api/v1/prod-track/  — 报工记录
  /api/v1/quality/     — 检验标准/检验记录
  /api/v1/inventory/   — 仓库/库存/出入库
  /api/v1/dashboard/   — 报表看板（聚合查询）
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.views.decorators.clickjacking import xframe_options_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    # ── 各业务模块路由 ──
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/sys-admin/', include('apps.sys_admin.urls')),
    path('api/v1/business/', include('apps.business.urls')),
    path('api/v1/base-data/', include('apps.base_data.urls')),
    path('api/v1/prod-plan/', include('apps.prod_plan.urls')),
    path('api/v1/work-order/', include('apps.work_order.urls')),
    path('api/v1/prod-track/', include('apps.prod_track.urls')),
    path('api/v1/quality/', include('apps.quality.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', xframe_options_exempt(serve), {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
