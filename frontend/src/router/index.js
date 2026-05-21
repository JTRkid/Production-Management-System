/** 路由配置 — 生产管理系统 */

import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: { title: '生产看板' },
      },
      {
        path: 'dashboard/reports',
        name: 'DashboardReports',
        component: () => import('@/views/dashboard/Reports.vue'),
        meta: { title: '生产报表' },
      },
      // 系统管理
      {
        path: 'sys-admin/users',
        name: 'SysUsers',
        component: () => import('@/views/sys-admin/Users.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'sys-admin/workshops',
        name: 'SysWorkshops',
        component: () => import('@/views/sys-admin/Workshops.vue'),
        meta: { title: '车间管理' },
      },
      {
        path: 'sys-admin/logs',
        name: 'SysLogs',
        component: () => import('@/views/sys-admin/Logs.vue'),
        meta: { title: '操作日志' },
      },
      // 业务管理
      {
        path: 'business/customers',
        name: 'BizCustomers',
        component: () => import('@/views/business/Customers.vue'),
        meta: { title: '客户管理' },
      },
      {
        path: 'business/sales-orders',
        name: 'BizSalesOrders',
        component: () => import('@/views/business/SalesOrders.vue'),
        meta: { title: '销售订单' },
      },
      {
        path: 'business/suppliers',
        name: 'BizSuppliers',
        component: () => import('@/views/business/Suppliers.vue'),
        meta: { title: '供应商管理' },
      },
      {
        path: 'business/purchase-orders',
        name: 'BizPurchaseOrders',
        component: () => import('@/views/business/PurchaseOrders.vue'),
        meta: { title: '采购订单' },
      },
      // 基础数据
      {
        path: 'base-data/materials',
        name: 'BaseMaterials',
        component: () => import('@/views/base-data/Materials.vue'),
        meta: { title: '物料主数据' },
      },
      {
        path: 'base-data/bom',
        name: 'BaseBOM',
        component: () => import('@/views/base-data/BOM.vue'),
        meta: { title: 'BOM管理' },
      },
      {
        path: 'base-data/routes',
        name: 'BaseRoutes',
        component: () => import('@/views/base-data/Routes.vue'),
        meta: { title: '工艺路线' },
      },
      {
        path: 'base-data/work-centers',
        name: 'BaseWorkCenters',
        component: () => import('@/views/base-data/WorkCenters.vue'),
        meta: { title: '工作中心' },
      },
      {
        path: 'base-data/equipment',
        name: 'BaseEquipment',
        component: () => import('@/views/base-data/Equipment.vue'),
        meta: { title: '设备台账' },
      },
      // 生产计划
      {
        path: 'prod-plan/plans',
        name: 'ProdPlans',
        component: () => import('@/views/prod-plan/Plans.vue'),
        meta: { title: '生产计划' },
      },
      // 工单管理
      {
        path: 'work-order/list',
        name: 'WorkOrderList',
        component: () => import('@/views/work-order/List.vue'),
        meta: { title: '工单列表' },
      },
      // 过程跟踪
      {
        path: 'prod-track/reports',
        name: 'ProdReports',
        component: () => import('@/views/prod-track/Reports.vue'),
        meta: { title: '报工记录' },
      },
      {
        path: 'prod-track/kanban',
        name: 'ProdKanban',
        component: () => import('@/views/prod-track/Kanban.vue'),
        meta: { title: '生产看板' },
      },
      // 质量管理
      {
        path: 'quality/standards',
        name: 'QualityStandards',
        component: () => import('@/views/quality/Standards.vue'),
        meta: { title: '检验标准' },
      },
      {
        path: 'quality/inspections',
        name: 'QualityInspections',
        component: () => import('@/views/quality/Inspections.vue'),
        meta: { title: '检验记录' },
      },
      // 库存管理
      {
        path: 'inventory/warehouses',
        name: 'InvWarehouses',
        component: () => import('@/views/inventory/Warehouses.vue'),
        meta: { title: '仓库管理' },
      },
      {
        path: 'inventory/stock',
        name: 'InvStock',
        component: () => import('@/views/inventory/Stock.vue'),
        meta: { title: '库存查询' },
      },
      {
        path: 'inventory/transactions',
        name: 'InvTransactions',
        component: () => import('@/views/inventory/Transactions.vue'),
        meta: { title: '出入库记录' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

/**
 * 全局路由守卫
 * - 已登录用户访问 /login → 重定向到 dashboard
 * - 未登录用户访问非公开页面 → 重定向到 /login
 */
router.beforeEach((to, from, next) => {
  const token = sessionStorage.getItem('access_token')
  const user = JSON.parse(sessionStorage.getItem('user') || 'null')

  if (to.meta.public) {
    // 公开页面：已登录时不允许再访问登录页，直接跳转首页
    if (token && to.path === '/login') {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    // 受保护页面：无 token 则跳转登录
    if (!token) {
      next('/login')
    } else {
      next()
    }
  }
})

export default router
