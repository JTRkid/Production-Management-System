/**
 * API 层 — 生产管理系统
 *
 * 基于 axios 封装的统一 HTTP 客户端。
 * - 自动附加 JWT Token 到请求头
 * - 401 时自动尝试 refresh token 续期
 * - 非 401 错误统一弹出 Element Plus 错误提示
 * - 响应拦截器自动剥离 axios 外层，直接返回 data
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

// 生产环境用相对路径（Nginx 反向代理），开发环境直连后端
const BASE_URL = import.meta.env.PROD
  ? '/api/v1'
  : 'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: BASE_URL, timeout: 15000 })

/** 请求拦截器：自动注入 Authorization: Bearer <token> */
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
}, (error) => Promise.reject(error))

/**
 * 响应拦截器
 * - 成功：直接返回 response.data（剥离 axios 包装）
 * - 401：尝试用 refresh token 续期一次，失败则跳转登录页
 * - 其他错误：弹出后端返回的 message 或通用提示
 */
api.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        // 尝试使用 refresh token 续期（仅重试一次）
        const refreshToken = sessionStorage.getItem('refresh_token')
        if (refreshToken && !error.config._retry) {
          error.config._retry = true
          try {
            const res = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh: refreshToken })
            sessionStorage.setItem('access_token', res.data.access)
            error.config.headers.Authorization = `Bearer ${res.data.access}`
            return api(error.config) // 续期成功，重放原请求
          } catch {
            // refresh token 也过期了，清除登录态
            sessionStorage.clear()
            window.location.href = '/login'
            return Promise.reject(error)
          }
        }
        // 无 refresh token 或已重试过，跳转登录
        sessionStorage.clear()
        window.location.href = '/login'
      } else {
        ElMessage.error(error.response.data?.message || '请求失败')
      }
    }
    return Promise.reject(error)
  },
)

export default api

// ── 认证 ──
export const authAPI = {
  login: (data) => api.post('/auth/login/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
}

// ── 用户 / 车间 / 日志 ──
export const userAPI = {
  list: (params) => api.get('/auth/users/', { params }),
  create: (data) => api.post('/auth/users/', data),
  update: (id, data) => api.put(`/auth/users/${id}/`, data),
  delete: (id) => api.delete(`/auth/users/${id}/`),
  resetPassword: (id) => api.post(`/auth/users/${id}/reset_password/`),
  toggleActive: (id) => api.post(`/auth/users/${id}/toggle_active/`),
}

export const workshopAPI = {
  list: (params) => api.get('/auth/workshops/', { params }),
  create: (data) => api.post('/auth/workshops/', data),
  update: (id, data) => api.put(`/auth/workshops/${id}/`, data),
  delete: (id) => api.delete(`/auth/workshops/${id}/`),
}

export const logAPI = {
  list: (params) => api.get('/auth/logs/', { params }),
}

// ── 业务管理 ──
export const customerAPI = {
  list: (params) => api.get('/business/customers/', { params }),
  create: (data) => api.post('/business/customers/', data),
  update: (id, data) => api.put(`/business/customers/${id}/`, data),
  delete: (id) => api.delete(`/business/customers/${id}/`),
}

export const salesOrderAPI = {
  list: (params) => api.get('/business/sales-orders/', { params }),
  create: (data) => api.post('/business/sales-orders/', data),
  update: (id, data) => api.put(`/business/sales-orders/${id}/`, data),
  delete: (id) => api.delete(`/business/sales-orders/${id}/`),
  approve: (id) => api.post(`/business/sales-orders/${id}/approve/`),
  cancel: (id) => api.post(`/business/sales-orders/${id}/cancel/`),
}

export const supplierAPI = {
  list: (params) => api.get('/business/suppliers/', { params }),
  create: (data) => api.post('/business/suppliers/', data),
  update: (id, data) => api.put(`/business/suppliers/${id}/`, data),
  delete: (id) => api.delete(`/business/suppliers/${id}/`),
}

export const purchaseOrderAPI = {
  list: (params) => api.get('/business/purchase-orders/', { params }),
  create: (data) => api.post('/business/purchase-orders/', data),
  update: (id, data) => api.put(`/business/purchase-orders/${id}/`, data),
  delete: (id) => api.delete(`/business/purchase-orders/${id}/`),
  approve: (id) => api.post(`/business/purchase-orders/${id}/approve/`),
  receive: (id, data) => api.post(`/business/purchase-orders/${id}/receive/`, data),
}

// ── 基础数据 ──
export const materialAPI = {
  list: (params) => api.get('/base-data/materials/', { params }),
  active: () => api.get('/base-data/materials/active/'),
  create: (data) => api.post('/base-data/materials/', data),
  update: (id, data) => api.put(`/base-data/materials/${id}/`, data),
  delete: (id) => api.delete(`/base-data/materials/${id}/`),
}

export const bomAPI = {
  list: (params) => api.get('/base-data/bom-items/', { params }),
  tree: (materialId) => api.get('/base-data/bom-items/tree/', { params: { material_id: materialId } }),
  create: (data) => api.post('/base-data/bom-items/', data),
  update: (id, data) => api.put(`/base-data/bom-items/${id}/`, data),
  delete: (id) => api.delete(`/base-data/bom-items/${id}/`),
}

export const routeAPI = {
  list: (params) => api.get('/base-data/routes/', { params }),
  steps: (id) => api.get(`/base-data/routes/${id}/steps/`),
  create: (data) => api.post('/base-data/routes/', data),
  update: (id, data) => api.put(`/base-data/routes/${id}/`, data),
  delete: (id) => api.delete(`/base-data/routes/${id}/`),
}

export const routeStepAPI = {
  list: (params) => api.get('/base-data/route-steps/', { params }),
  create: (data) => api.post('/base-data/route-steps/', data),
  update: (id, data) => api.put(`/base-data/route-steps/${id}/`, data),
  delete: (id) => api.delete(`/base-data/route-steps/${id}/`),
}

export const workCenterAPI = {
  list: (params) => api.get('/base-data/work-centers/', { params }),
  create: (data) => api.post('/base-data/work-centers/', data),
  update: (id, data) => api.put(`/base-data/work-centers/${id}/`, data),
  delete: (id) => api.delete(`/base-data/work-centers/${id}/`),
}

export const equipmentAPI = {
  list: (params) => api.get('/base-data/equipment/', { params }),
  create: (data) => api.post('/base-data/equipment/', data),
  update: (id, data) => api.put(`/base-data/equipment/${id}/`, data),
  delete: (id) => api.delete(`/base-data/equipment/${id}/`),
}

// ── 生产计划 ──
export const prodPlanAPI = {
  list: (params) => api.get('/prod-plan/production-plans/', { params }),
  create: (data) => api.post('/prod-plan/production-plans/', data),
  update: (id, data) => api.put(`/prod-plan/production-plans/${id}/`, data),
  delete: (id) => api.delete(`/prod-plan/production-plans/${id}/`),
  approve: (id) => api.post(`/prod-plan/production-plans/${id}/approve/`),
  release: (id) => api.post(`/prod-plan/production-plans/${id}/release/`),
  cancel: (id) => api.post(`/prod-plan/production-plans/${id}/cancel/`),
}

// ── 工单管理 ──
export const workOrderAPI = {
  list: (params) => api.get('/work-order/work-orders/', { params }),
  create: (data) => api.post('/work-order/work-orders/', data),
  update: (id, data) => api.put(`/work-order/work-orders/${id}/`, data),
  delete: (id) => api.delete(`/work-order/work-orders/${id}/`),
  dispatch: (id) => api.post(`/work-order/work-orders/${id}/dispatch/`),
  start: (id) => api.post(`/work-order/work-orders/${id}/start/`),
  complete: (id) => api.post(`/work-order/work-orders/${id}/complete/`),
  close: (id) => api.post(`/work-order/work-orders/${id}/close/`),
  report: (id, data) => api.post(`/work-order/work-orders/${id}/report/`, data),
}

// ── 过程跟踪 ──
export const workReportAPI = {
  list: (params) => api.get('/prod-track/work-reports/', { params }),
  create: (data) => api.post('/prod-track/work-reports/', data),
  myReports: (params) => api.get('/prod-track/work-reports/my_reports/', { params }),
}

// ── 质量管理 ──
export const inspectionStandardAPI = {
  list: (params) => api.get('/quality/standards/', { params }),
  create: (data) => api.post('/quality/standards/', data),
  update: (id, data) => api.put(`/quality/standards/${id}/`, data),
  delete: (id) => api.delete(`/quality/standards/${id}/`),
}

export const inspectionRecordAPI = {
  list: (params) => api.get('/quality/records/', { params }),
  create: (data) => api.post('/quality/records/', data),
  update: (id, data) => api.put(`/quality/records/${id}/`, data),
  delete: (id) => api.delete(`/quality/records/${id}/`),
}

// ── 库存管理 ──
export const warehouseAPI = {
  list: (params) => api.get('/inventory/warehouses/', { params }),
  create: (data) => api.post('/inventory/warehouses/', data),
  update: (id, data) => api.put(`/inventory/warehouses/${id}/`, data),
  delete: (id) => api.delete(`/inventory/warehouses/${id}/`),
}

export const inventoryAPI = {
  list: (params) => api.get('/inventory/inventories/', { params }),
}

export const transactionAPI = {
  list: (params) => api.get('/inventory/transactions/', { params }),
  inbound: (data) => api.post('/inventory/transactions/inbound/', data),
  outbound: (data) => api.post('/inventory/transactions/outbound/', data),
}

// ── 报表看板 ──
export const dashboardAPI = {                 // 导出一个对象，其他文件通过 import { dashboardAPI } from '@/api' 引用
  overview: () => api.get('/dashboard/overview/'),      // GET 请求：获取首页看板概览数据
  prodDaily: () => api.get('/dashboard/prod_daily/'),   // GET 请求：获取生产日报数据
  completionRate: () => api.get('/dashboard/completion_rate/'),   // GET 请求：获取生产计划完成率数据
  qualityTrend: () => api.get('/dashboard/quality_trend/'),   // GET 请求：获取质量趋势数据
}
